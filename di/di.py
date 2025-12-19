from inspect import (
    signature, 
    Parameter, 
    isasyncgenfunction, 
    isgeneratorfunction, 
    iscoroutinefunction,
    Signature
)
import asyncio
from contextlib import contextmanager, ExitStack
class Depends:
    def __init__(self, foo):
        self.func = foo
    def __str__(self):
        return self.func.__name__
    def __repr__(self):
        return "Depends"
def generic_di(func, is_dep=False):
    try:
        func_name = func.__name__
    except Exception as e:
        func_name = "unnamed"
    func_sig = signature(func)
    f_params = dict([(k, v) for k, v in func_sig.parameters.items()])
    dependencies = []
    for parameter, paramtype in [(k, v) for k, v in func_sig.parameters.items()]:
        if paramtype.annotation != Parameter.empty and '__metadata__' in dir(paramtype.annotation):
            for annotation in paramtype.annotation.__metadata__:
                if '__repr__' in dir(annotation) and annotation.__repr__() == "Depends":
                    del f_params[parameter]
                    dependency = annotation.func
                    dependency = generic_di(dependency, is_dep=True)
                    dep_params = dict([(k, v) for k, v in signature(dependency).parameters.items()])
                    f_params.update(dep_params)
                    dependencies.append((parameter, dependency))
                elif is_dep:
                    raise Exception("not yet implemented")
        # elif is_dep:
        #     raise Exception("not yet implemented")
    dependency_dict = {}
    for dep_name, dep in dependencies:
        try:
            dep.__dir__()
            is_class = False
        except TypeError:
            is_class = True
        if is_class:
            raise Exception("invalid dependency")
        elif iscoroutinefunction(dep):
            if dependency_dict.get('coroutinefunction') == None:
                dependency_dict['coroutinefunction'] = []
            dependency_dict['coroutinefunction'].append((dep_name, dep))
        elif isgeneratorfunction(dep):
            if dependency_dict.get('generatorfunction') == None:
                dependency_dict['generatorfunction'] = []
            dependency_dict['generatorfunction'].append((dep_name, dep))
        elif isasyncgenfunction(dep) or isgeneratorfunction(dep) or ('__enter__' in dep.__dir__() and '__exit__' in dep.__dir__()) or ('__aenter__' in dep.__dir__() and '__aexit__' in dep.__dir__()):
            raise Exception("not yet implemented")
        elif '__call__' in dir(dep):
            if dependency_dict.get('sync_callable') == None:
                dependency_dict['sync_callable'] = []
            dependency_dict['sync_callable'].append((dep_name, dep))
        else:
            raise Exception("not supported")
    f_sig = Signature(
        parameters = [v for _, v in f_params.items()],
        return_annotation = func_sig._return_annotation
    )
    if iscoroutinefunction(func):
        async def f(*args, **kwargs):
            nonlocal func_name# for debugger
            f_args = f_sig.bind(*args, **kwargs)
            dep_map = dict()
            if dependency_dict.get('sync_callable') != None:
                for dep_name, dep in dependency_dict['sync_callable']:
                    dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                    dep_argdict = dict()
                    for k, v in f_args.arguments.items():
                        if dep_paramdict.get(k) != None:
                            dep_argdict[k] = v
                    dep_map[dep_name] = dep(**dep_argdict)
            if dependency_dict.get('coroutinefunction') != None:
                for dep_name, dep in dependency_dict['coroutinefunction']:
                    dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                    dep_argdict = dict()
                    for k, v in f_args.arguments.items():
                        if dep_paramdict.get(k) != None:
                            dep_argdict[k] = v
                    dep_map[dep_name] = await dep(**dep_argdict)
            func_kwargs = dict()
            for k, v in f_args.arguments.items():
                if signature(func).parameters.get(k) != None:
                    func_kwargs[k] = v
            for k, v in dep_map.items():
                assert func_kwargs.get(k) == None
            if dependency_dict.get('generatorfunction') != None:
                raise Exception("not yet implemented")
            return await func(**func_kwargs, **dep_map)
    elif is_dep and (isgeneratorfunction(func) or dependency_dict.get('generatorfunction') != None):
        def f(*args, **kwargs):
            nonlocal func_name# for debugger
            f_args = f_sig.bind(*args, **kwargs)
            dep_map = dict()
            if dependency_dict.get('sync_callable') != None:
                for dep_name, dep in dependency_dict['sync_callable']:
                    dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                    dep_argdict = dict()
                    for k, v in f_args.arguments.items():
                        if dep_paramdict.get(k) != None:
                            dep_argdict[k] = v
                    dep_map[dep_name] = dep(**dep_argdict)
            if dependency_dict.get('coroutinefunction') != None:
                el = asyncio.new_event_loop()
                for dep_name, dep in dependency_dict['coroutinefunction']:
                    dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                    dep_argdict = dict()
                    for k, v in f_args.arguments.items():
                        if dep_paramdict.get(k) != None:
                            dep_argdict[k] = v
                    async def task():
                        dep_map[dep_name] = await dep(**dep_argdict)
                        return
                    lasttask = el.create_task(task())
                el.run_until_complete(lasttask)
                # raise Exception("not yet implemented")
            func_kwargs = dict()
            for k, v in f_args.arguments.items():
                if signature(func).parameters.get(k) != None:
                    func_kwargs[k] = v
            for k, v in dep_map.items():
                assert func_kwargs.get(k) == None
            if dependency_dict.get('generatorfunction') != None:
                with ExitStack() as st:
                    for dep_name, dep in dependency_dict['generatorfunction']:
                        dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                        dep_argdict = dict()
                        for k, v in f_args.arguments.items():
                            if dep_paramdict.get(k) != None:
                                dep_argdict[k] = v
                        dep_map[dep_name] = st.enter_context(contextmanager(dep)(**dep_argdict))
                    if isgeneratorfunction(func):
                        with contextmanager(func)(**func_kwargs, **dep_map) as ret_val:
                            yield ret_val
                        return
                    yield func(**func_kwargs, **dep_map)
                    return
            elif isgeneratorfunction(func):
                with contextmanager(func)(**func_kwargs, **dep_map) as ret_val:
                    yield ret_val
            else:
                assert False, "Unreachable"
    else:
        def f(*args, **kwargs):
            nonlocal func_name# for debugger
            nonlocal is_dep
            f_args = f_sig.bind(*args, **kwargs)
            dep_map = dict()
            if dependency_dict.get('sync_callable') != None:
                for dep_name, dep in dependency_dict['sync_callable']:
                    dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                    dep_argdict = dict()
                    for k, v in f_args.arguments.items():
                        if dep_paramdict.get(k) != None:
                            dep_argdict[k] = v
                    dep_map[dep_name] = dep(**dep_argdict)
            if dependency_dict.get('coroutinefunction') != None:
                el = asyncio.new_event_loop()
                for dep_name, dep in dependency_dict['coroutinefunction']:
                    dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                    dep_argdict = dict()
                    for k, v in f_args.arguments.items():
                        if dep_paramdict.get(k) != None:
                            dep_argdict[k] = v
                    async def task():
                        dep_map[dep_name] = await dep(**dep_argdict)
                        return
                    lasttask = el.create_task(task())
                el.run_until_complete(lasttask)
            func_kwargs = dict()
            for k, v in f_args.arguments.items():
                if signature(func).parameters.get(k) != None:
                    func_kwargs[k] = v
            for k, v in dep_map.items():
                assert func_kwargs.get(k) == None
            if dependency_dict.get('generatorfunction') != None:
                with ExitStack() as st:
                    for dep_name, dep in dependency_dict['generatorfunction']:
                        dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
                        dep_argdict = dict()
                        for k, v in f_args.arguments.items():
                            if dep_paramdict.get(k) != None:
                                dep_argdict[k] = v
                        dep_map[dep_name] = st.enter_context(contextmanager(dep)(**dep_argdict))
                    if isgeneratorfunction(func):
                        with contextmanager(func)(**func_kwargs, **dep_map) as ret_val:
                            return ret_val
                    return func(**func_kwargs, **dep_map)
            elif isgeneratorfunction(func):
                with contextmanager(func)(**func_kwargs, **dep_map) as ret_val:
                    return ret_val
            else:
                return func(**func_kwargs, **dep_map)
    f.__signature__ = f_sig
    return f
# def get_dep_argdict(f_args, dep_name, dep):
#     dep_paramdict = dict([(k, v) for k, v in signature(dep).parameters.items()])
#     dep_argdict = dict()
#     for k, v in f_args.arguments.items():
#         if dep_paramdict.get(k) != None:
#             dep_argdict[k] = v
#     return dep_argdict