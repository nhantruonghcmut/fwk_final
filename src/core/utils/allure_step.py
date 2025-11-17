# helpers/steps.py
from contextlib import contextmanager, ContextDecorator
import allure
import inspect
import threading
from functools import wraps
import json

_thread_local = threading.local()

def _find_driver_from_args_kwargs(args, kwargs):
    # tìm driver trong args/kwargs (thường là first arg self -> self.driver)
    # hoặc trong thread-local nếu bạn set trước
    # return None nếu không tìm thấy
    # Bạn có thể customize để phù hợp project (ví dụ check hasattr(obj, "driver"))
    for o in args:
        if hasattr(o, "driver"):
            return getattr(o, "driver")
    for v in kwargs.values():
        if hasattr(v, "driver"):
            return getattr(v, "driver")
    return getattr(_thread_local, "driver", None)

def set_thread_driver(driver):
    """(Tuỳ chọn) set driver vào thread-local để helper có thể tìm khi cần."""
    _thread_local.driver = driver

def clear_thread_driver():
    if hasattr(_thread_local, "driver"):
        del _thread_local.driver

@contextmanager
def step(name, *args, **kwargs):
    """
    Context manager để tạo step; tự attach screenshot/text khi exception.
    Có thể dùng ở bất kỳ file nào.
    """
    with allure.step(name):
        try:
            yield
        except Exception as exc:
            # cố gắng tìm driver để attach screenshot (nếu có)
            driver = _find_driver_from_args_kwargs(args, kwargs)
            try:
                if driver is not None:
                    try:
                        png = driver.get_screenshot_as_png()
                        allure.attach(png, name=f"screenshot_on_fail_{name}", attachment_type=allure.attachment_type.PNG)
                    except Exception:
                        # nếu driver không hỗ trợ hoặc lỗi thì ignore
                        pass
                # attach exception text
                allure.attach(str(exc), name=f"exception_{name}", attachment_type=allure.attachment_type.TEXT)
            except Exception:
                pass
            raise

class Step(ContextDecorator):
    """
    Decorator/class-based context manager: dùng để decorate method/function.
    Ví dụ:
      @Step("Open page")
      def open(...): ...
    """
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self._cm = step(self.name)
        return self._cm.__enter__()

    def __exit__(self, exc_type, exc, tb):
        return self._cm.__exit__(exc_type, exc, tb)

def step_decorator(name=None, attach_params=True, mask_sensitive=True):
    """
    Decorator tự động capture tên function và attach parameters.
    
    Hỗ trợ string interpolation: @step_decorator("Find by XPath: {xpath}")
    Các tham số sẽ tự động thay thế từ function arguments.
    
    Args:
        name: Custom step name (default: function name)
               Có thể dùng {param_name} để interpolate
        attach_params: Có attach parameters vào step (default: True)
        mask_sensitive: Ẩn sensitive data như password (default: True)
    
    Dùng:
        @step_decorator()
        @step_decorator("Find by XPath: {xpath}")
        @step_decorator("Login with {username}", attach_params=False)
        def my_method(self, ...): ...
    """
    def _decorator(func):
        step_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Resolve step name với string interpolation
            resolved_name = _resolve_step_name(step_name, func, args, kwargs)
            
            with step(resolved_name, *args, **kwargs):
                # Attach parameters nếu enabled
                if attach_params:
                    _attach_function_params(func, args, kwargs, mask_sensitive)
                return func(*args, **kwargs)
        
        return wrapper
    
    # Xử lý khi dùng @step_decorator mà không có ()
    if callable(name):
        func = name
        name = func.__name__
        return _decorator(func)
    
    return _decorator

def _resolve_step_name(template, func, args, kwargs):
    """
    Resolve step name template với actual parameter values.
    Ví dụ: "Find by XPath: {xpath}" → "Find by XPath: //*[@id='btn']"
    """
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    
    # Map args → kwargs
    bound_args = {}
    for i, arg in enumerate(args):
        if i < len(param_names):
            bound_args[param_names[i]] = arg
    
    bound_args.update(kwargs)
    
    # Format template
    try:
        # Truncate long values untuk step name
        formatted_args = {}
        for key, value in bound_args.items():
            if isinstance(value, str) and len(value) > 50:
                formatted_args[key] = f"{value[:50]}..."
            else:
                formatted_args[key] = value
        
        return template.format(**formatted_args)
    except (KeyError, ValueError):
        # Nếu format fail, return template as-is
        return template

def _attach_function_params(func, args, kwargs, mask_sensitive=True):
    """Attach function parameters vào allure step."""
    sig = inspect.signature(func)
    params = sig.parameters
    
    # Lấy parameter names
    param_names = list(params.keys())
    
    # Map args vào parameter names (bỏ 'self')
    param_values = {}
    for i, arg in enumerate(args):
        if i < len(param_names):
            param_name = param_names[i]
            if param_name != 'self':
                param_values[param_name] = arg
    
    # Thêm kwargs
    param_values.update({k: v for k, v in kwargs.items() if k != 'self'})
    
    if not param_values:
        return
    
    # Format parameters
    formatted = {}
    for key, value in param_values.items():
        formatted[key] = _format_param_value(value, key, mask_sensitive)
    
    # Attach
    allure.attach(
        json.dumps(formatted, indent=2, default=str),
        name=f"params_{func.__name__}",
        attachment_type=allure.attachment_type.JSON
    )

def _format_param_value(value, param_name, mask_sensitive=True):
    """Format parameter value, mask sensitive data nếu cần."""
    sensitive_keywords = ['password', 'pwd', 'secret', 'token', 'api_key', 'key']
    
    # Mask sensitive parameters
    if mask_sensitive and any(kw in param_name.lower() for kw in sensitive_keywords):
        if isinstance(value, str):
            return f"***{len(value)} chars***"
        return "***MASKED***"
    
    # Với locator tuple (By, value), format đẹp hơn
    if isinstance(value, tuple) and len(value) == 2:
        return f"Locator({value[0]}, '{value[1]}')"
    
    # Truncate long strings
    if isinstance(value, str) and len(value) > 100:
        return f"{value[:100]}... (+{len(value)-100} more chars)"
    
    return value
