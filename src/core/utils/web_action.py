"""
Web actions utility for Playwright operations.
"""
import time
from typing import Any, Optional, List, Dict, Union
from playwright.sync_api import Page, Locator, expect
from src.core.utils.report_logger import ReportLogger
from src.core.utils.config_manager import ConfigManager


class WebActions:
    """Utility class for web actions using Playwright."""
    
    def __init__(self, page: Page):
        self.page = page
        # Get logger from page (set in conftest) instead of creating new one
        self.logger = getattr(page, "logger", ReportLogger())
        self.config_manager = ConfigManager(self.logger)
    
    def _effective_timeout(self, timeout: Optional[int] = None) -> int:
        """Resolve effective timeout in ms: arg > page default (if set by base) > config default."""
        if timeout is not None:
            return timeout
        # Fallback to config default
        try:
            return int(self.config_manager.get_default_timeout())
        except Exception:
            return 30000
        
    def navigate_to(self, url: str, wait_until: str = "networkidle", timeout: Optional[int] = None):
        """Navigate to URL."""
        try:
            self.logger.log_action("navigate_to", "", url)
            self.page.goto(url, wait_until=wait_until, timeout=self._effective_timeout(timeout))
            self.logger.info(f"Navigated to: {url}")
        except Exception as e:
            self.logger.log_error(e, "navigate_to")
            raise
    
    def click(self, selector: str, **kwargs):
        """Click element by selector."""
        try:
            self.logger.log_action("click", selector)
            self.page.locator(selector).click(**kwargs)
        except Exception as e:
            self.logger.log_error(e, "click")
            raise
    
    def double_click(self, selector: str, **kwargs):
        """Double click element by selector."""
        try:
            self.logger.log_action("double_click", selector)
            self.page.locator(selector).dblclick(**kwargs)
        except Exception as e:
            self.logger.log_error(e, "double_click")
            raise
    
    def right_click(self, selector: str, **kwargs):
        """Right click element by selector."""
        try:
            self.logger.log_action("right_click", selector)
            self.page.locator(selector).click(button="right", **kwargs)
        except Exception as e:
            self.logger.log_error(e, "right_click")
            raise
    
    def hover(self, selector: str, **kwargs):
        """Hover over element by selector."""
        try:
            self.logger.log_action("hover", selector)
            self.page.locator(selector).hover(**kwargs)
        except Exception as e:
            self.logger.log_error(e, "hover")
            raise
    
    def fill(self, selector: str, value: str, **kwargs):
        """Fill input field by selector."""
        try:
            self.logger.log_action("fill", selector, value)
            self.page.locator(selector).fill(value, **kwargs)
        except Exception as e:
            self.logger.log_error(e, "fill")
            raise
    

    ## need fix code
    def type_text(self, selector: str, text: str, **kwargs):
        """Type text into element by selector."""
        try:
            self.logger.log_action("type_text", selector, text)
            # Use Playwright's native typing API
            self.page.locator(selector).type(text, **kwargs)
        except Exception as e:
            self.logger.log_error(e, "type_text")
            raise
    
    def clear(self, selector: str):
        """Clear input field by selector."""
        try:
            self.logger.log_action("clear", selector)
            self.page.locator(selector).clear()
        except Exception as e:
            self.logger.log_error(e, "clear")
            raise
    
    def select_option(self, selector: str, value: str):
        """Select option from dropdown by selector."""
        try:
            self.logger.log_action("select_option", selector, value)
            self.page.locator(selector).select_option(value)
        except Exception as e:
            self.logger.log_error(e, "select_option")
            raise
    
    def select_option_by_text(self, selector: str, text: str):
        """Select option by visible text."""
        try:
            self.logger.log_action("select_option_by_text", selector, text)
            self.page.locator(selector).select_option(label=text)
        except Exception as e:
            self.logger.log_error(e, "select_option_by_text")
            raise
    
    def check(self, selector: str):
        """Check checkbox by selector."""
        try:
            self.logger.log_action("check", selector)
            self.page.locator(selector).check()
        except Exception as e:
            self.logger.log_error(e, "check")
            raise
    
    def uncheck(self, selector: str):
        """Uncheck checkbox by selector."""
        try:
            self.logger.log_action("uncheck", selector)
            self.page.locator(selector).uncheck()
        except Exception as e:
            self.logger.log_error(e, "uncheck")
            raise
    
    def upload_file(self, selector: str, file_path: str):
        """Upload file to file input."""
        try:
            self.logger.log_action("upload_file", selector, file_path)
            self.page.locator(selector).set_input_files(file_path)
        except Exception as e:
            self.logger.log_error(e, "upload_file")
            raise
    
    def drag_and_drop(self, source_selector: str, target_selector: str):
        """Drag and drop element."""
        try:
            self.logger.log_action("drag_and_drop", f"{source_selector} -> {target_selector}")
            source = self.page.locator(source_selector)
            target = self.page.locator(target_selector)
            source.drag_to(target)
        except Exception as e:
            self.logger.log_error(e, "drag_and_drop")
            raise

    def scroll_to_element(self, selector: str, timeout: Optional[int] = None):
        """Scroll to element."""
        try:
            self.logger.log_action("scroll_to_element", selector)
            self.page.locator(selector).scroll_into_view_if_needed(timeout=self._effective_timeout(timeout))
        except Exception as e:
            self.logger.log_error(e, "scroll_to_element")
            raise
    
    def scroll_to_bottom(self):
        """Scroll to bottom of page."""
        try:
            self.logger.log_action("scroll_to_bottom")
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        except Exception as e:
            self.logger.log_error(e, "scroll_to_bottom")
            raise
    
    def scroll_to_top(self):
        """Scroll to top of page."""
        try:
            self.logger.log_action("scroll_to_top")
            self.page.evaluate("window.scrollTo(0, 0)")
        except Exception as e:
            self.logger.log_error(e, "scroll_to_top")
            raise
    
    def scroll_by(self, x: int, y: int):
        """Scroll by specified amount."""
        try:
            self.logger.log_action("scroll_by", "", f"x:{x}, y:{y}")
            self.page.evaluate(f"window.scrollBy({x}, {y})")
        except Exception as e:
            self.logger.log_error(e, "scroll_by")
            raise
    
    def wait_for_element(self, selector: str, timeout: Optional[int] = None):
        """Wait for element to be visible."""
        try:
            self.logger.log_action("wait_for_element", selector)
            self.page.wait_for_selector(selector, timeout=self._effective_timeout(timeout))
        except Exception as e:
            self.logger.log_error(e, "wait_for_element")
            raise
    
    def wait_for_text(self, text: str, timeout: Optional[int] = None):
        """Wait for text to appear."""
        try:
            self.logger.log_action("wait_for_text", "", text)
            self.page.wait_for_selector(f"text={text}", timeout=self._effective_timeout(timeout))
        except Exception as e:
            self.logger.log_error(e, "wait_for_text")
            raise
    
    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None):
        """Wait for URL to match pattern."""
        try:
            self.logger.log_action("wait_for_url", "", url_pattern)
            self.page.wait_for_url(url_pattern, timeout=self._effective_timeout(timeout))
        except Exception as e:
            self.logger.log_error(e, "wait_for_url")
            raise
    
    def wait_for_load_state(self, state: str = "networkidle", timeout: Optional[int] = None):
        """Wait for page load state."""
        try:
            self.logger.log_action("wait_for_load_state", "", state)
            self.page.wait_for_load_state(state, timeout=self._effective_timeout(timeout))
        except Exception as e:
            self.logger.log_error(e, "wait_for_load_state")
            raise
    
    def wait_for_function(self, function: str, timeout: Optional[int] = None):
        """Wait for function to return true."""
        try:
            self.logger.log_action("wait_for_function", "", function)
            self.page.wait_for_function(function, timeout=self._effective_timeout(timeout))
        except Exception as e:
            self.logger.log_error(e, "wait_for_function")
            raise
    
    def get_text(self, selector: str) -> str:
        """Get element text."""
        try:
            text = self.page.locator(selector).text_content()
            self.logger.log_action("get_text", selector, text)
            return text or ""
        except Exception as e:
            self.logger.log_error(e, "get_text")
            return ""
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get element attribute."""
        try:
            value = self.page.locator(selector).get_attribute(attribute)
            self.logger.log_action("get_attribute", f"{selector}.{attribute}", value or "")
            return value
        except Exception as e:
            self.logger.log_error(e, "get_attribute")
            return None
    
    def get_property(self, selector: str, property_name: str) -> Any:
        """Get element property."""
        try:
            value = self.page.locator(selector).evaluate(f"element => element.{property_name}")
            self.logger.log_action("get_property", f"{selector}.{property_name}", str(value))
            return value
        except Exception as e:
            self.logger.log_error(e, "get_property")
            return None
    
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        try:
            visible = self.page.locator(selector).is_visible()
            self.logger.log_action("is_visible", selector, str(visible))
            return visible
        except Exception as e:
            self.logger.log_error(e, "is_visible")
            return False
    
    def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled."""
        try:
            enabled = self.page.locator(selector).is_enabled()
            self.logger.log_action("is_enabled", selector, str(enabled))
            return enabled
        except Exception as e:
            self.logger.log_error(e, "is_enabled")
            return False
    
    def is_checked(self, selector: str) -> bool:
        """Check if element is checked."""
        try:
            checked = self.page.locator(selector).is_checked()
            self.logger.log_action("is_checked", selector, str(checked))
            return checked
        except Exception as e:
            self.logger.log_error(e, "is_checked")
            return False
    
    def count_elements(self, selector: str) -> int:
        """Count elements matching selector."""
        try:
            count = self.page.locator(selector).count()
            self.logger.log_action("count_elements", selector, str(count))
            return count
        except Exception as e:
            self.logger.log_error(e, "count_elements")
            return 0
    
    def get_all_texts(self, selector: str) -> List[str]:
        """Get all texts from elements matching selector."""
        try:
            texts = self.page.locator(selector).all_text_contents()
            self.logger.log_action("get_all_texts", selector, str(len(texts)))
            return texts
        except Exception as e:
            self.logger.log_error(e, "get_all_texts")
            return []
    
    def get_all_attributes(self, selector: str, attribute: str) -> List[str]:
        """Get all attribute values from elements matching selector."""
        try:
            attributes = []
            elements = self.page.locator(selector).all()
            for element in elements:
                attr_value = element.get_attribute(attribute)
                if attr_value:
                    attributes.append(attr_value)
            self.logger.log_action("get_all_attributes", f"{selector}.{attribute}", str(len(attributes)))
            return attributes
        except Exception as e:
            self.logger.log_error(e, "get_all_attributes")
            return []
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript on page."""
        try:
            self.logger.log_action("execute_script", "", script)
            result = self.page.evaluate(script, *args)
            return result
        except Exception as e:
            self.logger.log_error(e, "execute_script")
            raise
    
    def evaluate_element(self, selector: str, script: str) -> Any:
        """Execute JavaScript on specific element."""
        try:
            self.logger.log_action("evaluate_element", selector, script)
            result = self.page.locator(selector).evaluate(script)
            return result
        except Exception as e:
            self.logger.log_error(e, "evaluate_element")
            raise
    
    def take_screenshot(self, path: str = None) -> str:
        """Take page screenshot."""
        try:
            if not path:
                path = f"reports/screenshots/screenshot_{int(time.time())}.png"
            self.page.screenshot(path=path)
            self.logger.log_screenshot(path)
            return path
        except Exception as e:
            self.logger.log_error(e, "take_screenshot")
            return ""
    
    def take_element_screenshot(self, selector: str, path: str = None) -> str:
        """Take element screenshot."""
        try:
            if not path:
                path = f"reports/screenshots/element_{int(time.time())}.png"
            self.page.locator(selector).screenshot(path=path)
            self.logger.log_screenshot(path)
            return path
        except Exception as e:
            self.logger.log_error(e, "take_element_screenshot")
            return ""
    
    def get_page_title(self) -> str:
        """Get page title."""
        try:
            title = self.page.title()
            self.logger.log_action("get_page_title", "", title)
            return title
        except Exception as e:
            self.logger.log_error(e, "get_page_title")
            return ""
    
    def get_current_url(self) -> str:
        """Get current URL."""
        try:
            url = self.page.url
            self.logger.log_action("get_current_url", "", url)
            return url
        except Exception as e:
            self.logger.log_error(e, "get_current_url")
            return ""
    
    def refresh_page(self):
        """Refresh the page."""
        try:
            self.logger.log_action("refresh_page")
            self.page.reload()
            self.wait_for_load_state()
        except Exception as e:
            self.logger.log_error(e, "refresh_page")
            raise
    
    def go_back(self):
        """Go back to previous page."""
        try:
            self.logger.log_action("go_back")
            self.page.go_back()
            self.wait_for_load_state()
        except Exception as e:
            self.logger.log_error(e, "go_back")
            raise
    
    def go_forward(self):
        """Go forward to next page."""
        try:
            self.logger.log_action("go_forward")
            self.page.go_forward()
            self.wait_for_load_state()
        except Exception as e:
            self.logger.log_error(e, "go_forward")
            raise
    
    def switch_to_tab(self, index: int):
        """Switch to tab by index."""
        try:
            self.logger.log_action("switch_to_tab", "", str(index))
            pages = self.page.context.pages
            if index < len(pages):
                self.page = pages[index]
        except Exception as e:
            self.logger.log_error(e, "switch_to_tab")
            raise
    
    def close_tab(self):
        """Close current tab."""
        try:
            self.logger.log_action("close_tab")
            self.page.close()
        except Exception as e:
            self.logger.log_error(e, "close_tab")
            raise
    
    def handle_alert(self, action: str = "accept", text: str = ""):
        """Handle JavaScript alert."""
        try:
            self.logger.log_action("handle_alert", "", action)
            # if action == "accept":
            #     self.page.on("dialog", lambda dialog: dialog.accept(text) if text else dialog.accept())
            # else:
            #     self.page.on("dialog", lambda dialog: dialog.dismiss())
            def handle_dialog(dialog):
                self.logger.info(f"Dialog type: {dialog.type}, message: {dialog.message}")
                if action == "accept":
                    if text:
                        dialog.accept(text)
                    else:
                        dialog.accept()
                else:
                    dialog.dismiss()        
            # once() - chỉ xử lý 1 lần rồi tự động remove
            self.page.once("dialog", handle_dialog)
        except Exception as e:
            self.logger.log_error(e, "handle_alert")
            raise
    
    def download_file(self, selector: str) -> str:
        """Download file and return path."""
        try:
            self.logger.log_action("download_file", selector)
            with self.page.expect_download() as download_info:
                self.page.locator(selector).click()
            download = download_info.value
            return download.path()
        except Exception as e:
            self.logger.log_error(e, "download_file")
            raise
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies."""
        try:
            cookies = self.page.context.cookies()
            self.logger.log_action("get_cookies", "", str(len(cookies)))
            return cookies
        except Exception as e:
            self.logger.log_error(e, "get_cookies")
            return []
    
    def set_cookie(self, name: str, value: str, **kwargs):
        """Set cookie."""
        try:
            self.logger.log_action("set_cookie", "", f"{name}={value}")
            self.page.context.add_cookies([{"name": name, "value": value, **kwargs}])
        except Exception as e:
            self.logger.log_error(e, "set_cookie")
            raise
    
    def clear_cookies(self):
        """Clear all cookies."""
        try:
            self.logger.log_action("clear_cookies")
            self.page.context.clear_cookies()
        except Exception as e:
            self.logger.log_error(e, "clear_cookies")
            raise
    
    def get_local_storage(self, key: str = None) -> Union[Dict[str, str], str]:
        """Get local storage value(s)."""
        try:
            if key:
                value = self.page.evaluate(f"localStorage.getItem('{key}')")
                self.logger.log_action("get_local_storage", "", f"{key}={value}")
                return value
            else:
                storage = self.page.evaluate("Object.fromEntries(Object.entries(localStorage))")
                self.logger.log_action("get_local_storage", "", str(len(storage)))
                return storage
        except Exception as e:
            self.logger.log_error(e, "get_local_storage")
            return {} if key is None else ""
    
    def set_local_storage(self, key: str, value: str):
        """Set local storage value."""
        try:
            self.logger.log_action("set_local_storage", "", f"{key}={value}")
            self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")
        except Exception as e:
            self.logger.log_error(e, "set_local_storage")
            raise
    
    def clear_local_storage(self):
        """Clear local storage."""
        try:
            self.logger.log_action("clear_local_storage")
            self.page.evaluate("localStorage.clear()")
        except Exception as e:
            self.logger.log_error(e, "clear_local_storage")
            raise
    
    def get_session_storage(self, key: str = None) -> Union[Dict[str, str], str]:
        """Get session storage value(s)."""
        try:
            if key:
                value = self.page.evaluate(f"sessionStorage.getItem('{key}')")
                self.logger.log_action("get_session_storage", "", f"{key}={value}")
                return value
            else:
                storage = self.page.evaluate("Object.fromEntries(Object.entries(sessionStorage))")
                self.logger.log_action("get_session_storage", "", str(len(storage)))
                return storage
        except Exception as e:
            self.logger.log_error(e, "get_session_storage")
            return {} if key is None else ""
    
    def set_session_storage(self, key: str, value: str):
        """Set session storage value."""
        try:
            self.logger.log_action("set_session_storage", "", f"{key}={value}")
            self.page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")
        except Exception as e:
            self.logger.log_error(e, "set_session_storage")
            raise
    
    def clear_session_storage(self):
        """Clear session storage."""
        try:
            self.logger.log_action("clear_session_storage")
            self.page.evaluate("sessionStorage.clear()")
        except Exception as e:
            self.logger.log_error(e, "clear_session_storage")
            raise
