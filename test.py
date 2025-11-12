from typing import Annotated, get_type_hints

from inspect import getsource


def foo(x: int, y: Annotated[str, "adfadfsa", "qwreqer"]):
    return 0
def bar(*args, **kwargs):
    return 1
import inspect
from inspect import signature
print("signature of bar:", signature(bar).parameters['args']._kind)

print(getsource(foo))

print("signature of foo:", signature(foo).parameters['x'].annotation)
sig = signature(foo)
sig.parameters['y']._annotation = inspect.Parameter.empty
foo.__signature__ = sig
print("signature of foo:", signature(foo))