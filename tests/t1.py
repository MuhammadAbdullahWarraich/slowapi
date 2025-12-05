from di import *
from typing import Annotated

def bar():
    return 100
def foobar(a: Annotated[int, Depends(bar)]):
    return f"foobar<bar:{a}>"

@generic_di
def foo(x, y: Annotated[int, Depends(bar)], z: Annotated[str, Depends(foobar)]):
    print(f"the value of x is: {x}")
    print(f"the value of y is: {y}")
    print(f"the value of z is: {z}")

foo("harry_bhai")