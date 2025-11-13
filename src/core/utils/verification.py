"""
Verification utility for test assertions and validations.
"""
from typing import Any, Optional, List, Dict
from src.core.utils.report_logger import ReportLogger


class Verification:
    """Utility class for test verifications and assertions."""
    
    def __init__(self):
        self.logger = ReportLogger()
        
    def verify_equals(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Verify that actual equals expected."""
        try:
            result = actual == expected
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Equals verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Expected '{expected}', got '{actual}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_equals")
            return False
            
    def verify_not_equals(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Verify that actual does not equal expected."""
        try:
            result = actual != expected
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Not equals verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Values should not be equal, both are '{actual}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_not_equals")
            return False
            
    def verify_contains(self, container: Any, item: Any, message: str = "") -> bool:
        """Verify that container contains item."""
        try:
            result = item in container
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Contains verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: '{item}' not found in '{container}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_contains")
            return False
            
    def verify_not_contains(self, container: Any, item: Any, message: str = "") -> bool:
        """Verify that container does not contain item."""
        try:
            result = item not in container
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Not contains verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: '{item}' found in '{container}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_not_contains")
            return False
            
    def verify_true(self, condition: bool, message: str = "") -> bool:
        """Verify that condition is True."""
        try:
            result = bool(condition)
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'True verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Condition is False")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_true")
            return False
            
    def verify_false(self, condition: bool, message: str = "") -> bool:
        """Verify that condition is False."""
        try:
            result = not bool(condition)
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'False verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Condition is True")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_false")
            return False
            
    def verify_greater_than(self, actual: float, expected: float, message: str = "") -> bool:
        """Verify that actual is greater than expected."""
        try:
            result = actual > expected
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Greater than verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: {actual} is not greater than {expected}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_greater_than")
            return False
            
    def verify_less_than(self, actual: float, expected: float, message: str = "") -> bool:
        """Verify that actual is less than expected."""
        try:
            result = actual < expected
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Less than verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: {actual} is not less than {expected}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_less_than")
            return False
            
    def verify_greater_equal(self, actual: float, expected: float, message: str = "") -> bool:
        """Verify that actual is greater than or equal to expected."""
        try:
            result = actual >= expected
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Greater equal verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: {actual} is not greater than or equal to {expected}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_greater_equal")
            return False
            
    def verify_less_equal(self, actual: float, expected: float, message: str = "") -> bool:
        """Verify that actual is less than or equal to expected."""
        try:
            result = actual <= expected
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Less equal verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: {actual} is not less than or equal to {expected}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_less_equal")
            return False
            
    def verify_not_none(self, value: Any, message: str = "") -> bool:
        """Verify that value is not None."""
        try:
            result = value is not None
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Not None verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Value is None")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_not_none")
            return False
            
    def verify_none(self, value: Any, message: str = "") -> bool:
        """Verify that value is None."""
        try:
            result = value is None
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'None verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Value is not None, got '{value}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_none")
            return False
            
    def verify_not_empty(self, value: Any, message: str = "") -> bool:
        """Verify that value is not empty."""
        try:
            if hasattr(value, '__len__'):
                result = len(value) > 0
            else:
                result = bool(value)
                
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Not empty verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Value is empty")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_not_empty")
            return False
            
    def verify_empty(self, value: Any, message: str = "") -> bool:
        """Verify that value is empty."""
        try:
            if hasattr(value, '__len__'):
                result = len(value) == 0
            else:
                result = not bool(value)
                
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Empty verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Value is not empty")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_empty")
            return False
            
    def verify_regex_match(self, text: str, pattern: str, message: str = "") -> bool:
        """Verify that text matches regex pattern."""
        try:
            import re
            result = bool(re.search(pattern, text))
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Regex match verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Text '{text}' does not match pattern '{pattern}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_regex_match")
            return False
            
    def verify_regex_not_match(self, text: str, pattern: str, message: str = "") -> bool:
        """Verify that text does not match regex pattern."""
        try:
            import re
            result = not bool(re.search(pattern, text))
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Regex not match verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Text '{text}' matches pattern '{pattern}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_regex_not_match")
            return False
            
    def verify_list_equals(self, actual_list: List[Any], expected_list: List[Any], message: str = "") -> bool:
        """Verify that two lists are equal."""
        try:
            result = actual_list == expected_list
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'List equals verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Lists are not equal")
                self.logger.error(f"Expected: {expected_list}")
                self.logger.error(f"Actual: {actual_list}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_list_equals")
            return False
            
    def verify_dict_equals(self, actual_dict: Dict[str, Any], expected_dict: Dict[str, Any], message: str = "") -> bool:
        """Verify that two dictionaries are equal."""
        try:
            result = actual_dict == expected_dict
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Dict equals verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Dictionaries are not equal")
                self.logger.error(f"Expected: {expected_dict}")
                self.logger.error(f"Actual: {actual_dict}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_dict_equals")
            return False
            
    def verify_dict_contains(self, actual_dict: Dict[str, Any], expected_dict: Dict[str, Any], message: str = "") -> bool:
        """Verify that actual dictionary contains all keys and values from expected dictionary."""
        try:
            result = all(actual_dict.get(key) == value for key, value in expected_dict.items())
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Dict contains verification'}", result)
            
            if not result:
                missing_items = {k: v for k, v in expected_dict.items() if actual_dict.get(k) != v}
                self.logger.error(f"Verification failed: Dictionary does not contain expected items: {missing_items}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_dict_contains")
            return False
            
    def verify_exception_raised(self, func, *args, exception_type: type = Exception, message: str = "", **kwargs) -> bool:
        """Verify that function raises expected exception."""
        try:
            func(*args, **kwargs)
            self.logger.error(f"Verification failed: Expected {exception_type.__name__} was not raised")
            return False
        except exception_type:
            self.logger.log_verification(f"{message or 'Exception raised verification'}", True)
            return True
        except Exception as e:
            self.logger.error(f"Verification failed: Expected {exception_type.__name__}, got {type(e).__name__}")
            return False
            
    def verify_no_exception(self, func, *args, message: str = "", **kwargs) -> bool:
        """Verify that function does not raise any exception."""
        try:
            func(*args, **kwargs)
            self.logger.log_verification(f"{message or 'No exception verification'}", True)
            return True
        except Exception as e:
            self.logger.error(f"Verification failed: Unexpected exception {type(e).__name__}: {str(e)}")
            return False
            
    def verify_within_range(self, value: float, min_val: float, max_val: float, message: str = "") -> bool:
        """Verify that value is within specified range."""
        try:
            result = min_val <= value <= max_val
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Within range verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: {value} is not within range [{min_val}, {max_val}]")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_within_range")
            return False
            
    def verify_string_starts_with(self, text: str, prefix: str, message: str = "") -> bool:
        """Verify that string starts with prefix."""
        try:
            result = text.startswith(prefix)
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Starts with verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: '{text}' does not start with '{prefix}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_string_starts_with")
            return False
            
    def verify_string_ends_with(self, text: str, suffix: str, message: str = "") -> bool:
        """Verify that string ends with suffix."""
        try:
            result = text.endswith(suffix)
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Ends with verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: '{text}' does not end with '{suffix}'")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_string_ends_with")
            return False
            
    def verify_string_length(self, text: str, expected_length: int, message: str = "") -> bool:
        """Verify that string has expected length."""
        try:
            result = len(text) == expected_length
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'String length verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Expected length {expected_length}, got {len(text)}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_string_length")
            return False
            
    def verify_list_length(self, actual_list: List[Any], expected_length: int, message: str = "") -> bool:
        """Verify that list has expected length."""
        try:
            result = len(actual_list) == expected_length
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'List length verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Expected length {expected_length}, got {len(actual_list)}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_list_length")
            return False
            
    def verify_dict_length(self, actual_dict: Dict[str, Any], expected_length: int, message: str = "") -> bool:
        """Verify that dictionary has expected length."""
        try:
            result = len(actual_dict) == expected_length
            status = "PASSED" if result else "FAILED"
            self.logger.log_verification(f"{message or 'Dict length verification'}", result)
            
            if not result:
                self.logger.error(f"Verification failed: Expected length {expected_length}, got {len(actual_dict)}")
                
            return result
        except Exception as e:
            self.logger.log_error(e, "verify_dict_length")
            return False
