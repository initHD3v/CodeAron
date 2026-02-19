import time
import random
import logging
from typing import Callable, Any, TypeVar, Dict

T = TypeVar("T")
logger = logging.getLogger("Recovery")

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for exponential backoff retry strategy.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        raise e
                    
                    delay = base_delay * (2 ** (retries - 1)) + random.uniform(0, 1)
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} in {delay:.2f}s due to: {e}")
                    time.sleep(delay)
            return func(*args, **kwargs) # Should not be reachable
        return wrapper
    return decorator

class RecoveryEngine:
    """
    Responsibility: Handles partial failures and fallback logic.
    """
    @staticmethod
    def fallback_result(error_msg: str) -> Dict[str, Any]:
        return {
            "success": False,
            "output": f"Error: {error_msg}. System is in recovery mode.",
            "error_type": "recovered_failure"
        }
