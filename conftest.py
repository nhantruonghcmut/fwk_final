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
from src.core.browser.browser_factory import BrowserFactory
from src.core.browser.browser_type import BrowserType
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
browser_factory = BrowserFactory()
suite_listener = SuiteListener(config_manager,browser_factory,logger)
test_listener = TestListener(logger)
allure_helper = AllureEnvironmentHelper()


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
            
            # Clean allure results on start if configured
            if config_manager.should_clean_allure_on_start(): 
                import shutil
                from pathlib import Path
                
                results_path = Path(results_dir)
                if results_path.exists():
                    logger.info(f"[ALLURE] Cleaning results directory: {results_dir}")
                    shutil.rmtree(results_path)
                results_path.mkdir(parents=True, exist_ok=True)
            
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

def pytest_sessionfinish(session, exitstatus):
    # """Log session finish with accurate statistics."""
    # # Get the terminal reporter which has accurate final stats
    # terminalreporter = session.config.pluginmanager.get_plugin('terminalreporter')
    
    # if terminalreporter:
    #     stats = terminalreporter.stats
    #     passed = len(stats.get('passed', []))
    #     failed = len(stats.get('failed', []))
    #     skipped = len(stats.get('skipped', []))
    # else:
    #     # Fallback to session counters
    #     passed = session.testscollected - session.testsfailed
    #     failed = session.testsfailed
    #     skipped = 0
    
    # logger.info(f"Results - Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
    # passed = len([item for item in session.items if hasattr(item, 'rep_call') and item.rep_call.passed])
    # failed = len([item for item in session.items if hasattr(item, 'rep_call') and item.rep_call.failed])
    # skipped = len([item for item in session.items if hasattr(item, 'rep_call') and item.rep_call.skipped])
    
    # logger.log_suite_end("Test Automation Suite", passed, failed, skipped, 0)
    if config_manager.is_allure_enabled():
            try:
                import subprocess
                results_dir = config_manager.get_allure_results_directory()
                report_dir = config_manager.get_allure_report_directory()
                
                logger.info("=" * 60)
                logger.info("[ALLURE] Generating report...")
                
                # Generate report
                cmd = [
                    "allure", "generate",
                    results_dir,                 
                    "-o", report_dir,
                     '--single-file',"--clean", 
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"[ALLURE] ✅ Report generated: {report_dir}/index.html")
                    logger.info(f"[ALLURE] 🌐 Open with: allure open {report_dir}")
                else:
                    logger.error(f"[ALLURE] ❌ Failed to generate report: {result.stderr}")
                
                logger.info("=" * 60)
                
            except FileNotFoundError:
                logger.warning("[ALLURE] ⚠️ Allure CLI not found. Install with: scoop install allure")
            except Exception as e:
                logger.error(f"[ALLURE] ❌ Error generating report: {e}")


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
        test_context = getattr(request.node, "test_context", None)
        if test_context:
            test_context.set("page", page)
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


@pytest.fixture(scope="function")
def appium_service(worker_id):
    """
    Khởi động Appium service duy nhất per worker session.
    
    Đảm bảo:
    - Mỗi worker nhận port khác nhau
    - Tự động tìm port trống nếu port gợi ý bị chiếm
    - Cleanup service khi test kết thúc
    """
    start_port = get_port_for_worker(worker_id)

    logger.info(f"Starting Appium service on port {start_port}... for worker {worker_id}")

    service = AppiumService()
    
    try:
        # Khởi động Appium service
        service.start(args=['--port', str(start_port), '--relaxed-security'])
        
        # Chờ service khởi động
        time.sleep(2)
        
        # Verify service đang chạy
        if service.is_running:
            logger.info(f"Appium service running on port {start_port}")
            # Trả về dict chứa service và port
            yield {
                'service': service,
                'port': start_port,
                'url': f"http://localhost:{start_port}",
                'worker_id': worker_id
            }
        else:
            raise RuntimeError(f"Appium service failed to start on port {start_port}")
    
    except Exception as e:
        logger.error(f"Error starting Appium service: {e}")
        raise
    
    finally:
        # Cleanup: dừng service
        if service.is_running:
            logger.info(f"[{worker_id}] 🛑 Stopping Appium service on port {start_port}")
            service.stop()


@pytest.fixture(scope="session")
def appium_url(appium_service):
    """Lấy URL từ AppiumService."""
    return appium_service['url']



@pytest.fixture(scope="function") ## single
def appium_driver(request, appium_service) -> Generator[webdriver.Remote, None, None]:
    """
    Create Appium driver for mobile testing - SCOPE FUNCTION.
    Mỗi test function nhận một driver mới, đảm bảo môi trường độc lập.
    Tích hợp ADBUtil để kiểm tra device trước khi kết nối Appium
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
        pytest.skip(f"Thiếu thông tin cấu hình device: {', '.join(missing_keys)}")
    
    platform = device_cfg.get("platform_name", "").lower()
    
    # Android: cần appPackage và appActivity
    if platform == "android":       
        # Lấy device_id (udid) từ config hoặc device_name
        device_id = device_cfg.get("udid") or device_cfg.get("device_name", "")
        
        # Sử dụng ADBUtil để kiểm tra device
        adb_util = ADBUtil()
        
        # Kiểm tra device có connected không
        logger.info(f"[{worker_info}] [ADB] Đang kiểm tra device: {device_id}")
        if not adb_util.is_device_connected(device_id):
            # Nếu không tìm thấy device với ID chính xác, thử tìm device available
            devices = adb_util.get_devices()
            if not devices:
                pytest.skip(f"Không tìm thấy device nào được kết nối. Vui lòng kiểm tra ADB connection.")
            else:
                logger.warning(f"[ADB] Device {device_id} không tìm thấy. Các devices available: {[d['device_id'] for d in devices]}")
                # Nếu có device, dùng device đầu tiên
                device_id = devices[0]['device_id']
                logger.info(f"[{worker_info}] [ADB] Sử dụng device: {device_id}")
        
        # Đợi device ready
        logger.info(f"[ADB] Đang đợi device {device_id} sẵn sàng...")
        if not adb_util.wait_for_device(device_id, timeout=30):
            pytest.skip(f"Device {device_id} không sẵn sàng sau 30 giây")
        
        logger.info(f"[ADB] Device {device_id} đã sẵn sàng")
        
        # Lấy device info để log
        device_info = adb_util.get_device_info(device_id)
        if device_info:
            logger.info(f"[{worker_info}] [ADB] Device info: {device_info}")
        
        option = UiAutomator2Options()
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
            else:
                option.set_capability(k, v)
        
        # Đảm bảo có udid
        if not hasattr(option, 'udid') or not option.udid:
            option.udid = device_id
    
    # iOS: cần bundleId
    elif platform == "ios":
        if "bundleId" not in device_cfg or not device_cfg["bundleId"]:
            pytest.skip("Thiếu thông tin cấu hình iOS: bundleId")
        option = XCUITestOptions()
        for k, v in device_cfg.items():
            option.set_capability(k, v)
    else:
        pytest.skip(f"Unsupported platform: {platform}")
    
    logger.info(f"[APPIUM] Capabilities: {option.to_capabilities()}")
    
    try:        
        # Tạo driver với retry
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                logger.info(f"[{worker_info}] [APPIUM] Đang kết nối đến Appium server (lần thử {attempt + 1}/{max_retries})...")
                driver = webdriver.Remote(appium_service['url'], options=option)
                logger.info(f"[{worker_info}] [APPIUM-DONE] Đã tạo Appium driver thành công")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"[{worker_info}] [APPIUM] Kết nối thất bại (lần {attempt + 1}): {str(e)}")
                    logger.info(f"[{worker_info}] [APPIUM] Đợi {retry_delay} giây trước khi thử lại...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"[{worker_info}] [APPIUM-ERROR] Không thể kết nối đến Appium sau {max_retries} lần thử")
                    raise
        
        yield driver
        
    except Exception as e:
        logger.error(f"[{worker_info}] [APPIUM] ❌ Lỗi khi tạo Appium driver: {str(e)}")
        logger.error(f"[{worker_info}] [APPIUM] Chi tiết lỗi: {type(e).__name__}")
        pytest.fail(f"Không thể tạo Appium driver: {str(e)}")
        
    finally:
        # Cleanup
        if driver is not None:
            try:
                driver.quit()
                logger.debug(f"[{worker_info}] 🧹 Đã đóng Appium driver")
            except Exception as e:
                logger.warning(f"[{worker_info}] Lỗi khi đóng driver: {str(e)}")



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
    outcome = yield
    report = outcome.get_result()
    
    setattr(item, f"rep_{report.when}", report)
    
    if report.when == "call" and "browser" in item.funcargs:
        page = item.funcargs["browser"]
        
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
                    
                    # Attach to Allure if enabled
                    if config_manager.is_allure_enabled():
                        import allure
                        allure.attach.file(
                            screenshot_path,
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
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Hook called after all tests finish, before terminal summary.
    This is the BEST place to get accurate stats.
    """
    import time
    
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
    logger.info(f"[TERMINAL SUMMARY] Test execution completed")
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
    Hook called at session finish.
    Only handle Allure report generation here.
    Stats are logged in pytest_terminal_summary.
    """
    # Generate Allure report
    if config_manager.is_allure_enabled():
        try:
            import subprocess
            results_dir = config_manager.get_allure_results_directory()
            report_dir = config_manager.get_allure_report_directory()
            
            logger.info("=" * 60)
            logger.info("[ALLURE] Generating report...")
            
            cmd = [
                "allure", "generate",
                results_dir,                 
                "-o", report_dir,
                "--single-file", "--clean", 
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"[ALLURE] ✅ Report generated: {report_dir}/index.html")
                logger.info(f"[ALLURE] 🌐 Open with: allure open {report_dir}")
            else:
                logger.error(f"[ALLURE] ❌ Failed to generate report: {result.stderr}")
            
            logger.info("=" * 60)
            
        except FileNotFoundError:
            logger.warning("[ALLURE] ⚠️ Allure CLI not found. Install with: scoop install allure")
        except Exception as e:
            logger.error(f"[ALLURE] ❌ Error generating report: {e}")


def pytest_collection_modifyitems(config, items):
    # """
    # Modify test collection based on run mode.
    # """
    # Skip web tests in mobile mode
    # if config.getoption("--mobile"):
    #     for item in items:
    #         if any(m.name.endswith("_web") for m in item.iter_markers()):
    #             item.add_marker(pytest.mark.skip(reason="Mobile mode - skipping web test"))
    
    # # Skip mobile tests in web mode
    # else:
    #     for item in items:
    #         if any(m.name.endswith("_mobile") for m in item.iter_markers()):
    #             item.add_marker(pytest.mark.skip(reason="Web mode - skipping mobile test"))
    """
    Modify test collection based on run mode.
    - Mobile mode: skip web tests, group theo device để tránh tranh chấp thiết bị.
    - Web mode: skip mobile tests.
    """
    if config.getoption("--mobile"):
        for item in items:
            # Skip web tests trong mobile mode (giữ logic cũ)
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
            if any(m.name.endswith("_mobile") for m in item.iter_markers()):
                item.add_marker(pytest.mark.skip(reason="Web mode - skipping mobile test"))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    Hook called BEFORE each test.
    # Load pytest config từ config.yaml và tích hợp Test Listener
    """
    # Get pytest config section from config.yaml
    pytest_cfg = config_manager.get_config_value('pytest', {})
    
    # Log markers from config
    markers = config_manager.get_config_value('markers', {})
    # logger.debug(f"BBBBBBBBBBBBBB: {markers}")
    
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
    test_context.set_test_info(item.name, test_file)
    test_listener.on_test_start(item.name, test_context)
    
    # Thêm test context vào item để có thể sử dụng trong test
    item.test_context = test_context