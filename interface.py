import inspect
from typing import TypeVar

T = TypeVar("T", bound=type)

class interface:
    """
    Represents the base type for all interfaces. Provides the structural type checking via the `@implements` decorator.

    Note:
        This class cannot be instantiated and will raise a `RuntimeError` on attempt.
    """
    def __init__(self):
        raise RuntimeError("Cannot create an instance of an 'interface' type.")

def implements(interface_type : type[interface]):
    """
    A decorator for classes that simulate interface implementations. A class that is decorated with `@implements(<InterfaceType>)`,
    is forced to define all the methods that are declared in the specified interface type, to avoid the raise of a `NotImplementedException`.

    An interface must be a class that derives from the `interface` base type.

    Example:
        >>> class ILogger(interface):
        ...    def print(self, message):
        ...        pass
        ...
        >>> @implements(ILogger)
        ... class Consumer:
        ...    def print(self, message):
        ...        print(message)
        ...

    Notes:
        - A class can implement multiple interfaces by stacking multiple decorators.
        - The validation only checks the method signature (name and parameters).
          Any implementation defined within an interface method is ignored.

    Args:
        interface_type: a type that derives from `interface`.

    Raises:
        TypeError: If the given type is not an interface type.
        NotImplementedError: If a required method is missing.
    """
    if not issubclass(interface_type, interface):
        raise TypeError(f"The class '{interface_type.__name__}' is not an interface type.")

    def decorator(class_type : T) -> T:
        interface_funcs = inspect.getmembers(interface_type, predicate=inspect.isfunction)

        for itf_func_name, itf_func in interface_funcs:
            if itf_func_name.startswith("__"):
                continue

            itf_func_signature = inspect.signature(itf_func)
            itf_func_params_count = len(itf_func_signature.parameters)

            class_func = getattr(class_type, itf_func_name, None)

            if class_func is None:
                raise NotImplementedError(f"The class '{class_type.__name__}' does not implement '{interface_type.__name__}.{itf_func_name}{itf_func_signature}'")
            
            class_func_params_count = len(inspect.signature(class_func).parameters)

            if itf_func_params_count != class_func_params_count:
                raise NotImplementedError(f"The class '{class_type.__name__}' does not implement '{interface_type.__name__}.{itf_func_name}{itf_func_signature}'")

        return class_type
    
    return decorator