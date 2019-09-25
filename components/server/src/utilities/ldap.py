"""LDAP utility classes."""


class LDAPObject:  # pylint: disable=too-few-public-methods
    """Class helper that unpacks a python-ldap search result."""

    def __init__(self, entry) -> None:
        for key, values in entry.items():
            string_values = [value.decode('utf-8') for value in values]
            setattr(self, key, string_values if len(string_values) > 1 else string_values[0])

    def __getattr__(self, key: str) -> str:
        # Return a default value for non-existing keys
        return ""  # pragma: nocover
