class Metric:
    """Base class for metrics."""
    @classmethod
    def name(cls) -> str:
        return cls.__name__
