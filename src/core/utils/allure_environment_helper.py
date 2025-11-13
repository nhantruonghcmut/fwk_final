"""
Allure environment helper for setting up test environment information.
"""
import os
import platform
import socket
import time
from typing import Dict, Any
from src.core.utils.report_logger import ReportLogger
from src.core.utils.config_manager import ConfigManager


class AllureEnvironmentHelper:
    """Helper class for setting up Allure environment information."""
    
    def __init__(self):
        self.logger = ReportLogger()
        self.config_manager = ConfigManager( self.logger)
        
    def create_environment_file(self, output_dir: str = "reports/allure-results"):
        """Create Allure environment file."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            env_file_path = os.path.join(output_dir, "environment.properties")
            
            environment_data = self._get_environment_data()
            
            with open(env_file_path, 'w', encoding='utf-8') as f:
                for key, value in environment_data.items():
                    f.write(f"{key}={value}\n")
                    
            self.logger.info(f"Created Allure environment file: {env_file_path}")
            return env_file_path
            
        except Exception as e:
            self.logger.log_error(e, "create_environment_file")
            return ""
            
    def _get_environment_data(self) -> Dict[str, str]:
        """Get environment data for Allure."""
        try:
            environment_data = {
                "OS": platform.system(),
                "OS Version": platform.version(),
                "OS Release": platform.release(),
                "Architecture": platform.machine(),
                "Python Version": platform.python_version(),
                "Hostname": socket.gethostname(),
                "Environment": self.config_manager.get_current_environment(),
                "Test Framework": "Pytest + Playwright + Appium",
                "Browser Support": "Chromium, Firefox, WebKit, Edge, Chrome",
                "Mobile Support": "Android 11+, iOS 15+",
                "Parallel Execution": str(self.config_manager.is_parallel_enabled()),
                # "Headless Mode": str(self.config_manager.is_headless()),
                "Screenshot on Failure": str(self.config_manager.should_take_screenshot_on_failure()),
                "Default Timeout": str(self.config_manager.get_default_timeout()),
                "Retry Count": str(self.config_manager.get_retry_count())
            }
            
            # Add browser-specific information
            browser_config = self.config_manager.get_config().get("browsers", {})
            for browser, config in browser_config.items():
                environment_data[f"Browser.{browser}"] = "Enabled"
                
            # Add mobile configuration
            mobile_config = self.config_manager.get_mobile_config()
            if mobile_config:
                environment_data["Mobile.Android"] = "Supported"
                environment_data["Mobile.iOS"] = "Supported"
                
            # Add API configuration
            api_config = self.config_manager.get_api_config()
            if api_config:
                environment_data["API.Base URL"] = api_config.get("base_url", "Not configured")
                
            # Add database configuration
            db_config = self.config_manager.get_database_config()
            if db_config:
                environment_data["Database.URL"] = db_config.get("url", "Not configured")
                
            return environment_data
            
        except Exception as e:
            self.logger.log_error(e, "_get_environment_data")
            return {}
            
    def update_environment_file(self, additional_data: Dict[str, str], 
                              output_dir: str = "reports/allure-results"):
        """Update Allure environment file with additional data."""
        try:
            env_file_path = os.path.join(output_dir, "environment.properties")
            
            if os.path.exists(env_file_path):
                # Read existing data
                existing_data = {}
                with open(env_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            existing_data[key] = value
                            
                # Merge with additional data
                existing_data.update(additional_data)
                
                # Write updated data
                with open(env_file_path, 'w', encoding='utf-8') as f:
                    for key, value in existing_data.items():
                        f.write(f"{key}={value}\n")
                        
                self.logger.info(f"Updated Allure environment file with {len(additional_data)} new entries")
            else:
                self.logger.warning("Environment file not found, creating new one")
                self.create_environment_file(output_dir)
                
        except Exception as e:
            self.logger.log_error(e, "update_environment_file")
            
    def add_test_environment_info(self, test_name: str, environment_info: Dict[str, str]):
        """Add test-specific environment information."""
        try:
            # This could be used to add test-specific environment data
            # For now, we'll just log it
            self.logger.info(f"Test environment info for {test_name}: {environment_info}")
            
        except Exception as e:
            self.logger.log_error(e, "add_test_environment_info")
            
    def get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        try:
            return {
                "OS": platform.system(),
                "OS Version": platform.version(),
                "OS Release": platform.release(),
                "Architecture": platform.machine(),
                "Python Version": platform.python_version(),
                "Hostname": socket.gethostname(),
                "Processor": platform.processor(),
                "Python Implementation": platform.python_implementation(),
                "Python Compiler": platform.python_compiler()
            }
        except Exception as e:
            self.logger.log_error(e, "get_system_info")
            return {}
            
    def get_network_info(self) -> Dict[str, str]:
        """Get network information."""
        try:
            network_info = {}
            
            # Get local IP address
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                network_info["Local IP"] = local_ip
            except:
                network_info["Local IP"] = "Unknown"
                
            # Get hostname
            network_info["Hostname"] = socket.gethostname()
            
            # Get FQDN
            try:
                fqdn = socket.getfqdn()
                network_info["FQDN"] = fqdn
            except:
                network_info["FQDN"] = "Unknown"
                
            return network_info
            
        except Exception as e:
            self.logger.log_error(e, "get_network_info")
            return {}
            
    def get_python_packages_info(self) -> Dict[str, str]:
        """Get Python packages information."""
        try:
            packages_info = {}
            
            # Get installed packages
            try:
                import pkg_resources
                installed_packages = [d.project_name for d in pkg_resources.working_set]
                packages_info["Installed Packages Count"] = str(len(installed_packages))
                
                # Check for specific packages
                key_packages = ["pytest", "playwright", "appium-python-client", "allure-pytest"]
                for package in key_packages:
                    try:
                        version = pkg_resources.get_distribution(package).version
                        packages_info[f"Package.{package}"] = version
                    except:
                        packages_info[f"Package.{package}"] = "Not installed"
                        
            except ImportError:
                packages_info["Package Info"] = "pkg_resources not available"
                
            return packages_info
            
        except Exception as e:
            self.logger.log_error(e, "get_python_packages_info")
            return {}
            
    def create_categories_file(self, output_dir: str = "reports/allure-results"):
        """Create Allure categories file."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            categories_file_path = os.path.join(output_dir, "categories.json")
            
            categories = [
                {
                    "name": "Test Defects",
                    "matchedStatuses": ["failed"],
                    "messageRegex": ".*AssertionError.*"
                },
                {
                    "name": "Product Defects",
                    "matchedStatuses": ["failed"],
                    "messageRegex": ".*TimeoutError.*"
                },
                {
                    "name": "Test Infrastructure",
                    "matchedStatuses": ["broken"],
                    "messageRegex": ".*ConnectionError.*"
                },
                {
                    "name": "Skipped Tests",
                    "matchedStatuses": ["skipped"],
                    "messageRegex": ".*"
                }
            ]
            
            import json
            with open(categories_file_path, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2)
                
            self.logger.info(f"Created Allure categories file: {categories_file_path}")
            return categories_file_path
            
        except Exception as e:
            self.logger.log_error(e, "create_categories_file")
            return ""
            
    def create_executor_file(self, output_dir: str = "reports/allure-results"):
        """Create Allure executor file."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            executor_file_path = os.path.join(output_dir, "executor.json")
            
            executor_data = {
                "name": "Test Automation Framework",
                "type": "pytest",
                "buildName": f"Build_{int(time.time())}",
                "buildUrl": "https://github.com/your-repo/actions/runs/123456789",
                "reportUrl": "https://your-reports-url.com",
                "reportName": "Test Execution Report"
            }
            
            import json
            with open(executor_file_path, 'w', encoding='utf-8') as f:
                json.dump(executor_data, f, indent=2)
                
            self.logger.info(f"Created Allure executor file: {executor_file_path}")
            return executor_file_path
            
        except Exception as e:
            self.logger.log_error(e, "create_executor_file")
            return ""
            
    def setup_allure_environment(self, output_dir: str = "reports/allure-results"):
        """Setup complete Allure environment."""
        try:
            self.logger.info("Setting up Allure environment")
            
            # Create environment file
            env_file = self.create_environment_file(output_dir)
            
            # Create categories file
            categories_file = self.create_categories_file(output_dir)
            
            # Create executor file
            executor_file = self.create_executor_file(output_dir)
            
            self.logger.info("Allure environment setup completed")
            
            return {
                "environment_file": env_file,
                "categories_file": categories_file,
                "executor_file": executor_file
            }
            
        except Exception as e:
            self.logger.log_error(e, "setup_allure_environment")
            return {}
