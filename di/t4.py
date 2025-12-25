"""
ABOUT THIS TEST:
- A sync function has a sync generator as a dependency
"""

from di import *
from typing import Annotated

class UselessContextManager:
    def __init__(self):
        print("UselessContextManager.__init__ got called")
    def __enter__(self):
        print("UselessContextManager.__enter__ got called")
    def __exit__(self, exc_type, exc_value, traceback):
        print("UselessContextManager.__exit__ got called")

def bar():
    with UselessContextManager() as ucm:
        print("I am in with statement before yielding")
        yield 100
        print("I am in with statement after yielding")
# def bar():
#     print("in bar before yielding")
#     yield 100
#     print("in bar after yielding")
def bar2(a: int = 200):
    return a
def foobar(a: Annotated[int, Depends(bar)], b: Annotated[int, Depends(bar2)]):
    return f"foobar<bar:{a}, bar2:{b}>"

@generic_di
def foo(x, y: Annotated[int, Depends(bar)], z: Annotated[str, Depends(foobar)]):
    print(f"the value of x is: {x}")
    print(f"the value of y is: {y}")
    print(f"the value of z is: {z}")


def runnee():
    print(signature(foo))
    foo("harry_bhai")

def test(mode):
    from test_utils import run_test
    return run_test(mode, "t4", runnee)
