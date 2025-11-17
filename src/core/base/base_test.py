"""
Base test class providing common setup and teardown logic for web and mobile tests.
"""
import pytest
import traceback
from typing import Dict, Any, Optional
from src.core.utils.test_context import TestContext
from src.core.utils.config_manager import ConfigManager
from src.core.utils.report_logger import ReportLogger
from src.core.utils.verification import Verification


class BaseTest:
    """Base class for all test cases providing common functionality."""
    
    def __init__(self):
        self.test_context: Optional[TestContext] = None
        self.config_manager: Optional[ConfigManager] = None
        self.logger: Optional[ReportLogger] = None
        self.test_data: Dict[str, Any] = {}
        self.verify: Optional[Verification] = None  # Verification instance
    
    def _init_verification(self, logger: Optional[ReportLogger] = None):
        """
        Initialize Verification instance with logger.
        Should be called after logger is set (e.g., in BaseMobile/BaseWeb.__init__).
        
        Args:
            logger: ReportLogger instance. If None, uses self.logger or singleton.
        """
        logger_to_use = logger or self.logger or ReportLogger()
        self.verify = Verification(logger=logger_to_use)
        
    def setup_test(self, config_loader: ConfigManager, test_context: TestContext):
        """Setup test environment with configuration and context."""
        self.config_manager = config_loader
        self.test_context = test_context
        self.logger = ReportLogger()
        self.test_data = self.config_manager.get_test_data()
        
        self.logger.info(f"Setting up test: {self.__class__.__name__}")
        
    def teardown_test(self):
        """Cleanup test environment."""
        if self.logger:
            self.logger.info(f"Tearing down test: {self.__class__.__name__}")
            
        # Clear test context
        if self.test_context:
            self.test_context.clear()
            
    def get_test_data(self, key: str, default=None) -> Any:
        """Get test data by key with optional default value."""
        if key not in self.test_data and default is None:
            if self.logger:
                self.logger.warning(f"Test data key '{key}' not found")
        return self.test_data.get(key, default)
        
    def set_test_data(self, key: str, value: Any):
        """Set test data."""
        self.test_data[key] = value
        
    def log_test_step(self, step: str):
        """Log test step for reporting."""
        if self.logger:
            self.logger.info(f"Test Step: {step}")
            
    def log_verification(self, verification: str, result: bool):
        """Log verification result."""
        if self.logger:
            status = "PASSED" if result else "FAILED"
            self.logger.info(f"Verification: {verification} - {status}")
            
    def get_environment_config(self) -> Dict[str, Any]:
        """Get current environment configuration."""
        if not self.config_manager:
            raise RuntimeError("Config manager not initialized")
        return self.config_manager.get_environment_config()
        
    def get_app_config(self, app_type: str) -> Dict[str, Any]:
        """Get application-specific configuration."""
        if not self.config_manager:
            raise RuntimeError("Config manager not initialized")
        return self.config_manager.get_app_config(app_type)
        
    def capture_screenshot(self, name: str = None):
        """Capture screenshot for test reporting."""
        # Implementation depends on your driver implementation
        if self.test_context and hasattr(self.test_context, 'driver') and self.test_context.driver:
            screenshot_name = name or f"failure_{self.__class__.__name__}"
            try:
                self.test_context.driver.save_screenshot(f"reports/screenshots/{screenshot_name}.png")
                if self.logger:
                    self.logger.info(f"Screenshot captured: {screenshot_name}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to capture screenshot: {str(e)}")
    
    # Integration with pytest fixtures
    @pytest.fixture(autouse=True)
    def _setup_teardown_fixture(self, request, config_loader, test_context):
        """Automatically setup and teardown test using pytest fixtures."""
        # Setup
        self.setup_test(config_loader, test_context)
        
        yield
        
        # Teardown
        self.teardown_test()
        
        # Capture screenshot on failure
        if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
            self.capture_screenshot()
