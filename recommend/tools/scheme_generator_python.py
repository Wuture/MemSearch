from pydantic import create_model
import inspect
from inspect import Parameter

def generate_scheme_from_function(f):
    kw = {n:(o.annotation, ... if o.default==Parameter.empty else o.default)
        for n,o in inspect.signature(f).parameters.items()}
    s = create_model(f'Input for `{f.__name__}`', **kw).schema()
    return dict(name=f.__name__, description=f.__doc__, parameters=s)

if __name__ == "__main__":
    pass 