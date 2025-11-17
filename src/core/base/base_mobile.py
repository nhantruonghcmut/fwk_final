"""
Base class for mobile application page objects using Appium 3.x.

Design guideline:
- Keep ONLY app/device-level helpers here (launch/close/reset app, device state, context...).
- Provide element helper get_element(s) returning ElementObject for element-level actions.
- Delegate ANY element interactions and generic locator-based utilities to MobileActions/ElementObject.
"""
import time
from typing import Optional, List, Dict, Any, Tuple
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.core.base.base_test import BaseTest
from src.core.utils.mobile_action import MobileActions
from src.core.utils.element_object import ElementObject
from src.core.utils.report_logger import ReportLogger
from src.core.utils.screenshot_util import ScreenshotResult, ScreenshotUtil
from src.core.utils.allure_step import step_decorator





class BaseMobile(BaseTest):
    """Base class for mobile page objects."""
    
    def __init__(self, driver: webdriver.Remote):
        super().__init__()
        self.driver = driver
        self.test_context = getattr(driver, "test_context", None)
        self.mobile_actions = MobileActions(driver)
        self.logger = getattr(driver, "logger", ReportLogger())
        self.screenshot_util = getattr(driver, "screenshot_util", ScreenshotUtil(logger=self.logger))
        # Get default timeout from driver (set in conftest with correct env/platform config)
        self.default_timeout = getattr(driver, "default_timeout", 30)  # seconds
        self.element_timeout = getattr(driver, "element_timeout", 15)  # seconds
        
        # Khởi tạo Verification sau khi đã có logger
        self._init_verification(self.logger) 

    # ----------------- Element helpers (return ElementObject) -----------------
    @step_decorator("Get element")
    def get_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> ElementObject:
        """
        Get element by locator tuple (strategy, value) - wait until present.
        
        Note: No retry wrapper here - WebDriverWait already handles timeouts.
        Retry should only be used for actual connection errors, not for element finding.
        """
        element = WebDriverWait(self.driver, timeout or self.default_timeout).until(
            EC.presence_of_element_located(locator)
        )
        return ElementObject(element, self.driver)
        
    @step_decorator("Get elements")
    def get_elements(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> List[ElementObject]:
        """
        Get multiple elements by locator tuple - wait until at least one present.
        
        Note: No retry wrapper here - WebDriverWait already handles timeouts.
        """
        WebDriverWait(self.driver, timeout or self.default_timeout).until(
            EC.presence_of_all_elements_located(locator)
        )
        elements = self.driver.find_elements(*locator)
        return [ElementObject(element, self.driver) for element in elements]
    
    @step_decorator("Find element by ID: {element_id}", attach_params=False)
    def find_element_by_id(self, element_id: str, timeout: Optional[int] = None) -> ElementObject:
        """Find element by ID - wait until present."""
        try:
            locator = (AppiumBy.ID, element_id)
            element = WebDriverWait(self.driver, timeout or self.default_timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.info(f"Found element by ID: {element_id}")
            return ElementObject(element, self.driver)
        except Exception as e:
            self.logger.error(f"Failed to find element by ID: {element_id}. Error: {str(e)}")
            raise

    @step_decorator("Find element by XPath: {xpath}", attach_params=False)
    def find_element_by_xpath(self, xpath: str, timeout: Optional[int] = None) -> ElementObject:
        """Find element by XPath - wait until present."""
        try:
            locator = (AppiumBy.XPATH, xpath)
            element = WebDriverWait(self.driver, timeout or self.default_timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.info(f"Found element by XPath: {xpath}")
            return ElementObject(element, self.driver)
        except Exception as e:
            self.logger.error(f"Failed to find element by XPath: {xpath}. Error: {str(e)}")
            raise
    
    @step_decorator("Find element by class name: {class_name}", attach_params=False)
    def find_element_by_class_name(self, class_name: str, timeout: Optional[int] = None) -> ElementObject:
        """Find element by class name - wait until present."""
        try:
            locator = (AppiumBy.CLASS_NAME, class_name)
            element = WebDriverWait(self.driver, timeout or self.default_timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.info(f"Found element by class name: {class_name}")
            return ElementObject(element, self.driver)
        except Exception as e:
            self.logger.error(f"Failed to find element by class name: {class_name}. Error: {str(e)}")
            raise

    @step_decorator("Find element by accessibility ID: {accessibility_id}", attach_params=False)
    def find_element_by_accessibility_id(self, accessibility_id: str, timeout: Optional[int] = None) -> ElementObject:
        """Find element by accessibility ID - wait until present."""
        try:
            locator = (AppiumBy.ACCESSIBILITY_ID, accessibility_id)
            element = WebDriverWait(self.driver, timeout or self.default_timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.info(f"Found element by accessibility ID: {accessibility_id}")
            return ElementObject(element, self.driver)
        except Exception as e:
            self.logger.error(f"Failed to find element by accessibility ID: {accessibility_id}. Error: {str(e)}")
            raise

    @step_decorator("Find element by text: {text}", attach_params=False)
    def find_element_by_text(self, text: str, timeout: Optional[int] = None) -> ElementObject:
        """Find element by exact text - wait until present."""
        try:
            xpath = f'//*[@text="{text}"]'
            locator = (AppiumBy.XPATH, xpath)
            element = WebDriverWait(self.driver, timeout or self.default_timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.info(f"Found element by text: {text}")
            return ElementObject(element, self.driver)
        except Exception as e:
            self.logger.error(f"Failed to find element by text: {text}. Error: {str(e)}")
            raise
    
    @step_decorator("Find element by partial text: {partial_text}", attach_params=False)
    def find_element_by_partial_text(self, partial_text: str, timeout: Optional[int] = None) -> ElementObject:
        """Find element by partial text - wait until present."""
        try:
            xpath = f'//*[contains(@text, "{partial_text}")]'
            locator = (AppiumBy.XPATH, xpath)
            element = WebDriverWait(self.driver, timeout or self.default_timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.info(f"Found element by partial text: {partial_text}")
            return ElementObject(element, self.driver)
        except Exception as e:
            self.logger.error(f"Failed to find element by partial text: {partial_text}. Error: {str(e)}")
            raise

    def wait_for_element(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        element = self.mobile_actions.wait_for_element(locator, timeout or self.default_timeout)
        return ElementObject(element,self.driver)
        
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        element = self.mobile_actions.wait_for_element_visible(locator, timeout or self.default_timeout)
        return ElementObject(element,self.driver)
        
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        element = self.mobile_actions.wait_for_element_clickable(locator, timeout or self.default_timeout)
        return ElementObject(element,self.driver)
        
    def take_screenshot(self, name: str = None) ->ScreenshotResult:
        """Take screenshot (device-level)."""
        test_context = getattr(self, 'test_context', None) or getattr(self.driver, 'test_context', None)
        # self.logger.info(f" ^^^^^^^^^^^^^^^^^ Taking screenshot with test_context: {test_context}")
        return self.screenshot_util.take_mobile_screenshot(driver=self.driver,name=name,test_context=test_context)
        
    def get_page_source(self) -> str:
        return self.mobile_actions.get_page_source()
        
    def get_current_activity(self) -> str:
        return self.mobile_actions.get_current_activity()
        
    def get_current_package(self) -> str:
        return self.mobile_actions.get_current_package()
        
    def get_current_context(self) -> str:
        return self.mobile_actions.get_current_context()
        
    def switch_to_context(self, context_name: str):
        self.mobile_actions.switch_to_context(context_name)
        
    def get_available_contexts(self) -> List[str]:
        return self.mobile_actions.get_available_contexts()
        
    def switch_to_native_context(self):
        self.mobile_actions.switch_to_native_context()
        
    def switch_to_webview_context(self):
        self.mobile_actions.switch_to_webview_context()
                
    def install_app(self, app_path: str):
        self.mobile_actions.install_app(app_path)
        
    def uninstall_app(self, package_name: str):
        self.mobile_actions.uninstall_app(package_name)
        
    def launch_app(self, app_id: str):
        self.mobile_actions.launch_app(app_id)
    
    def close_app(self, app_id: Optional[str] = None):
        self.mobile_actions.close_app(app_id)       
        
    def reset_app(self):
        self.mobile_actions.reset_app()
        
    def background_app(self, seconds: int):
        self.mobile_actions.background_app(seconds)
        
    def hide_keyboard(self):
        self.mobile_actions.hide_keyboard()
        
    def is_keyboard_shown(self) -> bool:
        return self.mobile_actions.is_keyboard_shown()
        
    def press_keycode(self, keycode: int):
        self.mobile_actions.press_keycode(keycode)
        
    def long_press_keycode(self, keycode: int):
        self.mobile_actions.long_press_keycode(keycode)
        
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000):
        self.mobile_actions.swipe(start_x, start_y, end_x, end_y, duration)
        
    def swipe_up(self, duration: int = 1000):
        self.mobile_actions.swipe_up(duration)
        
    def swipe_down(self, duration: int = 1000):
        self.mobile_actions.swipe_down(duration)
        
    def swipe_left(self, duration: int = 1000):
        self.mobile_actions.swipe_left(duration)
        
    def swipe_right(self, duration: int = 1000):
        self.mobile_actions.swipe_right(duration)
        
    def scroll_to_element(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        self.mobile_actions.scroll_to_element(locator, timeout or self.default_timeout)
        
    def scroll_to_text(self, text: str, timeout: Optional[int] = None):
        self.mobile_actions.scroll_to_text(text, timeout or self.default_timeout)
        
    def scroll_to_coordinates(self, x: int, y: int, timeout: Optional[int] = None):
        self.mobile_actions.scroll_to_coordinates(x, y, timeout or self.default_timeout)

    def pinch_zoom(self, x: int, y: int, scale: float):
        self.mobile_actions.pinch_zoom(x, y, scale)
        
    def tap_element(self, locator: Tuple[str, str]):
        elementO = self.get_element(locator)
        self.mobile_actions.tap(elementO.element)
        
    def long_press_element(self, locator: Tuple[str, str], duration: int = 2000):
        elementO = self.get_element(locator)
        self.mobile_actions.long_press(elementO.element, duration)
        
    def double_tap_element(self, locator: Tuple[str, str]):
        elementO = self.get_element(locator)
        self.mobile_actions.double_tap(elementO.element)
        
    def tap_coordinates(self, x: int, y: int):
        self.mobile_actions.tap_coordinates(x, y)
        
    def long_press_coordinates(self, x: int, y: int, duration: int = 2000):
        self.mobile_actions.long_press_coordinates(x, y, duration)
        
    def drag_and_drop(self, source_locator: Tuple[str, str], target_locator: Tuple[str, str]):
        sourceO = self.get_element(source_locator)
        targetO = self.get_element(target_locator)
        self.mobile_actions.drag_and_drop(sourceO.element, targetO.element)

    def verify_element_present(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> bool:
        try:
            return self.mobile_actions.is_present(locator, timeout or self.default_timeout)
        except:
            return False

    def verify_element_visible(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> bool:
        return self.mobile_actions.is_visible(locator, timeout or self.default_timeout)

    def send_keys(self, locator: Tuple[str, str], text: str):
        elementO = self.get_element(locator)
        self.mobile_actions.send_keys(elementO.element, text)

    def verify_text_present(self, text: str) -> bool:
        try:
            self.mobile_actions.find_element_by_text(text)
            return True
        except:
            return False
            
    def get_element_text(self, locator: Tuple[str, str]) -> str:
        return self.mobile_actions.get_text(locator)
        
    def get_element_attribute(self, locator: Tuple[str, str], attribute: str) -> str:
        value = self.mobile_actions.get_attribute(locator, attribute)
        return value if value is not None else ""
        
    def get_element_count(self, locator: Tuple[str, str]) -> int:
        return self.mobile_actions.count_elements(locator)
        
    def get_screen_size(self) -> Dict[str, int]:
        return self.mobile_actions.get_screen_size()
        
    def get_device_time(self) -> str:
        return self.mobile_actions.get_device_time()
        
    def get_device_time_zone(self) -> str:
        return self.mobile_actions.get_device_time_zone()

    def get_network_connection(self) -> Dict[str, bool]:
        # For simplicity, delegate to MobileActions implementation
        # If MobileActions returns int, adapt to dict format as needed
        connection = self.mobile_actions.get_network_connection()
        if isinstance(connection, int):
            return {
                'airplane_mode': bool(connection & 0x1),
                'wifi': bool(connection & 0x2),
                'data': bool(connection & 0x4)
            }
        return connection

    def set_network_connection(self, connection_type: int):
        self.mobile_actions.set_network_connection(connection_type)
        
    def toggle_location_services(self):
        self.mobile_actions.toggle_location_services()
        
    def toggle_wifi(self):
        self.mobile_actions.toggle_wifi()
        
    def toggle_data(self):
        self.mobile_actions.toggle_data()
        
    def toggle_airplane_mode(self):
        self.mobile_actions.toggle_airplane_mode()
        
       
    def get_battery_info(self) -> Dict[str, Any]:
        return self.mobile_actions.get_battery_info()
        
    def get_performance_data(self, package_name: str, data_type: str) -> List[Dict[str, Any]]:
        return self.mobile_actions.get_performance_data(package_name, data_type)
        
    def start_recording_screen(self, **options):
        self.mobile_actions.start_recording_screen(**options)
        
    def stop_recording_screen(self) -> str:
        return self.mobile_actions.stop_recording_screen()
        
    def shake_device(self):
        self.mobile_actions.shake_device()
        
    def lock_device(self, seconds: int):
        self.mobile_actions.lock_device(seconds)
        
    def unlock_device(self):
        self.mobile_actions.unlock_device()
        
    def is_device_locked(self) -> bool:
        return self.mobile_actions.is_device_locked()
        
    def rotate_device(self, orientation: str):
        self.mobile_actions.rotate_device(orientation)
        
    def get_device_orientation(self) -> str:
        return self.mobile_actions.get_device_orientation()
