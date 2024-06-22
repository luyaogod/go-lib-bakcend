import time
from functools import wraps
from settings import mlog as log

def func_debug(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        log.debug(f"进入: {func.__name__}")
        result = await func(*args, **kwargs)
        end_time = time.time()
        log.debug(f"完成: {func.__name__} (Time taken: {end_time - start_time:.2f}s)")
        return result
    return wrapper