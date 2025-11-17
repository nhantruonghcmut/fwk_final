"""
Verification utility for test assertions and validations.
"""
from typing import Any, Optional, List, Dict
from src.core.utils.report_logger import ReportLogger

try:
    import allure
except ImportError:  # pragma: no cover - allure might be optional
    allure = None


class Verification:
    """Utility class for test verifications and assertions."""
    
    def __init__(self, logger: Optional[ReportLogger] = None):
        """
        Initialize Verification with logger.
        
        Args:
            logger: ReportLogger instance. If None, will use singleton instance.
        """
        # Sử dụng logger được truyền vào, hoặc fallback về singleton
        self.logger = logger or ReportLogger()
    
    def _attach_verification_details(self, expected: Any, actual: Any, result: bool, 
                                     error_msg: Optional[str] = None):
        """Attach verification details to Allure report."""
        try:
            if allure is None:
                return
            
            verification_details = f"""
            Expected: {expected}
            Actual: {actual}
            Result: {'PASSED' if result else 'FAILED'}
            """
            allure.attach(
                verification_details,
                name="Verification Details",
                attachment_type=allure.attachment_type.TEXT
            )
            
            if error_msg:
                allure.attach(
                    error_msg,
                    name="Error Message",
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception:
            # Ignore errors in attachment
            pass
    
    def verify_equals(self, actual: Any, expected: Any, message: str = "", 
                     step_name: str = None, create_allure_step: bool = False,
                     raise_on_fail: bool = True) -> bool:
        """
        Verify that actual equals expected.
        
        Args:
            actual: Actual value
            expected: Expected value
            message: Verification message for logging
            step_name: Name for Allure step (if create_allure_step=True)
            create_allure_step: If True, creates Allure step. If False (default), 
                               only attaches to current step or logs.
            raise_on_fail: If True, raises AssertionError on failure
            
        Returns:
            bool: True if verification passes
        """
        step_name = step_name or message or "Verify equals"
        
        def _do_verify():
            result = actual == expected
            status = "PASSED" if result else "FAILED"
            
            # Log verification
            self.logger.log_verification(f"{message or 'Equals verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Expected '{expected}', got '{actual}'"
                self.logger.error(error_msg)
            
            # Attach details to Allure
            self._attach_verification_details(expected, actual, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Expected '{expected}', got '{actual}'")
            
            return result
        
        # Tạo Allure step nếu được yêu cầu
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        # Không tạo step, chỉ verify và attach
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_equals")
            if raise_on_fail:
                raise
            return False
            
    def verify_not_equals(self, actual: Any, expected: Any, message: str = "",
                         step_name: str = None, create_allure_step: bool = False,
                         raise_on_fail: bool = True) -> bool:
        """Verify that actual does not equal expected."""
        step_name = step_name or message or "Verify not equals"
        
        def _do_verify():
            result = actual != expected
            self.logger.log_verification(f"{message or 'Not equals verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Values should not be equal, both are '{actual}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected, actual, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Values should not be equal")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_not_equals")
            if raise_on_fail:
                raise
            return False
            
    def verify_contains(self, container: Any, item: Any, message: str = "",
                       step_name: str = None, create_allure_step: bool = False,
                       raise_on_fail: bool = True) -> bool:
        """Verify that container contains item."""
        step_name = step_name or message or "Verify contains"
        
        def _do_verify():
            result = item in container
            self.logger.log_verification(f"{message or 'Contains verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: '{item}' not found in '{container}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(item, container, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: '{item}' not found in '{container}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_contains")
            if raise_on_fail:
                raise
            return False
            
    def verify_not_contains(self, container: Any, item: Any, message: str = "",
                           step_name: str = None, create_allure_step: bool = False,
                           raise_on_fail: bool = True) -> bool:
        """Verify that container does not contain item."""
        step_name = step_name or message or "Verify not contains"
        
        def _do_verify():
            result = item not in container
            self.logger.log_verification(f"{message or 'Not contains verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: '{item}' found in '{container}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(item, container, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: '{item}' found in '{container}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_not_contains")
            if raise_on_fail:
                raise
            return False
            
    def verify_true(self, condition: bool, message: str = "",
                   step_name: str = None, create_allure_step: bool = False,
                   raise_on_fail: bool = True) -> bool:
        """Verify that condition is True."""
        step_name = step_name or message or "Verify true"
        
        def _do_verify():
            result = bool(condition)
            self.logger.log_verification(f"{message or 'True verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = "Verification failed: Condition is False"
                self.logger.error(error_msg)
            
            self._attach_verification_details(True, condition, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Condition is False")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_true")
            if raise_on_fail:
                raise
            return False
            
    def verify_false(self, condition: bool, message: str = "",
                    step_name: str = None, create_allure_step: bool = False,
                    raise_on_fail: bool = True) -> bool:
        """Verify that condition is False."""
        step_name = step_name or message or "Verify false"
        
        def _do_verify():
            result = not bool(condition)
            self.logger.log_verification(f"{message or 'False verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = "Verification failed: Condition is True"
                self.logger.error(error_msg)
            
            self._attach_verification_details(False, condition, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Condition is True")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_false")
            if raise_on_fail:
                raise
            return False
            
    def verify_greater_than(self, actual: float, expected: float, message: str = "",
                           step_name: str = None, create_allure_step: bool = False,
                           raise_on_fail: bool = True) -> bool:
        """Verify that actual is greater than expected."""
        step_name = step_name or message or "Verify greater than"
        
        def _do_verify():
            result = actual > expected
            self.logger.log_verification(f"{message or 'Greater than verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: {actual} is not greater than {expected}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected, actual, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: {actual} is not greater than {expected}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_greater_than")
            if raise_on_fail:
                raise
            return False
            
    def verify_less_than(self, actual: float, expected: float, message: str = "",
                        step_name: str = None, create_allure_step: bool = False,
                        raise_on_fail: bool = True) -> bool:
        """Verify that actual is less than expected."""
        step_name = step_name or message or "Verify less than"
        
        def _do_verify():
            result = actual < expected
            self.logger.log_verification(f"{message or 'Less than verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: {actual} is not less than {expected}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected, actual, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: {actual} is not less than {expected}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_less_than")
            if raise_on_fail:
                raise
            return False
            
    def verify_greater_equal(self, actual: float, expected: float, message: str = "",
                            step_name: str = None, create_allure_step: bool = False,
                            raise_on_fail: bool = True) -> bool:
        """Verify that actual is greater than or equal to expected."""
        step_name = step_name or message or "Verify greater equal"
        
        def _do_verify():
            result = actual >= expected
            self.logger.log_verification(f"{message or 'Greater equal verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: {actual} is not greater than or equal to {expected}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected, actual, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: {actual} is not greater than or equal to {expected}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_greater_equal")
            if raise_on_fail:
                raise
            return False
            
    def verify_less_equal(self, actual: float, expected: float, message: str = "",
                         step_name: str = None, create_allure_step: bool = False,
                         raise_on_fail: bool = True) -> bool:
        """Verify that actual is less than or equal to expected."""
        step_name = step_name or message or "Verify less equal"
        
        def _do_verify():
            result = actual <= expected
            self.logger.log_verification(f"{message or 'Less equal verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: {actual} is not less than or equal to {expected}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected, actual, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: {actual} is not less than or equal to {expected}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_less_equal")
            if raise_on_fail:
                raise
            return False
            
    def verify_not_none(self, value: Any, message: str = "",
                       step_name: str = None, create_allure_step: bool = False,
                       raise_on_fail: bool = True) -> bool:
        """Verify that value is not None."""
        step_name = step_name or message or "Verify not none"
        
        def _do_verify():
            result = value is not None
            self.logger.log_verification(f"{message or 'Not None verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = "Verification failed: Value is None"
                self.logger.error(error_msg)
            
            self._attach_verification_details(None, value, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Value is None")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_not_none")
            if raise_on_fail:
                raise
            return False
            
    def verify_none(self, value: Any, message: str = "",
                   step_name: str = None, create_allure_step: bool = False,
                   raise_on_fail: bool = True) -> bool:
        """Verify that value is None."""
        step_name = step_name or message or "Verify none"
        
        def _do_verify():
            result = value is None
            self.logger.log_verification(f"{message or 'None verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Value is not None, got '{value}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(None, value, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Value is not None, got '{value}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_none")
            if raise_on_fail:
                raise
            return False
            
    def verify_not_empty(self, value: Any, message: str = "",
                        step_name: str = None, create_allure_step: bool = False,
                        raise_on_fail: bool = True) -> bool:
        """Verify that value is not empty."""
        step_name = step_name or message or "Verify not empty"
        
        def _do_verify():
            if hasattr(value, '__len__'):
                result = len(value) > 0
            else:
                result = bool(value)
            
            self.logger.log_verification(f"{message or 'Not empty verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = "Verification failed: Value is empty"
                self.logger.error(error_msg)
            
            self._attach_verification_details("not empty", value, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Value is empty")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_not_empty")
            if raise_on_fail:
                raise
            return False
            
    def verify_empty(self, value: Any, message: str = "",
                    step_name: str = None, create_allure_step: bool = False,
                    raise_on_fail: bool = True) -> bool:
        """Verify that value is empty."""
        step_name = step_name or message or "Verify empty"
        
        def _do_verify():
            if hasattr(value, '__len__'):
                result = len(value) == 0
            else:
                result = not bool(value)
            
            self.logger.log_verification(f"{message or 'Empty verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = "Verification failed: Value is not empty"
                self.logger.error(error_msg)
            
            self._attach_verification_details("empty", value, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Value is not empty")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_empty")
            if raise_on_fail:
                raise
            return False
            
    def verify_regex_match(self, text: str, pattern: str, message: str = "",
                          step_name: str = None, create_allure_step: bool = False,
                          raise_on_fail: bool = True) -> bool:
        """Verify that text matches regex pattern."""
        step_name = step_name or message or "Verify regex match"
        
        def _do_verify():
            import re
            result = bool(re.search(pattern, text))
            self.logger.log_verification(f"{message or 'Regex match verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Text '{text}' does not match pattern '{pattern}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(pattern, text, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Text '{text}' does not match pattern '{pattern}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_regex_match")
            if raise_on_fail:
                raise
            return False
            
    def verify_regex_not_match(self, text: str, pattern: str, message: str = "",
                              step_name: str = None, create_allure_step: bool = False,
                              raise_on_fail: bool = True) -> bool:
        """Verify that text does not match regex pattern."""
        step_name = step_name or message or "Verify regex not match"
        
        def _do_verify():
            import re
            result = not bool(re.search(pattern, text))
            self.logger.log_verification(f"{message or 'Regex not match verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Text '{text}' matches pattern '{pattern}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(pattern, text, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Text '{text}' matches pattern '{pattern}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_regex_not_match")
            if raise_on_fail:
                raise
            return False
            
    def verify_list_equals(self, actual_list: List[Any], expected_list: List[Any], message: str = "",
                          step_name: str = None, create_allure_step: bool = False,
                          raise_on_fail: bool = True) -> bool:
        """Verify that two lists are equal."""
        step_name = step_name or message or "Verify list equals"
        
        def _do_verify():
            result = actual_list == expected_list
            self.logger.log_verification(f"{message or 'List equals verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Lists are not equal"
                self.logger.error(error_msg)
                self.logger.error(f"Expected: {expected_list}")
                self.logger.error(f"Actual: {actual_list}")
            
            self._attach_verification_details(expected_list, actual_list, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Lists are not equal")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_list_equals")
            if raise_on_fail:
                raise
            return False
            
    def verify_dict_equals(self, actual_dict: Dict[str, Any], expected_dict: Dict[str, Any], message: str = "",
                          step_name: str = None, create_allure_step: bool = False,
                          raise_on_fail: bool = True) -> bool:
        """Verify that two dictionaries are equal."""
        step_name = step_name or message or "Verify dict equals"
        
        def _do_verify():
            result = actual_dict == expected_dict
            self.logger.log_verification(f"{message or 'Dict equals verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Dictionaries are not equal"
                self.logger.error(error_msg)
                self.logger.error(f"Expected: {expected_dict}")
                self.logger.error(f"Actual: {actual_dict}")
            
            self._attach_verification_details(expected_dict, actual_dict, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Dictionaries are not equal")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_dict_equals")
            if raise_on_fail:
                raise
            return False
            
    def verify_dict_contains(self, actual_dict: Dict[str, Any], expected_dict: Dict[str, Any], message: str = "",
                            step_name: str = None, create_allure_step: bool = False,
                            raise_on_fail: bool = True) -> bool:
        """Verify that actual dictionary contains all keys and values from expected dictionary."""
        step_name = step_name or message or "Verify dict contains"
        
        def _do_verify():
            result = all(actual_dict.get(key) == value for key, value in expected_dict.items())
            self.logger.log_verification(f"{message or 'Dict contains verification'}", result)
            
            error_msg = None
            if not result:
                missing_items = {k: v for k, v in expected_dict.items() if actual_dict.get(k) != v}
                error_msg = f"Verification failed: Dictionary does not contain expected items: {missing_items}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected_dict, actual_dict, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or "Verification failed: Dictionary does not contain expected items")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_dict_contains")
            if raise_on_fail:
                raise
            return False
            
    def verify_exception_raised(self, func, *args, exception_type: type = Exception, message: str = "",
                               step_name: str = None, create_allure_step: bool = False,
                               raise_on_fail: bool = True, **kwargs) -> bool:
        """Verify that function raises expected exception."""
        step_name = step_name or message or "Verify exception raised"
        
        def _do_verify():
            try:
                func(*args, **kwargs)
                error_msg = f"Verification failed: Expected {exception_type.__name__} was not raised"
                self.logger.error(error_msg)
                self._attach_verification_details(exception_type.__name__, "No exception", False, error_msg)
                if raise_on_fail:
                    raise AssertionError(error_msg)
                return False
            except exception_type:
                self.logger.log_verification(f"{message or 'Exception raised verification'}", True)
                self._attach_verification_details(exception_type.__name__, exception_type.__name__, True, None)
                return True
            except Exception as e:
                error_msg = f"Verification failed: Expected {exception_type.__name__}, got {type(e).__name__}"
                self.logger.error(error_msg)
                self._attach_verification_details(exception_type.__name__, type(e).__name__, False, error_msg)
                if raise_on_fail:
                    raise AssertionError(error_msg)
                return False
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_exception_raised")
            if raise_on_fail:
                raise
            return False
            
    def verify_no_exception(self, func, *args, message: str = "",
                           step_name: str = None, create_allure_step: bool = False,
                           raise_on_fail: bool = True, **kwargs) -> bool:
        """Verify that function does not raise any exception."""
        step_name = step_name or message or "Verify no exception"
        
        def _do_verify():
            try:
                func(*args, **kwargs)
                self.logger.log_verification(f"{message or 'No exception verification'}", True)
                self._attach_verification_details("No exception", "No exception", True, None)
                return True
            except Exception as e:
                error_msg = f"Verification failed: Unexpected exception {type(e).__name__}: {str(e)}"
                self.logger.error(error_msg)
                self._attach_verification_details("No exception", type(e).__name__, False, error_msg)
                if raise_on_fail:
                    raise AssertionError(error_msg)
                return False
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_no_exception")
            if raise_on_fail:
                raise
            return False
            
    def verify_within_range(self, value: float, min_val: float, max_val: float, message: str = "",
                           step_name: str = None, create_allure_step: bool = False,
                           raise_on_fail: bool = True) -> bool:
        """Verify that value is within specified range."""
        step_name = step_name or message or "Verify within range"
        
        def _do_verify():
            result = min_val <= value <= max_val
            self.logger.log_verification(f"{message or 'Within range verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: {value} is not within range [{min_val}, {max_val}]"
                self.logger.error(error_msg)
            
            expected_range = f"[{min_val}, {max_val}]"
            self._attach_verification_details(expected_range, value, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: {value} is not within range [{min_val}, {max_val}]")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_within_range")
            if raise_on_fail:
                raise
            return False
            
    def verify_string_starts_with(self, text: str, prefix: str, message: str = "",
                                  step_name: str = None, create_allure_step: bool = False,
                                  raise_on_fail: bool = True) -> bool:
        """Verify that string starts with prefix."""
        step_name = step_name or message or "Verify string starts with"
        
        def _do_verify():
            result = text.startswith(prefix)
            self.logger.log_verification(f"{message or 'Starts with verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: '{text}' does not start with '{prefix}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(prefix, text, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: '{text}' does not start with '{prefix}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_string_starts_with")
            if raise_on_fail:
                raise
            return False
            
    def verify_string_ends_with(self, text: str, suffix: str, message: str = "",
                               step_name: str = None, create_allure_step: bool = False,
                               raise_on_fail: bool = True) -> bool:
        """Verify that string ends with suffix."""
        step_name = step_name or message or "Verify string ends with"
        
        def _do_verify():
            result = text.endswith(suffix)
            self.logger.log_verification(f"{message or 'Ends with verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: '{text}' does not end with '{suffix}'"
                self.logger.error(error_msg)
            
            self._attach_verification_details(suffix, text, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: '{text}' does not end with '{suffix}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_string_ends_with")
            if raise_on_fail:
                raise
            return False
            
    def verify_string_length(self, text: str, expected_length: int, message: str = "",
                            step_name: str = None, create_allure_step: bool = False,
                            raise_on_fail: bool = True) -> bool:
        """Verify that string has expected length."""
        step_name = step_name or message or "Verify string length"
        
        def _do_verify():
            result = len(text) == expected_length
            self.logger.log_verification(f"{message or 'String length verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Expected length {expected_length}, got {len(text)}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected_length, len(text), result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Expected length {expected_length}, got {len(text)}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_string_length")
            if raise_on_fail:
                raise
            return False
            
    def verify_list_length(self, actual_list: List[Any], expected_length: int, message: str = "",
                          step_name: str = None, create_allure_step: bool = False,
                          raise_on_fail: bool = True) -> bool:
        """Verify that list has expected length."""
        step_name = step_name or message or "Verify list length"
        
        def _do_verify():
            result = len(actual_list) == expected_length
            self.logger.log_verification(f"{message or 'List length verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Expected length {expected_length}, got {len(actual_list)}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected_length, len(actual_list), result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Expected length {expected_length}, got {len(actual_list)}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_list_length")
            if raise_on_fail:
                raise
            return False
            
    def verify_dict_length(self, actual_dict: Dict[str, Any], expected_length: int, message: str = "",
                          step_name: str = None, create_allure_step: bool = False,
                          raise_on_fail: bool = True) -> bool:
        """Verify that dictionary has expected length."""
        step_name = step_name or message or "Verify dict length"
        
        def _do_verify():
            result = len(actual_dict) == expected_length
            self.logger.log_verification(f"{message or 'Dict length verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Expected length {expected_length}, got {len(actual_dict)}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected_length, len(actual_dict), result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Expected length {expected_length}, got {len(actual_dict)}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_dict_length")
            if raise_on_fail:
                raise
            return False
            
    def verify_is_instance(self, value: Any, expected_type: type, message: str = "",
                          step_name: str = None, create_allure_step: bool = False,
                          raise_on_fail: bool = True) -> bool:
        """Verify that value is an instance of expected_type."""
        step_name = step_name or message or "Verify is instance"
        
        def _do_verify():
            result = isinstance(value, expected_type)
            self.logger.log_verification(f"{message or 'Is instance verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Expected type {expected_type.__name__}, got {type(value).__name__}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(expected_type.__name__, type(value).__name__, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Expected type {expected_type.__name__}, got {type(value).__name__}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_is_instance")
            if raise_on_fail:
                raise
            return False
            
    def verify_almost_equal(self, actual: float, expected: float, tolerance: float = 0.0001, message: str = "",
                           step_name: str = None, create_allure_step: bool = False,
                           raise_on_fail: bool = True) -> bool:
        """Verify that actual is almost equal to expected within tolerance."""
        step_name = step_name or message or "Verify almost equal"
        
        def _do_verify():
            result = abs(actual - expected) <= tolerance
            self.logger.log_verification(f"{message or 'Almost equal verification'}", result)
            
            error_msg = None
            if not result:
                diff = abs(actual - expected)
                error_msg = f"Verification failed: Expected {expected} ± {tolerance}, got {actual} (difference: {diff})"
                self.logger.error(error_msg)
            
            expected_range = f"{expected} ± {tolerance}"
            self._attach_verification_details(expected_range, actual, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Expected {expected} ± {tolerance}, got {actual}")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_almost_equal")
            if raise_on_fail:
                raise
            return False
            
    def verify_dict_has_key(self, actual_dict: Dict[str, Any], key: str, message: str = "",
                           step_name: str = None, create_allure_step: bool = False,
                           raise_on_fail: bool = True) -> bool:
        """Verify that dictionary has the specified key."""
        step_name = step_name or message or "Verify dict has key"
        
        def _do_verify():
            result = key in actual_dict
            self.logger.log_verification(f"{message or 'Dict has key verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Dictionary does not have key '{key}'. Available keys: {list(actual_dict.keys())}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(key, list(actual_dict.keys()) if not result else key, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Dictionary does not have key '{key}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_dict_has_key")
            if raise_on_fail:
                raise
            return False
            
    def verify_dict_not_has_key(self, actual_dict: Dict[str, Any], key: str, message: str = "",
                                step_name: str = None, create_allure_step: bool = False,
                                raise_on_fail: bool = True) -> bool:
        """Verify that dictionary does not have the specified key."""
        step_name = step_name or message or "Verify dict not has key"
        
        def _do_verify():
            result = key not in actual_dict
            self.logger.log_verification(f"{message or 'Dict not has key verification'}", result)
            
            error_msg = None
            if not result:
                error_msg = f"Verification failed: Dictionary should not have key '{key}', but it exists with value: {actual_dict[key]}"
                self.logger.error(error_msg)
            
            self._attach_verification_details(f"not {key}", key, result, error_msg)
            
            if not result and raise_on_fail:
                raise AssertionError(error_msg or f"Verification failed: Dictionary should not have key '{key}'")
            
            return result
        
        if create_allure_step:
            try:
                if allure is not None:
                    with allure.step(step_name):
                        return _do_verify()
            except ImportError:
                pass
        
        try:
            return _do_verify()
        except AssertionError:
            raise
        except Exception as e:
            self.logger.log_error(e, "verify_dict_not_has_key")
            if raise_on_fail:
                raise
            return False
