"""Route value injection plugin."""

import inspect


class InjectionPlugin:
    """This plugin passes a value to route callbacks that accept a specific keyword argument.

    If a callback does not expect such a parameter, no value is passed.
    """

    api = 2

    def __init__(self, value, keyword: str) -> None:
        self.value = value
        self.keyword = keyword
        self.name = f"{keyword}-injection"

    def setup(self, app) -> None:
        """Make sure that other installed plugins don't use the same keyword argument."""
        for other in app.plugins:
            if isinstance(other, self.__class__) and other.keyword == self.keyword:  # pragma: no cover-behave
                raise RuntimeError("InjectionPlugin found another plugin with the same keyword.")

    def apply(self, callback, context):
        """Apply the plugin to the route."""
        # Override global configuration with route-specific values.
        configuration = context.config.get("injection") or {}
        value = configuration.get("value", self.value)
        keyword = configuration.get("keyword", self.keyword)

        # Test if the original callback accepts a keyword parameter.
        # Ignore it if it does not need a value.
        parameter_names = inspect.signature(context.callback).parameters.keys()
        if keyword not in parameter_names:
            return callback

        def wrapper(*args, **kwargs):
            """Wrap the route."""
            kwargs[keyword] = value
            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper
