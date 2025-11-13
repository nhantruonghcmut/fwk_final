"""
Element object wrapper for web and mobile elements.
"""
import time
from typing import Any, Optional, List, Dict
from playwright.sync_api import Locator as PlaywrightLocator
# from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement as AppiumWebElement  # Consider updating this import
from src.core.utils.report_logger import ReportLogger
from typing import Union, Any
from appium.webdriver.webdriver import WebDriver as AppiumDriver
from playwright.async_api import Page
from src.core.utils.web_action import WebActions
from src.core.utils.mobile_action import MobileActions

class ElementObject:
    """Wrapper class for web and mobile elements."""
    
    def __init__(self, element: Union[PlaywrightLocator, AppiumWebElement], root_driver: Any = None):
        self.element = element
        self.logger = ReportLogger()
        self.root_driver = root_driver or self._extract_driver(element)
        self.element_type = self._detect_element_type()
        self.action
    
    @property
    def action(self):
        if self.element_type == "playwright":
            return WebActions(self.root_driver)
        elif self.element_type == "appium":
            return MobileActions(self.root_driver)   
        
    def _extract_driver(self, element: Any) -> Any:
        for attr in ['page', '_page', '_parent']:
            if hasattr(element, attr):
                return getattr(element, attr)
        raise ValueError("Cannot extract driver from element")
    
    def _detect_element_type(self) -> str:
        """Detect element type (playwright or selenium)."""
        module_name = self.root_driver.__class__.__module__
        if 'playwright' in module_name:
            return "playwright"
        elif 'appium' in module_name:
            return "appium"
        return "unknown"
    
    def get_element(self, selector: Union[str, tuple]):
        """Get element by selector."""
        if self.element_type == "playwright":
            return ElementObject(self.element.locator(selector), self.root_driver)
        else:
            if isinstance(selector, tuple):
                locator = selector             
            else:
                locator = (AppiumBy.ID, selector)
            return ElementObject(self.element.find_element(*locator), self.root_driver)

    def get_elements(self, selector: Union[str, tuple]):
        """Get multiple elements by selector."""
        if self.element_type == "playwright":
            elements = self.element.locator(selector).all()
            return [ElementObject(element) for element in elements]
        else:
            strategy, value = selector if isinstance(selector, tuple) else ("id", selector)
            elements = self.element.find_elements(getattr(AppiumBy, strategy.upper()), value)
            return [ElementObject(element, self.root_driver) for element in elements]    

    def click(self, **kwargs):
        """Click element."""
        try:
            self.logger.log_action("click", str(self.element))
            if self.element_type == "playwright":
                self.element.click(**kwargs)
            else:
                self.element.click()
        except Exception as e:
            self.logger.log_error(e, "click")
            raise
    
    def double_click(self, **kwargs):
        """Double click element."""
        try:
            self.logger.log_action("double_click", str(self.element))
            if self.element_type == "playwright":
                self.element.dblclick(**kwargs)
            else:
                self.logger.log_error("Double click action is not implemented for Appium elements.")
        except Exception as e:
            self.logger.log_error(e, "double_click")
            raise
    
    def right_click(self, **kwargs):
        """Right click element."""
        try:
            self.logger.log_action("right_click", str(self.element))
            if self.element_type == "playwright":
                self.element.click(button="right", **kwargs)
            else:
                self.logger.log_error("Right click action is not implemented for Appium elements.")
        except Exception as e:
            self.logger.log_error(e, "right_click")
            raise
    
    def hover(self, **kwargs):
        """Hover over element."""
        try:
            self.logger.log_action("hover", str(self.element))
            if self.element_type == "playwright":
                self.element.hover(**kwargs)
            else:
                self.logger.log_error("Hover action is not implemented for Appium elements.")
        except Exception as e:
            self.logger.log_error(e, "hover")
            raise

    def double_tap(self):
        """Double tap element (Appium only)."""
        if self.element_type != "appium":
            self.logger.log_error("Double tap action is only implemented for Appium elements.")
            return
        else:
            try:
                self.logger.log_action("double_tap", str(self.element))
                self.action.double_tap(self.element)                
            except Exception as e:
                self.logger.log_error(e, "double_tap")
                raise

    def long_tap(self, duration=1000):
        """Long tap element (Appium only)."""
        if self.element_type != "appium":
            self.logger.log_error("Long tap action is only implemented for Appium elements.")
            return
        else:
            try:
                self.logger.log_action("long_tap", str(self.element))
                self.action.long_press(self.element, duration=duration)
            except Exception as e:
                self.logger.log_error(e, "long_tap")
                raise

    def fill(self, value: str, **kwargs):
        """Fill element with value."""
        try:
            self.logger.log_action("fill", str(self.element), value)
            if self.element_type == "playwright":
                self.element.fill(value, **kwargs)
            else:
                self.element.clear()
                self.element.send_keys(value)
        except Exception as e:
            self.logger.log_error(e, "fill")
            raise
    
    def type_text(self, text: str, **kwargs):
        """Type text into element."""
        try:
            self.logger.log_action("type_text", str(self.element), text)
            if self.element_type == "playwright":
                # Playwright Locator supports .type(text, **kwargs)
                self.element.type(text, **kwargs)
            else:
                self.element.send_keys(text)
        except Exception as e:
            self.logger.log_error(e, "type_text")
            raise
    
    def clear(self):
        """Clear element content."""
        try:
            self.logger.log_action("clear", str(self.element))
            if self.element_type == "playwright":
                self.element.clear()
            else:
                self.element.clear()
        except Exception as e:
            self.logger.log_error(e, "clear")
            raise
    
    def get_text(self) -> str:
        """Get element text."""
        try:
            if self.element_type == "playwright":
                return self.element.text_content()
            else:
                return self.element.text
        except Exception as e:
            self.logger.log_error(e, "get_text")
            return ""
    
    def get_attribute(self, attribute_name: str) -> Optional[str]:
        """Get element attribute."""
        try:
            if self.element_type == "playwright":
                return self.element.get_attribute(attribute_name)
            else:
                return self.element.get_attribute(attribute_name)
        except Exception as e:
            self.logger.log_error(e, "get_attribute")
            return None
    
    def get_property(self, property_name: str) -> Any:
        """Get element property."""
        try:
            if self.element_type == "playwright":
                return self.element.evaluate(f"element => element.{property_name}")
            else:
                return self.element.get_property(property_name)
        except Exception as e:
            self.logger.log_error(e, "get_property")
            return None
    
    def is_visible(self) -> bool:
        """Check if element is visible."""
        try:
            if self.element_type == "playwright":
                return self.element.is_visible()
            else:
                return self.element.is_displayed()
        except Exception as e:
            self.logger.log_error(e, "is_visible")
            return False
    
    def is_enabled(self) -> bool:
        """Check if element is enabled."""
        try:
            if self.element_type == "playwright":
                return self.element.is_enabled()
            else:
                return self.element.is_enabled()
        except Exception as e:
            self.logger.log_error(e, "is_enabled")
            return False
    
    def is_selected(self) -> bool:
        """Check if element is selected."""
        try:
            if self.element_type == "playwright":
                return self.element.is_checked()
            else:
                return self.element.is_selected()
        except Exception as e:
            self.logger.log_error(e, "is_selected")
            return False
    
    def wait_for_visible(self, timeout: int = 30000):
        """Wait for element to be visible."""
        try:
            if self.element_type == "playwright":
                self.element.wait_for(state="visible", timeout=timeout)
            else:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                WebDriverWait(self.element._parent, timeout/1000).until(EC.visibility_of(self.element))
        except Exception as e:
            self.logger.log_error(e, "wait_for_visible")
            raise
    
    def wait_for_hidden(self, timeout: int = 30000):
        """Wait for element to be hidden."""
        try:
            if self.element_type == "playwright":
                self.element.wait_for(state="hidden", timeout=timeout)
            else:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                WebDriverWait(self.element._parent, timeout/1000).until(EC.invisibility_of_element(self.element))
        except Exception as e:
            self.logger.log_error(e, "wait_for_hidden")
            raise


    def wait_for_text(self, text: str, timeout: int = 30000):
        """Wait for text to appear within this element. This is unified for both Playwright and Appium."""
        try:
            self.logger.log_action("wait_for_text", str(self.element), text)
            
            start_time = time.time()
            end_time = start_time + (timeout / 1000)
            
            while time.time() < end_time:
                current_text = self.get_text()
                if text in current_text:
                    return True
                time.sleep(0.1)
                
            raise TimeoutError(f"Timeout waiting for text '{text}' in element")
                
        except Exception as e:
            self.logger.log_error(e, "wait_for_text")
            raise

    def scroll_into_view(self):
        """Scroll element into view."""
        try:
            self.logger.log_action("scroll_into_view", str(self.element))
            if self.element_type == "playwright":
                self.element.scroll_into_view_if_needed()
            else:
                self.element._parent.execute_script("arguments[0].scrollIntoView(true);", self.element)
        except Exception as e:
            self.logger.log_error(e, "scroll_into_view")
            raise
    
    def select_option(self, value: str):
        """Select option from dropdown."""
        try:
            self.logger.log_action("select_option", str(self.element), value)
            if self.element_type == "playwright":
                self.element.select_option(value)
            else:
                from selenium.webdriver.support.ui import Select
                Select(self.element).select_by_value(value)
        except Exception as e:
            self.logger.log_error(e, "select_option")
            raise
    
    def select_option_by_text(self, text: str):
        """Select option by visible text."""
        try:
            self.logger.log_action("select_option_by_text", str(self.element), text)
            if self.element_type == "playwright":
                self.element.select_option(label=text)
            else:
                from selenium.webdriver.support.ui import Select
                Select(self.element).select_by_visible_text(text)
        except Exception as e:
            self.logger.log_error(e, "select_option_by_text")
            raise
    
    def check(self):
        """Check checkbox or radio button."""
        try:
            self.logger.log_action("check", str(self.element))
            if self.element_type == "playwright":
                self.element.check()
            else:
                if not self.element.is_selected():
                    self.element.click()
        except Exception as e:
            self.logger.log_error(e, "check")
            raise
    
    def uncheck(self):
        """Uncheck checkbox."""
        try:
            self.logger.log_action("uncheck", str(self.element))
            if self.element_type == "playwright":
                self.element.uncheck()
            else:
                if self.element.is_selected():
                    self.element.click()
        except Exception as e:
            self.logger.log_error(e, "uncheck")
            raise
    
    def upload_file(self, file_path: str):
        """Upload file to file input."""
        try:
            self.logger.log_action("upload_file", str(self.element), file_path)
            if self.element_type == "playwright":
                self.element.set_input_files(file_path)
            else:
                self.element.send_keys(file_path)
        except Exception as e:
            self.logger.log_error(e, "upload_file")
            raise
    
    def drag_to(self, target_element: 'ElementObject'):
        """Drag element to target."""
        try:
            self.logger.log_action("drag_to", str(self.element), str(target_element.element))
            if self.element_type == "playwright":
                self.element.drag_to(target_element.element)
            else:
                self.action.drag_and_drop(self.element, target_element.element)               

        except Exception as e:
            self.logger.log_error(e, "drag_to")
            raise
    
    def get_location(self) -> Dict[str, int]:
        """Get element location."""
        try:
            if self.element_type == "playwright":
                box = self.element.bounding_box()
                return {"x": box["x"], "y": box["y"]} if box else {"x": 0, "y": 0}
            else:
                location = self.element.location
                return {"x": location["x"], "y": location["y"]}
        except Exception as e:
            self.logger.log_error(e, "get_location")
            return {"x": 0, "y": 0}
    
    def get_size(self) -> Dict[str, int]:
        """Get element size."""
        try:
            if self.element_type == "playwright":
                box = self.element.bounding_box()
                return {"width": box["width"], "height": box["height"]} if box else {"width": 0, "height": 0}
            else:
                size = self.element.size
                return {"width": size["width"], "height": size["height"]}
        except Exception as e:
            self.logger.log_error(e, "get_size")
            return {"width": 0, "height": 0}
    
    def get_rect(self) -> Dict[str, int]:
        """Get element rectangle."""
        try:
            if self.element_type == "playwright":
                box = self.element.bounding_box()
                return box if box else {"x": 0, "y": 0, "width": 0, "height": 0}
            else:
                rect = self.element.rect
                return {"x": rect["x"], "y": rect["y"], "width": rect["width"], "height": rect["height"]}
        except Exception as e:
            self.logger.log_error(e, "get_rect")
            return {"x": 0, "y": 0, "width": 0, "height": 0}
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript on element."""
        try:
            self.logger.log_action("execute_script", str(self.element), script)
            if self.element_type == "playwright":
                return self.element.evaluate(script)
            else:
                return self.element._parent.execute_script(script, self.element, *args)
        except Exception as e:
            self.logger.log_error(e, "execute_script")
            raise
    
    def take_screenshot(self, path: str = None) -> str:
        """Take screenshot of element."""
        try:
            if self.element_type == "playwright":
                if not path:
                    path = f"reports/screenshots/element_{int(time.time())}.png"
                self.element.screenshot(path=path)
            else:
                if not path:
                    path = f"reports/screenshots/element_{int(time.time())}.png"
                self.element.screenshot(path)
            self.logger.log_screenshot(path)
            return path
        except Exception as e:
            self.logger.log_error(e, "take_screenshot")
            return ""
    
    def get_inner_html(self) -> str:
        """Get element inner HTML."""
        try:
            if self.element_type == "playwright":
                return self.element.inner_html()
            else:
                return self.element.get_attribute("innerHTML")
        except Exception as e:
            self.logger.log_error(e, "get_inner_html")
            return ""
    
    def get_outer_html(self) -> str:
        """Get element outer HTML."""
        try:
            if self.element_type == "playwright":
                # Playwright doesn't expose outer_html directly; use evaluate
                return self.element.evaluate("element => element.outerHTML")
            else:
                return self.element.get_attribute("outerHTML")
        except Exception as e:
            self.logger.log_error(e, "get_outer_html")
            return ""
    
    def count(self) -> int:
        """Get count of elements."""
        try:
            if self.element_type == "playwright":
                return self.element.count()
            else:
                return len(self.element) if hasattr(self.element, '__len__') else 1
        except Exception as e:
            self.logger.log_error(e, "count")
            return 0
    
    def all(self) -> List['ElementObject']:
        """Get all matching elements."""
        try:
            if self.element_type == "playwright":
                elements = self.element.all()
                return [ElementObject(element) for element in elements]
            else:
                self.logger.log_error("All elements action is not implemented for Appium elements.")
        except Exception as e:
            self.logger.log_error(e, "all")
            return []
    
    def first(self) -> 'ElementObject':
        """Get first matching element."""
        try:
            if self.element_type == "playwright":
                return ElementObject(self.element.first)
            else:
                self.logger.log_error("First element action is not implemented for Appium elements.")
        except Exception as e:
            self.logger.log_error(e, "first")
            return self
    
    def nth(self, index: int) -> 'ElementObject':
        """Get nth matching element."""
        try:
            if self.element_type == "playwright":
                return ElementObject(self.element.nth(index))
            else:
                self.logger.log_error("Nth element action is not implemented for Appium elements.")
        except Exception as e:
            self.logger.log_error(e, "nth")
            return self
    
    # ---------------- Escape hatches & extended APIs ----------------
    def raw(self) -> Any:
        """Return the underlying element (Playwright Locator or Appium WebElement)."""
        return self.element

    def as_playwright(self) -> Optional[PlaywrightLocator]:
        """Return Playwright Locator if available, otherwise None."""
        return self.element if self.element_type == "playwright" else None

    def as_appium(self) -> Optional[AppiumWebElement]:
        """Return Appium WebElement if available, otherwise None."""
        return self.element if self.element_type == "appium" else None

    def call(self, method_name: str, *args, **kwargs) -> Any:
        """Call a method on the underlying element as an escape hatch (with logging)."""
        try:
            self.logger.log_action(f"call:{method_name}", str(self.element))
            target = getattr(self.element, method_name)
            return target(*args, **kwargs)
        except Exception as e:
            self.logger.log_error(e, f"call:{method_name}")
            raise

    # Commonly used Locator-like methods
    def focus(self, **kwargs):
        try:
            self.logger.log_action("focus", str(self.element))
            if self.element_type == "playwright":
                self.element.focus(**kwargs)
            else:
                # Appium: best-effort by clicking to focus
                self.element.click()
        except Exception as e:
            self.logger.log_error(e, "focus")
            raise

    def blur(self):
        try:
            self.logger.log_action("blur", str(self.element))
            if self.element_type == "playwright":
                # Blur via evaluate, as Locator.blur may not exist on older versions
                self.element.evaluate("el => el.blur()")
            else:
                # Not applicable on Appium; no-op
                self.logger.log_error("Blur action is not implemented for Appium elements.")
        except Exception as e:
            self.logger.log_error(e, "blur")
            raise

    def press(self, key: str, **kwargs):
        try:
            self.logger.log_action("press", str(self.element), key)
            if self.element_type == "playwright":
                self.element.press(key, **kwargs)
            else:
                # Basic mapping for Appium: send_keys for single characters, ENTER mapping, etc.
                from selenium.webdriver.common.keys import Keys
                mapped = getattr(Keys, key.upper(), None)
                self.element.send_keys(mapped if mapped else key)
        except Exception as e:
            self.logger.log_error(e, "press")
            raise

    def input_value(self) -> str:
        try:
            if self.element_type == "playwright":
                return self.element.input_value()
            else:
                value = self.element.get_attribute("value")
                return value or ""
        except Exception as e:
            self.logger.log_error(e, "input_value")
            return ""

    def inner_text(self) -> str:
        try:
            if self.element_type == "playwright":
                return self.element.inner_text()
            else:
                # Approximation using JavaScript when possible
                try:
                    return self.element._parent.execute_script("return arguments[0].innerText", self.element)
                except Exception:
                    return self.element.text or ""
        except Exception as e:
            self.logger.log_error(e, "inner_text")
            return ""

    def dispatch_event(self, type: str, event_init: Optional[Dict[str, Any]] = None):
        try:
            self.logger.log_action("dispatch_event", str(self.element), type)
            if self.element_type == "playwright":
                self.element.dispatch_event(type, event_init or {})
            else:
                # Not supported natively on Appium; emulate via JS if in webview context
                try:
                    self.element._parent.execute_script(
                        "var e = new Event(arguments[1], {bubbles:true,cancelable:true}); arguments[0].dispatchEvent(e);",
                        self.element, type
                    )
                except Exception:
                    raise NotImplementedError("dispatch_event is not supported for native Appium elements")
        except Exception as e:
            self.logger.log_error(e, "dispatch_event")
            raise

    def evaluate(self, script: str, arg: Any = None) -> Any:
        try:
            self.logger.log_action("evaluate", str(self.element), script)
            if self.element_type == "playwright":
                return self.element.evaluate(script, arg) if arg is not None else self.element.evaluate(script)
            else:
                return self.element._parent.execute_script(script, self.element, arg) if arg is not None else self.element._parent.execute_script(script, self.element)
        except Exception as e:
            self.logger.log_error(e, "evaluate")
            raise
    
    def __str__(self) -> str:
        """String representation of element."""
        return f"ElementObject({self.element_type}: {str(self.element)})"
    
    def __repr__(self) -> str:
        """Representation of element."""
        return self.__str__()
