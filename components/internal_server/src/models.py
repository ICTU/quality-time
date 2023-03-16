import uuid
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class BaseSource(BaseModel):
    value: Optional[str]
    total: Optional[str]
    entities: Optional[list[dict]]
    connection_error: Optional[str]
    parse_error: Optional[str]
    api_url: Optional[str]
    landing_url: Optional[str]
    source_uuid: Optional[str]


class BaseMeasurement(BaseModel):
    metric_uuid: Optional[str]
    report_uuid: Optional[str]
    sources: Optional[list[BaseSource]]
    has_error: Optional[bool]
    start: Optional[datetime]
    end: Optional[datetime]
    count: Optional[dict]
    percentage: Optional[dict]


class DictOfMeasurements(BaseModel):
    measurements: list[BaseMeasurement]


class BaseMetricAttributes(BaseModel):
    type: Optional[str]
    sources: dict
    name: Optional[str]
    scale: str
    unit: Optional[str]
    addition: str
    accept_debt: bool
    debt_target: Optional[str]
    direction: Optional[str]
    target: str
    near_target: str
    tags: Optional[list[str]]


class BaseReport(BaseModel):
    _id: uuid.UUID
    title: str
    report_uuid: str
    subjects: dict
    timestamp: datetime
    delta:	Optional[dict]
    last:	bool


class BaseMetrics(BaseModel):
    __root__: Dict[str, BaseMetricAttributes]