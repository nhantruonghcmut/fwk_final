"""
Configuration manager for handling YAML configuration files.
Implements Lazy Evaluation for perfect test isolation.
"""
import os
import re
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from src.core.utils.config_reader import ConfigReader
from src.core.utils.report_logger import ReportLogger

if TYPE_CHECKING:
    from src.core.utils.report_logger import ReportLogger


class ConfigManager:
    """
    Manager for handling configuration with hierarchy support.
    Uses Lazy Evaluation to ensure perfect test isolation.
    
    Config Priority (Low to High):
    1. Global Config (config.yaml) - Shared across all tests
    2. Environment Config (environment/{env}.yaml) - Shared across all tests
    # 3. Suite Config (testdata/*.yaml > suite_config) - Per-test, isolated
    4. CLI Arguments - Runtime override
    
    Design Principle:
    - Global and Environment configs are loaded ONCE and shared (immutable)
    - Suite config is PER-TEST and replaced for each test (mutable, isolated)
    - Config values are computed LAZILY when requested (no merge cache)
    - This ensures NO cross-test contamination
    """
    
    def __init__(self, logger: ReportLogger):
        self.logger = logger
        self.config_cache = {}  # Cache for global/env configs only
        self.config_reader = ConfigReader(logger=self.logger)
        self.test_data = {}
        # ============================================
        # CORE DESIGN: Store configs separately by level
        # ============================================
        self._configs = {
            'global': {},      
            'environment': {},  
            'platform': {}
            # 'suite': {}         # ⚠️ Per-test, replaced each test (mutable, isolated)
        }
        self._platform = None  # web | mobile
        self._environment = None
        # Track if base configs are loaded
        self._base_configs_loaded = False

    def set_environment(self, environment: str):
        """Set environment and load environment-specific config"""      
        
        if environment and environment != self._environment:
            self._environment = environment
            env_config = self.config_reader.read_environment_config(environment)
            self._configs['environment'] = env_config.get(environment, {})
        
            self.logger.info(f"[CONFIG-DONE] Loaded new environment {environment} configuration")
    
    def set_platform(self, platform: str):
        """Set platform and load platform-specific config"""
        self._platform = platform
        
        if platform == "mobile":
            platform_config = self.config_reader.read_yaml("mobile_config.yaml")
            self._configs['platform'] = platform_config.get('mobile', {})
        elif platform == "web":
            platform_config = self.config_reader.read_yaml("web_config.yaml")
            self._configs['platform'] = platform_config.get('web', {})
        
        self.logger.info(f"[CONFIG-DONE] Loaded {platform} configuration")
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Priority:
        1. Platform config (mobile_config.yaml | web_config.yaml)
        2. Environment config
        3. Global config
        4. Default
        """
        keys = key_path.split('.')
        
        # 1. Check platform config (HIGHEST priority)
        if self._configs['platform']:
            value = self._get_nested_value(self._configs['platform'], keys)
            if value is not None:
                return value
        
        # 2. Check environment config
        value = self._get_nested_value(self._configs['environment'], keys)
        if value is not None:
            return value
        
        # 3. Check global config
        value = self._get_nested_value(self._configs['global'], keys)
        if value is not None:
            return value
        
        return default
    
    def _get_nested_value(self, config: dict, keys: list) -> Any:
        """
        Get nested value from dictionary using key path.
        
        Args:
            config: Dictionary to search
            keys: List of keys for nested path
            
        Returns:
            Value if found, None otherwise
        """
        if not config:
            return None
        
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    def get_parallel_workers(self) -> int:
        """Get parallel workers for current platform"""
        if self._platform:
            platform_parallel = self.get_config_value(f'{self._platform}.parallel', {})
            if platform_parallel and 'workers' in platform_parallel:
                return platform_parallel['workers']
        
        return self.get_config_value('parallel.workers', 2)
    
    def get_mobile_devices(self) -> List[Dict]:
        """Get mobile devices list"""
        self.logger.info(f"[CONFIG] Retrieving mobile devices list")
        return self.get_config_value(f'devices', []) 
    
  
    def _load_base_configs(self):
        """
        Load global and environment configs.
        These are loaded ONCE and shared across all tests.
        Process-safe for parallel execution.
        """
        if self._base_configs_loaded:
            return
        
        try:
            # Load global config
            if not self._configs['global']:
                self._configs['global'] = self.config_reader.read_main_config()
                self.config_cache['config'] = self._configs['global']
                print("[CONFIG] Loaded global config")
            
            # Load environment config
            if not self._configs['environment']:
                if self._environment:
                    env = self._environment
                else:
                    env = self._configs['global'].get('default_environment', 'dev')
                self._configs['environment'] = self.config_reader.read_environment_config(env)
                self.config_cache[f'env_{env}'] = self._configs['environment']
                self._environment = env
                print(f"[CONFIG-DONE] Loaded default environment config: {env}")

            
            self._base_configs_loaded = True
            ## after base configs loaded, create logger if exist conf
            if self.logger._default and self.get_logging_config():                
                self.logger.setup_logger(self)
                self.logger.info("Logger initialized with config")

        except Exception as e:
            print(f"[CONFIG-ERROR] Failed to load base configs: {e}")
            raise

    
    
    # ============================================
    # BROWSER CONFIGURATION (Lazy Computed)
    # ============================================
    
    def get_browser_config(self, browser_type: str) -> Dict[str, Any]:
        """
        Get browser-specific configuration with lazy evaluation.
        Computed fresh for each test - ensures isolation.
        
        Args:
            browser_type: Browser type (chromium, firefox, webkit, etc.)
            
        Returns:
            Dict containing browser configuration for current test
        """
        # Ensure base configs loaded
        if not self._base_configs_loaded:
            self._load_base_configs()
        
        config = {}
        
        # 1. Global browser config (base)
        global_browsers = self._configs['global'].get('browsers', {})
        if browser_type in global_browsers:
            config.update(global_browsers[browser_type])
        
        # 2. Environment browser override (if exists)
        env_browsers = self._configs['environment'].get('browsers', {})
        if browser_type in env_browsers:
            config.update(env_browsers[browser_type])
        
        # 3. Suite browser override (current test only)
        # suite_browser = self._configs['suite'].get('browser', {})
        
        # Override individual fields
        # if 'headless' in suite_browser:
        #     config['headless'] = suite_browser['headless']
        
        # if 'slow_mo' in suite_browser:
        #     config['slow_mo'] = suite_browser['slow_mo']
        
        # if 'viewport' in suite_browser:
        #     config['viewport'] = suite_browser['viewport']
        
        # if 'timeout' in suite_browser:
        #     config['timeout'] = suite_browser['timeout']
        
        # # Browser-specific suite overrides
        # if browser_type in suite_browser:
        #     browser_specific = suite_browser[browser_type]
        #     if isinstance(browser_specific, dict):
        #         config.update(browser_specific)
        
        # 4. Add context config if no viewport
        if 'viewport' not in config:
            context_viewport = self.get_config_value('context.viewport')
            if context_viewport:
                config['viewport'] = context_viewport
        
        return config
    

   
    # ============================================
    # TIMEOUT CONFIGURATION (Lazy Computed)
    # ============================================
    
    def get_default_timeout(self) -> int:
        """Get default timeout for current test."""
        return self.get_config_value('timeouts.default', 30000)
    
    def get_element_timeout(self) -> int:
        """Get element timeout for current test."""
        return self.get_config_value('timeouts.element', 10000)
    
    def get_page_load_timeout(self) -> int:
        """Get page load timeout for current test."""
        return self.get_config_value('timeouts.page_load', 30000)
    
    def get_navigation_timeout(self) -> int:
        """Get navigation timeout for current test."""
        return self.get_config_value('timeouts.navigation', 30000)
    
    def get_api_timeout(self) -> int:
        """Get API call timeout for current test."""
        return self.get_config_value('timeouts.api_call', 10000)
    
    def get_database_query_timeout(self) -> int:
        """Get database query timeout for current test."""
        return self.get_config_value('timeouts.database_query', 5000)
    
    # ============================================
    # RETRY CONFIGURATION (Lazy Computed)
    # ============================================
    
    def get_retry_count(self) -> int:
        """Get retry count for current test."""
        return self.get_config_value('retry.count', 3)
    
    def get_retry_delay(self) -> int:
        """Get retry delay for current test."""
        return self.get_config_value('retry.delay', 1000)
    
    # ============================================
    # SCREENSHOT CONFIGURATION (Lazy Computed)
    # ============================================
    
    def should_take_screenshot_on_failure(self) -> bool:
        """Check if screenshots should be taken on failure."""
        return self.get_config_value('screenshots.on_failure', True)
    
    def should_take_screenshot_on_success(self) -> bool:
        """Check if screenshots should be taken on success."""
        return self.get_config_value('screenshots.on_success', False)
    
    def get_screenshot_directory(self) -> str:
        """Get screenshot directory for current test."""
        return self.get_config_value('screenshots.directory', 'reports/screenshots')
    
    # ============================================
    # EXECUTION CONFIGURATION (Lazy Computed)
    # ============================================
    
    def is_parallel_enabled(self) -> bool:
        """Check if parallel execution is enabled."""
        if self._platform:
            platform_parallel = self.get_config_value(f'{self._platform}.parallel', {})
            if platform_parallel and 'enabled' in platform_parallel:
                return platform_parallel['enabled']
        return self.get_config_value("parallel.enabled", False)
    
    def get_max_failures(self) -> int:
        """Get maximum failures before stopping."""
        return self.get_config_value('execution.max_failures', 10)
    
    def should_stop_on_first_failure(self) -> bool:
        """Check if execution should stop on first failure."""
        return self.get_config_value('execution.stop_on_first_failure', False)
    
    # ============================================
    # URL CONFIGURATION (Lazy Computed)
    # ============================================
    
    def get_base_url(self, app_name: str = None) -> str:
        """
        Get base URL with priority:
        1. Environment apps.{app_name}.url
        2. Empty string
        
        Args:
            app_name: Application name (optional)
            
        Returns:
            Base URL string
        """

        
        # Priority 2: Environment config app URL
        if app_name:
            env_url = self.get_config_value(f'apps.{app_name}.url')
            if env_url:
                return self.expand_env_vars(env_url)
        
        return ""
    
    def get_api_base_url(self) -> str:
        """Get API base URL."""
        url = self.get_config_value('api.base_url', '')
        return self.expand_env_vars(url)
    
    # ============================================
    # ALLURE CONFIGURATION
    # ============================================
    
    def is_allure_enabled(self) -> bool:
        """Check if Allure reporting is enabled."""
        return self.get_config_value('allure.enabled', False)

    def get_allure_results_directory(self) -> str:
        """Get Allure results directory path."""
        return self.get_config_value('allure.results_dir', 'reports/allure-results')

    def get_allure_report_directory(self) -> str:
        """Get Allure report directory path."""
        return self.get_config_value('allure.report_dir', 'reports/allure-report')

    def should_clean_allure_on_start(self) -> bool:
        """
        Check if should clean Allure results on start.
        Handles both boolean and string values from YAML.
        """
        value = self.get_config_value('allure.clean_on_start', True)
        
        # Handle string values (YAML might parse as string in some cases)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        # Handle boolean values
        return bool(value)

    # ============================================
    # LOAD TEST DATA
    # ============================================
    
    def load_test_data(self, data_name: str) -> Dict[str, Any]:
        """
        Load test data from YAML file.
        
        Args:
            data_name: name of the data in test_data config (env, global config)
            Ex: test_data:
                    users_file: "testdata/users.yaml"
        Returns:
            Dict containing test data
        """
        self.logger.debug(f"Loading test data: {data_name} from ")
        self.logger.debug(f"test data dict: {self.get_config_value(f'test_data')}")
        if data_name not in self.test_data:
            try:
                data_file_path = self.get_config_value(f'test_data.{data_name}', '')
                if data_file_path == "":
                    self.logger.warning(f"⚠️ No test data file configured for '{data_name}'")
                    return {}
                self.logger.debug(f"🔍 Reading test data file: {data_file_path}")
                self.test_data[data_name] = self.config_reader.read_test_data(data_file_path)
                self.logger.debug(f"📊 Loaded test data: {data_file_path}: {self.test_data[data_name]}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load test data '{data_file_path}': {e}")
                return {}
        
        return self.test_data[data_name]
    
    # ============================================
    # BACKWARD COMPATIBILITY (Existing Methods)
    # ============================================
    
    def get_config(self) -> Dict[str, Any]:
        """Get global configuration (backward compatibility)."""
        if not self._base_configs_loaded:
            self._load_base_configs()
        return self._configs['global']
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment configuration (backward compatibility)."""
        if not self._base_configs_loaded:
            self._load_base_configs()
        return self._configs['environment']
    
    def get_current_environment(self) -> str:
        """Get current environment name."""
        return self._environment
    
    def get_context_config(self) -> Dict[str, Any]:
        """
        Get browser context configuration from web_config.yaml.
        Returns normalized context options ready for Playwright browser.new_context().
        
        Returns:
            Dict containing context configuration (viewport, user_agent, locale, etc.)
        """
        # Context config is only available for web platform
        if self._platform != "web":
            return {}
        
        # Get context config from platform config (web_config.yaml)
        # get_config_value() already prioritizes platform config over global config
        context_config = self.get_config_value('context', {})
        
        # Normalize context config to ensure proper format
        normalized = {}
        
        # Viewport: ensure it's a dict with width and height
        if 'viewport' in context_config:
            viewport = context_config['viewport']
            if isinstance(viewport, dict):
                normalized['viewport'] = viewport
            elif isinstance(viewport, (list, tuple)) and len(viewport) >= 2:
                normalized['viewport'] = {'width': viewport[0], 'height': viewport[1]}
        
        # User agent: string
        if 'user_agent' in context_config:
            normalized['user_agent'] = context_config['user_agent']
        
        # Locale: string
        if 'locale' in context_config:
            normalized['locale'] = context_config['locale']
        
        # Timezone ID: string
        if 'timezone_id' in context_config:
            normalized['timezone_id'] = context_config['timezone_id']
        
        # Permissions: list
        if 'permissions' in context_config:
            normalized['permissions'] = context_config['permissions']
        
        # Extra HTTP headers: dict
        if 'extra_http_headers' in context_config:
            normalized['extra_http_headers'] = context_config['extra_http_headers']
        
        return normalized
    
    def get_app_config(self, app_type: str) -> Dict[str, Any]:
        """Get application-specific configuration."""
        env_config = self.get_environment_config()
        apps = env_config.get("apps", {})
        return apps.get(app_type, {})
        
    def get_test_data(self) -> Dict[str, Any]:
        """Get test data configuration."""
        config = self.get_config()
        return config.get("test_data", {})
        
    def get_mobile_config(self) -> Dict[str, Any]:
        """Get mobile configuration."""
        config = self.get_config()
        return config.get("mobile", {})
    
    def get_mobile_context_config(self) -> Dict[str, Any]:
        """
        Get mobile context configuration (timezone, locale) from mobile_config.yaml.
        Returns normalized config ready for Appium capabilities.
        
        Returns:
            Dict containing mobile context configuration
        """
        # Context config is only available for mobile platform
        if self._platform != "mobile":
            return {}
        
        # Get context config from platform config (mobile_config.yaml)
        # get_config_value() already prioritizes platform config over global config
        context_config = self.get_config_value('context', {})
        
        normalized = {}
        
        # Timezone: Android uses 'timeZone', iOS uses 'appTimeZone'
        if 'timezone' in context_config:
            normalized['timezone'] = context_config['timezone']
        
        # Locale: Both platforms use 'locale'
        if 'locale' in context_config:
            normalized['locale'] = context_config['locale']
        
        return normalized
        
    def get_web_config(self) -> Dict[str, Any]:
        """Get web configuration."""
        config = self.get_config()
        return config.get("web", {})
    
    def get_trace_config(self) -> Dict[str, Any]:
        """
        Get Playwright tracing configuration from web_config.yaml.
        Returns default config if not found or platform is not web.
        
        Returns:
            Dict containing trace configuration (enabled, on_failure, on_success, directory, etc.)
        """
        if self._platform != "web":
            return {
                "enabled": False,
                "on_failure": False,
                "on_success": False,
                "directory": "reports/traces",
                "screenshots": True,
                "snapshots": True,
                "sources": True
            }
        
        trace_config = self.get_config_value("playwright.trace", {})
        
        # Return with defaults
        return {
            "enabled": trace_config.get("enabled", False),
            "on_failure": trace_config.get("on_failure", True),
            "on_success": trace_config.get("on_success", False),
            "directory": trace_config.get("directory", "reports/traces"),
            "screenshots": trace_config.get("screenshots", True),
            "snapshots": trace_config.get("snapshots", True),
            "sources": trace_config.get("sources", True)
        }
    
    def is_trace_enabled(self) -> bool:
        """Check if tracing is enabled."""
        trace_config = self.get_trace_config()
        return trace_config.get("enabled", False)
    
    def should_trace_on_failure(self) -> bool:
        """Check if trace should be saved on test failure."""
        trace_config = self.get_trace_config()
        return trace_config.get("enabled", False) and trace_config.get("on_failure", True)
    
    def should_trace_on_success(self) -> bool:
        """Check if trace should be saved on test success."""
        trace_config = self.get_trace_config()
        return trace_config.get("enabled", False) and trace_config.get("on_success", False)
    
    def get_trace_directory(self) -> str:
        """Get trace directory path."""
        trace_config = self.get_trace_config()
        return trace_config.get("directory", "reports/traces")


    def get_timeout_config(self) -> Dict[str, Any]:
        """Get timeout configuration."""
        return self.get_config_value('timeouts', {})
    
    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration."""
        return self.get_config_value('retry', {})
    
    def get_screenshot_config(self) -> Dict[str, Any]:
        """Get screenshot configuration."""
        return self.get_config_value('screenshots', {})
    
    def get_allure_config(self) -> Dict[str, Any]:
        """Get Allure configuration."""
        return self.get_config_value('allure', {})
    
    def get_parallel_config(self) -> Dict[str, Any]:
        """Get parallel execution configuration."""
        if self._platform:
            return self.get_config_value(f'{self._platform}.parallel', {})
        return self.get_config_value('parallel', {})
    
    def get_pytest_logging_config(self) -> Dict[str, Any]:
        """Get pytest's built-in logging configuration."""
        return self.get_config_value('pytest.logging', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration from config.yaml."""
        return self.get_config_value('logging', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.get_config_value('database', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self.get_config_value('api', {})
    
    def get_credentials(self, service: str) -> Dict[str, str]:
        """Get credentials for a specific service."""
        creds = self.get_config_value(f'credentials.{service}', {})
        # Expand environment variables in credentials
        return {k: self.expand_env_vars(v) if isinstance(v, str) else v 
                for k, v in creds.items()}
    
    # ============================================
    # ENVIRONMENT VARIABLES EXPANSION
    # ============================================
    
    def expand_env_vars(self, value: Any) -> Any:
        """
        Expand environment variables in config values.
        Supports ${VAR_NAME} and ${VAR_NAME:default_value} syntax.
        
        Args:
            value: Config value to expand
            
        Returns:
            Expanded value
            
        Examples:
            >>> expand_env_vars("${DB_HOST}")
            "localhost"  # From environment
            
            >>> expand_env_vars("${API_KEY:default_key}")
            "default_key"  # If API_KEY not set
        """
        if isinstance(value, str):
            # Pattern: ${VAR_NAME} or ${VAR_NAME:default_value}
            pattern = r'\$\{([^}:]+)(?::([^}]+))?\}'
            
            def replace_var(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) else ""
                return os.environ.get(var_name, default_value)
            
            return re.sub(pattern, replace_var, value)
        
        elif isinstance(value, dict):
            return {k: self.expand_env_vars(v) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self.expand_env_vars(item) for item in value]
        
        return value
    
    # ============================================
    # DEBUG & UTILITIES
    # ============================================
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            'environment': self.get_current_environment(),
            'parallel_enabled': self.is_parallel_enabled(),
            'parallel_workers': self.get_parallel_workers(),
            'allure_enabled': self.is_allure_enabled(),
            'screenshot_on_failure': self.should_take_screenshot_on_failure(),
            'default_timeout': self.get_default_timeout(),
            'retry_count': self.get_retry_count(),
            # 'has_suite_config': bool(self._configs['suite'])
        }
    
    # ============================================
    # CACHE MANAGEMENT
    # ============================================
    
    def clear_cache(self):
        """
        Clear configuration cache.
        NOTE: Only clears test data cache, not base configs.
        """
        # Keep base configs, only clear test data cache
        keys_to_remove = [k for k in self.config_cache.keys() if k.startswith('testdata_')]
        for key in keys_to_remove:
            del self.config_cache[key]
        
        self.logger.debug("🧹 Cleared test data cache")
    
    def reload_config(self):
        """
        Reload all configuration files.
        Forces re-reading from disk.
        """
        self.config_cache.clear()
        self._configs = {
            'global': {},
            'environment': {},
            # 'suite': {}
        }
        self._base_configs_loaded = False
        
        # Reload base configs
        self._load_base_configs()
        
        self.logger.info("🔄 Configuration reloaded")
    
    def validate_config(self) -> bool:
        """
        Validate configuration files.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Load and validate base configs
            self._load_base_configs()
            
            # Check required fields
            if not self._configs['global']:
                raise ValueError("Global config is empty")
            
            if not self._configs['environment']:
                raise ValueError("Environment config is empty")
            
            # Validate logging config
            self.get_logging_config()
            
            self.logger.info("[CONFIG-DONE] Configuration validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation failed: {e}")
            return False
