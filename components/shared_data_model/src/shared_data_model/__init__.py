"""The Quality-time data model."""

from .meta.data_model import DataModel
from .metrics import METRICS
from .scales import SCALES
from .sources import SOURCES
from .subjects import SUBJECTS

DATA_MODEL = DataModel(scales=SCALES, metrics=METRICS, sources=SOURCES, subjects=SUBJECTS)
DATA_MODEL_JSON = DATA_MODEL.json(exclude_none=True)
