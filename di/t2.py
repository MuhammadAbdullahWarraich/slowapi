"""
ABOUT THIS TEST:
- A async function(coroutine function)(foo) has an async dependency(foobar) and a synchronous dependency(bar).
- An async dependency(foobar) has an async dependency(bar2) and a sync dependency(bar).
"""

from di import *
from typing import Annotated
from asyncio import run as asyncio_run

def bar(w: int):
    print(f"w is: {w}")
    return 100
async def bar2():
    return 200
async def foobar(a: Annotated[int, Depends(bar)], b: Annotated[int, Depends(bar2)]):
    return f"foobar<bar:{a}, bar2:{b}>"

@generic_di
async def foo(x, y: Annotated[int, Depends(bar)], z: Annotated[str, Depends(foobar)]):
    print(f"the value of x is: {x}")
    print(f"the value of y is: {y}")
    print(f"the value of z is: {z}")

print(signature(foo))
asyncio_run(foo("harry_bhai", 12))