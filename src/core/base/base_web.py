"""
Base class for web application page objects using Playwright Sync API.
"""
import os
import time
from playwright.sync_api import Page, Locator, expect
from typing import Optional, List, Dict, Any
from src.core.base.base_test import BaseTest
from src.core.utils.web_action import WebActions
from src.core.utils.element_object import ElementObject
from src.core.utils.report_logger import ReportLogger
from  src.core.utils.screenshot_util import ScreenshotUtil
from typing import Union, Any

class BaseWeb(BaseTest):
    """Base class for web page objects."""
    
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.web_actions = WebActions(page)
        self.logger = ReportLogger()
        self.screenshot_util = ScreenshotUtil()

    def navigate_to(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000):
        """Navigate to a specific URL. 
           Option:
             wait_until: 'domcontentloaded' | 'networkidle'
             timeout: int (milliseconds)
        """
        self.log_test_step(f"Navigating to: {url}")
        # Delegate to WebActions to centralize logging/handling
        if wait_until == "domcontentloaded":
            self.page.goto(url, wait_until=wait_until, timeout=timeout)
        else:
            # For networkidle and others, reuse WebActions navigate for consistency
            self.web_actions.navigate_to(url, wait_until=wait_until)

    def get_title(self) -> str:
        return self.page.title()        
        
    def get_element(self, selector: str) -> ElementObject:
        """Get element by selector."""
        return ElementObject(self.page.locator(selector),self.page)
        
    def get_elements(self, selector: str) -> List[ElementObject]:
        """Get multiple elements by selector."""
        elements = self.page.locator(selector).all()
        return [ElementObject(element,self.page) for element in elements]
        
    def wait_for_element(self, element_obj, timeout=30000, state="visible"):
        """Wait for element to be in specified state."""
        try:
            # Use the element directly instead of trying to access selector
            if hasattr(element_obj, "element"):
                element_obj.element.wait_for(state=state, timeout=timeout)
            else:
                self.page.wait_for_selector(element_obj, timeout=timeout, state=state)
            return True
        except Exception as e:
            self.logger.error(f"Failed waiting for element {element_obj}: {str(e)}")
            return False
        
    def wait_for_page_load(self):
        """Wait for page to load completely."""
        self.page.wait_for_load_state("networkidle")
        
    def take_screenshot(self, name: str = None):
        """Take screenshot."""
        test_context = self.test_context if hasattr(self, 'test_context') else None
        return self.screenshot_util.take_screenshot(name, self.page, test_context=test_context)
        
    def get_page_title(self) -> str:
        """Get page title."""
        return self.web_actions.get_page_title()
        
    def get_current_url(self) -> str:
        """Get current URL."""
        return self.web_actions.get_current_url()
        
    def refresh_page(self):
        """Refresh the current page."""
        self.web_actions.refresh_page()
        
    def go_back(self):
        """Go back to previous page."""
        self.web_actions.go_back()
        
    def go_forward(self):
        """Go forward to next page."""
        self.web_actions.go_forward()
        
    def switch_to_tab(self, index: int):
        """Switch to tab by index."""
        pages = self.page.context.pages
        if index < len(pages):
            self.page = pages[index]
            
    def close_tab(self):
        """Close current tab."""
        self.page.close()
        
    def execute_javascript(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        return self.page.evaluate(script)
        
    def scroll_to_element(self, selector: str):
        """Scroll to element."""
        self.web_actions.scroll_to_element(selector)
        
    def scroll_to_bottom(self):
        """Scroll to bottom of page."""
        self.web_actions.scroll_to_bottom()
        
    def scroll_to_top(self):
        """Scroll to top of page."""
        self.web_actions.scroll_to_top()
        
    def hover_element(self, selector: str):
        """Hover over element."""
        self.web_actions.hover(selector)
        
    def double_click_element(self, selector: str):
        """Double click element."""
        self.web_actions.double_click(selector)
        
    def right_click_element(self, selector: str):
        """Right click element."""
        self.web_actions.right_click(selector)
        
    def drag_and_drop(self, source_selector: str, target_selector: str):
        """Drag and drop element."""
        self.web_actions.drag_and_drop(source_selector, target_selector)
        
    def upload_file(self, file_input_selector: str, file_path: str):
        """Upload file."""
        self.web_actions.upload_file(file_input_selector, file_path)
        
    def download_file(self, download_selector: str) -> str:
        """Download file and return path."""
        return self.web_actions.download_file(download_selector)
        
    def handle_alert(self, action: str = "accept"):
        """Handle JavaScript alert."""
        self.web_actions.handle_alert(action)
            
    def fill_form_field(self, selector: str, value: str):
        """Fill form field."""
        self.log_test_step(f"Filling field {selector} with value: {value}")
        self.web_actions.fill(selector, value)
        
    def select_dropdown_option(self, selector: str, value: str):
        """Select dropdown option."""
        self.log_test_step(f"Selecting option {value} from dropdown {selector}")
        self.web_actions.select_option(selector, value)
        
    def check_checkbox(self, selector: str):
        """Check checkbox."""
        self.web_actions.check(selector)
        
    def uncheck_checkbox(self, selector: str):
        """Uncheck checkbox."""
        self.web_actions.uncheck(selector)
        
    def select_radio_button(self, selector: str):
        """Select radio button."""
        self.page.locator(selector).check()
        
    def verify_element_present(self, selector: str) -> bool:
        """Verify element is present."""
        try:
            self.page.locator(selector).wait_for(timeout=5000)
            return True
        except:
            return False
            
    def verify_element_visible(self, selector: str) -> bool:
        """Verify element is visible."""
        try:
            return self.page.locator(selector).is_visible()
        except:
            return False
            
    def verify_text_present(self, text: str) -> bool:
        """Verify text is present on page."""
        try:
            return self.page.locator(f"text={text}").is_visible()
        except:
            return False
            
    def verify_url_contains(self, url_part: str) -> bool:
        """Verify URL contains specific part."""
        return url_part in self.get_current_url()
        
    def get_element_text(self, selector: str) -> str:
        """Get element text."""
        return self.page.locator(selector).text_content()
        
    def get_element_attribute(self, selector: str, attribute: str) -> str:
        """Get element attribute value."""
        return self.page.locator(selector).get_attribute(attribute)
        
    def get_element_count(self, selector: str) -> int:
        """Get count of elements matching selector."""
        return self.page.locator(selector).count()
        
    def wait_for_text(self, text: str, timeout: int = 30000):
        """Wait for text to appear."""
        self.page.wait_for_selector(f"text={text}", timeout=timeout)
        
    def wait_for_url_change(self, current_url: str, timeout: int = 30000):
        """Wait for URL to change."""
        self.page.wait_for_function(
            f"() => window.location.href !== '{current_url}'",
            timeout=timeout
        )
