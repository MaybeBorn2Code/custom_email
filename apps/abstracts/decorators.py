# Django
from django.shortcuts import render

# Python
import time
from typing import (
    Callable,
    Any
)


def perfomance_counter(func: Callable) -> Any:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start: float = time.perf_counter()
        result = func(*args, **kwargs)
        end: float = time.perf_counter()
        print(f'{func.__name__}: {(end-start):.2f} seconds.')
        return result
    return wrapper
