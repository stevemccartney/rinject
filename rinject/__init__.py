import inspect
import logging
from functools import partial
from typing import Callable, Hashable, Any


class Injector:
    def __init__(self, logger: Callable = logging.debug):
        """
        _bindings is a map of any hashable object to a callable that 'resolves' that object
        """
        self._bindings = {}
        self._logger = logger
        self.register_value(Injector, self)

    def inject(self, injection_target: Callable, *args, _partial=False, **kwargs):
        assert callable(injection_target)

        if inspect.isclass(injection_target):
            sig = inspect.signature(injection_target.__init__, follow_wrapped=True)
        else:
            sig = inspect.signature(injection_target, follow_wrapped=True)
        bound_args = sig.bind_partial(*args, **kwargs)  #  type: inspect.BoundArguments
        self._logger(f"bound args {bound_args.arguments}")
        for name, parameter in sig.parameters.items():
            if name in bound_args.arguments:
                self._logger(f"parameter {name} = {bound_args.arguments}")
                continue

            self._logger(f"parameter {name} is not supplied, searching for a binding")
            if parameter.annotation is not inspect.Signature.empty:
                try:
                    value = self.resolve(parameter.annotation)
                except KeyError:
                    pass
                else:
                    bound_args.arguments[name] = value
                    self._logger(f"parameter {name} bound to annotation key {parameter.annotation} = {value}")
                    continue

            try:
                value = self.resolve(name)
            except KeyError:
                pass
            else:
                bound_args.arguments[name] = value
                self._logger(f"parameter {name} bound to name key {name} = {value}")
                continue

            if (
                not (parameter.VAR_KEYWORD or parameter.VAR_POSITIONAL)
                and parameter.default is inspect.Signature.empty
            ):
                raise TypeError(
                    f"injection target: {injection_target}, args={args}, kwargs={kwargs} could not match "
                    f"parameter {parameter.name} with annotation {parameter.annotation} which "
                    f"has no entry for either the name or annotation and no default value "
                )

        if _partial is True:
            return partial(injection_target, *bound_args.args, **bound_args.kwargs)
        else:
            return injection_target(*bound_args.args, **bound_args.kwargs)

    def defer(self, func):
        """Wrap a call to inject so it can be deferred"""

        def wrap(*a, **kw):
            return self.inject(func, *a, **kw)

        return wrap

    def resolve(self, binding_key: Hashable) -> Any:
        """
        Resolve and return a single instance of an object or callable
        Raises a KeyError if the binding_key is not mapped
        """
        binding = self._bindings[binding_key](self)
        return binding

    def partial(self, injection_target: Callable, *args, **kwargs):
        """
        Return a partially applied instance of an object or callable
        """
        return self.inject(injection_target=injection_target, _partial=True, *args, **kwargs)

    def register(self, key: Hashable, provider: Callable):
        """
        Register a provider callable against a hashable key.
        The key is typically a type or a name so 'user_service' or UserService.
        A string key may also contain a double-underscore to indicate a get()
        """
        self._bindings[key] = provider
        self._logger(f"{self} registered provider {key} = {provider}")

    def register_value(self, key: Hashable, value: Any):
        self._bindings[key] = ValueProvider(value)
        self._logger(f"{self} registered ValueProvider {key} = {value}")

    def register_factory(self, key: Hashable, factory: Callable):
        self._bindings[key] = FactoryProvider(factory)
        self._logger(f"{self} registered FactoryProvider {key} = {factory}")

    def register_instance(self, key: Hashable, factory: Callable):
        self._bindings[key] = InstanceProvider(factory)
        self._logger(f"{self} registered InstanceProvider {key} = {factory}")


class FactoryProvider:
    def __init__(self, fn: Callable):
        self._fn = fn

    def __call__(self, injector: Injector):
        return injector.inject(self._fn)


class InstanceProvider:
    def __init__(self, fn: Callable):
        self._value = None
        self._instantiated = False
        self._fn = fn

    def __call__(self, injector: Injector):
        if not self._instantiated:
            self._value = injector.inject(self._fn)
            self._instantiated = True
        return self._value


class ValueProvider:
    def __init__(self, value: Any):
        self._value = value

    def __call__(self, injector: Injector):
        return self._value
