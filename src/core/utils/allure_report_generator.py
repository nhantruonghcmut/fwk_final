"""
Allure report generator for creating and managing Allure reports.
"""
import os
import json
import time
from typing import Any, Dict, List, Optional
from src.core.utils.report_logger import ReportLogger
from src.core.utils.config_manager import ConfigManager


class AllureReportGenerator:
    """Generator for Allure reports and attachments."""
    
    def __init__(self, logger: ReportLogger, config_manager: ConfigManager):
        self.logger = logger
        self.config_manager = config_manager
        self.results_dir = self.config_manager.get_allure_results_directory()
        self._ensure_results_directory()
        
    def _ensure_results_directory(self):
        """Ensure Allure results directory exists."""
        try:
            os.makedirs(self.results_dir, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create Allure results directory: {str(e)}")
            
    def add_attachment(self, name: str, content: str, attachment_type: str = "text/plain"):
        """Add attachment to Allure report."""
        try:
            import allure
            
            if attachment_type.startswith("text/"):
                allure.attach(content, name, attachment_type)
            else:
                allure.attach(content, name, attachment_type)
                
            self.logger.info(f"Added attachment: {name}")
            
        except ImportError:
            self.logger.warning("Allure not available, skipping attachment")
        except Exception as e:
            self.logger.log_error(e, "add_attachment")
            
    def add_screenshot(self, screenshot_path: str, name: str = "Screenshot"):
        """Add screenshot to Allure report."""
        try:
            import allure
            
            if os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    allure.attach(f.read(), name, allure.attachment_type.PNG)
                self.logger.info(f"Added screenshot: {name}")
            else:
                self.logger.warning(f"Screenshot file not found: {screenshot_path}")
                
        except ImportError:
            self.logger.warning("Allure not available, skipping screenshot")
        except Exception as e:
            self.logger.log_error(e, "add_screenshot")
    
    def add_trace(self, trace_path: str, name: str = "Playwright Trace"):
        """
        Add Playwright trace.zip file to Allure report.
        
        Args:
            trace_path: Path to trace.zip file
            name: Name for the attachment in Allure report
        """
        try:
            import allure
            
            if os.path.exists(trace_path):
                with open(trace_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name,
                        allure.attachment_type.ZIP,
                        extension="zip"
                    )
                self.logger.info(f"Added trace file to Allure: {name} ({trace_path})")
            else:
                self.logger.warning(f"Trace file not found: {trace_path}")
                
        except ImportError:
            self.logger.warning("Allure not available, skipping trace attachment")
        except Exception as e:
            self.logger.log_error(e, "add_trace")
            
    def add_log(self, log_content: str, name: str = "Test Log"):
        """Add log to Allure report."""
        try:
            import allure
            allure.attach(log_content, name, allure.attachment_type.TEXT)
            self.logger.info(f"Added log: {name}")
        except ImportError:
            self.logger.warning("Allure not available, skipping log")
        except Exception as e:
            self.logger.log_error(e, "add_log")
            
    def add_test_info(self, test_name: str, status: str):
        """Add test information to Allure report."""
        try:
            import allure
            
            allure.dynamic.title(test_name)
            allure.dynamic.description(f"Test status: {status}")
            
        except ImportError:
            self.logger.warning("Allure not available, skipping test info")
        except Exception as e:
            self.logger.log_error(e, "add_test_info")
            
    def add_test_result(self, test_name: str, result: str, duration: float, error: str = None):
        """Add test result to Allure report."""
        try:
            import allure
            
            allure.dynamic.title(test_name)
            allure.dynamic.description(f"Test result: {result}, Duration: {duration:.2f}s")
            
            if error:
                allure.attach(error, "Error Details", allure.attachment_type.TEXT)
                
        except ImportError:
            self.logger.warning("Allure not available, skipping test result")
        except Exception as e:
            self.logger.log_error(e, "add_test_result")
            
    def add_step_info(self, step_name: str, status: str):
        """Add step information to Allure report."""
        try:
            import allure
            
            with allure.step(step_name):
                allure.attach(f"Step status: {status}", "Step Info", allure.attachment_type.TEXT)
                
        except ImportError:
            self.logger.warning("Allure not available, skipping step info")
        except Exception as e:
            self.logger.log_error(e, "add_step_info")
            
    def add_step_result(self, step_name: str, result: str, error: str = None):
        """Add step result to Allure report."""
        try:
            import allure
            
            with allure.step(step_name):
                allure.attach(f"Step result: {result}", "Step Result", allure.attachment_type.TEXT)
                if error:
                    allure.attach(error, "Step Error", allure.attachment_type.TEXT)
                    
        except ImportError:
            self.logger.warning("Allure not available, skipping step result")
        except Exception as e:
            self.logger.log_error(e, "add_step_result")
            
    def add_verification(self, verification_data: Dict[str, Any]):
        """Add verification result to Allure report."""
        try:
            import allure
            
            verification_text = f"""
            Verification: {verification_data.get('name', 'Unknown')}
            Expected: {verification_data.get('expected', 'N/A')}
            Actual: {verification_data.get('actual', 'N/A')}
            Result: {'PASSED' if verification_data.get('result') else 'FAILED'}
            """
            
            allure.attach(verification_text, "Verification", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping verification")
        except Exception as e:
            self.logger.log_error(e, "add_verification")
            
    def add_test_context(self, context_info: Dict[str, Any]):
        """Add test context to Allure report."""
        try:
            import allure
            
            context_text = json.dumps(context_info, indent=2)
            allure.attach(context_text, "Test Context", allure.attachment_type.JSON)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping test context")
        except Exception as e:
            self.logger.log_error(e, "add_test_context")
            
    def add_test_data(self, data_type: str, data: Any):
        """Add test data to Allure report."""
        try:
            import allure
            
            if isinstance(data, (dict, list)):
                data_text = json.dumps(data, indent=2)
                allure.attach(data_text, f"Test Data - {data_type}", allure.attachment_type.JSON)
            else:
                allure.attach(str(data), f"Test Data - {data_type}", allure.attachment_type.TEXT)
                
        except ImportError:
            self.logger.warning("Allure not available, skipping test data")
        except Exception as e:
            self.logger.log_error(e, "add_test_data")
            
    def add_api_call(self, api_data: Dict[str, Any]):
        """Add API call information to Allure report."""
        try:
            import allure
            
            api_text = f"""
            API Call Details:
            Method: {api_data.get('method', 'N/A')}
            URL: {api_data.get('url', 'N/A')}
            Status Code: {api_data.get('status_code', 'N/A')}
            Response Time: {api_data.get('response_time', 'N/A')}ms
            """
            
            allure.attach(api_text, "API Call", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping API call")
        except Exception as e:
            self.logger.log_error(e, "add_api_call")
            
    def add_database_query(self, db_data: Dict[str, Any]):
        """Add database query information to Allure report."""
        try:
            import allure
            
            db_text = f"""
            Database Query Details:
            Query: {db_data.get('query', 'N/A')}
            Result Count: {db_data.get('result_count', 'N/A')}
            Execution Time: {db_data.get('execution_time', 'N/A')}ms
            """
            
            allure.attach(db_text, "Database Query", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping database query")
        except Exception as e:
            self.logger.log_error(e, "add_database_query")
            
    def add_mobile_action(self, mobile_data: Dict[str, Any]):
        """Add mobile action information to Allure report."""
        try:
            import allure
            
            mobile_text = f"""
            Mobile Action Details:
            Action Type: {mobile_data.get('action_type', 'N/A')}
            Element Info: {mobile_data.get('element_info', 'N/A')}
            Result: {mobile_data.get('result', 'N/A')}
            """
            
            allure.attach(mobile_text, "Mobile Action", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping mobile action")
        except Exception as e:
            self.logger.log_error(e, "add_mobile_action")
            
    def add_web_action(self, web_data: Dict[str, Any]):
        """Add web action information to Allure report."""
        try:
            import allure
            
            web_text = f"""
            Web Action Details:
            Action Type: {web_data.get('action_type', 'N/A')}
            Element Info: {web_data.get('element_info', 'N/A')}
            Result: {web_data.get('result', 'N/A')}
            """
            
            allure.attach(web_text, "Web Action", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping web action")
        except Exception as e:
            self.logger.log_error(e, "add_web_action")
            
    def add_error(self, error_message: str):
        """Add error information to Allure report."""
        try:
            import allure
            allure.attach(error_message, "Error", allure.attachment_type.TEXT)
        except ImportError:
            self.logger.warning("Allure not available, skipping error")
        except Exception as e:
            self.logger.log_error(e, "add_error")
            
    def add_warning(self, warning_message: str):
        """Add warning information to Allure report."""
        try:
            import allure
            allure.attach(warning_message, "Warning", allure.attachment_type.TEXT)
        except ImportError:
            self.logger.warning("Allure not available, skipping warning")
        except Exception as e:
            self.logger.log_error(e, "add_warning")
            
    def add_info(self, info_message: str):
        """Add info message to Allure report."""
        try:
            import allure
            allure.attach(info_message, "Info", allure.attachment_type.TEXT)
        except ImportError:
            self.logger.warning("Allure not available, skipping info")
        except Exception as e:
            self.logger.log_error(e, "add_info")
            
    def add_error_details(self, error_details: Dict[str, Any]):
        """Add detailed error information to Allure report."""
        try:
            import allure
            
            error_text = f"""
            Error Details:
            Test Name: {error_details.get('test_name', 'N/A')}
            Error Type: {error_details.get('error_type', 'N/A')}
            Error Message: {error_details.get('error_message', 'N/A')}
            Timestamp: {error_details.get('timestamp', 'N/A')}
            """
            
            allure.attach(error_text, "Error Details", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping error details")
        except Exception as e:
            self.logger.log_error(e, "add_error_details")
            
    def add_stack_trace(self, stack_trace: str):
        """Add stack trace to Allure report."""
        try:
            import allure
            allure.attach(stack_trace, "Stack Trace", allure.attachment_type.TEXT)
        except ImportError:
            self.logger.warning("Allure not available, skipping stack trace")
        except Exception as e:
            self.logger.log_error(e, "add_stack_trace")
            
    def add_metric(self, metric_name: str, value: Any, unit: str = ""):
        """Add metric to Allure report."""
        try:
            import allure
            
            metric_text = f"{metric_name}: {value} {unit}".strip()
            allure.attach(metric_text, "Metric", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping metric")
        except Exception as e:
            self.logger.log_error(e, "add_metric")
            
    def add_log_entry(self, level: str, message: str):
        """Add log entry to Allure report."""
        try:
            import allure
            
            log_text = f"[{level.upper()}] {message}"
            allure.attach(log_text, "Log Entry", allure.attachment_type.TEXT)
            
        except ImportError:
            self.logger.warning("Allure not available, skipping log entry")
        except Exception as e:
            self.logger.log_error(e, "add_log_entry")
            
    def set_test_description(self, description: str):
        """Set test description."""
        try:
            import allure
            allure.dynamic.description(description)
        except ImportError:
            self.logger.warning("Allure not available, skipping test description")
        except Exception as e:
            self.logger.log_error(e, "set_test_description")
            
    def add_test_tag(self, tag: str):
        """Add test tag."""
        try:
            import allure
            allure.dynamic.tag(tag)
        except ImportError:
            self.logger.warning("Allure not available, skipping test tag")
        except Exception as e:
            self.logger.log_error(e, "add_test_tag")
            
    def add_test_link(self, name: str, url: str):
        """Add test link."""
        try:
            import allure
            allure.dynamic.link(url, name)
        except ImportError:
            self.logger.warning("Allure not available, skipping test link")
        except Exception as e:
            self.logger.log_error(e, "add_test_link")
            
    def set_test_severity(self, severity: str):
        """Set test severity."""
        try:
            import allure
            allure.dynamic.severity(severity)
        except ImportError:
            self.logger.warning("Allure not available, skipping test severity")
        except Exception as e:
            self.logger.log_error(e, "set_test_severity")
            
    def set_test_owner(self, owner: str):
        """Set test owner."""
        try:
            import allure
            allure.label(owner)
        except ImportError:
            self.logger.warning("Allure not available, skipping test owner")
        except Exception as e:
            self.logger.log_error(e, "set_test_owner")
            
    def set_test_story(self, story: str):
        """Set test story."""
        try:
            import allure
            allure.dynamic.story(story)
        except ImportError:
            self.logger.warning("Allure not available, skipping test story")
        except Exception as e:
            self.logger.log_error(e, "set_test_story")
            
    def set_test_feature(self, feature: str):
        """Set test feature."""
        try:
            import allure
            allure.dynamic.feature(feature)
        except ImportError:
            self.logger.warning("Allure not available, skipping test feature")
        except Exception as e:
            self.logger.log_error(e, "set_test_feature")
            
    def set_test_epic(self, epic: str):
        """Set test epic."""
        try:
            import allure
            allure.dynamic.epic(epic)
        except ImportError:
            self.logger.warning("Allure not available, skipping test epic")
        except Exception as e:
            self.logger.log_error(e, "set_test_epic")
            
    def generate_report(self):
        """Generate Allure report.""" 
        try:
            if not self.config_manager.is_allure_enabled():
                self.logger.info("Allure reporting is disabled")
                return
                
            report_dir = self.config_manager.get_allure_report_directory()
            
            # Convert relative paths to absolute paths
            from pathlib import Path
            results_dir_abs = Path(self.results_dir).resolve()
            report_dir_abs = Path(report_dir).resolve()
            
            # Ensure directories exist
            os.makedirs(results_dir_abs, exist_ok=True)
            os.makedirs(report_dir_abs, exist_ok=True)
            
            # Check if results directory has any files
            if not any(results_dir_abs.iterdir()):
                self.logger.warning(f"No results found in {results_dir_abs}. Skipping report generation.")
                return
            
            # Generate report using allure command
            import subprocess
            import platform
            
            cmd = [
                "allure", "generate",
                str(results_dir_abs),
                "-o", str(report_dir_abs),
                "--single-file", "--clean"
            ]
            
            self.logger.info(f"Generating Allure report: {' '.join(cmd)}")
            
            # On Windows, use shell=True to ensure PATH is properly resolved
            # This allows subprocess to find commands in PATH like cmd.exe does
            use_shell = platform.system() == "Windows"
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=use_shell)
            
            if result.returncode == 0:
                report_file = report_dir_abs / "index.html"
                if report_file.exists():
                    self.logger.info(f"Allure report generated successfully: {report_file}")
                else:
                    self.logger.warning(f"Report file not found at expected location: {report_file}")
            else:
                self.logger.error(f"Failed to generate Allure report (exit code: {result.returncode})")
                if result.stdout:
                    self.logger.error(f"stdout: {result.stdout}")
                if result.stderr:
                    self.logger.error(f"stderr: {result.stderr}")
                
        except FileNotFoundError:
            self.logger.warning("Allure CLI not found. Install with: scoop install allure")
        except subprocess.TimeoutExpired:
            self.logger.error("Report generation timed out after 5 minutes")
        except Exception as e:
            self.logger.log_error(e, "generate_report")
            
            
