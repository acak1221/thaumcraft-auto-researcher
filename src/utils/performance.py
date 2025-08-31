"""Performance monitoring utilities."""
import time
import logging
from functools import wraps
from typing import Callable, Any


def timeit(func: Callable) -> Callable:
    """Decorator to measure and log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logging.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logging.debug(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise
    return wrapper


class PerfTimer:
    """Context manager for performance timing."""
    
    def __init__(self, name: str = "Operation", log_level: int = logging.DEBUG):
        self.name = name
        self.log_level = log_level
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start_time
        if exc_type is None:
            logging.log(self.log_level, f"{self.name} completed in {elapsed:.3f}s")
        else:
            logging.log(self.log_level, f"{self.name} failed after {elapsed:.3f}s")
        return False
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time so far."""
        if self.start_time is None:
            return 0.0
        return time.perf_counter() - self.start_time
