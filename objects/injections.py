"""Injections module."""

from .utils import is_provider


class Injection(object):

    """Base injection class."""

    __IS_INJECTION__ = True
    __slots__ = ('name', 'injectable')

    def __init__(self, name, injectable):
        """Initializer."""
        self.name = name
        self.injectable = injectable

    @property
    def value(self):
        """Return injectable value."""
        if is_provider(self.injectable):
            return self.injectable()
        return self.injectable


class KwArg(Injection):

    """Keyword argument injection."""

    __IS_KWARG_INJECTION__ = True


class Attribute(Injection):

    """Attribute injection."""

    __IS_ATTRIBUTE_INJECTION__ = True


class Method(Injection):

    """Method injection."""

    __IS_METHOD_INJECTION__ = True
