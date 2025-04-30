import inspect
import functions


def get_functions(module):
    functions_list = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            sig = inspect.signature(obj)
            functions_list.append({
                "name": name,
                "docstring": inspect.getdoc(obj),
                "signature": [s for s in sig.parameters.values()],
            })
    return functions_list

if __name__ == "__main__":
    functions_list = get_functions(functions)
    print(functions_list)