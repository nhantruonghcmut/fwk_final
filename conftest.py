"""
Pytest configuration and fixtures for test automation framework.
Implements config hierarchy: Global → Environment → Suite → CLI
"""
import os
import json
import pytest
import threading
import subprocess
import time
import socket
from typing import Generator, Dict, Any
from playwright.sync_api import Page
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from src.core.utils.config_manager import ConfigManager
from src.core.utils.test_context import TestContext
from src.core.utils.report_logger import ReportLogger
from src.core.utils.allure_environment_helper import AllureEnvironmentHelper
from src.core.utils.allure_report_generator import AllureReportGenerator
from src.core.browser.browser_factory import BrowserFactory
from src.core.browser.browser_type import BrowserType
from src.core.utils.screenshot_util import ScreenshotUtil
from src.core.listener.test_listener import TestListener
from src.core.listener.suite_listener import SuiteListener
from appium.webdriver.appium_service import AppiumService
from src.core.utils.adb_util import ADBUtil
# ============================================================================
# GLOBAL INSTANCES
# ============================================================================
logger = ReportLogger()
config_manager = ConfigManager(logger)
config_manager._load_base_configs()
screenshot_util = ScreenshotUtil(logger, config_manager)
browser_factory = BrowserFactory()
allure_generator = AllureReportGenerator(logger, config_manager)
suite_listener = SuiteListener(config_manager,browser_factory,logger, allure_generator)
test_listener = TestListener(logger, allure_generator)
allure_helper = AllureEnvironmentHelper()

# Global device locks for parallel execution (prevent concurrent access to same device)
_device_locks = {}


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================
def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (overrides config.yaml)"
    )
    parser.addoption(
        "--mobile",
        action="store_true",
        default=False,
        help="Run mobile tests instead of web"
    )
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to run tests on (overrides config.yaml)"
    )

    if config_manager.is_parallel_enabled():
        number_of_workers = config_manager.get_parallel_workers()
        parser.addoption(
            "--n",
            action="store",
            type=int,
            default=number_of_workers,
            help="Number of parallel workers (overrides config.yaml)"
        )


def pytest_ignore_collect(path, config):
    """
    Ignore collection of files based on directory path.
    - Always ignore src/ directory (framework code)
    - In mobile mode: ignore tests/web/ directory
    - In web mode: ignore tests/mobile/ directory
    """
    import os
    path_str = str(path)
    
    # Always ignore all files in src/ directory (framework code)
    if os.path.sep + "src" + os.path.sep in path_str or path_str.startswith("src" + os.path.sep):
        return True
    
    # Check if this is a test file (Python file)
    if not path_str.endswith(".py"):
        return None
    
    # Get mobile flag from config (may not be available yet, so use try-except)
    try:
        is_mobile = config.getoption("--mobile", default=False)
    except (ValueError, AttributeError):
        # Config option not available yet, skip filtering
        return None
    
    # Normalize path separators for cross-platform compatibility
    normalized_path = path_str.replace("\\", "/")
    
    # In mobile mode: ignore tests/web/ directory
    if is_mobile:
        if "/tests/web/" in normalized_path or normalized_path.startswith("tests/web/"):
            return True
    
    # In web mode (default): ignore tests/mobile/ directory
    else:
        if "/tests/mobile/" in normalized_path or normalized_path.startswith("tests/mobile/"):
            return True
    
    return None

def pytest_configure(config):
    """
    Configure pytest using config.yaml.
    """
    # Detect platform from CLI
    is_mobile = config.getoption("--mobile")
    platform = "mobile" if is_mobile else "web"
    config_manager.set_platform(platform)

    # Set environment from CLI
    environment = config.getoption("--env")
    if environment:
        config_manager.set_environment(environment)

    # ============================================
    # 1. ALLURE SETTINGS
    # ============================================
    
    if config_manager.is_allure_enabled():
        results_dir = config_manager.get_allure_results_directory()
        
        # Debug: Check clean_on_start value
        clean_on_start = config_manager.should_clean_allure_on_start()
        logger.info(f"[ALLURE] clean_on_start config value: {clean_on_start} (type: {type(clean_on_start)})")
        
        # Clean allure results on start if configured
        if clean_on_start:
            import shutil
            from pathlib import Path
            
            results_path = Path(results_dir)
            if results_path.exists():
                logger.info(f"[ALLURE] Cleaning results directory: {results_dir}")
                shutil.rmtree(results_path)
            results_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[ALLURE] Cleaned and recreated results directory: {results_dir}")
        else:
            logger.info(f"[ALLURE] Skipping clean (clean_on_start={clean_on_start})")
        
        logger.info(f"[ALLURE] Results directory: {results_dir}")
    
  
    # ============================================
    # 2. MARKERS
    # ============================================
    markers = config_manager.get_config_value('markers', {})
    if markers:
        logger.debug(f"Markers found: {markers}")
        for marker_name, description in markers.items():
            config.addinivalue_line("markers", f"{marker_name}: {description}")

def pytest_generate_tests(metafunc):   
    logger.debug(f"[DEBUG] from pytest_generate_tests'")

    data_files = config_manager.get_config_value('test_data', {})
    
    # Load all test data files and check for nested keys
    for config_key, file_path in data_files.items():
        logger.debug(f"[DEBUG] Checking test data file: {config_key} -> {file_path}")
        data = config_manager.load_test_data(config_key)
        
        # Check if config_key itself is a fixture name (direct match)
        if config_key in metafunc.fixturenames:
            if config_key in data:
                test_items = data[config_key]
                ids = [d.get("test_id", f"{config_key}_{i}") for i, d in enumerate(test_items)]
                metafunc.parametrize(config_key, test_items, ids=ids)
                logger.info(f"[PARAM] Parametrized test '{config_key}' with {len(test_items)} items")
        
        # Check for nested keys in the loaded data (for cases like colorNote_testsuite_A.yaml)
        if isinstance(data, dict):
            for nested_key, nested_data in data.items():
                if nested_key in metafunc.fixturenames:
                    if isinstance(nested_data, list):
                        ids = [d.get("test_id", f"{nested_key}_{i}") for i, d in enumerate(nested_data)]
                        metafunc.parametrize(nested_key, nested_data, ids=ids)
                        logger.info(f"[PARAM] Parametrized test '{nested_key}' with {len(nested_data)} items from file '{config_key}'")
    if "browser_type" in metafunc.fixturenames:
        browser_list = get_browser_list_from_config()
        metafunc.parametrize("browser_type", browser_list, ids=browser_list)
    if "appium_driver" in metafunc.fixturenames:
        device_list = get_mobile_device_list_from_config()
        ids = [d.get("device_name", f"device_{i}") for i, d in enumerate(device_list)]
        metafunc.parametrize("appium_driver", device_list, ids=ids, indirect=True)

# ============================================================================
# SESSION FIXTURES
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def suite_setup(request ):
    """
    Setup test suite - initialize config and reporting.
    # ALL settings from ConfigManager
    """
    # Validate config
    if not config_manager.validate_config():
        logger.warning("[WARNING] Configuration validation issues detected")
    
    # Setup Allure environment
    if config_manager.is_allure_enabled():
        allure_helper.setup_allure_environment()
    
    # Log config summary
    summary = config_manager.get_config_summary()
    logger.info(f"[CONFIG] Framework Configuration:")
    logger.info(f"   ├─ Environment: {summary.get('environment')}")
    logger.info(f"   ├─ Browser: {summary.get('browser_type')}")
    logger.info(f"   ├─ Parallel: {summary.get('parallel_enabled')}")
    logger.info(f"   ├─ Workers: {summary.get('parallel_workers')}")
    logger.info(f"   ├─ Timeout: {summary.get('default_timeout')}ms")
    logger.info(f"   ├─ Retry: {summary.get('retry_count')}")
    logger.info(f"   └─ Allure: {summary.get('allure_enabled')}")
    
    yield
    



@pytest.fixture(scope="session")
def test_context():
    """Create test context for sharing data across tests."""
    return TestContext()

def pytest_sessionstart(session):
    """
    Hook được gọi khi bắt đầu test session.
    Tích hợp Suite Listener tự động.
    """
    # Đếm số lượng test sẽ chạy
    test_count = len(session.items)
    
    # Gọi suite listener
    suite_listener.on_suite_start("Test Automation Suite", test_count)
    
    logger.info(f"[START] Test session started with {test_count} tests")



# ============================================================================
# FUNCTION FIXTURES - CONFIG HIERARCHY
# ============================================================================

@pytest.fixture(scope="function")
def test_config(request) -> 'Generator[Dict[str, Any]]':
    yield {}


# ============================================================================
# FUNCTION FIXTURES - BROWSER (WEB)
# ============================================================================
def get_browser_list_from_config(request=None):
    """
    Trả về danh sách browser ưu tiên theo thứ tự:
    1. CLI (--browser)
    2. ENV (environment.browser)
    3. Config mặc định (browsers)
    """
    # 1. CLI
    # if request:
    #     cli_browser = request.config.getoption("--browser")
    #     if cli_browser and isinstance(cli_browser, list) and len(cli_browser) > 0:
    #         return cli_browser

    # # 2. ENV
    # env_browser = config_manager.get_config_value("environment.browser", None)
    # if env_browser:
    #     if isinstance(env_browser, list):
    #         return env_browser
    #     return [env_browser]

    # 3. Config mặc định
    browsers_dict = config_manager.get_config_value("browsers", {})
    return list(browsers_dict.keys())


def get_mobile_device_list_from_config():
    """
    Trả về danh sách cấu hình device từ config.yaml.
    """
    devices = config_manager.get_mobile_devices()
    return devices


@pytest.fixture(scope="function")
def browser(request, browser_type, test_config) -> Generator[Page, None, None]:
    """
    Khởi tạo browser instance cho từng loại browser, lấy config chi tiết từ config.yaml.
    """
    # Lấy config chi tiết cho browser_type
    browser_config = config_manager.get_config_value(f"browsers.{browser_type}", {})
    logger.info(f"[BROWSER] Using browser config: {browser_config}")
    # Áp dụng override từ CLI nếu có
    if request.config.getoption("--headless"):
        browser_config["headless"] = True
    slowmo = request.config.getoption("--slowmo")
    if slowmo:
        browser_config["slow_mo"] = slowmo

    browser_type_enum = BrowserType.get_browser_type(browser_type)
    logger.info(f"[BROWSER] Creating browser: {browser_type} with config: {browser_config}")

    try:
        browser_obj, context, page = browser_factory.create_browser_with_page(
            browser_type_enum, **browser_config
        )
        # Set timeout nếu cần
        default_timeout = config_manager.get_default_timeout()
        navigation_timeout = config_manager.get_navigation_timeout()
        page.set_default_timeout(default_timeout)
        page.set_default_navigation_timeout(navigation_timeout)
        setattr(page, "screenshot_util", screenshot_util)
        setattr(page, "logger", logger)
        # Log browser info và configuration
        try:
            browser_version = browser_obj.version if hasattr(browser_obj, 'version') else ""
            context_config = config_manager.get_context_config()
            logger.log_browser_info(
                browser_type=browser_type,
                version=browser_version,
                headless=browser_config.get('headless', False),
                viewport=context_config.get('viewport'),
                user_agent=context_config.get('user_agent'),
                locale=context_config.get('locale'),
                timezone_id=context_config.get('timezone_id'),
                timeout=default_timeout
            )
        except Exception as e:
            logger.debug(f"Failed to log browser info: {e}")
        
        # Lưu context config vào test_context
        test_context = getattr(request.node, "test_context", None)
        if test_context:
            test_context.set("page", page)
            test_context.set_browser_type(browser_type)
            # Lưu browser context config để có thể truy cập sau này
            context_config = config_manager.get_context_config()
            if context_config:
                test_context.set_browser_context_config(context_config)
                logger.debug(f"[BROWSER] Context config saved to test_context: {context_config}")
        
        # Start tracing nếu được bật trong config
        if config_manager.is_trace_enabled():
            browser_factory.start_tracing(context)
            logger.info("[TRACE] Tracing started for test")
        
        yield page
    finally:
        current_thread = threading.current_thread()
        browser_factory.close_browser_for_thread(current_thread)
        browser_factory.close_context_for_thread(current_thread)


# ============================================================================
# FUNCTION FIXTURES - MOBILE
# ============================================================================
def get_appium_server_url(port: int) -> str:
    """Tạo URL Appium server dựa trên cổng."""
    return f"http://localhost:{port}"

def is_port_available(port: int, host: str = "localhost") -> bool:
    """Kiểm tra port có trống hay không."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex((host, port))
        return result != 0
    finally:
        sock.close()


def get_available_port(base_port: int, max_attempts: int = 20) -> int:
    """Tìm port trống bắt đầu từ base_port."""
    for offset in range(max_attempts):
        port = base_port + offset
        if is_port_available(port):
            return port
    
    raise RuntimeError(
        f"Không tìm được port trống trong range {base_port}-{base_port + max_attempts}"
    )


def get_port_for_worker(worker_id: str, base_port: int = 4723) -> int:
    """Allocate port dựa trên worker_id."""
    if worker_id == "master":
        suggested_port = base_port
    else:
        # gw0, gw1, gw2, ... -> cách nhau 10 port
        worker_num = int(worker_id.replace("gw", ""))
        suggested_port = base_port + (worker_num * 10)
    
    # Tìm port trống gần suggested_port
    actual_port = get_available_port(suggested_port)
    logger.info(f"[{worker_id}] Allocated port: {actual_port}")
    
    return actual_port


@pytest.fixture(scope="session")
def appium_service(request):
    """
    Start Appium service per worker session (one service per worker).
    
    Ensures:
    - Each worker gets a different port
    - Automatically finds available port if suggested port is taken
    - Cleans up service when worker session ends
    """
    # Get worker_id safely (may be "master" if not using xdist)
    # In pytest-xdist, worker_id is available via request.config.workerinput
    try:
        # Try to get worker_id from pytest-xdist workerinput
        if hasattr(request.config, 'workerinput') and request.config.workerinput:
            # worker = request.config.workerinput.get('workerid', 'master')
            worker = getattr(request.config, "workerinput", {}).get("workerid", "master")
        else:
            # Not using xdist or master process
            worker = "master"
    except (AttributeError, KeyError, TypeError):
        # Fallback to master if workerinput not available
        worker = "master"
    
    start_port = get_port_for_worker(worker)

    logger.info(f"[{worker}] Starting Appium service on port {start_port}...")

    service = AppiumService()
    
    try:
        # Start Appium service
        service.start(args=['--port', str(start_port), '--relaxed-security'])
        
        # Wait for service to start
        time.sleep(2)
        
        # Verify service is running
        if service.is_running:
            logger.info(f"[{worker}] Appium service running on port {start_port}")
            # Return dict containing service and port
            yield {
                'service': service,
                'port': start_port,
                'url': f"http://localhost:{start_port}",
                'worker_id': worker
            }
        else:
            raise RuntimeError(f"Appium service failed to start on port {start_port}")
    
    except Exception as e:
        logger.error(f"[{worker}] Error starting Appium service: {e}")
        raise
    
    finally:
        # Cleanup: stop service
        if service.is_running:
            logger.info(f"[{worker}] 🛑 Stopping Appium service on port {start_port}")
            try:
                service.stop()
            except Exception as e:
                logger.warning(f"[{worker}] Error stopping Appium service: {e}")


@pytest.fixture(scope="session")
def appium_url(appium_service):
    """Lấy URL từ AppiumService."""
    return appium_service['url']



@pytest.fixture(scope="function")
def appium_driver(request, appium_service) -> Generator[webdriver.Remote, None, None]:
    """
    Create Appium driver for mobile testing - SCOPE FUNCTION.
    Each test function gets a new driver, ensuring isolated environment.
    Integrates ADBUtil to check device before connecting to Appium.
    
    Note: appium_service is session-scoped (one per worker), but driver is function-scoped.
    """
    if not request.config.getoption("--mobile"):
        logger.warning("Mobile test skipped")
        pytest.skip("Skipping mobile test in web mode")
    
    device_cfg = request.param
    option = None
    driver = None
    worker_info = appium_service.get('worker_id', 'master')
    
    # Validate required keys
    required_keys = ["platform_name", "platform_version", "device_name", "automation_name"]
    missing_keys = [k for k in required_keys if k not in device_cfg or not device_cfg[k]]
    if missing_keys:
        pytest.skip(f"Missing device configuration: {', '.join(missing_keys)}")
    
    platform = device_cfg.get("platform_name", "").lower()
    
    # Thread lock for device access (prevent concurrent access to same device)
    # Use global locks dictionary to persist across fixture calls
    import threading
    global _device_locks
    
    device_id = device_cfg.get("udid") or device_cfg.get("device_name", "")
    if device_id not in _device_locks:
        _device_locks[device_id] = threading.Lock()
    
    device_lock = _device_locks[device_id]
    
    # Use lock to prevent concurrent access to same device (only during driver creation)
    with device_lock:
        # Android: need appPackage and appActivity
        if platform == "android":       
            # Get device_id (udid) from config or device_name
            device_id = device_cfg.get("udid") or device_cfg.get("device_name", "")
            
            # Use ADBUtil to check device
            adb_util = ADBUtil()
            
            # Check if device is connected
            logger.info(f"[{worker_info}] [ADB] Checking device: {device_id}")
            if not adb_util.is_device_connected(device_id):
                # If device with exact ID not found, try to find available device
                devices = adb_util.get_devices()
                if not devices:
                    pytest.skip(f"No devices found. Please check ADB connection.")
                else:
                    logger.warning(f"[{worker_info}] [ADB] Device {device_id} not found. Available devices: {[d['device_id'] for d in devices]}")
                    # If devices available, use first one
                    device_id = devices[0]['device_id']
                    logger.info(f"[{worker_info}] [ADB] Using device: {device_id}")
            
            # Wait for device ready
            logger.info(f"[{worker_info}] [ADB] Waiting for device {device_id} to be ready...")
            if not adb_util.wait_for_device(device_id, timeout=30):
                pytest.skip(f"Device {device_id} not ready after 30 seconds")
            
            logger.info(f"[{worker_info}] [ADB] Device {device_id} is ready")
            
            # Get device info for logging
            device_info = adb_util.get_device_info(device_id)
            if device_info:
                logger.info(f"[{worker_info}] [ADB] Device info: {device_info}")
            
            option = UiAutomator2Options()
            
            # Get mobile context config (timezone, locale) - can be overridden per device
            mobile_context = config_manager.get_mobile_context_config()
            
            # Apply timezone and locale from config (if not overridden in device_cfg)
            # Android uses 'timeZone' capability
            if 'timezone' not in device_cfg and mobile_context.get('timezone'):
                option.set_capability('timeZone', mobile_context['timezone'])
                logger.debug(f"[{worker_info}] [APPIUM] Applied timezone from config: {mobile_context['timezone']}")
            
            # Locale works for both platforms
            if 'locale' not in device_cfg and mobile_context.get('locale'):
                option.set_capability('locale', mobile_context['locale'])
                logger.debug(f"[{worker_info}] [APPIUM] Applied locale from config: {mobile_context['locale']}")
            
            for k, v in device_cfg.items():
                # Map snake_case to camelCase for Appium capabilities
                if k == "platform_name":
                    option.platform_name = v
                elif k == "platform_version":
                    option.platform_version = v
                elif k == "device_name":
                    option.device_name = v
                elif k == "automation_name":
                    option.automation_name = v
                elif k == "app_package":
                    option.app_package = v
                elif k == "app_activity":
                    option.app_activity = v
                elif k == "udid":
                    option.udid = v
                elif k == "no_reset":
                    option.no_reset = v
                elif k == "full_reset":
                    option.full_reset = v
                elif k == "new_command_timeout":
                    option.new_command_timeout = v
                elif k == "timezone":
                    # Android: timeZone capability
                    option.set_capability('timeZone', v)
                    logger.debug(f"[{worker_info}] [APPIUM] Applied timezone from device config: {v}")
                elif k == "locale":
                    # Both platforms: locale capability
                    option.set_capability('locale', v)
                    logger.debug(f"[{worker_info}] [APPIUM] Applied locale from device config: {v}")
                else:
                    option.set_capability(k, v)
            
            # Ensure udid is set
            if not hasattr(option, 'udid') or not option.udid:
                option.udid = device_id
        
        # iOS: need bundleId
        elif platform == "ios":
            if "bundleId" not in device_cfg or not device_cfg["bundleId"]:
                pytest.skip("Missing iOS configuration: bundleId")
            option = XCUITestOptions()
            
            # Get mobile context config (timezone, locale) - can be overridden per device
            mobile_context = config_manager.get_mobile_context_config()
            
            # Apply timezone and locale from config (if not overridden in device_cfg)
            # iOS uses 'appTimeZone' capability
            if 'timezone' not in device_cfg and mobile_context.get('timezone'):
                option.set_capability('appTimeZone', mobile_context['timezone'])
                logger.debug(f"[{worker_info}] [APPIUM] Applied timezone from config: {mobile_context['timezone']}")
            
            # Locale works for both platforms
            if 'locale' not in device_cfg and mobile_context.get('locale'):
                option.set_capability('locale', mobile_context['locale'])
                logger.debug(f"[{worker_info}] [APPIUM] Applied locale from config: {mobile_context['locale']}")
            
            for k, v in device_cfg.items():
                if k == "timezone":
                    # iOS: appTimeZone capability
                    option.set_capability('appTimeZone', v)
                    logger.debug(f"[{worker_info}] [APPIUM] Applied timezone from device config: {v}")
                elif k == "locale":
                    # Both platforms: locale capability
                    option.set_capability('locale', v)
                    logger.debug(f"[{worker_info}] [APPIUM] Applied locale from device config: {v}")
                else:
                    option.set_capability(k, v)
        else:
            pytest.skip(f"Unsupported platform: {platform}")
        
        logger.info(f"[{worker_info}] [APPIUM] Capabilities: {option.to_capabilities()}")
        
        # Create driver with retry (inside lock to prevent concurrent creation)
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                logger.info(f"[{worker_info}] [APPIUM] Connecting to Appium server (attempt {attempt + 1}/{max_retries})...")
                driver = webdriver.Remote(appium_service['url'], options=option)
                logger.info(f"[{worker_info}] [APPIUM-DONE] Appium driver created successfully")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"[{worker_info}] [APPIUM] Connection failed (attempt {attempt + 1}): {str(e)}")
                    logger.info(f"[{worker_info}] [APPIUM] Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"[{worker_info}] [APPIUM-ERROR] Cannot connect to Appium after {max_retries} attempts")
                    raise
        
        # Log mobile info và configuration sau khi driver được tạo
        try:
            device_name = device_cfg.get("device_name", "")
            platform_version = device_cfg.get("platform_version", "")
            mobile_context = config_manager.get_mobile_context_config()
            
            # Get capabilities for logging
            capabilities = option.to_capabilities() if hasattr(option, 'to_capabilities') else {}
            
            logger.log_mobile_info(
                platform=platform,
                device_name=device_name,
                version=platform_version,
                automation_name=device_cfg.get("automation_name"),
                udid=device_cfg.get("udid"),
                app_package=device_cfg.get("app_package") if platform == "android" else None,
                app_activity=device_cfg.get("app_activity") if platform == "android" else None,
                bundle_id=device_cfg.get("bundleId") if platform == "ios" else None,
                timezone=mobile_context.get('timezone') or device_cfg.get('timezone'),
                locale=mobile_context.get('locale') or device_cfg.get('locale'),
                no_reset=device_cfg.get("no_reset"),
                full_reset=device_cfg.get("full_reset")
            )
        except Exception as e:
            logger.debug(f"Failed to log mobile info: {e}")
    
    # Set device_name and platform to test_context
    test_context = getattr(request.node, "test_context", None)
    if test_context:
        device_name = device_cfg.get("device_name", "")
        test_context.set_device_name(device_name)
        test_context.set_platform("mobile")
    setattr(driver, "test_context", test_context)
    setattr(driver, "screenshot_util", screenshot_util)
    setattr(driver, "logger", logger)
    # Yield driver outside lock to allow concurrent test execution
    try:
        yield driver
    except Exception as e:
        logger.error(f"[{worker_info}] [APPIUM] ❌ Error during test execution: {str(e)}")
        raise
    finally:
        # Cleanup
        if driver is not None:
            try:
                driver.quit()
                logger.debug(f"[{worker_info}] 🧹 Appium driver closed")
            except Exception as e:
                logger.warning(f"[{worker_info}] Error closing driver: {str(e)}")



@pytest.fixture(scope="function")
def app_urls(request, test_config) -> dict[str, str]:
    """
    Provide base URLs for all apps as a dict.
    Example: { "b2c_web": "...", "b2b_web": "...", ... }
    """
    # Lấy danh sách apps từ environment config
    apps = config_manager.get_config_value("apps", {})
    base_urls = {}
    for app_name, app_cfg in apps.items():
        url = app_cfg.get("url", "")
        if url:
            base_urls[app_name] = url
    if not base_urls:
        logger.warning("[WARNING] No URL configured")
    # logger.info(f"Base URLs: {base_urls}")
    return base_urls

# ============================================================================
# PYTEST HOOKS
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Generate test report and take screenshots.
    # Screenshot config from ConfigManager
    """
    # Try to set test_data to test_context when fixtures are resolved (during call phase)
    if call.when == "call":
        test_context = getattr(item, "test_context", None)
        if test_context:
            # Try to get test_data from funcargs (now fixtures should be resolved)
            if hasattr(item, 'funcargs'):
                for key, value in item.funcargs.items():
                    if isinstance(value, dict) and ('test_id' in value or 'testID' in value or 'testId' in value):
                        # This is likely a test data fixture
                        test_context.set_test_data(value)
                        break
    
    outcome = yield
    report = outcome.get_result()
    
    setattr(item, f"rep_{report.when}", report)
    
    if report.when == "call" and "browser" in item.funcargs:
        page = item.funcargs["browser"]
        current_thread = threading.current_thread()
        context = browser_factory.get_context_for_thread(current_thread)
        
        # Handle tracing: stop and save trace.zip
        if context and config_manager.is_trace_enabled():
            should_save_trace = False
            trace_name = None
            
            if report.failed and config_manager.should_trace_on_failure():
                should_save_trace = True
                trace_name = f"Trace - {item.name} (Failed)"
            elif report.passed and config_manager.should_trace_on_success():
                should_save_trace = True
                trace_name = f"Trace - {item.name} (Passed)"
            
            if should_save_trace:
                try:
                    from pathlib import Path
                    import os
                    import time
                    
                    trace_dir = config_manager.get_trace_directory()
                    Path(trace_dir).mkdir(parents=True, exist_ok=True)
                    
                    # Generate trace file name with test name and timestamp
                    timestamp = int(time.time())
                    safe_test_name = item.name.replace(" ", "_").replace("/", "_")[:50]  # Limit length
                    trace_filename = f"trace_{safe_test_name}_{timestamp}.zip"
                    trace_path = os.path.join(trace_dir, trace_filename)
                    
                    # Stop tracing and save
                    saved_trace_path = browser_factory.stop_tracing(context, trace_path)
                    
                    if saved_trace_path and os.path.exists(saved_trace_path):
                        logger.info(f"[TRACE] Trace saved: {saved_trace_path}")
                        
                        # Attach trace to Allure if enabled
                        if config_manager.is_allure_enabled():
                            allure_generator.add_trace(saved_trace_path, trace_name or "Playwright Trace")
                            logger.info(f"[TRACE] Trace attached to Allure: {trace_name}")
                        
                        # Add trace path to test_context
                        test_context = getattr(item, "test_context", None)
                        if test_context:
                            test_context.set("trace_path", saved_trace_path)
                    else:
                        logger.warning("[TRACE] Failed to save trace file")
                        
                except Exception as e:
                    logger.error(f"[TRACE] Error handling trace: {e}")
            else:
                # Stop tracing without saving (if not configured to save)
                try:
                    # Just stop tracing, don't save
                    if context:
                        context.tracing.stop()
                        logger.debug("[TRACE] Tracing stopped (not saved)")
                except Exception as e:
                    logger.debug(f"[TRACE] Error stopping trace: {e}")
        
        # Screenshot on failure
        if report.failed and config_manager.should_take_screenshot_on_failure():
            # Check if test listener đã chụp screenshot trong step hiện tại
            if not test_listener.has_screenshot_taken_in_current_step():
                try:
                    from pathlib import Path
                    
                    screenshot_dir = config_manager.get_screenshot_directory()
                    Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                    
                    screenshot_path = f"{screenshot_dir}/{item.name}_failure.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    
                    logger.info(f"Screenshot saved: {screenshot_path}")
                    
                    # Thêm screenshot vào test_context
                    test_context = getattr(item, "test_context", None)
                    if test_context:
                        test_context.add_screenshot(screenshot_path, "Failure Screenshot")
                    
                    # Attach to Allure if enabled
                    if config_manager.is_allure_enabled():
                        import allure
                        # Read binary and attach
                        with open(screenshot_path, 'rb') as f:
                            allure.attach(
                                f.read(),
                                name="Failure Screenshot",
                                attachment_type=allure.attachment_type.PNG
                            )
                except Exception as e:
                    logger.error(f"Failed to take screenshot: {e}")
            else:
                logger.info("Skipping automatic screenshot - already taken by test listener")
        
        # Screenshot on success
        elif report.passed and config_manager.should_take_screenshot_on_success():
            try:
                from pathlib import Path
                
                screenshot_dir = config_manager.get_screenshot_directory()
                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                
                screenshot_path = f"{screenshot_dir}/{item.name}_success.png"
                page.screenshot(path=screenshot_path, full_page=True)
                
                logger.info(f"Screenshot saved: {screenshot_path}")
                
                # Thêm screenshot vào test_context
                test_context = getattr(item, "test_context", None)
                if test_context:
                    test_context.add_screenshot(screenshot_path, "Success Screenshot")
            
            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")
        
        # Notify test listener với thông tin chi tiết
        if report.failed:
            error_msg = str(report.longrepr) if hasattr(report, 'longrepr') and report.longrepr else None
            test_listener.on_test_end(item.name, "FAILED", Exception(error_msg) if error_msg else None)
        elif report.skipped:
            test_listener.on_test_end(item.name, "SKIPPED", None)
        else:
            test_listener.on_test_end(item.name, "PASSED", None)
        
        # Notify suite listener với đầy đủ thông tin cho Allure-style report
        if report.when == "call":
            # Lấy test context từ item
            test_context = getattr(item, "test_context", None)
            
            # Lấy class và method từ item
            test_class = None
            test_method = item.name
            if hasattr(item, "cls") and item.cls:
                test_class = item.cls.__name__
            elif hasattr(item, "parent") and hasattr(item.parent, "cls") and item.parent.cls:
                test_class = item.parent.cls.__name__
            
            # Lấy test file path
            test_file = item.fspath.strpath if hasattr(item, 'fspath') else str(item.path)
            try:
                test_file = os.path.relpath(test_file, os.getcwd())
            except ValueError:
                pass
            
            # Lấy steps từ test_context
            steps = []
            if test_context:
                raw_steps = test_context.get_steps()
                for step in raw_steps:
                    # Thêm status cho step (mặc định PASSED, có thể cải thiện sau)
                    step_with_status = {
                        "name": step.get("name", "Unknown Step"),
                        "data": step.get("data"),
                        "timestamp": step.get("timestamp", ""),
                        "status": step.get("status", "PASSED")
                    }
                    steps.append(step_with_status)
            
            # Lấy screenshots từ test_context
            screenshots = []
            if test_context:
                raw_screenshots = test_context.get_screenshots()
                for screenshot in raw_screenshots:
                    if isinstance(screenshot, dict):
                        screenshots.append(screenshot.get("path", ""))
                    elif isinstance(screenshot, str):
                        screenshots.append(screenshot)
            
            # Tính duration
            duration = report.duration if hasattr(report, 'duration') else 0
            
            # Xác định result
            if report.failed:
                result = "FAILED"
                error_msg = str(report.longrepr) if hasattr(report, 'longrepr') and report.longrepr else None
            elif report.skipped:
                result = "SKIPPED"
                error_msg = None
            else:
                result = "PASSED"
                error_msg = None
            
            # Gọi suite_listener.on_test_end với đầy đủ thông tin
            suite_listener.on_test_end(
                test_name=item.name,
                test_file=test_file,
                result=result,
                duration=duration,
                error=error_msg,
                test_class=test_class,
                test_method=test_method,
                steps=steps,
                screenshots=screenshots
            )
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Hook called after all tests finish, before terminal summary.
    This is the BEST place to get accurate stats.
    """ 
    try:
        workerinput = getattr(config, 'workerinput', None)
        if workerinput and isinstance(workerinput, dict):
            workerid = workerinput.get('workerid')
            if workerid != 'master':
                logger.info(f"[TERMINAL-SUMMARY] Skipping report on worker: {workerid}")
                return
    except (AttributeError, TypeError, KeyError):
        logger.info(f"[TERMINAL-SUMMARY] Skipping report on worker: {workerid}")
        return
    
    # Calculate duration
    if hasattr(suite_listener, 'suite_start_time'):
        duration = time.time() - suite_listener.suite_start_time
    else:
        duration = 0.0
    
    # ✅ Get stats from terminalreporter (most accurate)
    stats = terminalreporter.stats
    passed = len(stats.get('passed', []))
    failed = len(stats.get('failed', []))
    skipped = len(stats.get('skipped', []))
    
    logger.info("=" * 60)
    logger.info(f"[TERMINAL-SUMMARY] Test execution completed")
    logger.info(f"  - Passed: {passed}")
    logger.info(f"  - Failed: {failed}")
    logger.info(f"  - Skipped: {skipped}")
    logger.info(f"  - Duration: {duration:.2f}s")
    logger.info("=" * 60)
    
    # Log suite end
    suite_listener.on_suite_end(
        suite_name="Test Automation Suite",
        passed=passed,
        failed=failed,
        skipped=skipped
    )
    logger.log_suite_end("Test Automation Suite", passed, failed, skipped, duration)


def pytest_sessionfinish(session, exitstatus):
    """
    Only generate report on master process, skip on workers.
    """
    try:
        workerinput = getattr(session.config, 'workerinput', None)
        if workerinput and isinstance(workerinput, dict):
            workerid = workerinput.get('workerid', 'master')
            if workerid != 'master':
                logger.info(f"[ALLURE] Skipping report on worker: {workerid}")
                return
    except (AttributeError, TypeError, KeyError):
        pass   


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection based on run mode.
    Note: Files in tests/web/ and tests/mobile/ are already filtered in pytest_ignore_collect.
    This function handles:
    - Additional marker-based filtering (for tests outside standard directories)
    - Device grouping for mobile tests (parallel execution)
    """
    if config.getoption("--mobile"):
        for item in items:
            # Skip web tests by marker (backup filter for tests outside tests/web/)
            if any(m.name.endswith("_web") for m in item.iter_markers()):
                item.add_marker(pytest.mark.skip(reason="Mobile mode - skipping web test"))

            # Gắn group theo device để tất cả test cùng device chạy trên 1 worker
            # (yêu cầu pytest-xdist với --dist=loadgroup)
            try:
                if hasattr(item, "callspec") and "appium_driver" in item.callspec.params:
                    dev_cfg = item.callspec.params["appium_driver"]
                    group_key = dev_cfg.get("udid") or dev_cfg.get("device_name") or "unknown_device"
                    item.add_marker(pytest.mark.xdist_group(group_key))
            except Exception:
                # Không chặn collection nếu không lấy được param
                pass
    else:
        for item in items:
            # Skip mobile tests by marker (backup filter for tests outside tests/mobile/)
            if any(m.name.endswith("_mobile") for m in item.iter_markers()):
                item.add_marker(pytest.mark.skip(reason="Web mode - skipping mobile test"))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    Hook called BEFORE each test.
    # Load pytest config từ config.yaml và tích hợp Test Listener
    """  
    # Get test file path
    test_file = item.fspath.strpath if hasattr(item, 'fspath') else str(item.path)
    
    # Make path relative for cleaner logs
    try:
        test_file = os.path.relpath(test_file, os.getcwd())
    except ValueError:
        pass
    
    # Log test start with both required arguments
    logger.log_test_start(
        test_name=item.name,
        test_file=test_file
    )
    
    # Tích hợp Test Listener - gọi khi bắt đầu test
    test_context = TestContext()
    test_context.set_test_name(item.name)
    test_context.set_test_file(test_file)
    
    # Set test class and method
    test_class = None
    test_method = item.name
    if hasattr(item, "cls") and item.cls:
        test_class = item.cls.__name__
        test_context.set_test_class(test_class)
    elif hasattr(item, "parent") and hasattr(item.parent, "cls") and item.parent.cls:
        test_class = item.parent.cls.__name__
        test_context.set_test_class(test_class)
    
    test_context.set_test_method(test_method)
    
    # Set platform
    is_mobile = item.config.getoption("--mobile")
    platform = "mobile" if is_mobile else "web"
    test_context.set_platform(platform)
    
    # Try to get test_data from funcargs (parametrize fixtures)
    # Note: funcargs may not be available yet in pytest_runtest_setup
    # Will be set later when fixtures are resolved
    
    test_listener.on_test_start(item.name, test_context)
    
    # Thêm test context vào item để có thể sử dụng trong test
    item.test_context = test_context