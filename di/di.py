from inspect import (
    signature, 
    Parameter, 
    isasyncgenfunction, 
    isgeneratorfunction, 
    iscoroutinefunction,
    Signature
)
import asyncio
class Depends:
    def __init__(self, foo):
        self.func = foo
    def __str__(self):
        return self.func.__name__
    def __repr__(self):
        return "Depends"
# ASSUMPTIONS & FUNCTIONALITY:
# 1. dependencies can take no parameters other than other dependencies
# 2. user won't self-call a dependency
# 3. both the top-level function(the argument of the initial call to generic_di) and dependencies are synchronous callables(functions or any object with __call__ implemented)
# 4. recursive dependencies are allowed
def generic_di(func, is_dep=False):
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
        elif isasyncgenfunction(dep) or iscoroutinefunction(dep) or isgeneratorfunction(dep) or ('__enter__' in dep.__dir__() and '__exit__' in dep.__dir__()) or ('__aenter__' in dep.__dir__() and '__aexit__' in dep.__dir__()):
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
            return await func(**func_kwargs, **dep_map)
    else:
        def f(*args, **kwargs):
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
                    dep_map[dep_name] = dep(**dep_argdict)
                    async def task():
                        dep_map[dep_name] = await dep(**dep_argdict)
                    lasttask = el.create_task(task())
                el.run_until_complete(lasttask)
                # raise Exception("not yet implemented")
            func_kwargs = dict()
            for k, v in f_args.arguments.items():
                if signature(func).parameters.get(k) != None:
                    func_kwargs[k] = v
            for k, v in dep_map.items():
                assert func_kwargs.get(k) == None
            return func(**func_kwargs, **dep_map)
    f.__signature__ = f_sig
    return f