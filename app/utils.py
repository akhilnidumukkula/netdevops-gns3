from typing import Optional, Sequence, Any, List, Dict, Union, Type, TypeVar, Callable, Tuple
import os
import functools
import random
import asyncio
import time
import logging
import traceback
import uuid

T = TypeVar("T")

logger = logging.getLogger(__name__)

def create_repr(obj: Any, attrs: Optional[Sequence[str]] = None):
    if attrs is None:
        attrs = obj.__dict__.keys()
    attrs_kv: List[str] = []
    for attr in attrs:
        attr_value = getattr(obj, attr)
        if attr_value is not None:
            attrs_kv.append(f"{attr}={attr_value!r}")
    attrs_repr = ", ".join(attrs_kv)
    return f"{obj.__class__.__qualname__}({attrs_repr})"


def filter_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value for key, value in data.items()
        if value is not None
    }
    
def is_env_var(env_var: str) -> bool:
    env_var_str = os.getenv(env_var, "").lower()
    return env_var_str in ("yes", "true", "y", "1")

def with_semaphore(semaphore: asyncio.Semaphore, timeout: Optional[float] = None, random_timeout: bool = False):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args):
            async with semaphore:
                result = await func(*args)
                if timeout:
                    if random_timeout:
                        timeout_value = random.randint(0, timeout)
                    else:
                        timeout_value=timeout
                    await asyncio.sleep(timeout_value)
            return result
        return wrapped
    return wrapper

# noinspection PyShadowingNames
def retry(exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]], max_retries: int = 5, delay: int= 3, delay_multiplier: int = 2) -> Callable[[T], T]:
    """
    Retry calling the decorated function using an exponential backoff.
    
    Args:
        exceptions: A single exception or a tuple of Exceptions to trigger retry
        max_retires: Number of times to retry before failing.
        delay: Initial delay between retries in seconds.
        delay_multiplier: Delay multipler (e.g. value of 2 will double the delay each retry).
    """
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            attempt_num = 0
            mdelay = delay
            while attempt_num < max_retries:
                try:
                    return f(*args, **kwargs)
                except exceptions:
                    attempt_num += 1
                    logger.warning("Retry attempt #%d/%d in %d seconds ...\n%s", attempt_num, max_retries, mdelay, traceback.format_exc(limit=1))
                    time.sleep(mdelay)
                    mdelay *= delay_multiplier
            
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def create_random_data() -> Dict[str, Any]:
        random_data = [str(uuid.uuid4() for i in range(1000))]
        host_vars: Dict[str, Any] = {"random": random_data}
        return host_vars
