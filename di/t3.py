"""
ABOUT THIS TEST:
- A synchronous function(foo) has an synchronous dependency(foobar) and an async dependency(bar).
- A synchronous dependency(foobar) has a synchronous dependency(bar2) and an async dependency(bar).
"""

from di import *
from typing import Annotated

async def bar():
    return 100
def bar2(a: int = 200):
    return a
def foobar(a: Annotated[int, Depends(bar)], b: Annotated[int, Depends(bar2)]):
    return f"foobar<bar:{a}, bar2:{b}>"

@generic_di
def foo(x, y: Annotated[int, Depends(bar)], z: Annotated[str, Depends(foobar)]):
    print(f"the value of x is: {x}")
    print(f"the value of y is: {y}")
    print(f"the value of z is: {z}")

foo("harry_bhai")
print("sig of foo:", signature(foo).parameters)
print("sig of foobar:", signature(foobar).parameters)
print("sig of bar:", signature(bar).parameters)
print("sig of bar2:", signature(bar2).parameters)