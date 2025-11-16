"""
Test context for thread-safe test data and state management.
"""
import threading
from typing import Any, Dict, Optional, List
from datetime import datetime
from src.core.utils.report_logger import ReportLogger


class TestContext:
    """Thread-safe test context for managing test data and state."""
    
    def __init__(self):
        self.logger = ReportLogger()
        self._lock = threading.RLock()
        self._data = {}
        self._test_info = {}
        self._start_time = datetime.now()
        self._thread_id = threading.current_thread().ident
        
    def set(self, key: str, value: Any):
        """Set context data."""
        with self._lock:
            self._data[key] = value
            self.logger.debug(f"Test context set: {key} = {value}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get context data."""
        with self._lock:
            return self._data.get(key, default)
            
    def has(self, key: str) -> bool:
        """Check if key exists in context."""
        with self._lock:
            return key in self._data
            
    def remove(self, key: str):
        """Remove key from context."""
        with self._lock:
            if key in self._data:
                del self._data[key]
                self.logger.debug(f"Test context removed: {key}")
                
    def clear(self):
        """Clear all context data."""
        with self._lock:
            self._data.clear()
            self._test_info.clear()
            self.logger.debug("Test context cleared")
    def clear_steps(self):
        """Clear all test steps."""
        with self._lock:
            self.set("test_steps", [])
        
    def clear_errors(self):
        """Clear all errors."""
        with self._lock:
            self.set("errors", [])

    def update(self, data: Dict[str, Any]):
        """Update context with dictionary."""
        with self._lock:
            self._data.update(data)
            self.logger.debug(f"Test context updated with {len(data)} items")
            
    def get_all(self) -> Dict[str, Any]:
        """Get all context data."""
        with self._lock:
            return self._data.copy()
            
    def set_test_info(self, key: str, value: Any):
        """Set test information."""
        with self._lock:
            self._test_info[key] = value
            self.logger.debug(f"Test info set: {key} = {value}")
            
    def get_test_info(self, key: str, default: Any = None) -> Any:
        """Get test information."""
        with self._lock:
            return self._test_info.get(key, default)
            
    def get_all_test_info(self) -> Dict[str, Any]:
        """Get all test information."""
        with self._lock:
            return self._test_info.copy()
            
    def set_test_name(self, test_name: str):
        """Set test name."""
        self.set_test_info("test_name", test_name)
        
    def get_test_name(self) -> Optional[str]:
        """Get test name."""
        return self.get_test_info("test_name")
        
    def set_test_file(self, test_file: str):
        """Set test file."""
        self.set_test_info("test_file", test_file)
        
    def get_test_file(self) -> Optional[str]:
        """Get test file."""
        return self.get_test_info("test_file")
        
    def set_test_class(self, test_class: str):
        """Set test class."""
        self.set_test_info("test_class", test_class)
        
    def get_test_class(self) -> Optional[str]:
        """Get test class."""
        return self.get_test_info("test_class")
        
    def set_test_method(self, test_method: str):
        """Set test method."""
        self.set_test_info("test_method", test_method)
        
    def get_test_method(self) -> Optional[str]:
        """Get test method."""
        return self.get_test_info("test_method")
        
    def set_browser_type(self, browser_type: str):
        """Set browser type."""
        self.set_test_info("browser_type", browser_type)
        
    def get_browser_type(self) -> Optional[str]:
        """Get browser type."""
        return self.get_test_info("browser_type")
        
    def set_platform(self, platform: str):
        """Set platform (web/mobile)."""
        self.set_test_info("platform", platform)
        
    def get_platform(self) -> Optional[str]:
        """Get platform."""
        return self.get_test_info("platform")
        
    def set_device_name(self, device_name: str):
        """Set device name."""
        self.set_test_info("device_name", device_name)
        
    def get_device_name(self) -> Optional[str]:
        """Get device name."""
        return self.get_test_info("device_name")
        
    def set_app_type(self, app_type: str):
        """Set application type."""
        self.set_test_info("app_type", app_type)
        
    def get_app_type(self) -> Optional[str]:
        """Get application type."""
        return self.get_test_info("app_type")
        
    def set_environment(self, environment: str):
        """Set environment."""
        self.set_test_info("environment", environment)
        
    def get_environment(self) -> Optional[str]:
        """Get environment."""
        return self.get_test_info("environment")
    
    def set_browser_context_config(self, context_config: Dict[str, Any]):
        """Set browser context configuration (viewport, user_agent, locale, etc.)."""
        self.set("browser_context_config", context_config)
        
    def get_browser_context_config(self) -> Optional[Dict[str, Any]]:
        """Get browser context configuration."""
        return self.get("browser_context_config")
        
    def set_user_credentials(self, username: str, password: str):
        """Set user credentials."""
        self.set("username", username)
        self.set("password", password)
        
    def get_user_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """Get user credentials."""
        return self.get("username"), self.get("password")
        
    def set_test_data(self, test_data: Dict[str, Any]):
        """Set test data."""
        self.set("test_data", test_data)
        
    def get_test_data(self) -> Optional[Dict[str, Any]]:
        """Get test data."""
        return self.get("test_data")
        
    def set_api_response(self, endpoint: str, response: Any):
        """Set API response."""
        api_responses = self.get("api_responses", {})
        api_responses[endpoint] = response
        self.set("api_responses", api_responses)
        
    def get_api_response(self, endpoint: str) -> Any:
        """Get API response."""
        api_responses = self.get("api_responses", {})
        return api_responses.get(endpoint)
        
    def set_database_result(self, query: str, result: Any):
        """Set database query result."""
        db_results = self.get("database_results", {})
        db_results[query] = result
        self.set("database_results", db_results)
        
    def get_database_result(self, query: str) -> Any:
        """Get database query result."""
        db_results = self.get("database_results", {})
        return db_results.get(query)
        
    def add_step(self, step_name: str, step_data: Any = None):
        """Add test step."""
        steps = self.get("test_steps", [])
        step = {
            "name": step_name,
            "data": step_data,
            "timestamp": datetime.now().isoformat()
        }
        steps.append(step)
        self.set("test_steps", steps)
        
    def get_steps(self) -> List[Dict[str, Any]]:
        """Get all test steps."""
        return self.get("test_steps", [])
        
    def add_verification(self, verification_name: str, expected: Any, actual: Any, result: bool):
        """Add verification result."""
        verifications = self.get("verifications", [])
        verification = {
            "name": verification_name,
            "expected": expected,
            "actual": actual,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        verifications.append(verification)
        self.set("verifications", verifications)
        
    def get_verifications(self) -> List[Dict[str, Any]]:
        """Get all verifications."""
        return self.get("verifications", [])
        
    def add_error(self, error: Exception, context: str = ""):
        """Add error to context."""
        errors = self.get("errors", [])
        error_info = {
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        errors.append(error_info)
        self.set("errors", errors)
        
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self.get("errors", [])
        
    def add_screenshot(self, screenshot_path: str, description: str = ""):
        """Add screenshot to context."""
        screenshots = self.get("screenshots", [])
        screenshot_info = {
            "path": screenshot_path,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        screenshots.append(screenshot_info)
        self.set("screenshots", screenshots)
        
    def get_screenshots(self) -> List[Dict[str, Any]]:
        """Get all screenshots."""
        return self.get("screenshots", [])
        
    def add_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Add performance metric."""
        metrics = self.get("performance_metrics", [])
        metric = {
            "name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
        metrics.append(metric)
        self.set("performance_metrics", metrics)
        
    def get_performance_metrics(self) -> List[Dict[str, Any]]:
        """Get all performance metrics."""
        return self.get("performance_metrics", [])
        
    def set_test_status(self, status: str):
        """Set test status."""
        self.set_test_info("status", status)
        
    def get_test_status(self) -> Optional[str]:
        """Get test status."""
        return self.get_test_info("status")
        
    def set_test_result(self, result: str):
        """Set test result."""
        self.set_test_info("result", result)
        
    def get_test_result(self) -> Optional[str]:
        """Get test result."""
        return self.get_test_info("result")
        
    def get_duration(self) -> float:
        """Get test duration in seconds."""
        end_time = datetime.now()
        duration = (end_time - self._start_time).total_seconds()
        return duration
        
    def get_context_info(self) -> Dict[str, Any]:
        """Get comprehensive context information."""
        with self._lock:
            info = {
                "thread_id": self._thread_id,
                "start_time": self._start_time.isoformat(),
                "duration": self.get_duration(),
                "test_info": self._test_info.copy(),
                "data_keys": list(self._data.keys()),
                "data_count": len(self._data),
                "steps_count": len(self.get_steps()),
                "verifications_count": len(self.get_verifications()),
                "errors_count": len(self.get_errors()),
                "screenshots_count": len(self.get_screenshots()),
                "performance_metrics_count": len(self.get_performance_metrics())
            }
            # Include browser context config if available
            browser_context_config = self.get_browser_context_config()
            if browser_context_config:
                info["browser_context_config"] = browser_context_config
            return info
            
    def get_next_snapshot_stt(self, test_id: str) -> int:
        """Get next snapshot sequence number for a test ID and increment it."""
        with self._lock:
            snapshot_counters = self.get("snapshot_counters", {})
            current_stt = snapshot_counters.get(test_id, 0)
            next_stt = current_stt + 1
            snapshot_counters[test_id] = next_stt
            self.set("snapshot_counters", snapshot_counters)
            return next_stt
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        return {
            "test_name": self.get_test_name(),
            "test_file": self.get_test_file(),
            "test_class": self.get_test_class(),
            "test_method": self.get_test_method(),
            "platform": self.get_platform(),
            "browser_type": self.get_browser_type(),
            "device_name": self.get_device_name(),
            "app_type": self.get_app_type(),
            "environment": self.get_environment(),
            "status": self.get_test_status(),
            "result": self.get_test_result(),
            "duration": self.get_duration(),
            "steps": len(self.get_steps()),
            "verifications": len(self.get_verifications()),
            "errors": len(self.get_errors()),
            "screenshots": len(self.get_screenshots()),
            "performance_metrics": len(self.get_performance_metrics())
        }
        
    def export_to_dict(self) -> Dict[str, Any]:
        """Export context to dictionary."""
        with self._lock:
            return {
                "test_info": self._test_info.copy(),
                "data": self._data.copy(),
                "steps": self.get_steps(),
                "verifications": self.get_verifications(),
                "errors": self.get_errors(),
                "screenshots": self.get_screenshots(),
                "performance_metrics": self.get_performance_metrics(),
                "context_info": self.get_context_info()
            }
            
    def import_from_dict(self, data: Dict[str, Any]):
        """Import context from dictionary."""
        with self._lock:
            if "test_info" in data:
                self._test_info.update(data["test_info"])
            if "data" in data:
                self._data.update(data["data"])
            if "steps" in data:
                self.set("test_steps", data["steps"])
            if "verifications" in data:
                self.set("verifications", data["verifications"])
            if "errors" in data:
                self.set("errors", data["errors"])
            if "screenshots" in data:
                self.set("screenshots", data["screenshots"])
            if "performance_metrics" in data:
                self.set("performance_metrics", data["performance_metrics"])
                
    def is_empty(self) -> bool:
        """Check if context is empty."""
        with self._lock:
            return len(self._data) == 0 and len(self._test_info) == 0
            
    def get_size(self) -> int:
        """Get context size."""
        with self._lock:
            return len(self._data) + len(self._test_info)
            
    def __str__(self) -> str:
        """String representation of context."""
        return f"TestContext(thread_id={self._thread_id}, size={self.get_size()})"
        
    def __repr__(self) -> str:
        """Representation of context."""
        return self.__str__()
