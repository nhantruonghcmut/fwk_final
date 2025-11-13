"""
Browser type enumeration for supported browsers.
"""
from enum import Enum


class BrowserType(Enum):
    """Enumeration of supported browser types."""
    
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    EDGE = "msedge"
    CHROME = "chrome"
    
    @classmethod
    def get_all_browsers(cls) -> list:
        """Get all supported browser types."""
        return [browser.value for browser in cls]
        
    @classmethod
    def is_supported(cls, browser_name: str) -> bool:
        """Check if browser is supported."""
        return browser_name.lower() in [browser.value for browser in cls]
        
    @classmethod
    def get_browser_type(cls, browser_name: str) -> 'BrowserType':
        """Get browser type by name."""
        browser_name = browser_name.lower()
        for browser in cls:
            if browser.value == browser_name:
                return browser
        raise ValueError(f"Unsupported browser: {browser_name}")
        
    def __str__(self) -> str:
        """String representation of browser type."""
        return self.value
