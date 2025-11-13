"""
Centralized logging utility using ReportLogger.
"""
import logging
import os
import sys
import threading
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from src.core.utils.config_manager import ConfigManager

class ReportLogger:
    """Centralized logging utility for test automation."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation with config_manager support."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ReportLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger if not already initialized."""
        if not hasattr(self, 'initialized'):
            self._logger = None
            self.log_config = None
            self.initialized = True
            self._default = True
            self._setup_default_logger()
            print("default_logger initialized")

    def setup_logger(self,_config_manager ):
        """Setup logger configuration."""
        try:
            self.log_config = _config_manager.get_logging_config()
            self._default = False

            # Create logger
            self._logger = logging.getLogger("TestAutomation")
            self._logger.setLevel(logging.DEBUG)
            
            # Clear existing handlers
            self._logger.handlers.clear()
            
            # Setup formatters
            self._setup_formatters()
            
            # Setup handlers
            self._setup_handlers()
            
        except Exception as e:
            print(f"Failed to setup logger: {str(e)} \n The framework is now switching to use default logger")
            self._setup_default_logger()
    
    def _setup_formatters(self):
        """Setup log formatters."""
        self.formatters = {
            'detailed': logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            'simple': logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            'json': logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        }
    
    def _setup_handlers(self):
        """Setup log handlers."""
        if not self.log_config:
            self._setup_default_logger()
            return
            
        # Console handler
        if self.log_config.get('console', {}).get('enabled', True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.log_config.get('console', {}).get('level', 'INFO')))
            console_handler.setFormatter(self.formatters[self.log_config.get('console', {}).get('format', 'simple')])
            self._logger.addHandler(console_handler)
        
        # File handler
        if self.log_config.get('file', {}).get('enabled', True):
            log_dir = self.log_config.get('file', {}).get('directory', 'reports/logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"test_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, self.log_config.get('file', {}).get('level', 'DEBUG')))
            file_handler.setFormatter(self.formatters[self.log_config.get('file', {}).get('format', 'detailed')])
            self._logger.addHandler(file_handler)
        
        # Error file handler
        if self.log_config.get('error_file', {}).get('enabled', True):
            log_dir = self.log_config.get('error_file', {}).get('directory', 'reports/logs')
            os.makedirs(log_dir, exist_ok=True)
            
            error_file = os.path.join(log_dir, f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            error_handler = logging.FileHandler(error_file, encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self.formatters[self.log_config.get('error_file', {}).get('format', 'detailed')])
            self._logger.addHandler(error_handler)
    
    def _setup_default_logger(self):
        """Setup default logger configuration."""
        self._logger = logging.getLogger("TestAutomation")
        self._logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self._logger.addHandler(console_handler)
        
        # File handler
        os.makedirs('reports/logs', exist_ok=True)
        file_handler = logging.FileHandler(
            f'reports/logs/test_execution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self._logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self._logger.critical(message, *args, **kwargs)
    
    def log(self, level: str, message: str, *args, **kwargs):
        """Log message with specified level."""
        log_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.log(log_level, message, *args, **kwargs)
    
    def log_test_start(self, test_name: str, test_file: str):
        """Log test start."""
        self.info(f"[START] Starting test: {test_name} in {test_file}")
    
    def log_test_end(self, test_name: str, result: str, duration: float):
        """Log test end."""
        status_emoji = "[OK]" if result == "PASSED" else "[FAIL]" if result == "FAILED" else "[SKIP]"
        self.info(f"{status_emoji} Test completed: {test_name} - {result} ({duration:.2f}s)")
    
    def log_test_step(self, step: str):
        """Log test step."""
        self.info(f"[STEP] Test Step: {step}")
    
    def log_verification(self, verification: str, result: bool):
        """Log verification result."""
        status = "[OK] PASSED" if result else "[FAIL] FAILED"
        self.info(f"[VERIFY] Verification: {verification} - {status}")
    
    def log_action(self, action: str, element: str = "", value: str = ""):
        """Log user action."""
        if element and value:
            self.info(f"[ACTION] Action: {action} on '{element}' with value '{value}'")
        elif element:
            self.info(f"[ACTION] Action: {action} on '{element}'")
        else:
            self.info(f"[ACTION] Action: {action}")
    
    def log_api_call(self, method: str, url: str, status_code: int, response_time: float):
        """Log API call."""
        self.info(f"[API] API Call: {method} {url} - {status_code} ({response_time:.2f}ms)")
    
    def log_database_query(self, query: str, result_count: int, execution_time: float):
        """Log database query."""
        self.info(f"[DB] Database Query: {query} - {result_count} results ({execution_time:.2f}ms)")
    
    def log_screenshot(self, screenshot_path: str):
        """Log screenshot taken."""
        self.info(f"[SCREENSHOT] Screenshot taken: {screenshot_path}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with context."""
        error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
        self.error(error_msg)
        
        # Log stack trace
        import traceback
        self.debug(f"Stack trace:\n{traceback.format_exc()}")
    
    def log_warning(self, warning: str, context: str = ""):
        """Log warning with context."""
        warning_msg = f"[WARNING] Warning in {context}: {warning}" if context else f"[WARNING] Warning: {warning}"
        self.warning(warning_msg)
    
    def log_info(self, info: str, context: str = ""):
        """Log info with context."""
        info_msg = f"[INFO] Info in {context}: {info}" if context else f"[INFO] Info: {info}"
        self.info(info_msg)
    
    def log_performance(self, operation: str, duration: float):
        """Log performance metric."""
        self.info(f"Performance: {operation} took {duration:.2f}ms")
    
    def log_configuration(self, config_name: str, config_value: Any):
        """Log configuration value."""
        self.debug(f"[CONFIG] Configuration: {config_name} = {config_value}")
    
    def log_environment(self, environment: str):
        """Log environment information."""
        self.info(f"[ENV] Environment: {environment}")
    
    def log_browser_info(self, browser_type: str, version: str = ""):
        """Log browser information."""
        browser_info = f"[BROWSER] Browser: {browser_type}"
        if version:
            browser_info += f" (Version: {version})"
        self.info(browser_info)
    
    def log_mobile_info(self, platform: str, device_name: str, version: str = ""):
        """Log mobile device information."""
        mobile_info = f"📱 Mobile: {platform} - {device_name}"
        if version:
            mobile_info += f" (Version: {version})"
        self.info(mobile_info)
    
    def log_suite_start(self, suite_name: str, test_count: int):
        """Log test suite start."""
        self.info(f"[SUITE] Starting test suite: {suite_name} ({test_count} tests)")
    
    def log_suite_end(self, suite_name: str, passed: int, failed: int, skipped: int, duration: float):
        """Log test suite end."""
        total = passed + failed + skipped
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.info(f"Test suite completed: {suite_name}")
        self.info(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
        self.info(f"Pass rate: {pass_rate:.1f}%")
        self.info(f"Duration: {duration:.2f} seconds")
    
    def get_log_file_path(self) -> Optional[str]:
        """Get current log file path."""
        for handler in self._logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler.baseFilename
        return None
    
    def get_log_level(self) -> str:
        """Get current log level."""
        return logging.getLevelName(self._logger.level)
    
    def set_log_level(self, level: str):
        """Set log level."""
        log_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.setLevel(log_level)
        for handler in self._logger.handlers:
            handler.setLevel(log_level)
    
    def add_handler(self, handler: logging.Handler):
        """Add custom handler."""
        self._logger.addHandler(handler)
    
    def remove_handler(self, handler: logging.Handler):
        """Remove handler."""
        self._logger.removeHandler(handler)
    
    def clear_handlers(self):
        """Clear all handlers."""
        self._logger.handlers.clear()
    
    def get_logger(self) -> 'logging._logger':
        """Get the underlying logger instance."""
        if self._logger is None:
            self._setup_default_logger()
        return self._logger
    
    def create_child_logger(self, name: str) -> 'logging._logger':
        # """Create child logger."""
        # return self._logger.getChild(name)
        """Create child logger with unique name for parallel tests."""
        if self._logger is None:
            self._setup_default_logger()

        child_name = f"{self._logger.name}.{name}.{threading.get_ident()}"
        return self._logger.getChild(child_name)
    
    def log_dict(self, data: Dict[str, Any], title: str = "Data"):
        """Log dictionary data in formatted way."""
        self.info(f"📋 {title}:")
        for key, value in data.items():
            self.info(f"  {key}: {value}")
    
    def log_list(self, data: list, title: str = "List"):
        """Log list data in formatted way."""
        self.info(f"📋 {title}:")
        for i, item in enumerate(data):
            self.info(f"  [{i}]: {item}")
    
    def log_separator(self, char: str = "=", length: int = 50):
        """Log separator line."""
        self.info(char * length)
    
    def log_header(self, title: str, char: str = "=", length: int = 50):
        """Log header with title."""
        self.log_separator(char, length)
        self.info(f" {title} ")
        self.log_separator(char, length)
    
    def log_footer(self, title: str, char: str = "=", length: int = 50):
        """Log footer with title."""
        self.log_separator(char, length)
        self.info(f" {title} ")
        self.log_separator(char, length)
    
    def flush_logs(self):
        """Flush all log handlers."""
        for handler in self._logger.handlers:
            handler.flush()
    
    def close_logs(self):
        """Close all log handlers."""
        for handler in self._logger.handlers:
            handler.close()
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get log statistics."""
        stats = {
            "log_level": self.get_log_level(),
            "handlers_count": len(self._logger.handlers),
            "log_file": self.get_log_file_path()
        }
        
        # Count log levels if possible
        if hasattr(self._logger, 'handlers'):
            for handler in self._logger.handlers:
                if hasattr(handler, 'level'):
                    stats[f"handler_{type(handler).__name__}_level"] = logging.getLevelName(handler.level)
        
        return stats
