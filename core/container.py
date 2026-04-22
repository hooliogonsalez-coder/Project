import logging
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Container:
    def __init__(self):
        self._services: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any] | type] = {}
        self._singletons_created: dict[type, Any] = {}

    def register(self, cls_or_interface: type[T], factory: type[T] | Callable[[], T] | None = None) -> None:
        self._services[cls_or_interface] = None
        self._factories[cls_or_interface] = cls_or_interface if factory is None else factory

    def register_instance(self, cls_or_interface: type[T], instance: T) -> None:
        self._services[cls_or_interface] = instance
        self._factories[cls_or_interface] = instance
        self._singletons_created[cls_or_interface] = instance

    def get(self, cls_or_interface: type[T]) -> T:
        if cls_or_interface in self._singletons_created:
            return self._singletons_created[cls_or_interface]

        if cls_or_interface not in self._factories:
            raise KeyError(f"Service {cls_or_interface.__name__} not registered")

        factory = self._factories[cls_or_interface]

        if callable(factory) and not isinstance(factory, type):
            instance = factory()
        elif isinstance(factory, type):
            instance = self._resolve_dependencies(factory)
        else:
            instance = factory

        self._singletons_created[cls_or_interface] = instance
        return instance

    def _resolve_dependencies(self, cls: type[T]) -> T:
        try:
            import inspect
            sig = inspect.signature(cls.__init__)
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                if param.annotation == inspect.Parameter.empty:
                    continue
                if isinstance(param.annotation, type) and issubclass(param.annotation, ABC):
                    kwargs[param_name] = self.get(param.annotation)
            return cls(**kwargs)
        except (ImportError, AttributeError):
            return cls()

    def has(self, cls_or_interface: type[T]) -> bool:
        return cls_or_interface in self._factories

    def clear(self) -> None:
        self._services.clear()
        self._factories.clear()
        self._singletons_created.clear()


from abc import ABC