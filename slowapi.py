from starlette.applications import Starlette
from starlette.responses import JSONResponse
from di.di import *

def handle_rets(func):
    from inspect import iscoroutinefunction
    def map_res(res):
        if type(res) in (list, dict):
            return JSONResponse(res)
        else:
            raise AssertionError("not yet implemented")
    if iscoroutinefunction(func):
        async def f(*args, **kwargs):
            x = await func(*args, **kwargs)
            return map_res(x)
    else:
        def f(*args, **kwargs):
            x = func(*args, **kwargs)
            return map_res(x)
    from inspect import signature
    f.__signature__ = signature(func)
    return f

class SlowAPI(Starlette):
    def __init__(self):
        super().__init__(self)
    def get(self, path, /):
        def foo(route_handler):
            route_handler = generic_di(route_handler)
            route_handler = handle_rets(route_handler)
            self.add_route(path, route_handler)
        return foo