"""
Configuration reader utility for reading YAML configuration files.
"""
import os
import re
import yaml
from functools import cached_property
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.utils.report_logger import ReportLogger

class ConfigReader:
    """Utility class for reading configuration files."""

    def __init__(self, config_dir: str = "src/config", logger = None):
        self.config_dir = config_dir
        self.logger = logger

         
    def read_yaml(self, file_path: str) -> Dict[str, Any]:
        """Read YAML file and return its contents."""
        try:
            full_path = os.path.join(self.config_dir, file_path)
            self.logger.debug(f"🔍 Reading YAML file: {full_path}")
            with open(full_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)
                return content if content is not None else {}
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {full_path}")  # ← Fix: use self.logger
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file {full_path}: {str(e)}")  # ← Fix
            return {}
        except Exception as e:
            self.logger.error(f"Error reading configuration file {full_path}: {str(e)}")  # ← Fix
            return {}
    
    # ============================================
    # NEW: Environment Variable Support
    # ============================================
    
    def expand_env_vars_in_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand environment variables in entire config.
        Supports ${VAR_NAME} and ${VAR_NAME:default} syntax.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Config with expanded environment variables
        """
        def expand_value(value):
            if isinstance(value, str):
                # Pattern: ${VAR_NAME} or ${VAR_NAME:default_value}
                pattern = r'\$\{([^}:]+)(?::([^}]+))?\}'
                
                def replace_var(match):
                    var_name = match.group(1)
                    default_value = match.group(2) if match.group(2) else ""
                    return os.environ.get(var_name, default_value)
                
                return re.sub(pattern, replace_var, value)
            
            elif isinstance(value, dict):
                return {k: expand_value(v) for k, v in value.items()}
            
            elif isinstance(value, list):
                return [expand_value(item) for item in value]
            
            return value
        
        return expand_value(config)
    
    def read_yaml_with_env_expansion(self, file_path: str) -> Dict[str, Any]:
        """
        Read YAML file and expand environment variables.
        
        Args:
            file_path: Relative path to YAML file
            
        Returns:
            Config with expanded environment variables
        """
        config = self.read_yaml(file_path)
        return self.expand_env_vars_in_config(config)
            
    def read_environment_config(self, environment: str) -> Dict[str, Any]:
        """Read environment-specific configuration with env var expansion."""
        return self.read_yaml_with_env_expansion(f"environment/{environment}.yaml")
        
    def read_test_data(self, data_file_path: str) -> Dict[str, Any]:
        """Read test data configuration."""
        return self.read_yaml(data_file_path)
        
    def read_main_config(self) -> Dict[str, Any]:
        """Read main configuration file."""
        return self.read_yaml("config.yaml")        
        
    def get_all_config_files(self) -> List[str]:
        """Get list of all configuration files."""
        config_files = []
        for root, dirs, files in os.walk(self.config_dir):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.config_dir)
                    config_files.append(rel_path)
        return config_files
        
    def validate_yaml_syntax(self, file_path: str) -> bool:
        """Validate YAML syntax of a file."""
        try:
            full_path = os.path.join(self.config_dir, file_path)
            with open(full_path, 'r', encoding='utf-8') as file:
                yaml.safe_load(file)
            return True
        except yaml.YAMLError:
            return False
        except Exception:
            return False
    
    # ============================================
    # Keep all existing methods below
    # ============================================
    
    def get_config_value(self, file_path: str, key_path: str, default: Any = None) -> Any:
        """Get a specific value from configuration using dot notation."""
        config = self.read_yaml(file_path)
        keys = key_path.split('.')
        
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
                
        return current
        
    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries."""
        merged = {}
        for config in configs:
            merged.update(config)
        return merged
        
    def get_nested_value(self, config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        """Get nested value from configuration using dot notation."""
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
                
        return current
        
    def set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any):
        """Set nested value in configuration using dot notation."""
        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
    def filter_config(self, config: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """Filter configuration by key prefix."""
        filtered = {}
        for key, value in config.items():
            if key.startswith(prefix):
                filtered[key] = value
        return filtered
        
    def get_config_section(self, config: Dict[str, Any], section: str) -> Dict[str, Any]:
        """Get a specific section from configuration."""
        return config.get(section, {})
        
    def has_config_section(self, config: Dict[str, Any], section: str) -> bool:
        """Check if configuration has a specific section."""
        return section in config
        
    def get_config_keys(self, config: Dict[str, Any]) -> List[str]:
        """Get all keys from configuration."""
        return list(config.keys())
        
    def get_config_values(self, config: Dict[str, Any]) -> List[Any]:
        """Get all values from configuration."""
        return list(config.values())
        
    def is_config_empty(self, config: Dict[str, Any]) -> bool:
        """Check if configuration is empty."""
        return len(config) == 0
        
    def get_config_size(self, config: Dict[str, Any]) -> int:
        """Get configuration size."""
        return len(config)
        
    def deep_copy_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of configuration."""
        import copy
        return copy.deepcopy(config)
        
    def flatten_config(self, config: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested configuration."""
        items = []
        for k, v in config.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_config(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
        
    def unflatten_config(self, config: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
        """Unflatten configuration."""
        result = {}
        for key, value in config.items():
            keys = key.split(sep)
            current = result
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        return result
        
    def validate_required_keys(self, config: Dict[str, Any], required_keys: List[str]) -> bool:
        """Validate that configuration has all required keys."""
        missing_keys = []
        for key in required_keys:
            if key not in config:
                missing_keys.append(key)
                
        if missing_keys:
            self.logger.error(f"Missing required configuration keys: {missing_keys}")  # ← Fix
            return False
            
        return True
        
    def validate_config_types(self, config: Dict[str, Any], type_mapping: Dict[str, type]) -> bool:
        """Validate configuration value types."""
        for key, expected_type in type_mapping.items():
            if key in config:
                if not isinstance(config[key], expected_type):
                    self.logger.error(f"Configuration key '{key}' has wrong type. Expected {expected_type}, got {type(config[key])}")  # ← Fix
                    return False
        return True
        
    def get_config_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a configuration file."""
        try:
            full_path = os.path.join(self.config_dir, file_path)
            stat = os.stat(full_path)
            config = self.read_yaml(file_path)
            
            return {
                "file_path": full_path,
                "file_size": stat.st_size,
                "modified_time": stat.st_mtime,
                "config_keys": list(config.keys()),
                "config_size": len(config),
                "is_valid_yaml": self.validate_yaml_syntax(file_path)
            }
        except Exception as e:
            self.logger.error(f"Failed to get config info for {file_path}: {str(e)}")  # ← Fix
            return {}
