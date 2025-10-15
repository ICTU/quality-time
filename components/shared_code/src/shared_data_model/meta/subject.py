"""Data model subject."""

from pydantic import BaseModel, Field

from .base import DocumentedModel


class SubjectContainer(BaseModel):
    """Base model for subject containers."""

    subjects: dict[str, Subject] = Field(default_factory=dict)

    @property
    def all_subjects(self) -> dict[str, Subject]:
        """Return all subjects, recursively."""
        all_subjects = {**self.subjects}
        for subject in self.subjects.values():
            all_subjects.update(**subject.all_subjects)
        return all_subjects


class Subject(SubjectContainer, DocumentedModel):
    """Base model for subjects."""

    metrics: list[str] = Field(default_factory=list)

    @property
    def all_metrics(self) -> list[str]:  # pragma: no feature-test-cover
        """Return all metrics, recursively."""
        all_metrics = {*self.metrics}
        for subject in self.all_subjects.values():
            all_metrics |= {*subject.metrics}
        return sorted(all_metrics)


SubjectContainer.model_rebuild()
