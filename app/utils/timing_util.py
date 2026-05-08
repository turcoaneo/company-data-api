import threading
import time
from functools import wraps

from app.utils.logger_util import get_logger

logger = get_logger()


def log_thread_id(thread_id, name=None):
    thread_info = f'Thread - {thread_id}'
    if name is not None:
        thread_info = f'{name} | {thread_info}'
    return thread_info


def elapsed_time(label=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            thread_id = threading.get_ident()
            name = label or func.__name__
            logger.info(f"[{name} | {log_thread_id(thread_id)}] started")
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"[{name} | {log_thread_id(thread_id)}] completed in {duration:.3f}s")
            return result

        return wrapper

    return decorator
