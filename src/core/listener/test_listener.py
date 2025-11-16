"""
Test listener for handling individual test events and Allure attachments.
"""
import os
import time
from typing import Dict, Any, Optional
from src.core.utils.report_logger import ReportLogger
from src.core.utils.screenshot_util import ScreenshotUtil
from src.core.utils.allure_report_generator import AllureReportGenerator
from src.core.utils.test_context import TestContext


class TestListener:
    """Listener for handling individual test events."""
    
    def __init__(self, logger: ReportLogger, allure_generator: AllureReportGenerator):
        self.logger = logger
        self.screenshot_util = ScreenshotUtil()
        self.allure_generator = allure_generator
        self.test_start_time = None
        self.test_context = None
        self.current_step = None
        self.step_stack = []
        self._screenshot_taken_in_step = False
        
    def on_test_start(self, test_name: str, test_context: TestContext):
        """Handle test start event."""
        self.test_start_time = time.time()
        self.test_context = test_context
        
        self.logger.info(f"Starting test: {test_name}")
        self.logger.info(f"Test context: {test_context.get_context_info()}")
        
        # Add test start information to Allure
        self.allure_generator.add_test_info(test_name, "STARTED")
        
    def on_test_end(self, test_name: str, result: str, error: Optional[Exception] = None):
        """Handle test end event."""
        duration = time.time() - self.test_start_time if self.test_start_time else 0
        
        self.logger.info(f"Test completed: {test_name} - {result} ({duration:.2f}s)")
        
        # Cleanup step stack nếu còn step chưa đóng
        try:
            while self.step_stack:
                step = self.step_stack.pop()
                step.__exit__(None, None, None)
            self.current_step = None
        except Exception as e:
            self.logger.log_error(e, "cleanup_step_stack")
        
        # Handle test failure
        if result == "FAILED" and error:
            self._handle_test_failure(test_name, error)
            
        # Add test result to Allure
        self.allure_generator.add_test_result(test_name, result, duration, str(error) if error else None)
        
        # Add test context to Allure
        if self.test_context:
            self.allure_generator.add_test_context(self.test_context.get_context_info())
            
    def on_step_start(self, step_name: str):
        """Handle test step start event."""
        self.logger.info(f"Test step: {step_name}")
        
        # Reset screenshot flag cho step mới
        self._screenshot_taken_in_step = False
        
        # Thêm step vào test_context
        if self.test_context:
            self.test_context.add_step(step_name, None)
        
        try:
            import allure
            # Tạo Allure step context
            self.current_step = allure.step(step_name)
            self.step_stack.append(self.current_step)
            self.current_step.__enter__()
            
            self.allure_generator.add_step_info(step_name, "STARTED")
        except ImportError:
            self.logger.warning("Allure not available, skipping step context")
        except Exception as e:
            self.logger.log_error(e, "on_step_start")
        
    def on_step_end(self, step_name: str, result: str, error: Optional[Exception] = None):
        """Handle test step end event."""
        self.logger.info(f"Step completed: {step_name} - {result}")
        
        if result == "FAILED" and error:
            self.logger.error(f"Step failed: {step_name} - {str(error)}")
        
        # Cập nhật status cho step cuối cùng trong test_context
        if self.test_context:
            steps = self.test_context.get_steps()
            if steps:
                # Tìm step cuối cùng có tên trùng với step_name
                for step in reversed(steps):
                    if step.get("name") == step_name:
                        step["status"] = result
                        if error:
                            step["error"] = str(error)
                        break
        
        # Đóng Allure step context
        try:
            if self.step_stack:
                current_step = self.step_stack.pop()
                current_step.__exit__(None, None, None)
                
                # Cập nhật current_step nếu còn step trong stack
                if self.step_stack:
                    self.current_step = self.step_stack[-1]
                else:
                    self.current_step = None
        except Exception as e:
            self.logger.log_error(e, "on_step_end")
            
        self.allure_generator.add_step_result(step_name, result, str(error) if error else None)
        
    def on_verification(self, verification_name: str, expected: Any, actual: Any, result: bool):
        """Handle verification event."""
        status = "PASSED" if result else "FAILED"
        self.logger.info(f"Verification: {verification_name} - {status}")
        
        verification_data = {
            "name": verification_name,
            "expected": expected,
            "actual": actual,
            "result": result
        }
        
        self.allure_generator.add_verification(verification_data)
        
    def on_screenshot_taken(self, screenshot_path: str, description: str = "Screenshot"):
        """Handle screenshot taken event."""
        self.logger.info(f"Screenshot taken: {screenshot_path}")
        
        # Thêm screenshot vào test_context
        if self.test_context:
            self.test_context.add_screenshot(screenshot_path, description)
        
        try:
            import allure
            import os
            
            if os.path.exists(screenshot_path):
                # Attach screenshot vào step hiện tại hoặc test level
                if self.current_step is not None:
                    # Attach vào step hiện tại
                    with allure.step(f"Screenshot: {description}"):
                        with open(screenshot_path, 'rb') as f:
                            allure.attach(f.read(), description, allure.attachment_type.PNG)
                    self.logger.info(f"Added screenshot to current step: {description}")
                    # Set flag để pytest hook biết đã chụp screenshot
                    self._screenshot_taken_in_step = True
                else:
                    # Attach vào test level nếu không có step context
                    self.allure_generator.add_screenshot(screenshot_path, description)
                    self.logger.info(f"Added screenshot to test level: {description}")
                    # Set flag cho test level screenshot
                    self._screenshot_taken_in_step = True
            else:
                self.logger.warning(f"Screenshot file not found: {screenshot_path}")
                
        except ImportError:
            self.logger.warning("Allure not available, skipping screenshot")
        except Exception as e:
            self.logger.log_error(e, "on_screenshot_taken")
        
    def has_screenshot_taken_in_current_step(self) -> bool:
        """Check if screenshot has been taken in current step."""
        return self._screenshot_taken_in_step
        
    def on_log_entry(self, level: str, message: str):
        """Handle log entry event."""
        self.logger.log(level, message)
        self.allure_generator.add_log_entry(level, message)
        
    def on_data_used(self, data_type: str, data: Any):
        """Handle test data usage event."""
        self.logger.info(f"Using test data: {data_type}")
        self.allure_generator.add_test_data(data_type, data)
        
    def on_api_call(self, method: str, url: str, status_code: int, response_time: float):
        """Handle API call event."""
        self.logger.info(f"API call: {method} {url} - {status_code} ({response_time:.2f}ms)")
        
        api_data = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_time": response_time
        }
        
        self.allure_generator.add_api_call(api_data)
        
    def on_database_query(self, query: str, result_count: int, execution_time: float):
        """Handle database query event."""
        self.logger.info(f"Database query: {query} - {result_count} results ({execution_time:.2f}ms)")
        
        db_data = {
            "query": query,
            "result_count": result_count,
            "execution_time": execution_time
        }
        
        self.allure_generator.add_database_query(db_data)
        
    def on_mobile_action(self, action_type: str, element_info: Dict[str, Any], result: str):
        """Handle mobile action event."""
        self.logger.info(f"Mobile action: {action_type} on {element_info} - {result}")
        
        mobile_data = {
            "action_type": action_type,
            "element_info": element_info,
            "result": result
        }
        
        self.allure_generator.add_mobile_action(mobile_data)
        
    def on_web_action(self, action_type: str, element_info: Dict[str, Any], result: str):
        """Handle web action event."""
        self.logger.info(f"Web action: {action_type} on {element_info} - {result}")
        
        web_data = {
            "action_type": action_type,
            "element_info": element_info,
            "result": result
        }
        
        self.allure_generator.add_web_action(web_data)
        
    def on_error_occurred(self, error: Exception, context: str = ""):
        """Handle error occurrence event."""
        error_message = f"Error in {context}: {str(error)}" if context else str(error)
        self.logger.error(error_message)
        
        # Take screenshot on error
        screenshot_result = self.screenshot_util.take_screenshot("error")
        if screenshot_result:
            self.allure_generator.add_screenshot(screenshot_result.path, f"Error Screenshot - {context}")
            
        self.allure_generator.add_error(error_message)
        
    def on_warning_occurred(self, warning_message: str, context: str = ""):
        """Handle warning occurrence event."""
        warning = f"Warning in {context}: {warning_message}" if context else warning_message
        self.logger.warning(warning)
        self.allure_generator.add_warning(warning)
        
    def on_info_message(self, message: str, context: str = ""):
        """Handle info message event."""
        info = f"Info in {context}: {message}" if context else message
        self.logger.info(info)
        self.allure_generator.add_info(info)
        
    def _handle_test_failure(self, test_name: str, error: Exception):
        """Handle test failure with screenshot and error details."""
        try:
            # Take screenshot on failure
            screenshot_result = self.screenshot_util.take_screenshot(f"failure_{test_name}")
            if screenshot_result:
                self.allure_generator.add_screenshot(screenshot_result.path, f"Failure Screenshot - {test_name}")
                
            # Add error details
            error_details = {
                "test_name": test_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": time.time()
            }
            
            self.allure_generator.add_error_details(error_details)
            
            # Log error stack trace
            import traceback
            stack_trace = traceback.format_exc()
            self.logger.error(f"Test failure stack trace:\n{stack_trace}")
            self.allure_generator.add_stack_trace(stack_trace)
            
        except Exception as e:
            self.logger.error(f"Failed to handle test failure: {str(e)}")
            
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get test statistics."""
        if not self.test_start_time:
            return {}
            
        duration = time.time() - self.test_start_time
        
        return {
            "duration": duration,
            "start_time": self.test_start_time,
            "end_time": time.time(),
            "context_info": self.test_context.get_context_info() if self.test_context else {}
        }
        
    def add_custom_metric(self, metric_name: str, value: Any, unit: str = ""):
        """Add custom metric to test."""
        self.logger.info(f"Metric: {metric_name} = {value} {unit}")
        self.allure_generator.add_metric(metric_name, value, unit)
        
    def add_custom_attachment(self, name: str, content: str, attachment_type: str = "text/plain"):
        """Add custom attachment to test."""
        self.allure_generator.add_attachment(name, content, attachment_type)
        
    def set_test_description(self, description: str):
        """Set test description."""
        self.allure_generator.set_test_description(description)
        
    def add_test_tag(self, tag: str):
        """Add test tag."""
        self.allure_generator.add_test_tag(tag)
        
    def add_test_link(self, name: str, url: str):
        """Add test link."""
        self.allure_generator.add_test_link(name, url)
        
    def set_test_severity(self, severity: str):
        """Set test severity."""
        self.allure_generator.set_test_severity(severity)
        
    def set_test_owner(self, owner: str):
        """Set test owner."""
        self.allure_generator.set_test_owner(owner)
        
    def set_test_story(self, story: str):
        """Set test story."""
        self.allure_generator.set_test_story(story)
        
    def set_test_feature(self, feature: str):
        """Set test feature."""
        self.allure_generator.set_test_feature(feature)
        
    def set_test_epic(self, epic: str):
        """Set test epic."""
        self.allure_generator.set_test_epic(epic)
