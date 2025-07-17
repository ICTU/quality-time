"""Route value injection plugin."""

import inspect
from annotationlib import Format
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from bottle import Bottle, Route


class InjectionPlugin[ValueType]:
    """Plugin to pass a value to route callbacks that accept a specific keyword argument.

    If a callback does not expect such a parameter, no value is passed.
    """

    api = 2

    def __init__(self, value: ValueType, keyword: str) -> None:
        self.value = value
        self.keyword = keyword
        self.name = f"{keyword}-injection"

    def setup(self, app: Bottle) -> None:
        """Make sure that other installed plugins don't use the same keyword argument."""
        for other in app.plugins:
            if isinstance(other, self.__class__) and other.keyword == self.keyword:  # pragma: no feature-test-cover
                msg = "InjectionPlugin found another plugin with the same keyword."
                raise RuntimeError(msg)

    def apply[ReturnType](self, callback: Callable[..., ReturnType], context: Route) -> Callable[..., ReturnType]:
        """Apply the plugin to the route."""
        # Override global configuration with route-specific values.
        configuration = context.config.get("injection") or {}
        value = configuration.get("value", self.value)
        keyword = configuration.get("keyword", self.keyword)

        # Test if the original callback accepts a keyword parameter. Ignore it if it does not need a value.
        # Pass annotation_format=Format.STRING so types can be imported under an "if TYPE_CHECKING:" block.
        parameter_names = inspect.signature(context.callback, annotation_format=Format.STRING).parameters.keys()
        if keyword not in parameter_names:
            return callback

        def wrapper(*args, **kwargs) -> ReturnType:
            """Wrap the route."""
            kwargs[keyword] = value
            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper
