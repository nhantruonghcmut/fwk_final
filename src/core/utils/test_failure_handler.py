"""
Test failure handler for managing test failures and recovery.
"""
import traceback
from typing import Any, Dict, List, Optional, Callable
from src.core.utils.report_logger import ReportLogger
from src.core.utils.screenshot_util import ScreenshotUtil


class TestFailureHandler:
    """Handler for managing test failures and recovery strategies."""
    
    def __init__(self):
        self.logger = ReportLogger()
        self.screenshot_util = ScreenshotUtil()
        self.failure_count = 0
        self.recovery_strategies = {}
        
    def handle_failure(self, test_name: str, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Handle test failure with recovery strategies."""
        try:
            self.failure_count += 1
            self.logger.error(f"Test failure #{self.failure_count}: {test_name}")
            self.logger.error(f"Error: {str(error)}")
            
            # Log stack trace
            stack_trace = traceback.format_exc()
            self.logger.error(f"Stack trace:\n{stack_trace}")
            
            # Take screenshot if available
            self._take_failure_screenshot(test_name, context)
            
            # Log context information
            if context:
                self.logger.error(f"Failure context: {context}")
                
            # Attempt recovery
            recovery_success = self._attempt_recovery(test_name, error, context)
            
            return recovery_success
            
        except Exception as e:
            self.logger.log_error(e, "handle_failure")
            return False
            
    # def _take_failure_screenshot(self, test_name: str, context: Dict[str, Any]):
    #     """Take screenshot on failure."""
    #     try:
    #         if context and "page" in context:
    #             screenshot_path = self.screenshot_util.take_screenshot_on_failure(test_name, page=context["page"])
    #         elif context and "driver" in context:
    #             screenshot_path = self.screenshot_util.take_screenshot_on_failure(test_name, driver=context["driver"])
    #         else:
    #             screenshot_path = self.screenshot_util.take_screenshot_on_failure(test_name)
                
    #         if screenshot_path:
    #             self.logger.info(f"Failure screenshot saved: {screenshot_path}")
                
    #     except Exception as e:
    #         self.logger.log_error(e, "_take_failure_screenshot")
    
    def _take_failure_screenshot(self, test_name: str, context: Dict[str, Any]):
        """Take screenshot on failure."""
        try:
            # Add explicit check for page object
            if context and "page" in context and context["page"] is not None:
                screenshot_path = self.screenshot_util.take_screenshot_on_failure(test_name, page=context["page"])
            elif context and "driver" in context and context["driver"] is not None:
                screenshot_path = self.screenshot_util.take_screenshot_on_failure(test_name, driver=context["driver"])
            else:
                self.logger.error("No page or driver provided for screenshot")
                return
                
            if screenshot_path:
                self.logger.info(f"Failure screenshot saved: {screenshot_path}")
                
        except Exception as e:
            self.logger.log_error(e, "_take_failure_screenshot")
            
    def _attempt_recovery(self, test_name: str, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from failure."""
        try:
            error_type = type(error).__name__
            
            # Check if recovery strategy exists for this error type
            if error_type in self.recovery_strategies:
                recovery_func = self.recovery_strategies[error_type]
                self.logger.info(f"Attempting recovery for {error_type}")
                
                try:
                    recovery_result = recovery_func(test_name, error, context)
                    if recovery_result:
                        self.logger.info(f"Recovery successful for {test_name}")
                        return True
                    else:
                        self.logger.warning(f"Recovery failed for {test_name}")
                        return False
                except Exception as recovery_error:
                    self.logger.error(f"Recovery strategy failed: {str(recovery_error)}")
                    return False
            else:
                self.logger.info(f"No recovery strategy found for {error_type}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "_attempt_recovery")
            return False
            
    def add_recovery_strategy(self, error_type: str, recovery_func: Callable):
        """Add recovery strategy for specific error type."""
        try:
            self.recovery_strategies[error_type] = recovery_func
            self.logger.info(f"Added recovery strategy for {error_type}")
        except Exception as e:
            self.logger.log_error(e, "add_recovery_strategy")
            
    def remove_recovery_strategy(self, error_type: str):
        """Remove recovery strategy for specific error type."""
        try:
            if error_type in self.recovery_strategies:
                del self.recovery_strategies[error_type]
                self.logger.info(f"Removed recovery strategy for {error_type}")
        except Exception as e:
            self.logger.log_error(e, "remove_recovery_strategy")
            
    def get_recovery_strategies(self) -> Dict[str, Callable]:
        """Get all recovery strategies."""
        return self.recovery_strategies.copy()
        
    def clear_recovery_strategies(self):
        """Clear all recovery strategies."""
        self.recovery_strategies.clear()
        self.logger.info("Cleared all recovery strategies")
        
    def get_failure_count(self) -> int:
        """Get total failure count."""
        return self.failure_count
        
    def reset_failure_count(self):
        """Reset failure count."""
        self.failure_count = 0
        self.logger.info("Reset failure count")
        
    def create_failure_report(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create failure report."""
        try:
            report = {
                "total_failures": len(failures),
                "failure_types": {},
                "failure_details": failures,
                "recovery_attempts": 0,
                "successful_recoveries": 0
            }
            
            # Count failure types
            for failure in failures:
                error_type = failure.get("error_type", "Unknown")
                report["failure_types"][error_type] = report["failure_types"].get(error_type, 0) + 1
                
            # Count recovery attempts and successes
            for failure in failures:
                if failure.get("recovery_attempted"):
                    report["recovery_attempts"] += 1
                if failure.get("recovery_successful"):
                    report["successful_recoveries"] += 1
                    
            return report
            
        except Exception as e:
            self.logger.log_error(e, "create_failure_report")
            return {}
            
    def analyze_failure_patterns(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze failure patterns."""
        try:
            analysis = {
                "most_common_error": None,
                "most_common_test": None,
                "failure_rate_by_test": {},
                "failure_rate_by_error": {},
                "recovery_success_rate": 0
            }
            
            if not failures:
                return analysis
                
            # Count failures by error type
            error_counts = {}
            test_counts = {}
            recovery_attempts = 0
            successful_recoveries = 0
            
            for failure in failures:
                error_type = failure.get("error_type", "Unknown")
                test_name = failure.get("test_name", "Unknown")
                
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
                test_counts[test_name] = test_counts.get(test_name, 0) + 1
                
                if failure.get("recovery_attempted"):
                    recovery_attempts += 1
                if failure.get("recovery_successful"):
                    successful_recoveries += 1
                    
            # Find most common error and test
            if error_counts:
                analysis["most_common_error"] = max(error_counts, key=error_counts.get)
            if test_counts:
                analysis["most_common_test"] = max(test_counts, key=test_counts.get)
                
            # Calculate failure rates
            total_failures = len(failures)
            for error_type, count in error_counts.items():
                analysis["failure_rate_by_error"][error_type] = (count / total_failures) * 100
                
            for test_name, count in test_counts.items():
                analysis["failure_rate_by_test"][test_name] = (count / total_failures) * 100
                
            # Calculate recovery success rate
            if recovery_attempts > 0:
                analysis["recovery_success_rate"] = (successful_recoveries / recovery_attempts) * 100
                
            return analysis
            
        except Exception as e:
            self.logger.log_error(e, "analyze_failure_patterns")
            return {}
            
    def suggest_improvements(self, failures: List[Dict[str, Any]]) -> List[str]:
        """Suggest improvements based on failure analysis."""
        try:
            suggestions = []
            analysis = self.analyze_failure_patterns(failures)
            
            # Suggest based on most common error
            if analysis.get("most_common_error"):
                most_common_error = analysis["most_common_error"]
                suggestions.append(f"Focus on fixing {most_common_error} - most common failure type")
                
            # Suggest based on most common test
            if analysis.get("most_common_test"):
                most_common_test = analysis["most_common_test"]
                suggestions.append(f"Review {most_common_test} - most failing test")
                
            # Suggest based on recovery success rate
            recovery_rate = analysis.get("recovery_success_rate", 0)
            if recovery_rate < 50:
                suggestions.append("Improve recovery strategies - low success rate")
            elif recovery_rate > 80:
                suggestions.append("Recovery strategies are working well")
                
            # Suggest based on failure patterns
            if len(failures) > 10:
                suggestions.append("Consider implementing better error handling")
                
            return suggestions
            
        except Exception as e:
            self.logger.log_error(e, "suggest_improvements")
            return []
            
    def log_failure_summary(self, failures: List[Dict[str, Any]]):
        """Log failure summary."""
        try:
            if not failures:
                self.logger.info("No failures to summarize")
                return
                
            analysis = self.analyze_failure_patterns(failures)
            suggestions = self.suggest_improvements(failures)
            
            self.logger.info("=== FAILURE SUMMARY ===")
            self.logger.info(f"Total failures: {len(failures)}")
            
            if analysis.get("most_common_error"):
                self.logger.info(f"Most common error: {analysis['most_common_error']}")
                
            if analysis.get("most_common_test"):
                self.logger.info(f"Most failing test: {analysis['most_common_test']}")
                
            if analysis.get("recovery_success_rate") is not None:
                self.logger.info(f"Recovery success rate: {analysis['recovery_success_rate']:.1f}%")
                
            if suggestions:
                self.logger.info("Suggestions:")
                for suggestion in suggestions:
                    self.logger.info(f"  - {suggestion}")
                    
        except Exception as e:
            self.logger.log_error(e, "log_failure_summary")
            
    def create_failure_log(self, failures: List[Dict[str, Any]], file_path: str):
        """Create failure log file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("TEST FAILURE LOG\n")
                f.write("=" * 50 + "\n\n")
                
                for i, failure in enumerate(failures, 1):
                    f.write(f"Failure #{i}\n")
                    f.write(f"Test: {failure.get('test_name', 'Unknown')}\n")
                    f.write(f"Error: {failure.get('error', 'Unknown')}\n")
                    f.write(f"Error Type: {failure.get('error_type', 'Unknown')}\n")
                    f.write(f"Timestamp: {failure.get('timestamp', 'Unknown')}\n")
                    f.write(f"Recovery Attempted: {failure.get('recovery_attempted', False)}\n")
                    f.write(f"Recovery Successful: {failure.get('recovery_successful', False)}\n")
                    f.write("-" * 30 + "\n\n")
                    
            self.logger.info(f"Failure log created: {file_path}")
            
        except Exception as e:
            self.logger.log_error(e, "create_failure_log")
            
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get failure statistics."""
        try:
            return {
                "total_failures": self.failure_count,
                "recovery_strategies_count": len(self.recovery_strategies),
                "available_recovery_strategies": list(self.recovery_strategies.keys())
            }
        except Exception as e:
            self.logger.log_error(e, "get_failure_statistics")
            return {}
