from pydantic import create_model
import inspect, json 
from inspect import Parameter
import platform
import subprocess
import os


# os.system("shortcuts run 'Timer'")

def generate_schema_from_function(f):
    kw = {n:(o.annotation, ... if o.default==Parameter.empty else o.default)
        for n,o in inspect.signature(f).parameters.items()}
    s = create_model(f'Input for `{f.__name__}`', **kw).schema()
    return dict(name=f.__name__, description=f.__doc__, parameters=s)


def run_shortcut (shortcut):
    "Runs given shortcut"
    try:
        os.system ("shortcuts run " + "'" + shortcut +"'")
        return "Sucessfully run shortcut " + shortcut
    except Exception as e:
        print(f"An error occurred: {e}")
        return e
    # return 
run_shortcut ('Send iMessage')

# generate_schema_from_function (run_shortcut)


