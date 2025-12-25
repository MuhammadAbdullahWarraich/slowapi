"""
ABOUT THIS TEST:
- A synchronous function(foo) has an synchronous dependency(foobar) and an async dependency(bar).
- A synchronous dependency(foobar) has a synchronous dependency(bar2) and an async dependency(bar).

Note: Any parameter of a dependency that isn't a dependency and doesn't have a default value mustn't have the same name as any parameter(dependency or otherwise). 
TODO: this rule must be rethought because multiple dependencies in the same dependency chain may require a Request object, for example, which should have the same name as a convention.
"""

from di import *
from typing import Annotated

async def bar():
    return 100
# def bar2(a: int = 200):
def bar2(wow: int):
    return wow
def foobar(a: Annotated[int, Depends(bar)], b: Annotated[int, Depends(bar2)]):
    return f"foobar<bar:{a}, bar2:{b}>"

@generic_di
def foo(x, y: Annotated[int, Depends(bar)], z: Annotated[str, Depends(foobar)]):
    print(f"the value of x is: {x}")
    print(f"the value of y is: {y}")
    print(f"the value of z is: {z}")


def runnee():
    foo("harry_bhai", 1212)
    print("sig of foo:", signature(foo).parameters)
    print("sig of foobar:", signature(foobar).parameters)
    print("sig of bar:", signature(bar).parameters)
    print("sig of bar2:", signature(bar2).parameters)

def test(mode):
    from test_utils import run_test
    return run_test(mode, "t3", runnee)
