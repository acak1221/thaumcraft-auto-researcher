"""
Safe operations module for type checking and validation.
"""
import logging
import os
from pathlib import Path
from typing import Union, Any, Optional


def safe_int_operation(value: Any, operation: str, operand: int, default: int = 0) -> int:
    """
    Safely perform integer operations with None/type checking.
    
    Args:
        value: The value to operate on
        operation: Operation type ('add', 'subtract', 'multiply', 'divide')
        operand: The operand for the operation
        default: Default value if input is None or invalid
        
    Returns:
        Result of the operation or default value
    """
    if value is None:
        value = default
    
    if not isinstance(value, (int, float)):
        logging.warning(f"Expected number, got {type(value)}: {value}, using default {default}")
        value = default
    
    try:
        if operation == 'add':
            return int(value + operand)
        elif operation == 'subtract':
            return max(0, int(value - operand))  # Prevent negative values
        elif operation == 'multiply':
            return int(value * operand)
        elif operation == 'divide':
            if operand == 0:
                logging.error("Division by zero attempted")
                return default
            return int(value / operand)
        else:
            logging.error(f"Unknown operation: {operation}")
            return default
    except Exception as e:
        logging.error(f"Error in safe_int_operation: {e}")
        return default


def safe_path_join(base_path: str, *paths: str) -> str:
    """
    Safely join paths, preventing path traversal attacks.
    
    Args:
        base_path: Base directory path
        *paths: Path components to join
        
    Returns:
        Safely joined path
        
    Raises:
        ValueError: If path traversal is detected
    """
    try:
        base = Path(base_path).resolve()
        target = base.joinpath(*paths).resolve()
        
        # Check if target is within base directory
        target.relative_to(base)
        
        return str(target)
    except ValueError:
        raise ValueError(f"Path traversal attempt detected: {base_path} + {paths}")


def validate_coordinates(x: Any, y: Any) -> tuple[float, float]:
    """
    Validate and convert coordinates to float.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        Tuple of validated coordinates
        
    Raises:
        TypeError: If coordinates are not numeric
        ValueError: If coordinates are infinite or NaN
    """
    if not all(isinstance(coord, (int, float)) for coord in [x, y]):
        raise TypeError(f"Coordinates must be numbers, got {type(x)}, {type(y)}")
    
    x, y = float(x), float(y)
    
    # Check for invalid values
    import math
    if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
        raise ValueError(f"Coordinates must be finite numbers, got {x}, {y}")
    
    return x, y


def safe_dict_get(dictionary: dict, key: str, default: Any = None, expected_type: type = None) -> Any:
    """
    Safely get value from dictionary with type checking.
    
    Args:
        dictionary: Dictionary to get value from
        key: Key to look up
        default: Default value if key not found
        expected_type: Expected type for value validation
        
    Returns:
        Value from dictionary or default
    """
    if not isinstance(dictionary, dict):
        logging.warning(f"Expected dict, got {type(dictionary)}")
        return default
    
    value = dictionary.get(key, default)
    
    if expected_type is not None and value is not None:
        if not isinstance(value, expected_type):
            logging.warning(f"Expected {expected_type}, got {type(value)} for key '{key}'")
            return default
    
    return value


def safe_file_operation(func, *args, **kwargs):
    """
    Safely execute file operations with error handling.
    
    Args:
        func: Function to execute
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of function or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return None
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        return None
    except OSError as e:
        logging.error(f"OS error: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in file operation: {e}")
        return None


class RateLimiter:
    """Rate limiter to prevent excessive operations."""
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def allow_call(self) -> bool:
        """
        Check if a call is allowed within rate limits.
        
        Returns:
            True if call is allowed, False otherwise
        """
        import time
        now = time.time()
        
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            return False
        
        self.calls.append(now)
        return True
    
    def reset(self):
        """Reset the rate limiter."""
        self.calls.clear()