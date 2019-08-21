"""LDAP utility classes."""


class LDAPObject:  # pylint: disable=too-few-public-methods
    """Class helper that unpacks a python-ldap search result."""

    def __init__(self, t) -> None:
        # pylint: disable=invalid-name
        self.dn, attrs = t
        for key, value in attrs.items():
            setattr(self, key, [i.decode('utf-8') for i in value] if len(value) > 1 else value[0].decode('utf-8'))


class LDAPUserObject(LDAPObject):  # pylint: disable=too-few-public-methods
    """Class helper that represents a LDAP user object."""
    # pylint: disable=invalid-name
    dn: str = ""
    cn: str = ""
    uid: str = ""
