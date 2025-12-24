# """
# ABOUT THIS TEST:
# - An async function has an async generator as a dependency
# """

# from di import *
# from typing import Annotated
# import asyncio

# class UselessAsyncContextManager:
#     def __init__(self):
#         print("UselessAsyncContextManager.__init__ got called")
#     async def __aenter__(self):
#         print("UselessAsyncContextManager.__aenter__ got called")
#     async def __aexit__(self, exc_type, exc_value, traceback):
#         print("UselessAsyncContextManager.__aexit__ got called")
#     def __await__(self):
#         pass

# async def bar():
#     async with UselessAsyncContextManager() as ucm:
#         print("I am in async with statement before yielding")
#         yield 100
#         print("I am in async with statement after yielding")

# @generic_di
# async def foo(x, y: Annotated[int, Depends(bar)]):
#     print(f"the value of x is: {x}")
#     print(f"the value of y is: {y}")

# print(signature(foo))

# asyncio.run(foo("harry_bhai"))
"""
ABOUT THIS TEST:
- A sync function has a sync generator as a dependency
"""

from di import *
from typing import Annotated

class UselessContextManager:
    def __init__(self):
        print("UselessContextManager.__init__ got called")
    async def __aenter__(self):
        print("UselessContextManager.__aenter__ got called")
    async def __aexit__(self, exc_type, exc_value, traceback):
        print("UselessContextManager.__aexit__ got called")

async def bar():
    async with UselessContextManager() as ucm:
        print("I am in with statement before yielding")
        yield 100
        print("I am in with statement after yielding")
# def bar():
#     print("in bar before yielding")
#     yield 100
#     print("in bar after yielding")
def bar2(a: int = 200):
    return a
async def foobar(a: Annotated[int, Depends(bar)], b: Annotated[int, Depends(bar2)]):
    return f"foobar<bar:{a}, bar2:{b}>"

@generic_di
async def foo(x, y: Annotated[int, Depends(bar)], z: Annotated[str, Depends(foobar)]):
    print(f"the value of x is: {x}")
    print(f"the value of y is: {y}")
    print(f"the value of z is: {z}")

print(signature(foo))
import asyncio
asyncio.run(foo("harry_bhai"))