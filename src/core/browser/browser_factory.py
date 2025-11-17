"""
Browser factory for creating thread-safe browser instances using Playwright Sync API.
"""
import os
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from src.core.browser.browser_type import BrowserType
from src.core.utils.config_manager import ConfigManager
from src.core.utils.report_logger import ReportLogger


class BrowserFactory:
    """Factory class for creating and managing browser instances."""
    
    _instance = None
    _lock = threading.Lock()
    _browsers: Dict[threading.Thread, Browser] = {}
    _contexts: Dict[threading.Thread, BrowserContext] = {}
    _playwright = None
    
    # ============================================
    # BROWSER OPTIONS vs CONTEXT OPTIONS
    # ============================================
    # These are options that go to browser.launch()
    BROWSER_OPTIONS = {
        'headless', 'args', 'channel', 'downloads_path',
        'executable_path', 'extra_http_headers', 'proxy',
        'slow_mo', 'timeout', 'trace', 'env'
    }
    
    # These are options that go to browser.new_context()
    CONTEXT_OPTIONS = {
        'viewport', 'screen', 'device_scale_factor',
        'is_mobile', 'has_touch', 'locale', 'timezone_id',
        'geolocation', 'permissions', 'ignore_https_errors',
        'extra_http_headers', 'offline', 'http_credentials',
        'color_scheme', 'reduced_motion', 'forced_colors',
        'storage_state', 'record_video_dir', 'record_video_size'
    }
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BrowserFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize browser factory."""
        if not hasattr(self, 'initialized'):
            self.logger = ReportLogger()
            self.config_manager = ConfigManager(self.logger)
            self.initialized = True
    
    def _separate_options(self, options: Dict[str, Any]) -> tuple[Dict, Dict]:
        """
        Separate options into browser_options and context_options.
        
        Args:
            options: Combined options dict
            
        Returns:
            Tuple of (browser_options, context_options)
        """
        browser_options = {}
        context_options = {}
        
        for key, value in options.items():
            if key in self.BROWSER_OPTIONS:
                browser_options[key] = value
            elif key in self.CONTEXT_OPTIONS:
                context_options[key] = value
            else:
                # Default to context options if ambiguous
                context_options[key] = value
        
        return browser_options, context_options
    
    def start_playwright(self):
        """Start Playwright instance."""
        if self._playwright is None:
            with self._lock:
                if self._playwright is None:
                    self._playwright = sync_playwright().start()
                    self.logger.info("Playwright started")
    
    def stop_playwright(self):
        """Stop Playwright instance."""
        with self._lock:
            try:
                if self._playwright:
                    self._playwright.stop()
                    self._playwright = None
                    self.logger.info("Playwright stopped")
            except Exception as e:
                self.logger.error(f"Failed to stop Playwright: {str(e)}")
    
    def create_browser(self, browser_type: BrowserType, **kwargs) -> Browser:
        """
        Create browser instance for current thread.
        [OK] Filters out context options before launching
        """
        current_thread = threading.current_thread()
        
        # Start Playwright if not already started
        self.start_playwright()
        
        # Get base browser configuration from ConfigManager
        config_options = self.config_manager.get_browser_config(browser_type.value)
        
        # Merge: config < kwargs (kwargs override config)
        all_options = {**config_options, **kwargs}
        
        # [OK] CRITICAL: Separate browser options from context options
        browser_options, context_options = self._separate_options(all_options)
        
        # Store context options for later use in create_context()
        self._context_options = context_options
        
        try:
            self.logger.debug(f"Browser options: {browser_options}")
            
            if browser_type == BrowserType.CHROMIUM:
                browser = self._playwright.chromium.launch(**browser_options)
            elif browser_type == BrowserType.FIREFOX:
                browser = self._playwright.firefox.launch(**browser_options)
            elif browser_type == BrowserType.WEBKIT:
                browser = self._playwright.webkit.launch(**browser_options)
            elif browser_type == BrowserType.EDGE:
                browser = self._playwright.chromium.launch(
                    channel="msedge",
                    **browser_options
                )
            elif browser_type == BrowserType.CHROME:
                browser = self._playwright.chromium.launch(
                    channel="chrome",
                    **browser_options
                )
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            # Store browser for current thread
            with self._lock:
                self._browsers[current_thread] = browser
            self.logger.info(f"[OK] Created {browser_type.value} browser for thread {current_thread.name}")
            
            return browser
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to create {browser_type.value} browser: {str(e)}")
            raise
    
    def create_context(self, browser: Optional[Browser] = None, **kwargs) -> BrowserContext:
        """
        Create browser context for current thread.
        [OK] Uses separated context options
        """
        current_thread = threading.current_thread()
        
        if browser is None:
            browser = self.get_browser_for_thread(current_thread)
        
        if browser is None:
            raise RuntimeError("No browser available for current thread")
        
        # Start with stored context options from create_browser()
        context_config = getattr(self, '_context_options', {}).copy()
        
        # Get default context config from ConfigManager
        default_context = self.config_manager.get_context_config()
        
        # Merge: default < stored < provided kwargs
        # (kwargs have highest priority)
        all_options = {**default_context, **context_config, **kwargs}
        
        # [OK] CRITICAL: Filter out any browser options that might have been passed
        browser_options, context_options = self._separate_options(all_options)
        
        try:
            self.logger.debug(f"Context options: {context_options}")
            
            context = browser.new_context(**context_options)
            
            with self._lock:
                self._contexts[current_thread] = context
            
            self.logger.info(f"[OK] Created browser context for thread {current_thread.name}")
            
            return context
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to create browser context: {str(e)}")
            raise
    
    def create_page(self, context: Optional[BrowserContext] = None) -> Page:
        """Create new page."""
        current_thread = threading.current_thread()
        
        if context is None:
            context = self.get_context_for_thread(current_thread)
        
        if context is None:
            raise RuntimeError("No browser context available for current thread")
        
        try:
            page = context.new_page()
            self.logger.info(f"[OK] Created new page for thread {current_thread.name}")
            
            return page
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to create page: {str(e)}")
            raise
    
    def get_browser_for_thread(self, thread: threading.Thread) -> Optional[Browser]:
        """Get browser instance for specific thread."""
        with self._lock:
            return self._browsers.get(thread)
    
    def get_context_for_thread(self, thread: threading.Thread) -> Optional[BrowserContext]:
        """Get browser context for specific thread."""
        with self._lock:
            return self._contexts.get(thread)
    
    def get_page_for_thread(self, thread: threading.Thread) -> Optional[Page]:
        """Get page for specific thread."""
        context = self.get_context_for_thread(thread)
        if context:
            pages = context.pages
            return pages[0] if pages else None
        return None
    
    def close_browser_for_thread(self, thread: threading.Thread):
        """Close browser for specific thread."""
        with self._lock:
            browser = self._browsers.get(thread)
            if browser:
                try:
                    browser.close()
                    del self._browsers[thread]
                    self.logger.info(f"[CLEANUP] Closed browser for thread {thread.name}")
                except Exception as e:
                    self.logger.error(f"[ERROR] Failed to close browser for thread {thread.name}: {str(e)}")
    
    def close_context_for_thread(self, thread: threading.Thread):
        """Close browser context for specific thread."""
        with self._lock:
            context = self._contexts.get(thread)
            if context:
                try:
                    context.close()
                    del self._contexts[thread]
                    self.logger.info(f"[CLEANUP] Closed browser context for thread {thread.name}")
                except Exception as e:
                    self.logger.error(f"[ERROR] Failed to close browser context for thread {thread.name}: {str(e)}")
    
    def close_all_browsers(self):
        """Close all browser instances."""
        with self._lock:
            threads_to_close = list(self._browsers.keys())

        for thread in threads_to_close:
            self.close_browser_for_thread(thread)

        with self._lock:
            threads_to_close = list(self._contexts.keys())
        for thread in threads_to_close:
            self.close_context_for_thread(thread)
        
        self.stop_playwright()
        self.logger.info("Closed all browsers and contexts")
    
    def get_browser_info(self) -> Dict[str, Any]:
        """Get information about all browser instances."""
        with self._lock:
            info = {
                "active_browsers": len(self._browsers),
                "active_contexts": len(self._contexts),
                "playwright_running": self._playwright is not None,
                "threads": {}
            }
            
            for thread, browser in self._browsers.items():
                info["threads"][thread.name] = {
                    "browser_type": type(browser).__name__,
                    "has_context": thread in self._contexts
                }
            
        return info
    
    def is_browser_running(self, thread: threading.Thread) -> bool:
        """Check if browser is running for specific thread."""
        with self._lock:
            browser = self._browsers.get(thread)
            if browser:
                try:
                    # Try to get browser version to check if it's still running
                    browser.version
                    return True
                except:
                    # Browser is closed, remove from dict
                    del self._browsers[thread]
                    return False
            return False
    
    def restart_browser_for_thread(self, thread: threading.Thread, browser_type: BrowserType):
        """Restart browser for specific thread."""
        self.close_browser_for_thread(thread)
        self.close_context_for_thread(thread)
        return self.create_browser(browser_type)
    
    def create_browser_with_context(self, browser_type: BrowserType, **kwargs) -> tuple[Browser, BrowserContext]:
        """Create browser and context together."""
        browser = self.create_browser(browser_type, **kwargs)
        context = self.create_context(browser)
        return browser, context
    
    def create_browser_with_page(self, browser_type: BrowserType, **kwargs) -> tuple[Browser, BrowserContext, Page]:
        """
        Create browser, context, and page together.
        [OK] Properly separates browser and context options
        """
        browser = self.create_browser(browser_type, **kwargs)
        context = self.create_context(browser)
        page = self.create_page(context)
        return browser, context, page
    
    # ============================================
    # TRACING METHODS
    # ============================================
    
    def start_tracing(self, context: Optional[BrowserContext] = None, **kwargs):
        """
        Start tracing for browser context.
        
        Args:
            context: Browser context to start tracing on. If None, uses current thread's context.
            **kwargs: Tracing options (screenshots, snapshots, sources)
        """
        if context is None:
            current_thread = threading.current_thread()
            context = self.get_context_for_thread(current_thread)
        
        if context is None:
            self.logger.warning("[TRACE] No context available for tracing")
            return False
        
        try:
            # Get trace config from ConfigManager
            trace_config = self.config_manager.get_trace_config()
            
            # Build tracing options
            tracing_options = {
                "screenshots": kwargs.get("screenshots", trace_config.get("screenshots", True)),
                "snapshots": kwargs.get("snapshots", trace_config.get("snapshots", True)),
                "sources": kwargs.get("sources", trace_config.get("sources", True))
            }
            
            context.tracing.start(**tracing_options)
            self.logger.info(f"[TRACE] Started tracing for context (screenshots={tracing_options['screenshots']}, snapshots={tracing_options['snapshots']}, sources={tracing_options['sources']})")
            return True
            
        except Exception as e:
            self.logger.error(f"[TRACE] Failed to start tracing: {str(e)}")
            return False
    
    def stop_tracing(self, context: Optional[BrowserContext] = None, path: Optional[str] = None) -> Optional[str]:
        """
        Stop tracing and save to file.
        
        Args:
            context: Browser context to stop tracing on. If None, uses current thread's context.
            path: Path to save trace.zip file. If None, generates path from config.
            
        Returns:
            Path to saved trace.zip file, or None if failed
        """
        if context is None:
            current_thread = threading.current_thread()
            context = self.get_context_for_thread(current_thread)
        
        if context is None:
            self.logger.warning("[TRACE] No context available to stop tracing")
            return None
        
        try:
            # Generate path if not provided
            if path is None:
                trace_dir = self.config_manager.get_trace_directory()
                Path(trace_dir).mkdir(parents=True, exist_ok=True)
                timestamp = int(time.time())
                path = os.path.join(trace_dir, f"trace_{timestamp}.zip")
            
            # Ensure directory exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            # Stop tracing and save
            context.tracing.stop(path=path)
            self.logger.info(f"[TRACE] Stopped tracing and saved to: {path}")
            return path
            
        except Exception as e:
            self.logger.error(f"[TRACE] Failed to stop tracing: {str(e)}")
            return None