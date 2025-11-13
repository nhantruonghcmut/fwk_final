from src.core.utils.config_manager import ConfigManager
from src.core.utils.report_logger import ReportLogger

logger = ReportLogger()
config_manager = ConfigManager(logger)

# Force load configs
config_manager._load_base_configs()

# Get markers
markers = config_manager.get_config_value('markers', {})

print(f"Base configs loaded: {config_manager._base_configs_loaded}")
print(f"Global config keys: {list(config_manager._configs['global'].keys())}")
print(f"Markers: {markers}")
print(f"Marker count: {len(markers) if markers else 0}")