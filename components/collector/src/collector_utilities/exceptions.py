"""Collector exceptions."""

from collections.abc import Collection


class CollectorError(Exception):
    """Something went wrong collecting information."""


class ZipfileError(CollectorError):
    """Zip file does not contain the expected files."""

    def __init__(self, file_extensions: list[str]) -> None:
        super().__init__(f"Zipfile contains no files with extension {' or '.join(file_extensions)}")


class XMLRootElementError(CollectorError):
    """XML root element does not match expected tags."""

    def __init__(self, allowed_root_tags: Collection[str], tag: str) -> None:
        super().__init__(f'The XML root element should be one of "{allowed_root_tags}" but is "{tag}"')


class NotFoundError(CollectorError):
    """Something could not be found."""

    def __init__(self, type_of_thing: str, name_of_thing: str, extra: str = "") -> None:
        message = f"{type_of_thing} '{name_of_thing}' not found"
        if extra:
            message += f". {extra}."
        super().__init__(message)
