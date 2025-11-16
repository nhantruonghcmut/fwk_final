"""
Suite listener for handling test suite setup and teardown events.
"""
import os
import time
from typing import Dict, Any
from src.core.utils.config_manager import ConfigManager
from src.core.utils.report_logger import ReportLogger
from src.core.utils.allure_report_generator import AllureReportGenerator
from src.core.browser.browser_factory import BrowserFactory


class SuiteListener:
    """Listener for handling test suite events."""
    
    def __init__(self, config_manager: ConfigManager, browser_factory: BrowserFactory, logger: ReportLogger, allure_generator: AllureReportGenerator):
        self.logger = logger
        self.config_manager = config_manager
        self.allure_generator = allure_generator
        self.browser_factory = browser_factory
        self.suite_start_time = None
        self.suite_end_time = None
        self.test_results = []
        
    def on_suite_start(self, suite_name: str, test_count: int):
        """Handle test suite start event."""
        self.suite_start_time = time.time()
        self.logger.info(f"Starting test suite: {suite_name}")
        self.logger.info(f"Total tests in suite: {test_count}")
        
        # Create reports directory
        self._create_reports_directory()
        
        # Setup environment
        self._setup_environment()
        
        # Log suite configuration
        self._log_suite_configuration()
        
    def on_suite_end(self, suite_name: str, passed: int, failed: int, skipped: int):
        """Handle test suite end event."""
        self.suite_end_time = time.time()
        duration = self.suite_end_time - self.suite_start_time if self.suite_start_time else 0
        
        self.logger.info(f"Test suite completed: {suite_name}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Results - Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
        
        # Generate reports
        self._generate_reports(suite_name, passed, failed, skipped, duration)
        
        # Cleanup
        self._cleanup_suite()
        
    def on_test_start(self, test_name: str, test_file: str):
        """Handle individual test start event."""
        self.logger.info(f"Starting test: {test_name} in {test_file}")
        
    def on_test_end(self, test_name: str, test_file: str, result: str, duration: float, 
                   error: str = None, test_class: str = None, test_method: str = None,
                   steps: list = None, screenshots: list = None):
        """Handle individual test end event."""
        test_result = {
            "name": test_name,
            "file": test_file,
            "class": test_class or "N/A",
            "method": test_method or test_name,
            "result": result,
            "duration": duration,
            "error": error,
            "steps": steps or [],
            "screenshots": screenshots or [],
            "timestamp": time.time()
        }
        self.test_results.append(test_result)
        
        status_emoji = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "⏭️"
        self.logger.info(f"{status_emoji} Test completed: {test_name} - {result} ({duration:.2f}s)")
        
        if error:
            self.logger.error(f"Test error: {error}")
            
    def on_browser_start(self, browser_type: str):
        """Handle browser start event."""
        self.logger.info(f"Starting browser: {browser_type}")
        
    def on_browser_end(self, browser_type: str):
        """Handle browser end event."""
        self.logger.info(f"Closing browser: {browser_type}")
        
    def on_mobile_session_start(self, platform: str, device_name: str):
        """Handle mobile session start event."""
        self.logger.info(f"Starting mobile session: {platform} - {device_name}")
        
    def on_mobile_session_end(self, platform: str, device_name: str):
        """Handle mobile session end event."""
        self.logger.info(f"Ending mobile session: {platform} - {device_name}")
        
    def _create_reports_directory(self):
        """Create reports directory structure."""
        directories = [
            "reports",
            "reports/screenshots",
            "reports/logs",
            "reports/allure-results",
            "reports/allure-report",
            "reports/excel",
            "reports/pdf"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        self.logger.info("Created reports directory structure")
        
    def _setup_environment(self):
        """Setup test environment."""
        environment = self.config_manager.get_current_environment()
        self.logger.info(f"Test environment: {environment}")
        
        # Set environment variables
        env_config = self.config_manager.get_environment_config()
        for key, value in env_config.get("environment_variables", {}).items():
            os.environ[key] = str(value)
            
    def _log_suite_configuration(self):
        """Log suite configuration."""
        self.logger.info("Suite Configuration:")
        self.logger.info(f"  Environment: {self.config_manager.get_current_environment()}")
        self.logger.info(f"  Parallel execution: {self.config_manager.is_parallel_enabled()}")
        self.logger.info(f"  Headless mode: {self.config_manager.get_config_value('headless')}")
        self.logger.info(f"  Screenshot on failure: {self.config_manager.should_take_screenshot_on_failure()}")
        
    def _generate_reports(self, suite_name: str, passed: int, failed: int, skipped: int, duration: float):
        """Generate test reports."""
        try:
            # Generate Allure report
            self.allure_generator.generate_report()
            
            # Generate Allure-style reports (PDF và Excel)
            if (self.config_manager.get_config_value("reports.excel.enabled") or 
                self.config_manager.get_config_value("reports.pdf.enabled")):
                
                # Tạo cấu trúc suites_data cho Allure-style report
                suites_data = self._prepare_allure_style_data(suite_name, passed, failed, skipped, duration)
                
                # Generate Excel Allure-style report
                if self.config_manager.get_config_value("reports.excel.enabled"):
                    from src.core.utils.excel_util import ExcelUtil
                    excel_util = ExcelUtil()
                    excel_path = excel_util.generate_allure_style_report(suites_data, f"Test Execution Report - {suite_name}")
                    self.logger.info(f"Generated Allure-style Excel report: {excel_path}")
                
                # Generate PDF Allure-style report
                if self.config_manager.get_config_value("reports.pdf.enabled"):
                    from src.core.utils.pdf_util import PDFUtil
                    pdf_util = PDFUtil()
                    pdf_path = pdf_util.generate_allure_style_report(suites_data, f"Test Execution Report - {suite_name}")
                    self.logger.info(f"Generated Allure-style PDF report: {pdf_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate reports: {str(e)}")
            
    def _prepare_allure_style_data(self, suite_name: str, passed: int, failed: int, skipped: int, duration: float) -> list:
        """Chuẩn bị dữ liệu theo format Allure-style cho PDF và Excel reports."""
        try:
            # Chuyển đổi test_results thành format Allure-style
            test_cases = []
            for test_result in self.test_results:
                # Lấy steps và thêm status nếu chưa có
                steps = []
                for step in test_result.get("steps", []):
                    step_with_status = {
                        "name": step.get("name", "Unknown Step"),
                        "data": step.get("data"),
                        "timestamp": step.get("timestamp", ""),
                        "status": step.get("status", "PASSED")  # Default to PASSED if not specified
                    }
                    steps.append(step_with_status)
                
                # Lấy screenshots paths
                screenshots = []
                for screenshot in test_result.get("screenshots", []):
                    if isinstance(screenshot, dict):
                        screenshots.append(screenshot.get("path", ""))
                    elif isinstance(screenshot, str):
                        screenshots.append(screenshot)
                
                test_case = {
                    "name": test_result.get("name", "Unknown Test"),
                    "file": test_result.get("file", "Unknown"),
                    "class": test_result.get("class", "N/A"),
                    "method": test_result.get("method", "N/A"),
                    "result": test_result.get("result", "UNKNOWN"),
                    "duration": test_result.get("duration", 0),
                    "error": test_result.get("error"),
                    "steps": steps,
                    "screenshots": screenshots
                }
                test_cases.append(test_case)
            
            # Tạo suite data
            suite_data = {
                "name": suite_name,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": passed + failed + skipped,
                "duration": duration,
                "test_cases": test_cases
            }
            
            return [suite_data]
            
        except Exception as e:
            self.logger.error(f"Failed to prepare Allure-style data: {str(e)}")
            return []
            
    def _cleanup_suite(self):
        """Cleanup after suite completion."""
        try:
            # Close all browsers
            self.browser_factory.close_all_browsers()
            
            # Cleanup temporary files
            self._cleanup_temp_files()
            
            self.logger.info("Suite cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup suite: {str(e)}")
            
    def _cleanup_temp_files(self):
        """Cleanup temporary files."""
        temp_dirs = ["temp", "downloads"]
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
    def get_suite_statistics(self) -> Dict[str, Any]:
        """Get suite statistics."""
        if not self.test_results:
            return {}
            
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["result"] == "PASSED"])
        failed_tests = len([t for t in self.test_results if t["result"] == "FAILED"])
        skipped_tests = len([t for t in self.test_results if t["result"] == "SKIPPED"])
        
        total_duration = sum(t["duration"] for t in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "suite_duration": self.suite_end_time - self.suite_start_time if self.suite_start_time and self.suite_end_time else 0
        }
        
    def add_custom_attachment(self, name: str, content: str, attachment_type: str = "text/plain"):
        """Add custom attachment to Allure report."""
        self.allure_generator.add_attachment(name, content, attachment_type)
        
    def add_screenshot_attachment(self, screenshot_path: str, name: str = "Screenshot"):
        """Add screenshot attachment to Allure report."""
        self.allure_generator.add_screenshot(screenshot_path, name)
        
    def add_log_attachment(self, log_content: str, name: str = "Test Log"):
        """Add log attachment to Allure report."""
        self.allure_generator.add_log(log_content, name)
