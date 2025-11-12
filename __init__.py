# TODO: add support for async functions
# TODO: complete implementation for async_generator and asynccontextmanager
# TODO: test all cases, test also on your FYP backend
from typing import Annotated
from fastapi import FastAPI
def foo():
    print("hello from foo!", "\"1\"")
    return 1


class Depends:
    def __init__(self, foo):
        self.func = foo
    def __str__(self):
        return self.func.__name__
    def __repr__(self):
        return "Depends"
def generic_di(func, debug = False):
    from inspect import signature
    f_sig = signature(func)
    # from inspect import signature
    # if func.__name__ == "get_users":
    #     print("__doc__ signature of func:", signature(func).__doc__)
    #     print("__dir__() signature of func:", signature(func).__dir__())
    # print("signature.parameters of func:", signature(func).parameters)
    # print("signature.parameters of func:", dir(signature(func).parameters))
    f_params = dict([(k, v) for k, v in f_sig.parameters.items()])
    # print("f_params:", f_params)
    #     print("signature.parameters[0] of func:", signature(func).parameters['cur'])
    #     print("signature.parameters[0].__dir__() of func:", signature(func).parameters['cur'].__dir__())
    #     print("signature.parameters[0].__doc__ of func:", signature(func).parameters['cur'].__doc__)
    from inspect import stack
    # st = stack()
    # for frame in st:
    #     print("filename of frame:", frame.filename)
    #     print("function of frame:", frame.function)
    #     print("\n\nthis frame's locals:\n", frame.frame.f_locals)
    #     print("\n\nthis frame's globals:\n", frame.frame.f_globals.get(dependency_str), "\n\n")
    from typing import get_type_hints
    dependencies = []
    for parameter, paramtype in [(k, v) for k, v in get_type_hints(func, include_extras=True).items()]:
        #print("parameter:", parameter)
        #print("paramtype:", paramtype)
        if '__metadata__' in dir(paramtype):
            for annotation in paramtype.__metadata__:
                if '__repr__' in dir(annotation) and annotation.__repr__() == "Depends":
                    assert parameter in f_sig.parameters, "get_type_hints is supposed to return a subset of parameters in inspect.Signature.parameters"
                    del f_params[parameter]
                    # dependency_str = annotation.__str__()
                    #print("globals:", globals())
                    #print("dependency_str:", dependency_str)
                    # dependency_exists = False
                    dependency = annotation.func
                    # for frame in stack(): # I am an idiot. I could've just used annotation.func
                    #     if None != frame.frame.f_globals.get(dependency_str):
                    #         dependency_exists = True
                    #         dependency = frame.frame.f_globals.get(dependency_str)
                    #         break
                        # print("filename of frame:", frame.filename)
                        # print("function of frame:", frame.function)
                        # print("looking for dependency in this frame's globals:", frame.frame.f_globals.get(dependency_str))
                        # print("looking for dependency in this frame's locals:", frame.frame.f_locals.get(dependency_str), "\n")
                    # assert dependency_str in globals()
                    # assert dependency_exists
                    dependency = generic_di(dependency) # for recursive dependencies
                    dependencies.append((parameter, dependency))
    # print(dependencies)
    dependency_dict = {}
    from inspect import isgeneratorfunction, isasyncgenfunction
    for dependency_arg, dependency in dependencies:
        if isasyncgenfunction(dependency):
            # asynchronous generator
            if dependency_dict.get("async_generator") == None:
                dependency_dict["async_generator"] = []
            dependency_dict["async_generator"].append((dependency_arg, dependency))
        elif isgeneratorfunction(dependency):
            # synchronous generator
            if dependency_dict.get("sync_generator") == None:
                dependency_dict["sync_generator"] = []
            dependency_dict["sync_generator"].append((dependency_arg, dependency))
        elif '__enter__' in dependency.__dir__() and '__exit__' in dependency.__dir__():
            # contextmanager
            if dependency_dict.get("contextmanager") == None:
                dependency_dict["contextmanager"] = []
            dependency_dict["contextmanager"].append((dependency_arg, dependency))
        elif '__aenter__' in dependency.__dir__() and '__aexit__' in dependency.__dir__():
            # asynchronouscontextmanager
            if dependency_dict.get("asynccontextmanager") == None:
                dependency_dict["asynccontextmanager"] = []
            dependency_dict["asynccontextmanager"].append((dependency_arg, dependency))
        elif '__call__' in dependency.__dir__():
            # normal function
            if dependency_dict.get("function") == None:
                dependency_dict["function"] = []
            dependency_dict["function"].append((dependency_arg, dependency))
        else:
            raise ValueError("Invalid dependency")
    # print(f"FOR FUNCTION {func.__name__}, dependency_dict:{dependency_dict}")
    if dependency_dict.get("asynccontextmanager") == None and dependency_dict.get("async_generator") == None:
        # print("here")
        def f(*args, **kwargs):
            # print("here where i am not supposed to be", "args:", args, "kwargs:", kwargs)
            from contextlib import ExitStack
            with ExitStack() as st:
                cm_deps = None
                sgen_deps = None
                if dependency_dict.get("contextmanager") != None:
                    cm_deps = [(arg_name, st.enter_context(cm)) for arg_name, cm in dependency_dict["contextmanager"]]
                if dependency_dict.get("sync_generator") != None:
                    from contextlib import contextmanager
                    sgen_deps = [(arg_name, st.enter_context(contextmanager(sgen))) for arg_name, sgen in dependency_dict["sync_generator"]]
                if cm_deps is not None:
                    for arg_name, dep in cm_deps:
                        kwargs[arg_name] = dep
                if sgen_deps is not None:
                    for arg_name, dep in sgen_deps:
                        kwargs[arg_name] = dep
                if dependency_dict.get("function") != None:
                    for arg_name, dep in dependency_dict["function"]:
                        kwargs[arg_name] = dep()# change to add request if needed
                return func(*args, **kwargs)
        # from inspect import getsource
        # print("final source code of function:", getsource(f))
        from inspect import Signature
        f_params = [v for _, v in f_params.items()]
        # print("finally -> f_params:", f_params)
        f.__signature__ = Signature(parameters=f_params, return_annotation=f_sig._return_annotation)
        # print("f.__signature__:", signature(f))
        return f
    else:
        # raise AssertionError("Not yet implemented")
        import re
        import inspect
        if inspect.iscoroutinefunction(func):
            async def f(*args, **kwargs):
                from contextlib import ExitStack, AsyncExitStack
                async with AsyncExitStack() as st:# TODO: Figure out what arrangement of with statements of ExitStack and AsyncExitStack is best for our application. Maybe the user should think about this instead of us, like they should decide that heavy sync dependencies should not be managed in async functions due to performance constraints(also figure out the terminology, i mean how to describe slowdown of performance in terms of the event loop and the thread pool)
                    acm_deps = None
                    asgen_deps = None
                    if dependency_dict.get("asynccontextmanager") != None:
                        acm_deps = [(arg_name, await st.enter_async_context(acm)) for arg_name, acm in dependency_dict["asynccontextmanager"]]
                    if dependency_dict.get("async_generator") != None:
                        from contextlib import asynccontextmanager
                        asgen_deps = [(arg_name, await st.enter_async_context(asynccontextmanager(asgen)())) for arg_name, asgen in dependency_dict["async_generator"]]
                    if acm_deps is not None:
                        for arg_name, dep in acm_deps:
                            kwargs[arg_name] = dep
                    if asgen_deps is not None:
                        for arg_name, dep in asgen_deps:
                            kwargs[arg_name] = dep
                    if dependency_dict.get("function") != None:
                        for arg_name, dep_func in dependency_dict["function"]:
                            if re.match(r"^async", inspect.getsource(dep_func)) != None:
                                kwargs[arg_name] = await dep_func()# TODO: add option to add arguments to dependencies
                            else:
                                pass
                                # TODO: append ot list of sync functions
                    with ExitStack() as st:# TODO: move async with statement inside sync with statement with the async with statement at the end for performance
                        cm_deps = None
                        sgen_deps = None
                        if dependency_dict.get("contextmanager") != None:
                            cm_deps = [(arg_name, st.enter_context(cm)) for arg_name, cm in dependency_dict["contextmanager"]]
                        if dependency_dict.get("sync_generator") != None:
                            from contextlib import contextmanager
                            sgen_deps = [(arg_name, st.enter_context(contextmanager(sgen))) for arg_name, sgen in dependency_dict["sync_generator"]]
                        if cm_deps is not None:
                            for arg_name, dep in cm_deps:
                                kwargs[arg_name] = dep
                        if sgen_deps is not None:
                            for arg_name, dep in sgen_deps:
                                kwargs[arg_name] = dep
                        if dependency_dict.get("function") != None:
                            for arg_name, dep_func in dependency_dict["function"]:
                                if re.match(r"^async", inspect.getsource(dep_func)) == None:# TODO: make it faster by making a list of func functions in else of adding async functions; see above
                                    kwargs[arg_name] = dep_func()
                                    # TODO: consider moving this out of context manager scope for performance
    
                        x = await func(*args, **kwargs)
                        # print("got this from func:", x)
                        return x
            from inspect import Signature
            f_params = [v for _, v in f_params.items()]
            # print("finally -> f_params:", f_params)
            f.__signature__ = Signature(parameters=f_params, return_annotation=f_sig._return_annotation)
            # print("f.__signature__:", signature(f))
            return f
        else:# TODO: CONSIDER THAT MAYBE THIS SHOULD NEVER BE IMPLEMENTED
            assert False, f"not yet implemented {inspect.getsource(func)}"
        # from inspect import getsource
        # print("final source code of function:", getsource(f))

    # for dependency_arg, dependency in dependencies:                                 
    #     if '__aiter__' in dependency.__dir__():
    #         # asynchronous generator
    #         async def f(*args, **kwargs):
    #             from contextlib import asynccontextmanager
    #             withparam = asynccontextmanager(dependency)
    #             print(withparam.__dir__())
    #             async with withparam() as param:
    #                 kwargs[dependency_arg] = param
    #                 return func(*args, **kwargs)
    #         func = f
    #     elif '__iter__' in dependency.__dir__():
    #         # synchronous generator
    #         def f(*args, **kwargs):
    #             from contextlib import contextmanager
    #             withparam = contextmanager(dependency)
    #             print(withparam.__dir__())
    #             with withparam() as param:
    #                 kwargs[dependency_arg] = param
    #                 return func(*args, **kwargs)
    #         func = f
    #     elif '__enter__' in dependency.__dir__() and '__exit__' in dependency.__dir__():
    #         # contextmanager
    #         def f(*args, **kwargs):
    #             with dependency() as dep:
    #                 kwargs[dependency_arg] = dep
    #                 return func(*args, **kwargs)
    #         func = f
    #     elif '__aenter__' in dependency.__dir__() and '__aexit__' in dependency.__dir__():
    #         # asynchronouscontextmanager
    #         async def f(*args, **kwargs):
    #             async with dependency() as dep:
    #                 kwargs[dependency_arg] = dep
    #                 return func(*args, **kwargs)
    #         func = f
    #     elif '__call__' in dependency.__dir__():
    #         # normal function
    #         print("dependency is a normal function")
    #         def f(*args, **kwargs):
    #             dep = dependency()
    #             kwargs[dependency_arg] = dep
    #             func(*args, **kwargs)
    #         func = f
    #         print(func)
    #         print(f)
    #     else:
    #         raise ValueError("Invalid dependency")
    # return func
class SlowAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get(self, *args, **kwargs):
        dec = FastAPI.get(self, *args, **kwargs)
        def func(req_handler):
            req_handler = generic_di(req_handler)
            ret = dec(req_handler)
            #print("what is signature of final function?", ret.__signature__)
            # print("is this a callable?", ret)
            return ret
        return func
    def post(self, *args, **kwargs):
        dec = FastAPI.post(self, *args, **kwargs)
        def func(req_handler):
            req_handler = generic_di(req_handler)
            ret = dec(req_handler)
            # print("is this a callable?", ret)
            return ret
        return func

# @generic_di
# def bar(w: str, x: Annotated[int, Depends(foo)], y: Annotated[int, Depends(foo)]):
#     print("hello from bar!", f"\"{x+y}\"")
#     return w

# print("hello before bar")
# print(bar("bye"))
