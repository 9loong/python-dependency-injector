"""Catalog module."""

import six

from .errors import Error
from .utils import is_provider


class CatalogMetaClass(type):

    """Providers catalog meta class."""

    def __new__(mcs, class_name, bases, attributes):
        """Meta class factory."""
        providers = dict()
        new_attributes = dict()
        for name, value in six.iteritems(attributes):
            if is_provider(value):
                providers[name] = value
            new_attributes[name] = value

        cls = type.__new__(mcs, class_name, bases, new_attributes)
        cls.providers = cls.providers.copy()
        cls.providers.update(providers)
        return cls


@six.add_metaclass(CatalogMetaClass)
class AbstractCatalog(object):

    """Abstract providers catalog."""

    providers = dict()

    __slots__ = ('_used_providers',)

    def __init__(self, *used_providers):
        """Initializer."""
        self._used_providers = set(used_providers)

    def __getattribute__(self, item):
        """Return providers."""
        attribute = super(AbstractCatalog, self).__getattribute__(item)
        if item in ('providers', '_used_providers',):
            return attribute

        if attribute not in self._used_providers:
            raise Error('Provider \'{0}\' '.format(item) +
                        'is not listed in dependencies')
        return attribute

    @classmethod
    def filter(cls, provider_type):
        """Return dict of providers, that are instance of provided type."""
        return dict((name, provider)
                    for name, provider in six.iteritems(cls.providers)
                    if isinstance(provider, provider_type))

    @classmethod
    def override(cls, overriding):
        """Override current catalog providers by overriding catalog providers.

        :type overriding: AbstractCatalog
        """
        for name, provider in six.iteritems(overriding.providers):
            cls.providers[name].override(provider)


def override(catalog):
    """Catalog overriding decorator."""
    def decorator(overriding_catalog):
        """Overriding decorator."""
        catalog.override(overriding_catalog)
        return overriding_catalog
    return decorator
