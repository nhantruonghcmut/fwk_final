"""
Mobile actions utility for Appium operations.
"""
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Any, Optional, List, Dict, Tuple, Union
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.extensions.action_helpers import ActionHelpers
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from appium.webdriver.webelement import WebElement 
from src.core.utils.report_logger import ReportLogger
from src.core.utils.mobile_retry import retry_on_connection_error, check_driver_health


class MobileActions:
    """Utility class for mobile actions using Appium."""
    
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.logger = ReportLogger()
        
    # ---------------- Platform helpers ----------------
    def get_platform(self) -> str:
        try:
            return (self.driver.capabilities.get('platformName') or '').lower()
        except Exception:
            return ''

    def is_android(self) -> bool:
        return self.get_platform() == 'android'

    def is_ios(self) -> bool:
        return self.get_platform() == 'ios'
        
    def tap(self, locator: Union[Tuple[str, str], WebElement], **kwargs):
        """Tap element by locator."""
        try:
            self.logger.log_action("tap", str(locator))
            if isinstance(locator, tuple):
                element = self.driver.find_element(*locator)
            else:
                element = locator
            element.click()
        except Exception as e:
            self.logger.log_error(e, "tap")
            raise
    def click(self, locator: Union[Tuple[str, str], WebElement], **kwargs):
        """Click element by locator."""
        try:
            self.logger.log_action("click", str(locator))
            if isinstance(locator, tuple):
                element = self.driver.find_element(*locator)
            else:
                element = locator
            element.click()
        except Exception as e:
            self.logger.log_error(e, "click")
            raise

    def tap_coordinates(self, x: int, y: int):
        """Tap at coordinates."""
        try:
            self.logger.log_action("tap_coordinates", "", f"x:{x}, y:{y}")
            action = ActionBuilder(self.driver, mouse=PointerInput(POINTER_TOUCH, "touch"))
            action.pointer_action.move_to_location(x, y)
            action.pointer_action.click()
            action.perform()
        except Exception as e:
            self.logger.log_error(e, "tap_coordinates")
            raise
    
    def long_press(self, locator: Union[Tuple[str, str], WebElement], duration: int = 2000):
        """Long press element."""
        try:
            if isinstance(locator, tuple):
                element = self.driver.find_element(*locator)
            else:
                element = locator
            self.logger.log_action("long_press", str(locator), f"duration:{duration}")
            # Dùng W3C Actions
            actions = ActionBuilder(self.driver, mouse=PointerInput(POINTER_TOUCH, "touch"))
            actions.pointer_action.move_to(element)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(duration / 1000)  # convert to seconds
            actions.pointer_action.pointer_up()
            actions.perform()
        except Exception as e:
            self.logger.log_error(e, "long_press")
            raise
    
    def long_press_coordinates(self, x: int, y: int, duration: int = 2000):
        """Long press at coordinates."""
        try:
            self.logger.log_action("long_press_coordinates", "", f"x:{x}, y:{y}, duration:{duration}")
            # TouchAction(self.driver).long_press(x=x, y=y, duration=duration).perform()
            action = ActionBuilder(self.driver, mouse=PointerInput(POINTER_TOUCH, "touch"))
            action.pointer_action.move_to_location(x, y)
            action.pointer_action.pointer_down()
            action.pointer_action.pause(duration / 1000)  # convert to seconds
            action.pointer_action.pointer_up()
            action.perform()
        except Exception as e:
            self.logger.log_error(e, "long_press_coordinates")
            raise
    
        """Double tap element."""
    def  double_tap(self, locator: Union[Tuple[str, str],WebElement], time_delay: int = 100):
        try:
            self.logger.log_action("double_tap", str(locator))
            if isinstance(locator, tuple):
                element = self.driver.find_element(*locator)
            else:
                element = locator
            # TouchAction(self.driver).tap(element, count=2).perform()
            action = ActionBuilder(self.driver, mouse=PointerInput(POINTER_TOUCH, "touch"))
            action.pointer_action.move_to(element)
            action.pointer_action.click()
            action.pointer_action.pause(time_delay/1000)
            action.pointer_action.click()
            action.perform()
        except Exception as e:
            self.logger.log_error(e, "double_tap")
            raise
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000):
        """Swipe from start to end coordinates."""
        try:
            self.logger.log_action("swipe", "", f"from({start_x},{start_y}) to({end_x},{end_y})")
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        except Exception as e:
            self.logger.log_error(e, "swipe")
            raise
    
    def swipe_up(self, duration: int = 1000):
        """Swipe up."""
        try:
            self.logger.log_action("swipe_up")
            size = self.driver.get_window_size()
            start_x = size['width'] // 2
            start_y = size['height'] * 3 // 4
            end_y = size['height'] // 4
            self.swipe(start_x, start_y, start_x, end_y, duration)
        except Exception as e:
            self.logger.log_error(e, "swipe_up")
            raise
    
    def swipe_down(self, duration: int = 1000):
        """Swipe down."""
        try:
            self.logger.log_action("swipe_down")
            size = self.driver.get_window_size()
            start_x = size['width'] // 2
            start_y = size['height'] // 4
            end_y = size['height'] * 3 // 4
            self.swipe(start_x, start_y, start_x, end_y, duration)
        except Exception as e:
            self.logger.log_error(e, "swipe_down")
            raise
    
    def swipe_left(self, duration: int = 1000):
        """Swipe left."""
        try:
            self.logger.log_action("swipe_left")
            size = self.driver.get_window_size()
            start_x = size['width'] * 3 // 4
            start_y = size['height'] // 2
            end_x = size['width'] // 4
            self.swipe(start_x, start_y, end_x, start_y, duration)
        except Exception as e:
            self.logger.log_error(e, "swipe_left")
            raise
    
    def swipe_right(self, duration: int = 1000):
        """Swipe right."""
        try:
            self.logger.log_action("swipe_right")
            size = self.driver.get_window_size()
            start_x = size['width'] // 4
            start_y = size['height'] // 2
            end_x = size['width'] * 3 // 4
            self.swipe(start_x, start_y, end_x, start_y, duration)
        except Exception as e:
            self.logger.log_error(e, "swipe_right")
            raise
    
    def scroll_to_element(self, locator: Tuple[str, str], timeout: int = 30, 
                     wait_after_scroll: float = 0.5, short_find_timeout: float = 2):
        """
        Scroll until element is found in DOM and scroll to it.
        
        Args:
            locator: Tuple of (By strategy, locator value)
            timeout: Total maximum time in seconds
            wait_after_scroll: Wait time after each scroll in seconds
            short_find_timeout: Timeout to check presence after each scroll in seconds
        """
        try:
            self.logger.log_action("scroll_to_element_start", str(locator))

            
            end_time = time.time() + timeout
            
            # 1) Quick check if element already in DOM
            try:
                element = WebDriverWait(self.driver, short_find_timeout).until(
                    EC.presence_of_element_located(locator)
                )
                self.logger.log_action("element_already_found", str(locator))
                # Element is in DOM, scroll to it directly
                self.driver.execute_script("mobile: scrollToElement", {'element': element, 'toVisible': True})
                return
            except TimeoutException:
                pass
            
            # 2) Scroll loop until timeout
            scroll_count = 0
            while time.time() < end_time:
                scroll_count += 1
                # Perform swipe first
                self.swipe_up()
                self.logger.log_action("scrolling", str(locator), f"attempt:{scroll_count}")
                
                # Wait after scroll for content to settle
                time.sleep(wait_after_scroll)
                
                # Check if element is now in DOM
                try:
                    element = WebDriverWait(self.driver, short_find_timeout).until(
                        EC.presence_of_element_located(locator)
                    )
                    # Element is found in DOM, scroll to it
                    self.logger.log_action("element_found_after_scroll", str(locator), f"scrolls:{scroll_count}")
                    self.driver.execute_script("mobile: scrollToElement", {
                        'element': element, 
                        'toVisible': True
                    })
                    return
                except TimeoutException:
                    continue  # Element not found yet, continue scrolling
                
            # Timeout reached
            self.logger.log_action("element_not_found_after_timeout", str(locator), f"scrolls:{scroll_count}")
            raise TimeoutException(f"Element {locator} not found after {timeout}s and {scroll_count} scroll attempts")
            
        except Exception as e:
            self.logger.log_error(e, "scroll_to_element")
            raise
    
    def scroll_to_text(self, text: str, timeout: int = 30, 
                  wait_after_scroll: float = 0.5, short_find_timeout: float = 2):
        """
        Scroll until text is found in DOM and scroll to it.
        
        Args:
            text: Text to search for
            timeout: Total maximum time in seconds
            wait_after_scroll: Wait time after each scroll in seconds
            short_find_timeout: Timeout to check presence after each scroll in seconds
        """
        try:
            self.logger.log_action("scroll_to_text_start", "", text)
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            import time
            
            text_locator = (AppiumBy.XPATH, f"//*[@text='{text}']")
            end_time = time.time() + timeout
            
            # 1) Quick check if text already in DOM
            try:
                element = WebDriverWait(self.driver, short_find_timeout).until(
                    EC.presence_of_element_located(text_locator)
                )
                self.logger.log_action("text_already_found", "", text)
                # Text is in DOM, scroll to it directly
                self.driver.execute_script("mobile: scrollToElement", {'element': element, 'toVisible': True})
                return
            except TimeoutException:
                pass
            
            # 2) Scroll loop until timeout
            scroll_count = 0
            platform = self.driver.capabilities.get('platformName', '').lower()
            
            while time.time() < end_time:
                scroll_count += 1
                
                # Platform-specific scroll approach
                if platform == 'android':
                    # Try using UiScrollable for Android (scrolls AND finds)
                    try:
                        self.logger.log_action("using_uiscrollable", "", f"text:{text}, attempt:{scroll_count}")
                        element = self.driver.find_element(
                            AppiumBy.ANDROID_UIAUTOMATOR,
                            f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("{text}"))'
                        )
                        # UiScrollable already scrolled if element found
                        self.logger.log_action("text_found_with_uiscrollable", "", f"text:{text}, scrolls:{scroll_count}")
                        return
                    except Exception as e:
                        # UiScrollable didn't find the text or failed
                        self.logger.log_action("uiscrollable_failed", "", f"text:{text}, error:{str(e)[:100]}")
                        # Fall back to generic swipe
                        self.swipe_up()
                else:
                    # For iOS, try finding element first
                    try:
                        element = self.driver.find_element(*text_locator)
                        # Text found in DOM, scroll to it
                        try:
                            self.logger.log_action("scrolling_to_text", "", f"text:{text}, attempt:{scroll_count}")
                            self.driver.execute_script("mobile: scrollToElement", {
                                'element': element,
                                'toVisible': True
                            })
                            return
                        except Exception as scroll_err:
                            # mobile: scrollToElement failed, use swipe
                            self.swipe_up()
                    except NoSuchElementException:
                        # Text not in DOM, swipe to load more content
                        self.swipe_up()
                
                # Wait after scroll for content to settle
                time.sleep(wait_after_scroll)
                
                # Check if text is now in DOM
                try:
                    element = WebDriverWait(self.driver, short_find_timeout).until(
                        EC.presence_of_element_located(text_locator)
                    )
                    # Text found in DOM, scroll to it
                    self.logger.log_action("text_found_after_scroll", "", f"text:{text}, scrolls:{scroll_count}")
                    self.driver.execute_script("mobile: scrollToElement", {
                        'element': element,
                        'toVisible': True
                    })
                    return
                except TimeoutException:
                    continue  # Text not found yet, continue scrolling
                
            # Timeout reached
            self.logger.log_action("text_not_found_after_timeout", "", f"text:{text}, scrolls:{scroll_count}")
            raise TimeoutException(f"Text '{text}' not found after {timeout}s and {scroll_count} scroll attempts")
            
        except Exception as e:
            self.logger.log_error(e, "scroll_to_text")
            raise    

    def scroll_to_coordinates(self, x: int, y: int, timeout: int = 30, 
                         wait_after_scroll: float = 0.5):
        """
        Scroll to specific coordinates on the screen.
        
        Args:
            x: Target x coordinate
            y: Target y coordinate
            timeout: Total maximum time in seconds
            wait_after_scroll: Wait time after each scroll in seconds
        """
        try:
            self.logger.log_action("scroll_to_coordinates_start", "", f"x:{x}, y:{y}")
            import time
            
            # Get current screen dimensions
            screen_size = self.driver.get_window_size()
            screen_width = screen_size['width']
            screen_height = screen_size['height']
            
            # Check if coordinates are within screen bounds
            if x < 0 or x > screen_width or y < 0 or y > screen_height:
                self.logger.log_action("coordinates_out_of_bounds", "", 
                                    f"target:({x},{y}) screen:({screen_width},{screen_height})")
                raise ValueError(f"Coordinates ({x},{y}) are outside screen bounds ({screen_width},{screen_height})")
            
            # Calculate center of screen as reference point
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # Try direct scroll using mobile: scrollGesture first
            try:
                self.logger.log_action("direct_scroll_gesture", "", f"to:({x},{y})")
                
                # Try platform-specific scroll command
                platform = self.driver.capabilities.get('platformName', '').lower()
                
                if platform == 'android':
                    # Android scrollGesture
                    result = self.driver.execute_script('mobile: scrollGesture', {
                        'left': center_x, 'top': center_y, 
                        'width': 10, 'height': 10,
                        'direction': 'down' if y > center_y else 'up',
                        'percent': min(abs(y - center_y) / screen_height, 0.8),
                        'speed': 2500
                    })
                    
                    if result:
                        self.logger.log_action("direct_scroll_success", "", f"to:({x},{y})")
                        return
                        
                elif platform == 'ios':
                    # iOS scrollGesture
                    result = self.driver.execute_script('mobile: scroll', {
                        'direction': 'down' if y > center_y else 'up',
                        'x': x, 'y': y
                    })
                    
                    if result:
                        self.logger.log_action("direct_scroll_success", "", f"to:({x},{y})")
                        return
                    
            except Exception as scroll_err:
                self.logger.log_action("direct_scroll_failed", "", f"error:{str(scroll_err)[:100]}")
                # Continue to fallback approach
            
            # Use a series of swipes to navigate to the coordinates
            self.logger.log_action("using_swipe_approach", "", f"to:({x},{y})")
            
            end_time = time.time() + timeout
            scroll_count = 0
            
            while time.time() < end_time:
                scroll_count += 1
                
                # Determine swipe direction based on target coordinates vs center
                if abs(y - center_y) > abs(x - center_x):
                    # Vertical scrolling needed more
                    if y < center_y:
                        # Swipe up to reach elements above
                        self.swipe_up()
                        self.logger.log_action("swipe_up_to_target", "", f"attempt:{scroll_count}")
                    else:
                        # Swipe down to reach elements below
                        self.swipe_down()
                        self.logger.log_action("swipe_down_to_target", "", f"attempt:{scroll_count}")
                else:
                    # Horizontal scrolling needed more
                    if x < center_x:
                        # Swipe left to reach elements to the right
                        self.swipe_left()
                        self.logger.log_action("swipe_left_to_target", "", f"attempt:{scroll_count}")
                    else:
                        # Swipe right to reach elements to the left
                        self.swipe_right()
                        self.logger.log_action("swipe_right_to_target", "", f"attempt:{scroll_count}")
                
                # Wait after scroll
                time.sleep(wait_after_scroll)
                
                # Check if we're close enough to the target
                # (This is a simple proximity check - could be improved with visual verification)
                if scroll_count >= 5:  # After a few scrolls, we assume we're close enough
                    self.logger.log_action("assumed_scroll_completion", "", f"scrolls:{scroll_count}")
                    break
                    
            self.logger.log_action("scroll_to_coordinates_complete", "", f"scrolls:{scroll_count}")
                
        except Exception as e:
            self.logger.log_error(e, "scroll_to_coordinates")
            raise
    
    def pinch_zoom(self, x: int, y: int, scale: float):
        """Pinch zoom at coordinates."""
        try:
            self.logger.log_action("pinch_zoom", "", f"x:{x}, y:{y}, scale:{scale}")
            # self.driver.execute_script("mobile: pinchOpen", {"x": x, "y": y, "scale": scale})                   
            # finger1 = PointerInput(POINTER_TOUCH, "finger1")
            # finger2 = PointerInput(POINTER_TOUCH, "finger2")
            
            # Complex gesture - tốt nhất dùng mobile: command nếu có
            self.driver.execute_script('mobile: pinchOpenGesture', {
                'x': x, 
                'y': y, 
                'percent': scale
            })
        except Exception as e:
            self.logger.log_error(e, "pinch_zoom")
            raise
    
    def drag_and_drop(self, source_locator: Union[Tuple[str, str], WebElement], target_locator: Union[Tuple[str, str], WebElement]):
        """Drag and drop element."""
        try:
            print("###########################################################################################")
            self.logger.log_action("drag_and_drop", f"{source_locator} -> {target_locator}")
            if isinstance(source_locator, tuple):
                source = self.driver.find_element(*source_locator)
            else:
                source = source_locator
            if isinstance(target_locator, tuple):
                target = self.driver.find_element(*target_locator)
            else:
                target = target_locator
            # TouchAction(self.driver).long_press(source).move_to(target).release().perform()
            actions = ActionBuilder(self.driver, mouse=PointerInput(POINTER_TOUCH, "touch"))
            actions.pointer_action.move_to(source)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(0.5)
            actions.pointer_action.move_to(target)
            actions.pointer_action.pointer_up()
            actions.perform()
        except Exception as e:
            self.logger.log_error(e, "drag_and_drop")
            raise
    
    def send_keys(self, locator: Union[Tuple[str, str], WebElement], text: str):
        """Send keys to element."""
        try:
            self.logger.log_action("send_keys", str(locator), text)
            if isinstance(locator, tuple):
                element = self.driver.find_element(*locator)
            else:
                element = locator
            element.send_keys(text)
        except Exception as e:
            self.logger.log_error(e, "send_keys")
            raise
    
    def clear_text(self, locator: Tuple[str, str]):
        """Clear text from element."""
        try:
            self.logger.log_action("clear_text", str(locator))
            element = self.driver.find_element(*locator)
            element.clear()
        except Exception as e:
            self.logger.log_error(e, "clear_text")
            raise
    
    def get_text(self, locator: Union[Tuple[str, str], WebElement]) -> str:
        """Get element text."""
        try:
            if isinstance(locator, tuple):
                element = self.driver.find_element(*locator)
            else:
                element = locator
            text = element.text
            self.logger.log_action("get_text", str(locator), text)
            return text
        except Exception as e:
            self.logger.log_error(e, "get_text")
            return ""
    
    def get_attribute(self, locator: Union[Tuple[str, str], WebElement], attribute: str) -> Optional[str]:
        """Get element attribute."""
        try:
            if isinstance(locator, tuple):
                element = self.driver.find_element(*locator)
            else:
                element = locator
            value = element.get_attribute(attribute)
            self.logger.log_action("get_attribute", f"{str(locator)}.{attribute}", value or "")
            return value
        except Exception as e:
            self.logger.log_error(e, "get_attribute")
            return None
    
    def is_displayed(self, locator: Tuple[str, str]) -> bool:
        """Check if element is displayed."""
        try:
            element = self.driver.find_element(*locator)
            displayed = element.get_attribute('displayed')
            self.logger.log_action("is_displayed", str(locator), str(displayed))
            return displayed
        except Exception as e:
            self.logger.log_error(e, "is_displayed")
            return False
    def is_visible(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> bool:
        """Check if element is visible."""
        try:
            # Use WebDriverWait with visibility_of_element_located - more reliable
            WebDriverWait(self.driver, timeout or self.default_timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception as e:
            self.logger.log_warning(e, "verify_element_visible")
            return False
    def is_present(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> bool:
        """Verify element exists in DOM (may not be visible)."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception as e:
            self.logger.log_warning(e, "verify_element_present")
            return False

    def is_enabled(self, locator: Tuple[str, str]) -> bool:
        """Check if element is enabled."""
        try:
            element = self.driver.find_element(*locator)
            enabled = element.is_enabled()
            self.logger.log_action("is_enabled", str(locator), str(enabled))
            return enabled
        except Exception as e:
            self.logger.log_error(e, "is_enabled")
            return False
    
    def is_selected(self, locator: Tuple[str, str]) -> bool:
        """Check if element is selected."""
        try:
            element = self.driver.find_element(*locator)
            selected = element.is_selected()
            self.logger.log_action("is_selected", str(locator), str(selected))
            return selected
        except Exception as e:
            self.logger.log_error(e, "is_selected")
            return False
    
    @retry_on_connection_error()
    def wait_for_element(self, locator: Tuple[str, str], timeout_default: int = 30):
        """Wait for element to be present."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("wait_for_element", str(locator))
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout_default)
            element = wait.until(EC.presence_of_element_located(locator))
            return element
        except Exception as e:
            self.logger.log_error(e, "wait_for_element")
            raise
    
    @retry_on_connection_error()
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = 30):
        """Wait for element to be visible."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("wait_for_element_visible", str(locator))
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            return element
        except Exception as e:
            self.logger.log_error(e, "wait_for_element_visible")
            raise
    
    @retry_on_connection_error()
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = 30):
        """Wait for element to be clickable."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("wait_for_element_clickable", str(locator))
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            return element
        except Exception as e:
            self.logger.log_error(e, "wait_for_element_clickable")
            raise
    
    def wait_for_text(self, text: str, timeout: int = 30):
        """Wait for text to appear."""
        try:
            self.logger.log_action("wait_for_text", "", text)
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, f"//*[@text='{text}']")))
            return element
        except Exception as e:
            self.logger.log_error(e, "wait_for_text")
            raise
    
    def hide_keyboard(self):
        """Hide keyboard."""
        try:
            self.logger.log_action("hide_keyboard")
            self.driver.hide_keyboard()
        except Exception as e:
            self.logger.log_error(e, "hide_keyboard")
            raise
    
    def is_keyboard_shown(self) -> bool:
        """Check if keyboard is shown."""
        try:
            shown = self.driver.is_keyboard_shown()
            self.logger.log_action("is_keyboard_shown", "", str(shown))
            return shown
        except Exception as e:
            self.logger.log_error(e, "is_keyboard_shown")
            return False
    
    def press_keycode(self, keycode: int):
        """Press keycode (Android only)."""
        try:
            if not self.is_android():
                self.logger.warning("press_keycode is Android-only")
                return
            self.logger.log_action("press_keycode", "", str(keycode))
            self.driver.press_keycode(keycode)
        except Exception as e:
            self.logger.log_error(e, "press_keycode")
            raise
    
    def long_press_keycode(self, keycode: int):
        """Long press keycode (Android only)."""
        try:
            if not self.is_android():
                self.logger.warning("long_press_keycode is Android-only")
                return
            self.logger.log_action("long_press_keycode", "", str(keycode))
            self.driver.long_press_keycode(keycode)
        except Exception as e:
            self.logger.log_error(e, "long_press_keycode")
            raise
    
    def take_screenshot(self, path: str = None) -> str:
        """Take screenshot."""
        try:
            if not path:
                path = f"reports/screenshots/mobile_{int(time.time())}.png"
            self.driver.save_screenshot(path)
            self.logger.log_screenshot(path)
            return path
        except Exception as e:
            self.logger.log_error(e, "take_screenshot")
            return ""
    
    def get_page_source(self) -> str:
        """Get page source."""
        try:
            source = self.driver.page_source
            self.logger.log_action("get_page_source", "", f"length:{len(source)}")
            return source
        except Exception as e:
            self.logger.log_error(e, "get_page_source")
            return ""
    
    def get_current_activity(self) -> str:
        """Get current activity (Android only)."""
        try:
            if not self.is_android():
                self.logger.warning("get_current_activity is Android-only")
                return ""
            activity = self.driver.current_activity
            self.logger.log_action("get_current_activity", "", activity)
            return activity
        except Exception as e:
            self.logger.log_error(e, "get_current_activity")
            return ""
    
    def get_current_package(self) -> str:
        """Get current package (Android only)."""
        try:
            if not self.is_android():
                self.logger.warning("get_current_package is Android-only")
                return ""
            package = self.driver.current_package
            self.logger.log_action("get_current_package", "", package)
            return package
        except Exception as e:
            self.logger.log_error(e, "get_current_package")
            return ""
    
    def get_current_context(self) -> str:
        """Get current context."""
        try:
            context = self.driver.current_context
            self.logger.log_action("get_current_context", "", context)
            return context
        except Exception as e:
            self.logger.log_error(e, "get_current_context")
            return ""
    
    def switch_to_context(self, context_name: str):
        """Switch to specific context."""
        try:
            self.logger.log_action("switch_to_context", "", context_name)
            self.driver.switch_to.context(context_name)
        except Exception as e:
            self.logger.log_error(e, "switch_to_context")
            raise
    
    def get_available_contexts(self) -> List[str]:
        """Get available contexts."""
        try:
            contexts = self.driver.contexts
            self.logger.log_action("get_available_contexts", "", str(len(contexts)))
            return contexts
        except Exception as e:
            self.logger.log_error(e, "get_available_contexts")
            return []
    
    def switch_to_native_context(self):
        """Switch to native context."""
        try:
            self.logger.log_action("switch_to_native_context")
            self.driver.switch_to.context("NATIVE_APP")
        except Exception as e:
            self.logger.log_error(e, "switch_to_native_context")
            raise
    
    def switch_to_webview_context(self):
        """Switch to webview context."""
        try:
            self.logger.log_action("switch_to_webview_context")
            contexts = self.get_available_contexts()
            for context in contexts:
                if "WEBVIEW" in context:
                    self.driver.switch_to.context(context)
                    break
        except Exception as e:
            self.logger.log_error(e, "switch_to_webview_context")
            raise
    
    def install_app(self, app_path: str):
        """Install app."""
        try:
            self.logger.log_action("install_app", "", app_path)
            self.driver.install_app(app_path)
        except Exception as e:
            self.logger.log_error(e, "install_app")
            raise
    
    def uninstall_app(self, package_name: str):
        """Uninstall app."""
        try:
            self.logger.log_action("uninstall_app", "", package_name)
            self.driver.remove_app(package_name)
        except Exception as e:
            self.logger.log_error(e, "uninstall_app")
            raise
    
    def launch_app(self, app_id: str):
        """Launch app."""
        try:
            self.logger.log_action("launch_app", "", app_id)
            self.driver.activate_app(app_id)
        except Exception as e:
            self.logger.log_error(e, "launch_app")
            raise
    
    def close_app(self, app_id: str = None):
        """Close app."""
        try:
            if app_id:
                self.logger.log_action("close app", "", app_id)
                self.driver.terminate_app(app_id)
                return
            package = self.driver.current_package
            self.logger.log_action("close current app", "", package)
            self.driver.terminate_app(package)
        except Exception as e:
            self.logger.log_error(e, "close_app")
            raise
    
    def reset_app(self):
        """Reset app with fallback (Android: clear data + relaunch)."""
        try:
            self.logger.log_action("reset_app")
            if hasattr(self.driver, 'reset'):
                return self.driver.reset()
            if self.is_android():
                try:
                    pkg = self.driver.current_package
                    try:
                        self.driver.terminate_app(pkg)
                    except Exception:
                        pass
                    self.driver.execute_script('mobile: shell', {
                        'command': 'pm', 'args': ['clear', pkg]
                    })
                    self.driver.activate_app(pkg)
                    self.logger.log_action("reset_app_android_fallback", "", pkg)
                    return
                except Exception as inner:
                    self.logger.log_error(inner, "reset_app_android_fallback")
            else:
                self.logger.warning("reset_app: limited on iOS without reinstall")
        except Exception as e:
            self.logger.log_error(e, "reset_app")
            raise
    
    def background_app(self, seconds: int):
        """Background app for specified seconds."""
        try:
            self.logger.log_action("background_app", "", str(seconds))
            self.driver.background_app(seconds)
        except Exception as e:
            self.logger.log_error(e, "background_app")
            raise
    
    def get_screen_size(self) -> Dict[str, int]:
        """Get screen size."""
        try:
            size = self.driver.get_window_size()
            self.logger.log_action("get_screen_size", "", f"{size['width']}x{size['height']}")
            return size
        except Exception as e:
            self.logger.log_error(e, "get_screen_size")
            return {"width": 0, "height": 0}
    
    def get_device_time(self) -> str:
        """Get device time."""
        try:
            device_time = self.driver.get_device_time()
            self.logger.log_action("get_device_time", "", device_time)
            return device_time
        except Exception as e:
            self.logger.log_error(e, "get_device_time")
            return ""
    
    def get_device_time_zone(self) -> str:
        """Get device time zone (platform-aware)."""
        try:
            if hasattr(self.driver, 'get_device_time_zone'):
                timezone = self.driver.get_device_time_zone()
                self.logger.log_action("get_device_time_zone", "", timezone)
                return timezone or "Unknown"
            if self.is_android():
                tz = self.driver.execute_script(
                    'mobile: shell',
                    {'command': 'getprop', 'args': ['persist.sys.timezone']}
                )
                tz = (tz or "").strip()
                self.logger.log_action("get_device_time_zone_android_fallback", "", tz)
                return tz or "Unknown"
            self.logger.warning("get_device_time_zone on iOS is limited; returning Unknown")
            return "Unknown"
        except Exception as e:
            self.logger.log_error(e, "get_device_time_zone")
            return "Unknown"
    
    def get_network_connection(self) -> int:
        """Get network connection type (legacy bitmask on Android)."""
        try:
            if hasattr(self.driver, 'get_network_connection'):
                connection = self.driver.network_connection
                self.logger.log_action("get_network_connection", "", str(connection))
                return connection
            if self.is_android():
                airplane = self.driver.execute_script('mobile: shell', {
                    'command': 'settings', 'args': ['get', 'global', 'airplane_mode_on']
                }).strip() == '1'
                wifi = self.driver.execute_script('mobile: shell', {
                    'command': 'settings', 'args': ['get', 'global', 'wifi_on']
                }).strip() == '1'
                data = self.driver.execute_script('mobile: shell', {
                    'command': 'settings', 'args': ['get', 'global', 'mobile_data']
                }).strip() == '1'
                value = (1 if airplane else 0) | (2 if wifi else 0) | (4 if data else 0)
                self.logger.log_action("get_network_connection_fallback", "", str(value))
                return value
            self.logger.warning("get_network_connection limited on iOS; returning 0")
            return 0
        except Exception as e:
            self.logger.log_error(e, "get_network_connection")
            return 0
    
    def set_network_connection(self, connection_type: int):
        """Set network connection (Android supports legacy bitmask)."""
        try:
            self.logger.log_action("set_network_connection", "", str(connection_type))
            if hasattr(self.driver, 'set_network_connection'):
                return self.driver.set_network_connection(connection_type)
            if self.is_android():
                airplane = bool(connection_type & 0x1)
                wifi = bool(connection_type & 0x2)
                data = bool(connection_type & 0x4)
                self.driver.execute_script('mobile: shell', {
                    'command': 'settings', 'args': ['put', 'global', 'airplane_mode_on', '1' if airplane else '0']
                })
                self.driver.execute_script('mobile: shell', {
                    'command': 'am', 'args': ['broadcast', '-a', 'android.intent.action.AIRPLANE_MODE']
                })
                if not airplane:
                    self.driver.execute_script('mobile: shell', {
                        'command': 'svc', 'args': ['wifi', 'enable' if wifi else 'disable']
                    })
                    self.driver.execute_script('mobile: shell', {
                        'command': 'svc', 'args': ['data', 'enable' if data else 'disable']
                    })
                return
            self.logger.warning("set_network_connection limited on iOS")
        except Exception as e:
            self.logger.log_error(e, "set_network_connection")
            raise
    
    def toggle_location_services(self):
        """Toggle location services (Android only)."""
        try:
            if not self.is_android():
                self.logger.warning("toggle_location_services is Android-only")
                return
            self.logger.log_action("toggle_location_services")
            self.driver.toggle_location_services()
        except Exception as e:
            self.logger.log_error(e, "toggle_location_services")
            raise
    
    def toggle_wifi(self):
        """Toggle WiFi."""
        try:
            self.logger.log_action("toggle_wifi")
            if hasattr(self.driver, 'toggle_wifi'):
                return self.driver.toggle_wifi()
            if self.is_android():
                try:
                    current = self.driver.execute_script('mobile: shell', {
                        'command': 'settings', 'args': ['get', 'global', 'wifi_on']
                    }).strip()
                    target = 'disable' if current == '1' else 'enable'
                    self.driver.execute_script('mobile: shell', {
                        'command': 'svc', 'args': ['wifi', target]
                    })
                    return
                except Exception as inner:
                    self.logger.log_error(inner, "toggle_wifi_android_fallback")
            self.logger.warning("Toggle WiFi on iOS is limited/not supported via Appium")
        except Exception as e:
            self.logger.log_error(e, "toggle_wifi")
            raise
    
    def toggle_data(self):
        """Toggle mobile data."""
        try:
            self.logger.log_action("toggle_data")
            if hasattr(self.driver, 'toggle_data'):
                return self.driver.toggle_data()
            if self.is_android():
                try:
                    current = self.driver.execute_script('mobile: shell', {
                        'command': 'settings', 'args': ['get', 'global', 'mobile_data']
                    }).strip()
                    target = 'disable' if current == '1' else 'enable'
                    self.driver.execute_script('mobile: shell', {
                        'command': 'svc', 'args': ['data', target]
                    })
                    return
                except Exception as inner:
                    self.logger.log_error(inner, "toggle_data_android_fallback")
            self.logger.warning("Toggle mobile data on iOS is limited/not supported via Appium")
        except Exception as e:
            self.logger.log_error(e, "toggle_data")
            raise
    
    def toggle_airplane_mode(self):
        """Toggle airplane mode."""
        try:
            self.logger.log_action("toggle_airplane_mode")
            if hasattr(self.driver, 'toggle_airplane_mode'):
                return self.driver.toggle_airplane_mode()
            if self.is_android():
                result = self.driver.execute_script('mobile: shell', {
                                'command': 'settings get global airplane_mode_on'
                            })    
                current_state = int(result.strip())
                new_state = 1 - current_state  # Toggle: 0->1 hoặc 1->0    
                # Bật/tắt
                self.driver.execute_script('mobile: shell', {
                    'command': f'settings put global airplane_mode_on {new_state}'
                })
            else:
                self.logger.warning("Toggle airplane mode on iOS is limited/not supported via Appium")
        except Exception as e:
            self.logger.log_error(e, "toggle_airplane_mode")
            raise
    
    def toggle_bluetooth(self):
        """Toggle Bluetooth."""
        try:
            self.logger.log_action("toggle_bluetooth")
            self.driver.toggle_bluetooth()
        except Exception as e:
            self.logger.log_error(e, "toggle_bluetooth")
            raise
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information."""
        try:
            battery_info = self.driver.execute_script('mobile: batteryInfo')
            self.logger.log_action("get_battery_info", "", str(battery_info))
            return battery_info
        except Exception as e:
            self.logger.log_error(e, "get_battery_info")
            return {}
    
    def get_performance_data(self, package_name: str, data_type: str) -> List[Dict[str, Any]]:
        """Get performance data."""
        try:
            performance_data = self.driver.get_performance_data(package_name, data_type)
            self.logger.log_action("get_performance_data", "", f"{package_name}.{data_type}")
            return performance_data
        except Exception as e:
            self.logger.log_error(e, "get_performance_data")
            return []
    
    def start_recording_screen(self, **options):
        """Start recording screen."""
        try:
            self.logger.log_action("start_recording_screen")
            self.driver.start_recording_screen(**options)
        except Exception as e:
            self.logger.log_error(e, "start_recording_screen")
            raise
    
    def stop_recording_screen(self) -> str:
        """Stop recording screen and return base64 data."""
        try:
            self.logger.log_action("stop_recording_screen")
            recording_data = self.driver.stop_recording_screen()
            return recording_data
        except Exception as e:
            self.logger.log_error(e, "stop_recording_screen")
            return ""
    
    def shake_device(self):
        """Shake device (iOS only)."""
        try:
            if not self.is_ios():
                self.logger.warning("shake_device is iOS-only")
                return
            self.logger.log_action("shake_device")
            self.driver.shake()
        except Exception as e:
            self.logger.log_error(e, "shake_device")
            raise
    
    def lock_device(self, seconds: int):
        """Lock device for specified seconds."""
        try:
            self.logger.log_action("lock_device", "", str(seconds))
            self.driver.lock(seconds)
        except Exception as e:
            self.logger.log_error(e, "lock_device")
            raise
    
    def unlock_device(self):
        """Unlock device."""
        try:
            self.logger.log_action("unlock_device")
            self.driver.unlock()
        except Exception as e:
            self.logger.log_error(e, "unlock_device")
            raise
    
    def is_device_locked(self) -> bool:
        """Check if device is locked."""
        try:
            locked = self.driver.is_locked()
            self.logger.log_action("is_device_locked", "", str(locked))
            return locked
        except Exception as e:
            self.logger.log_error(e, "is_device_locked")
            return False
    
    def rotate_device(self, orientation: str):
        """Rotate device to specified orientation."""
        try:
            self.logger.log_action("rotate_device", "", orientation)
            self.driver.orientation = orientation
        except Exception as e:
            self.logger.log_error(e, "rotate_device")
            raise
    
    def get_device_orientation(self) -> str:
        """Get device orientation."""
        try:
            orientation = self.driver.orientation
            self.logger.log_action("get_device_orientation", "", orientation)
            return orientation
        except Exception as e:
            self.logger.log_error(e, "get_device_orientation")
            return ""
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript on page."""
        try:
            self.logger.log_action("execute_script", "", script)
            result = self.driver.execute_script(script, *args)
            return result
        except Exception as e:
            self.logger.log_error(e, "execute_script")
            raise
    
    @retry_on_connection_error()
    def find_element_by_id(self, element_id: str):
        """Find element by ID."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("find_element_by_id", "", element_id)
            element = self.driver.find_element(AppiumBy.ID, element_id)
            return element
        except Exception as e:
            self.logger.log_error(e, "find_element_by_id")
            raise
    
    @retry_on_connection_error()
    def find_element_by_xpath(self, xpath: str):
        """Find element by XPath."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("find_element_by_xpath", "", xpath)
            element = self.driver.find_element(AppiumBy.XPATH, xpath)
            return element
        except Exception as e:
            self.logger.log_error(e, "find_element_by_xpath")
            raise
    
    @retry_on_connection_error()
    def find_element_by_class_name(self, class_name: str):
        """Find element by class name."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("find_element_by_class_name", "", class_name)
            element = self.driver.find_element(AppiumBy.CLASS_NAME, class_name)
            return element
        except Exception as e:
            self.logger.log_error(e, "find_element_by_class_name")
            raise
    
    @retry_on_connection_error()
    def find_element_by_accessibility_id(self, accessibility_id: str):
        """Find element by accessibility ID."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("find_element_by_accessibility_id", "", accessibility_id)
            element = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_id)
            return element
        except Exception as e:
            self.logger.log_error(e, "find_element_by_accessibility_id")
            raise
    
    @retry_on_connection_error()
    def find_element_by_text(self, text: str):
        """Find element by text."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("find_element_by_text", "", text)
            element = self.driver.find_element(AppiumBy.XPATH, f"//*[@text='{text}']")
            return element
        except Exception as e:
            self.logger.log_error(e, "find_element_by_text")
            raise
    
    @retry_on_connection_error()
    def find_element_by_partial_text(self, partial_text: str):
        """Find element by partial text."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("find_element_by_partial_text", "", partial_text)
            element = self.driver.find_element(AppiumBy.XPATH, f"//*[contains(@text,'{partial_text}')]")
            return element
        except Exception as e:
            self.logger.log_error(e, "find_element_by_partial_text")
            raise
    
    @retry_on_connection_error()
    def find_elements(self, locator: Tuple[str, str]) -> List:
        """Find multiple elements by locator."""
        try:
            # Check driver health before operation
            if not check_driver_health(self.driver):
                self.logger.warning("[RETRY] Driver session appears unhealthy, attempting operation anyway...")
            
            self.logger.log_action("find_elements", str(locator))
            elements = self.driver.find_elements(*locator)
            self.logger.log_action("find_elements_result", str(locator), str(len(elements)))
            return elements
        except Exception as e:
            self.logger.log_error(e, "find_elements")
            return []
    
    def count_elements(self, locator: Tuple[str, str]) -> int:
        """Count elements matching locator."""
        try:
            elements = self.find_elements(locator)
            count = len(elements)
            self.logger.log_action("count_elements", str(locator), str(count))
            return count
        except Exception as e:
            self.logger.log_error(e, "count_elements")
            return 0
