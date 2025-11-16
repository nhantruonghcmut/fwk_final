"""
Retry utilities for mobile operations to handle connection issues.
Provides decorators and helpers to retry operations when encountering
WebDriver connection errors like "socket hang up".

Configuration is read from:
1. mobile.connection_retry (mobile_config.yaml) - highest priority
2. retry (config.yaml) - fallback
3. Default values - if not found in config
"""
import time
from functools import wraps
from typing import Callable, Any
from selenium.common.exceptions import WebDriverException
from appium.webdriver.webdriver import WebDriver
from src.core.utils.report_logger import ReportLogger
from src.core.utils.config_manager import ConfigManager


def _get_retry_config() -> tuple[int, float]:
    """
    Get retry configuration from config files.
    
    Priority:
    1. mobile.connection_retry (mobile_config.yaml)
    2. retry (config.yaml)
    3. Default values (max_retries=3, delay=2.0)
    
    Returns:
        Tuple of (max_retries, delay)
    """
    logger = ReportLogger()
    config_manager = ConfigManager(logger)
    
    # Load base configs if not already loaded
    if not config_manager._base_configs_loaded:
        config_manager._load_base_configs()
    
    # Try to get connection_retry from mobile config first
    connection_retry = config_manager.get_config_value('mobile.connection_retry', {})
    if connection_retry and isinstance(connection_retry, dict):
        max_retries = connection_retry.get('max_retries')
        delay = connection_retry.get('delay')
        if max_retries is not None and delay is not None:
            return int(max_retries), float(delay)
    
    # Fallback to general retry config
    retry_config = config_manager.get_config_value('retry', {})
    if retry_config and isinstance(retry_config, dict):
        max_retries = retry_config.get('count')
        delay = retry_config.get('delay', 1000) / 1000.0  # Convert ms to seconds
        if max_retries is not None:
            return int(max_retries), float(delay)
    
    # Default values
    return 3, 2.0


def retry_on_connection_error():
    """
    Decorator to retry operations on connection errors.
    
    This decorator catches WebDriverException errors that indicate connection
    issues (socket hang up, proxy errors, etc.) and retries the operation
    with linear backoff (delay increases linearly with each attempt).
    
    Configuration is automatically read from config files:
    - mobile.connection_retry (mobile_config.yaml) - highest priority
    - retry (config.yaml) - fallback
    - Default: max_retries=3, delay=2.0 seconds
    
    Returns:
        Decorated function that retries on connection errors
    
    Example:
        @retry_on_connection_error()
        def find_element(self, locator):
            return self.driver.find_element(*locator)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = ReportLogger()
            # Get retry config from config files
            max_retries, delay = _get_retry_config()
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except WebDriverException as e:
                    error_msg = str(e).lower()
                    
                    # Critical errors that should NOT be retried (require driver restart)
                    critical_errors = [
                        'instrumentation process is not running',
                        'instrumentation process crashed',
                        'uiautomator2 server crashed',
                        'session deleted',
                        'session terminated'
                    ]
                    
                    # If it's a critical error, re-raise immediately (no retry)
                    if any(keyword in error_msg for keyword in critical_errors):
                        logger.error(
                            f"[CRITICAL] {func.__name__} failed with critical error (cannot retry): {str(e)[:200]}"
                        )
                        raise
                    
                    # Check for connection-related errors that CAN be retried
                    connection_errors = [
                        'socket hang up',
                        'could not proxy command',
                        'connection refused',
                        'connection reset',
                        'session not created',
                        'invalid session id',
                        'no such session',
                        'session does not exist',
                        'connection aborted',
                        'broken pipe'
                    ]
                    
                    if any(keyword in error_msg for keyword in connection_errors):
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = delay * (attempt + 1)  # Linear backoff
                            logger.warning(
                                f"[RETRY] {func.__name__} failed with connection error "
                                f"(attempt {attempt + 1}/{max_retries}): {str(e)[:100]}"
                            )
                            logger.info(f"[RETRY] Waiting {wait_time:.1f} seconds before retry...")
                            time.sleep(wait_time)
                            continue
                    
                    # Re-raise if not a connection error or critical error
                    raise
                except Exception as e:
                    # Re-raise non-WebDriver exceptions immediately
                    raise
            
            # All retries exhausted
            logger.error(
                f"[RETRY] {func.__name__} failed after {max_retries} attempts. "
                f"Last error: {str(last_exception)[:200] if last_exception else 'Unknown'}"
            )
            raise last_exception if last_exception else Exception("Retry failed with unknown error")
        
        return wrapper
    return decorator


def check_driver_health(driver: WebDriver) -> bool:
    """
    Check if driver session is still alive and healthy.
    
    This function performs a lightweight check to verify that the Appium
    driver session is still valid and can communicate with the server.
    
    Args:
        driver: Appium WebDriver instance
        
    Returns:
        True if driver is healthy, False otherwise
    
    Example:
        if not check_driver_health(self.driver):
            logger.warning("Driver session appears to be dead")
    """
    if driver is None:
        return False
    
    try:
        # Try a simple operation to check connection
        # For Android, try to get current activity
        try:
            _ = driver.current_activity
            return True
        except (WebDriverException, AttributeError):
            # Fallback: try to get current package
            try:
                _ = driver.current_package
                return True
            except (WebDriverException, AttributeError):
                # For iOS or other platforms, try session_id
                try:
                    _ = driver.session_id
                    return True
                except (WebDriverException, AttributeError):
                    return False
    except Exception:
        return False

