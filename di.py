from inspect import (
    signature, 
    Parameter, 
    isasyncgenfunction, 
    isgeneratorfunction, 
    iscoroutinefunction,
    Signature
)
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
                    dependencies.append((parameter, dependency))
                elif is_dep:
                    raise Exception("not yet implemented")
        elif is_dep:
            raise Exception("not yet implemented")
    dependency_dict = {}
    for dep_name, dep in dependencies:
        if isasyncgenfunction(dep) or iscoroutinefunction(dep) or isgeneratorfunction(dep) or ('__enter__' in dir(dep) and '__exit__' in dir(dep)) or ('__aenter__' in dir(dep) and '__aexit__' in dir(dep)):
            raise Exception("not yet implemented")
        elif '__call__' in dir(dep):
            if dependency_dict.get('sync_callable') == None:
                dependency_dict['sync_callable'] = []
            dependency_dict['sync_callable'].append((dep_name, dep))
        else:
            raise Exception("not supported")
    def f(*args, **kwargs):
        if dependency_dict.get('sync_callable') != None:
            for dep_name, dep in dependency_dict['sync_callable']:
                kwargs[dep_name] = dep()
        return func(*args, **kwargs)
    f.__signature__ = Signature(
        parameters = [v for _, v in f_params.items()],
        return_annotation = func_sig._return_annotation
    )
    return f