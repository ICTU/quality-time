class LDAPObject(object):
    """
    Class helper that unpacks a python-ldap search result
    """

    def __init__(self, t) -> None:
        super(object, self).__init__()

        self.dn, attrs = t

        for k, v in attrs.items():
            setattr(
                self, k, [i.decode('utf-8') for i in v]
                if len(v) > 1
                else v[0].decode('utf-8')
            )


class LDAPUserObject(LDAPObject):
    dn: str = None
    cn: str = None
    uid: str = None
