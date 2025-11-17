"""
Screenshot utility for capturing screenshots on test failures and success.
"""
import os
import time
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from playwright.sync_api import Page
from appium import webdriver
from src.core.utils.report_logger import ReportLogger
from src.core.utils.config_manager import ConfigManager


@dataclass
class ScreenshotResult:
    """Result object containing screenshot path and binary data."""
    path: str
    binary: bytes
    
    def attach_to_allure(self, name: str = "Screenshot") -> str:
        """Helper method to attach screenshot to Allure report.
        
        Args:
            name: Name for the attachment in Allure report
            
        Returns:
            str: The screenshot path (for logging purposes)
        """
        try:
            import allure
            allure.attach(self.binary, name, allure.attachment_type.PNG)
        except ImportError:
            # Allure not available, skip silently
            pass
        except Exception as e:
            # Log error but don't fail
            pass
        return self.path
    
    def __bool__(self) -> bool:
        """Check if screenshot result is valid."""
        return bool(self.path and self.binary)
    
    def __str__(self) -> str:
        """Return path as string representation."""
        return self.path
    
    def __repr__(self) -> str:
        """Return representation without binary data."""
        binary_size = len(self.binary) if self.binary else 0
        return f"ScreenshotResult(path='{self.path}', binary_size={binary_size} bytes)"


class ScreenshotUtil:
    """Utility class for taking screenshots."""
    
    def __init__(self, logger: Optional[ReportLogger] = None, config_manager: Optional[ConfigManager] = None):
        self.logger = logger if logger else ReportLogger()
        self.config_manager = config_manager if config_manager else ConfigManager(self.logger)
        self.screenshot_dir = self.config_manager.get_screenshot_directory()
        self._ensure_screenshot_directory()
        
    def _ensure_screenshot_directory(self):
        """Ensure screenshot directory exists."""
        try:
            os.makedirs(self.screenshot_dir, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create screenshot directory: {str(e)}")
            
    def _generate_auto_snapshot_name(self, test_context=None) -> str:
        """Generate automatic snapshot name in format: [device_name/browser_type]_testsuite_testcase_testID_stt"""
        try:
            # Try to get test_context from pytest item if not provided
            if test_context is None:
                try:
                    import _pytest
                    import inspect
                    # Try to get request from call stack
                    frame = inspect.currentframe()
                    while frame:
                        frame = frame.f_back
                        if frame and 'request' in frame.f_locals:
                            request = frame.f_locals.get('request')
                            if request and hasattr(request, 'node') and hasattr(request.node, 'test_context'):
                                test_context = request.node.test_context
                                break
                except:
                    pass
            
            if test_context is None:
                # Fallback to timestamp if no context available
                self.logger.warning("No test_context available, using timestamp for screenshot name")
                return f"screenshot_{int(time.time())}"
            
            # Get test suite name (from test file)
            test_file = test_context.get_test_file()
            if test_file:
                # Extract filename without extension
                test_suite = os.path.splitext(os.path.basename(test_file))[0]
                # Remove 'test_' prefix if exists
                test_suite = re.sub(r'^test_', '', test_suite, flags=re.IGNORECASE)
            else:
                test_suite = "unknown_suite"
            
            # Get test case name (from test method) - remove parametrize suffix
            test_case = test_context.get_test_name() or test_context.get_test_method()
            if test_case:
                # Remove 'test_' prefix if exists
                test_case = re.sub(r'^test_', '', test_case, flags=re.IGNORECASE)
                # Remove parametrize suffix like [TC003_COMPLEX_001-emulator-5556]
                test_case = re.sub(r'\[.*?\]$', '', test_case)
            else:
                test_case = "unknown_case"
            
            # Get device_name (for mobile) or browser_type (for web)
            platform = test_context.get_platform() or "unknown"
            device_or_browser = "unknown"
            
            if platform == "mobile":
                device_name = test_context.get_device_name()
                if device_name:
                    device_or_browser = device_name
            else:
                browser_type = test_context.get_browser_type()
                if browser_type:
                    device_or_browser = browser_type
            
            # Sanitize device_or_browser name
            device_or_browser = re.sub(r'[<>:"/\\|?*]', '_', device_or_browser)
            device_or_browser = re.sub(r'\s+', '_', device_or_browser)
            
            # Get test ID from test data
            test_data = test_context.get_test_data()
            test_id = "unknown_id"
            
            # Try to get test_id from test_data
            if test_data:
                # Try different possible keys for test_id
                test_id = (test_data.get('test_id') or 
                          test_data.get('testID') or 
                          test_data.get('testId') or
                          "unknown_id")
            
            # If still unknown, try to extract from test_name (parametrize format: [TC003_COMPLEX_001-...])
            if test_id == "unknown_id":
                test_name = test_context.get_test_name() or ""
                # Extract test_id from format: test_name[TC003_COMPLEX_001-emulator-5556]
                match = re.search(r'\[([A-Z0-9_]+)', test_name)
                if match:
                    test_id = match.group(1)
            
            # If still unknown, try to get from pytest item's funcargs (parametrize fixtures)
            if test_id == "unknown_id":
                try:
                    import _pytest
                    import inspect
                    # Try to get request from call stack
                    frame = inspect.currentframe()
                    while frame:
                        frame = frame.f_back
                        if frame and 'request' in frame.f_locals:
                            request = frame.f_locals.get('request')
                            if request and hasattr(request, 'node'):
                                # Check funcargs for test data fixtures
                                funcargs = getattr(request.node, 'funcargs', {})
                                for key, value in funcargs.items():
                                    if isinstance(value, dict) and ('test_id' in value or 'testID' in value or 'testId' in value):
                                        test_id = value.get('test_id') or value.get('testID') or value.get('testId', "unknown_id")
                                        # Also set to test_context for future use
                                        test_context.set_test_data(value)
                                        break
                                if test_id != "unknown_id":
                                    break
                except Exception as e:
                    self.logger.debug(f"Could not get test_id from funcargs: {str(e)}")
            
            # Get next sequence number for this test_id
            stt = test_context.get_next_snapshot_stt(test_id)
            
            # Generate name: [device_name/browser_type]_testsuite_testcase_testID_stt
            name = f"{device_or_browser}_{test_suite}_{test_case}_{test_id}_{stt}"
            
            # Sanitize name (remove invalid characters for filename)
            name = re.sub(r'[<>:"/\\|?*]', '_', name)
            name = re.sub(r'\s+', '_', name)
            
            return name
            
        except Exception as e:
            self.logger.warning(f"Failed to generate auto snapshot name: {str(e)}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return f"screenshot_{int(time.time())}"
    
    def take_screenshot(self, name: str = None, page: Page = None, driver: webdriver.Remote = None, test_context=None) -> ScreenshotResult:
        """Take screenshot using Playwright or Appium.
        
        Args:
            name: Screenshot name. If None, will auto-generate based on test context.
            page: Playwright page object (for web)
            driver: Appium driver object (for mobile)
            test_context: TestContext object for auto-generating name
            
        Returns:
            ScreenshotResult: Object containing path and binary data
        """
        try:
            if not name:
                name = self._generate_auto_snapshot_name(test_context)
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            screenshot_binary = b""
            
            if page:
                # Playwright screenshot - get binary first, then save
                screenshot_binary = page.screenshot()
                # Save to file
                with open(screenshot_path, 'wb') as f:
                    f.write(screenshot_binary)
                self.logger.log_screenshot(screenshot_path)
            elif driver:
                # Appium screenshot - save first, then read binary
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, 'rb') as f:
                    screenshot_binary = f.read()
                self.logger.log_screenshot(screenshot_path)
            else:
                self.logger.error("No page or driver provided for screenshot")
                return ScreenshotResult("", b"")
                
            return ScreenshotResult(screenshot_path, screenshot_binary)
            
        except Exception as e:
            self.logger.log_error(e, "take_screenshot")
            return ScreenshotResult("", b"")
            
    def take_element_screenshot(self, element, name: str = None, test_context=None) -> ScreenshotResult:
        """Take screenshot of specific element.
        
        Returns:
            ScreenshotResult: Object containing path and binary data
        """
        try:
            if not name:
                name = self._generate_auto_snapshot_name(test_context)
                name = f"element_{name}"
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            screenshot_binary = b""
            
            # Check if element is Playwright or Selenium
            if hasattr(element, 'screenshot'):
                # Try Playwright element first (has screenshot method that can return bytes)
                try:
                    # Playwright element - get binary first
                    screenshot_binary = element.screenshot()
                    # Save to file
                    with open(screenshot_path, 'wb') as f:
                        f.write(screenshot_binary)
                except TypeError:
                    # If screenshot() requires path parameter, use path
                    element.screenshot(path=screenshot_path)
                    with open(screenshot_path, 'rb') as f:
                        screenshot_binary = f.read()
            else:
                self.logger.error("Unsupported element type for screenshot")
                return ScreenshotResult("", b"")
                
            self.logger.log_screenshot(screenshot_path)
            return ScreenshotResult(screenshot_path, screenshot_binary)
            
        except Exception as e:
            self.logger.log_error(e, "take_element_screenshot")
            return ScreenshotResult("", b"")
            
    def take_full_page_screenshot(self, page: Page, name: str = None, test_context=None) -> ScreenshotResult:
        """Take full page screenshot.
        
        Returns:
            ScreenshotResult: Object containing path and binary data
        """
        try:
            if not name:
                name = self._generate_auto_snapshot_name(test_context)
                name = f"fullpage_{name}"
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            # Playwright full page screenshot - get binary first
            screenshot_binary = page.screenshot(full_page=True)
            # Save to file
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_binary)
            self.logger.log_screenshot(screenshot_path)
            return ScreenshotResult(screenshot_path, screenshot_binary)
            
        except Exception as e:
            self.logger.log_error(e, "take_full_page_screenshot")
            return ScreenshotResult("", b"")
            
    def take_mobile_screenshot(self, driver: webdriver.Remote, name: str = None, test_context=None) -> ScreenshotResult:
        """Take mobile screenshot.
        
        Returns:
            ScreenshotResult: Object containing path and binary data
        """
        try:
            if not name:
                name = self._generate_auto_snapshot_name(test_context)
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            # Appium screenshot - save first, then read binary
            driver.save_screenshot(screenshot_path)
            with open(screenshot_path, 'rb') as f:
                screenshot_binary = f.read()
            self.logger.log_screenshot(screenshot_path)
            return ScreenshotResult(screenshot_path, screenshot_binary)
            
        except Exception as e:
            self.logger.log_error(e, "take_mobile_screenshot")
            return ScreenshotResult("", b"")
            
    def take_screenshot_on_failure(self, test_name: str, page: Page = None, driver: webdriver.Remote = None, test_context=None) -> ScreenshotResult:
        """Take screenshot on test failure.
        
        Returns:
            ScreenshotResult: Object containing path and binary data
        """
        if not self.config_manager.should_take_screenshot_on_failure() or (page==None and driver==None):
            return ScreenshotResult("", b"")
            
        # Use auto-generated name if test_context is provided, otherwise use test_name
        if test_context:
            name = None  # Will auto-generate
        else:
            name = f"failure_{test_name}_{int(time.time())}"
        return self.take_screenshot(name, page, driver, test_context)
        
    def take_screenshot_on_success(self, test_name: str, page: Page = None, driver: webdriver.Remote = None, test_context=None) -> ScreenshotResult:
        """Take screenshot on test success.
        
        Returns:
            ScreenshotResult: Object containing path and binary data
        """
        if not self.config_manager.should_take_screenshot_on_success():
            return ScreenshotResult("", b"")
            
        # Use auto-generated name if test_context is provided, otherwise use test_name
        if test_context:
            name = None  # Will auto-generate
        else:
            name = f"success_{test_name}_{int(time.time())}"
        return self.take_screenshot(name, page, driver, test_context)
        
    def take_screenshot_on_step(self, step_name: str, page: Page = None, driver: webdriver.Remote = None, test_context=None) -> ScreenshotResult:
        """Take screenshot on test step.
        
        Returns:
            ScreenshotResult: Object containing path and binary data
        """
        # Use auto-generated name if test_context is provided, otherwise use step_name
        if test_context:
            name = None  # Will auto-generate
        else:
            name = f"step_{step_name}_{int(time.time())}"
        return self.take_screenshot(name, page, driver, test_context)
        
    def cleanup_old_screenshots(self, days_old: int = 7):
        """Cleanup screenshots older than specified days."""
        try:
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            deleted_count = 0
            for filename in os.listdir(self.screenshot_dir):
                file_path = os.path.join(self.screenshot_dir, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        
            self.logger.info(f"Cleaned up {deleted_count} old screenshots")
            
        except Exception as e:
            self.logger.log_error(e, "cleanup_old_screenshots")
            
    def get_screenshot_info(self) -> Dict[str, Any]:
        """Get screenshot directory information."""
        try:
            if not os.path.exists(self.screenshot_dir):
                return {"directory": self.screenshot_dir, "exists": False}
                
            files = os.listdir(self.screenshot_dir)
            screenshot_files = [f for f in files if f.endswith('.png')]
            
            total_size = 0
            for filename in screenshot_files:
                file_path = os.path.join(self.screenshot_dir, filename)
                total_size += os.path.getsize(file_path)
                
            return {
                "directory": self.screenshot_dir,
                "exists": True,
                "total_files": len(screenshot_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.log_error(e, "get_screenshot_info")
            return {"directory": self.screenshot_dir, "exists": False, "error": str(e)}
            
    def compress_screenshot(self, screenshot_path: str, quality: int = 85) -> str:
        """Compress screenshot to reduce file size."""
        try:
            from PIL import Image
            
            if not os.path.exists(screenshot_path):
                return screenshot_path
                
            # Open image
            image = Image.open(screenshot_path)
            
            # Create compressed version
            compressed_path = screenshot_path.replace('.png', '_compressed.jpg')
            image.save(compressed_path, 'JPEG', quality=quality, optimize=True)
            
            # Get file sizes
            original_size = os.path.getsize(screenshot_path)
            compressed_size = os.path.getsize(compressed_path)
            
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            self.logger.info(f"Screenshot compressed: {compression_ratio:.1f}% size reduction")
            
            # Remove original if compression was successful
            if compressed_size < original_size:
                os.remove(screenshot_path)
                return compressed_path
            else:
                os.remove(compressed_path)
                return screenshot_path
                
        except ImportError:
            self.logger.warning("PIL not available for screenshot compression")
            return screenshot_path
        except Exception as e:
            self.logger.log_error(e, "compress_screenshot")
            return screenshot_path
            
    def create_screenshot_gallery(self, output_path: str = None) -> str:
        """Create HTML gallery of screenshots."""
        try:
            if not output_path:
                output_path = os.path.join(self.screenshot_dir, "screenshot_gallery.html")
                
            screenshot_files = [f for f in os.listdir(self.screenshot_dir) if f.endswith('.png')]
            screenshot_files.sort(reverse=True)  # Most recent first
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Screenshot Gallery</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
                    .screenshot { border: 1px solid #ddd; padding: 10px; text-align: center; }
                    .screenshot img { max-width: 100%; height: auto; }
                    .screenshot h3 { margin: 10px 0; color: #333; }
                    .screenshot p { margin: 5px 0; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <h1>Screenshot Gallery</h1>
                <p>Generated on: {timestamp}</p>
                <div class="gallery">
            """.format(timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
            
            for filename in screenshot_files:
                file_path = os.path.join(self.screenshot_dir, filename)
                file_size = os.path.getsize(file_path)
                file_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
                
                html_content += f"""
                    <div class="screenshot">
                        <h3>{filename}</h3>
                        <img src="{filename}" alt="{filename}">
                        <p>Size: {file_size} bytes</p>
                        <p>Created: {file_time}</p>
                    </div>
                """
            
            html_content += """
                </div>
            </body>
            </html>
            """
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.logger.info(f"Screenshot gallery created: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.log_error(e, "create_screenshot_gallery")
            return ""
            
    def get_screenshot_statistics(self) -> Dict[str, Any]:
        """Get screenshot statistics."""
        try:
            info = self.get_screenshot_info()
            if not info.get("exists"):
                return info
                
            files = os.listdir(self.screenshot_dir)
            screenshot_files = [f for f in files if f.endswith('.png')]
            
            # Categorize screenshots
            failure_screenshots = [f for f in screenshot_files if f.startswith('failure_')]
            success_screenshots = [f for f in screenshot_files if f.startswith('success_')]
            step_screenshots = [f for f in screenshot_files if f.startswith('step_')]
            other_screenshots = [f for f in screenshot_files if not any(f.startswith(prefix) for prefix in ['failure_', 'success_', 'step_'])]
            
            return {
                **info,
                "failure_screenshots": len(failure_screenshots),
                "success_screenshots": len(success_screenshots),
                "step_screenshots": len(step_screenshots),
                "other_screenshots": len(other_screenshots),
                "total_screenshots": len(screenshot_files)
            }
            
        except Exception as e:
            self.logger.log_error(e, "get_screenshot_statistics")
            return {"error": str(e)}
