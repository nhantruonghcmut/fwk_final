"""
Main entry point for pytest execution with config integration.
Builds pytest CLI arguments from config.yaml and allows CLI overrides.

Usage:
    python pytest_main.py --mobile -v tests/
    python pytest_main.py --web --timeout=60 tests/
    python pytest_main.py -n=4 --alluredir=results tests/
"""
import sys
import subprocess
from typing import List, Tuple
from src.core.utils.config_manager import ConfigManager
from src.core.utils.report_logger import ReportLogger

logger = ReportLogger()
config_manager = ConfigManager(logger)
config_manager._load_base_configs()


def has_cli_option(args: List[str], option: str) -> bool:
    """Check if CLI arguments contain a specific option."""
    return any(arg.startswith(option) for arg in args)


def extract_config_args(args: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separate config-specific args from pytest args.
    
    Config args: --mobile, --web
    Pytest args: Everything else
    
    Returns:
        Tuple of (config_args, pytest_args)
    """
    config_args = []
    pytest_args = []
    
    for arg in args:
        if arg in ("--mobile", "--web"):
            config_args.append(arg)
        else:
            pytest_args.append(arg)
    
    return config_args, pytest_args


def extract_cli_option_value(args: List[str], option: str) -> str:
    """Extract option value from CLI args. E.g., --timeout=60 -> '60'"""
    for arg in args:
        if arg.startswith(option + "="):
            return arg.split("=", 1)[1]
        elif arg.startswith(option):
            return None  # Flag without value
    return None


def build_pytest_args_from_config(
    config_args: List[str],
    cli_pytest_args: List[str]
) -> List[str]:
    """
    Build complete pytest CLI arguments from config.yaml + CLI overrides.
    CLI arguments ALWAYS take priority over config values.
    
    Args:
        config_args: Config-specific arguments (--mobile, --web)
        cli_pytest_args: Pytest CLI arguments (from user CLI)
    
    Returns:
        Complete list of pytest CLI arguments
    """
    pytest_args = []
    
    # 0. Set platform from config args or CLI
    if "--mobile" in config_args or has_cli_option(cli_pytest_args, "--mobile"):
        config_manager.set_platform("mobile")
        if not has_cli_option(cli_pytest_args, "--mobile"):
            pytest_args.append("--mobile")
        logger.info("[CONFIG] Platform set to: MOBILE (from CLI)")
    elif "--web" in config_args or has_cli_option(cli_pytest_args, "--web"):
        config_manager.set_platform("web")
        if not has_cli_option(cli_pytest_args, "--web"):
            pytest_args.append("--web")
        logger.info("[CONFIG] Platform set to: WEB (from CLI)")
    else:
        logger.warning("[CONFIG] No platform flag detected, using default")
    
    # 1. Parallel workers (-n) - CLI takes priority
    has_workers = False
    if has_cli_option(cli_pytest_args, "-n"):
        has_workers = True
        logger.info("[CONFIG] Using parallel workers from CLI")
    elif config_manager.is_parallel_enabled():
        workers = config_manager.get_parallel_workers()
        pytest_args.append(f"-n={workers}")
        has_workers = True
        logger.info(f"[CONFIG] Added parallel workers from config: -n={workers}")
    
    # 1.1. Distribution mode (--dist=loadgroup) - Only if CLI doesn't override
    if not has_cli_option(cli_pytest_args, "--dist"):
        if has_workers and (has_cli_option(cli_pytest_args, "--mobile") or "--mobile" in config_args):
            pytest_args.append("--dist=loadgroup")
            logger.info("[CONFIG] Added distribution mode from config: --dist=loadgroup")
    
    # 2. Allure reporting (--alluredir) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--alluredir"):
        logger.info("[CONFIG] Using alluredir from CLI")
    elif config_manager.is_allure_enabled():
        allure_results_dir = config_manager.get_allure_results_directory()
        pytest_args.append(f"--alluredir={allure_results_dir}")
        logger.info(f"[CONFIG] Added alluredir from config: {allure_results_dir}")
    
    # 3. Max failures (--maxfail) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--maxfail"):
        logger.info("[CONFIG] Using maxfail from CLI")
    else:
        maxfail = config_manager.get_config_value("pytest.execution.maxfail")
        if maxfail:
            pytest_args.append(f"--maxfail={maxfail}")
            logger.info(f"[CONFIG] Added maxfail from config: {maxfail}")
    
    # 4. Verbose (-v, -vv) - CLI takes priority
    if has_cli_option(cli_pytest_args, "-v") or has_cli_option(cli_pytest_args, "-q"):
        logger.info("[CONFIG] Using verbosity from CLI")
    else:
        verbose = config_manager.get_config_value("pytest.execution.verbose")
        if verbose:
            pytest_args.append("-v")
            logger.info("[CONFIG] Added verbose mode from config: -v")
    
    # 5. Timeout (--timeout) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--timeout"):
        logger.info("[CONFIG] Using timeout from CLI")
    else:
        timeout = config_manager.get_config_value("pytest.timeout.value")
        if timeout:
            pytest_args.append(f"--timeout={timeout}")
            logger.info(f"[CONFIG] Added timeout from config: {timeout}s")
    
    # 6. Traceback style (--tb) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--tb"):
        logger.info("[CONFIG] Using traceback style from CLI")
    else:
        traceback_style = config_manager.get_config_value("pytest.execution.traceback")
        if traceback_style:
            pytest_args.append(f"--tb={traceback_style}")
            logger.info(f"[CONFIG] Added traceback style from config: {traceback_style}")
    
    # 7. Show durations (--durations) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--durations"):
        logger.info("[CONFIG] Using durations from CLI")
    else:
        show_durations = config_manager.get_config_value("pytest.execution.show_durations")
        if show_durations:
            pytest_args.append(f"--durations={show_durations}")
            logger.info(f"[CONFIG] Added durations from config: {show_durations}")
    
    # 8. Disable warnings (--disable-warnings) - CLI takes priority
    if not has_cli_option(cli_pytest_args, "--disable-warnings"):
        disable_warnings = config_manager.get_config_value("pytest.execution.disable_warnings")
        if disable_warnings:
            pytest_args.append("--disable-warnings")
            logger.info("[CONFIG] Added from config: --disable-warnings")
    
    # 9. Strict markers (--strict-markers) - CLI takes priority
    if not has_cli_option(cli_pytest_args, "--strict-markers"):
        strict_markers = config_manager.get_config_value("pytest.execution.strict_markers")
        if strict_markers:
            pytest_args.append("--strict-markers")
            logger.info("[CONFIG] Added from config: --strict-markers")
    
    # 10. Strict config (--strict-config) - CLI takes priority
    if not has_cli_option(cli_pytest_args, "--strict-config"):
        strict_config = config_manager.get_config_value("pytest.execution.strict_config")
        if strict_config:
            pytest_args.append("--strict-config")
            logger.info("[CONFIG] Added from config: --strict-config")
    
    # 11. Collection - ignore directories (--ignore) - Merge both
    if not has_cli_option(cli_pytest_args, "--ignore"):
        norecursedirs = config_manager.get_config_value("pytest.collection.norecursedirs")
        if norecursedirs:
            for dir_pattern in norecursedirs:
                pytest_args.append(f"--ignore={dir_pattern}")
            logger.info(f"[CONFIG] Added ignore directory from config: {norecursedirs}")
    
    # 12. Collection - ignore files (--ignore) - Merge both
    collect_ignore = config_manager.get_config_value("pytest.collection.collect_ignore")
    if collect_ignore:
        for ignore_pattern in collect_ignore:
            if not any(arg == ignore_pattern or arg.endswith(ignore_pattern) for arg in cli_pytest_args):
                pytest_args.append(f"--ignore={ignore_pattern}")
        logger.info(f"[CONFIG] Added ignore file from config: {collect_ignore}")
    
    # 13. Logging CLI level (--log-cli-level) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--log-cli-level"):
        logger.info("[CONFIG] Using log-cli-level from CLI")
    else:
        log_cli_enabled = config_manager.get_config_value("pytest.logging.cli.enabled")
        if log_cli_enabled:
            log_level = config_manager.get_config_value("pytest.logging.cli.level")
            if log_level:
                pytest_args.append(f"--log-cli-level={log_level}")
                logger.info(f"[CONFIG] Added log-cli-level from config: {log_level}")
    
    # 14. Logging CLI format (--log-cli-format) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--log-cli-format"):
        logger.info("[CONFIG] Using log-cli-format from CLI")
    else:
        log_format = config_manager.get_config_value("pytest.logging.cli.format")
        if log_format:
            pytest_args.append(f"--log-cli-format={log_format}")
            logger.info(f"[CONFIG] Added log-cli-format from config: {log_format}")
    
    # 15. Logging CLI date format (--log-cli-date-format) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--log-cli-date-format"):
        logger.info("[CONFIG] Using log-cli-date-format from CLI")
    else:
        log_date_format = config_manager.get_config_value("pytest.logging.cli.date_format")
        if log_date_format:
            pytest_args.append(f"--log-cli-date-format={log_date_format}")
            logger.info(f"[CONFIG] Added log-cli-date-format from config: {log_date_format}")
    
    # 16. Logging file (--log-file) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--log-file"):
        logger.info("[CONFIG] Using log-file from CLI")
    else:
        log_file_enabled = config_manager.get_config_value("pytest.logging.file.enabled")
        if log_file_enabled:
            log_file_path = config_manager.get_config_value("pytest.logging.file.path")
            if log_file_path:
                pytest_args.append(f"--log-file={log_file_path}")
                logger.info(f"[CONFIG] Added log-file from config: {log_file_path}")
    
    # 17. Logging file level (--log-file-level) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--log-file-level"):
        logger.info("[CONFIG] Using log-file-level from CLI")
    else:
        log_file_level = config_manager.get_config_value("pytest.logging.file.level")
        if log_file_level:
            pytest_args.append(f"--log-file-level={log_file_level}")
            logger.info(f"[CONFIG] Added log-file-level from config: {log_file_level}")
    
    # 18. Logging file format (--log-file-format) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--log-file-format"):
        logger.info("[CONFIG] Using log-file-format from CLI")
    else:
        log_file_format = config_manager.get_config_value("pytest.logging.file.format")
        if log_file_format:
            pytest_args.append(f"--log-file-format={log_file_format}")
            logger.info(f"[CONFIG] Added log-file-format from config: {log_file_format}")
    
    # 19. Logging file date format (--log-file-date-format) - CLI takes priority
    if has_cli_option(cli_pytest_args, "--log-file-date-format"):
        logger.info("[CONFIG] Using log-file-date-format from CLI")
    else:
        log_file_date_format = config_manager.get_config_value("pytest.logging.file.date_format")
        if log_file_date_format:
            pytest_args.append(f"--log-file-date-format={log_file_date_format}")
            logger.info(f"[CONFIG] Added log-file-date-format from config: {log_file_date_format}")
    
    # Merge: config args + cli pytest args (CLI already takes priority via checks above)
    final_args = pytest_args + cli_pytest_args
    
    return final_args


def main():
    """Main entry point."""
    cli_args = sys.argv[1:]
    
    # Separate config args from pytest args
    config_args, pytest_args = extract_config_args(cli_args)
    
    # ============================================
    # CLEAN PYTEST LOG FILES (if configured)
    # ============================================
    # This must be done BEFORE pytest starts
    pytest_logging_config = config_manager.get_pytest_logging_config()
    if pytest_logging_config:
        file_config = pytest_logging_config.get('file', {})
        if file_config.get('enabled', False):
            clean_on_start = file_config.get('clean_on_start', False)
            # Handle both boolean and string values
            if isinstance(clean_on_start, str):
                clean_on_start = clean_on_start.lower() in ('true', '1', 'yes', 'on')
            clean_on_start = bool(clean_on_start)
            
            if clean_on_start:
                import logging
                from pathlib import Path
                log_file_path = file_config.get('path', 'reports/logs/pytest.log')
                log_path = Path(log_file_path)
                log_dir = log_path.parent
                
                # Get list of files currently in use by log handlers
                files_in_use = set()
                root_logger = logging.getLogger()
                test_logger = logging.getLogger("TestAutomation")
                
                for handler in root_logger.handlers + test_logger.handlers:
                    if isinstance(handler, logging.FileHandler):
                        try:
                            handler_file = Path(handler.baseFilename)
                            if handler_file.exists():
                                files_in_use.add(handler_file.resolve())
                        except (AttributeError, OSError):
                            pass
                
                # Delete each file in the logs directory, skip files in use
                if log_dir.exists() and log_dir.is_dir():
                    deleted_count = 0
                    skipped_count = 0
                    for file in log_dir.iterdir():
                        if file.is_file():
                            file_resolved = file.resolve()
                            if file_resolved in files_in_use:
                                skipped_count += 1
                                logger.debug(f"[PYTEST-LOG] Skipping file in use: {file.name}")
                            else:
                                try:
                                    file.unlink()
                                    deleted_count += 1
                                except PermissionError:
                                    skipped_count += 1
                                    logger.debug(f"[PYTEST-LOG] Could not delete file (locked): {file.name}")
                    
                    if deleted_count > 0:
                        logger.info(f"[PYTEST-LOG] Deleted {deleted_count} file(s) from directory: {log_dir}")
                    if skipped_count > 0:
                        logger.info(f"[PYTEST-LOG] Skipped {skipped_count} file(s) (in use or locked)")
                
                # Ensure directory exists
                log_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"[PYTEST-LOG] Log file will be created at: {log_file_path}")
    
    # Build complete pytest arguments from config + CLI
    # Custom options (--env, etc.) sẽ được lấy từ pytest_configure hook
    final_pytest_args = build_pytest_args_from_config(config_args, pytest_args)
    
    # Log configuration summary
    logger.info("=" * 70)
    logger.info("PYTEST CONFIGURATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Original CLI Arguments:  {' '.join(cli_args) if cli_args else '(none)'}")
    logger.info(f"Config Arguments:        {' '.join(config_args) if config_args else '(none)'}")
    logger.info(f"Pytest Arguments:        {' '.join(pytest_args) if pytest_args else '(none)'}")
    logger.info("-" * 70)
    logger.info(f"Final Pytest Arguments:  {' '.join(final_pytest_args)}")
    
    # Execute pytest
    cmd = ["pytest"] + final_pytest_args
    logger.info(f"Executing: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()