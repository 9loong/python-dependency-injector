"""Catalogs module."""

import six

from .errors import Error
from .errors import UndefinedProviderError

from .utils import is_provider
from .utils import is_catalog
from .utils import ensure_is_provider
from .utils import ensure_is_catalog_bundle


@six.python_2_unicode_compatible
class CatalogBundle(object):
    """Bundle of catalog providers."""

    catalog = None
    """:type: DeclarativeCatalog"""

    __IS_CATALOG_BUNDLE__ = True
    __slots__ = ('providers', '__dict__')

    def __init__(self, *providers):
        """Initializer."""
        self.providers = dict()
        for provider in providers:
            provider_name = self.catalog.get_provider_bind_name(provider)
            self.providers[provider_name] = provider
        self.__dict__.update(self.providers)
        super(CatalogBundle, self).__init__()

    @classmethod
    def sub_cls_factory(cls, catalog):
        """Create bundle class for catalog.

        :rtype: CatalogBundle
        :return: Subclass of CatalogBundle
        """
        return type('BundleSubclass', (cls,), dict(catalog=catalog))

    def get_provider(self, name):
        """Return provider with specified name or raise an error."""
        try:
            return self.providers[name]
        except KeyError:
            raise Error('Provider "{0}" is not a part of {1}'.format(name,
                                                                     self))

    def has_provider(self, name):
        """Check if there is provider with certain name."""
        return name in self.providers

    def __getattr__(self, item):
        """Raise an error on every attempt to get undefined provider."""
        if item.startswith('__') and item.endswith('__'):
            return super(CatalogBundle, self).__getattr__(item)
        raise UndefinedProviderError('Provider "{0}" is not a part '
                                     'of {1}'.format(item, self))

    def __repr__(self):
        """Return string representation of catalog bundle."""
        return '<{0}.Bundle({1})>'.format(
            self.catalog.name, ', '.join(six.iterkeys(self.providers)))

    __str__ = __repr__


@six.python_2_unicode_compatible
class DynamicCatalog(object):
    """Catalog of providers."""

    __IS_CATALOG__ = True
    __slots__ = ('name', 'providers', 'provider_names', 'overridden_by',
                 'Bundle')

    def __init__(self, **providers):
        """Initializer.

        :type providers: dict[str, dependency_injector.providers.Provider]
        """
        self.name = '.'.join((self.__class__.__module__,
                              self.__class__.__name__))
        self.providers = dict()
        self.provider_names = dict()
        self.overridden_by = tuple()

        self.Bundle = CatalogBundle.sub_cls_factory(self)

        self.bind_providers(providers)

    def is_bundle_owner(self, bundle):
        """Check if catalog is bundle owner."""
        return ensure_is_catalog_bundle(bundle) and bundle.catalog is self

    def get_provider_bind_name(self, provider):
        """Return provider's name in catalog."""
        if not self.is_provider_bound(provider):
            raise Error('Can not find bind name for {0} in catalog {1}'.format(
                provider, self))
        return self.provider_names[provider]

    def is_provider_bound(self, provider):
        """Check if provider is bound to the catalog."""
        return provider in self.provider_names

    def filter(self, provider_type):
        """Return dict of providers, that are instance of provided type."""
        return dict((name, provider)
                    for name, provider in six.iteritems(self.providers)
                    if isinstance(provider, provider_type))

    @property
    def is_overridden(self):
        """Check if catalog is overridden by another catalog."""
        return bool(self.overridden_by)

    @property
    def last_overriding(self):
        """Return last overriding catalog."""
        try:
            return self.overridden_by[-1]
        except (TypeError, IndexError):
            raise Error('Catalog {0} is not overridden'.format(self))

    def override(self, overriding):
        """Override current catalog providers by overriding catalog providers.

        :type overriding: DynamicCatalog
        """
        self.overridden_by += (overriding,)
        for name, provider in six.iteritems(overriding.providers):
            self.get_provider(name).override(provider)

    def reset_last_overriding(self):
        """Reset last overriding catalog."""
        if not self.is_overridden:
            raise Error('Catalog {0} is not overridden'.format(self))
        self.overridden_by = self.overridden_by[:-1]
        for provider in six.itervalues(self.providers):
            provider.reset_last_overriding()

    def reset_override(self):
        """Reset all overridings for all catalog providers."""
        self.overridden_by = tuple()
        for provider in six.itervalues(self.providers):
            provider.reset_override()

    def get_provider(self, name):
        """Return provider with specified name or raise an error."""
        try:
            return self.providers[name]
        except KeyError:
            raise UndefinedProviderError('{0} has no provider with such '
                                         'name - {1}'.format(self, name))

    def bind_provider(self, name, provider):
        """Bind provider to catalog with specified name."""
        provider = ensure_is_provider(provider)

        if name in self.providers:
            raise Error('Catalog {0} already has provider with '
                        'such name - {1}'.format(self, name))
        if provider in self.provider_names:
            raise Error('Catalog {0} already has such provider '
                        'instance - {1}'.format(self, provider))

        self.providers[name] = provider
        self.provider_names[provider] = name

    def bind_providers(self, providers):
        """Bind providers dictionary to catalog."""
        for name, provider in six.iteritems(providers):
            self.bind_provider(name, provider)

    def has_provider(self, name):
        """Check if there is provider with certain name."""
        return name in self.providers

    def __getattr__(self, name):
        """Return provider with specified name or raise en error."""
        return self.get_provider(name)

    def __repr__(self):
        """Return Python representation of catalog."""
        return '<{0}({1})>'.format(self.name,
                                   ', '.join(six.iterkeys(self.providers)))

    __str__ = __repr__


@six.python_2_unicode_compatible
class DeclarativeCatalogMetaClass(type):
    """Declarative catalog meta class."""

    def __new__(mcs, class_name, bases, attributes):
        """Declarative catalog class factory."""
        cls = type.__new__(mcs, class_name, bases, attributes)

        cls_providers = tuple((name, provider)
                              for name, provider in six.iteritems(attributes)
                              if is_provider(provider))

        inherited_providers = tuple((name, provider)
                                    for base in bases if is_catalog(base)
                                    for name, provider in six.iteritems(
                                        base.providers))

        providers = cls_providers + inherited_providers

        cls.name = '.'.join((cls.__module__, cls.__name__))

        cls.catalog = DynamicCatalog()
        cls.catalog.name = cls.name
        cls.catalog.bind_providers(dict(providers))

        cls.cls_providers = dict(cls_providers)
        cls.inherited_providers = dict(inherited_providers)

        cls.Bundle = cls.catalog.Bundle

        return cls

    @property
    def providers(cls):
        """Return dict of catalog's providers."""
        return cls.catalog.providers

    @property
    def overridden_by(cls):
        """Return tuple of overriding catalogs."""
        return cls.catalog.overridden_by

    @property
    def is_overridden(cls):
        """Check if catalog is overridden by another catalog."""
        return cls.catalog.is_overridden

    @property
    def last_overriding(cls):
        """Return last overriding catalog."""
        return cls.catalog.last_overriding

    def __repr__(cls):
        """Return string representation of the catalog."""
        return '<{0}({1})>'.format(cls.name,
                                   ', '.join(six.iterkeys(cls.providers)))

    __str__ = __repr__


@six.add_metaclass(DeclarativeCatalogMetaClass)
class DeclarativeCatalog(object):
    """Declarative catalog catalog of providers.

    :type name: str
    :param name: Catalog's name

    :type catalog: DynamicCatalog
    :param catalog: Instance of dynamic catalog

    :type Bundle: CatalogBundle
    :param Bundle: Catalog's bundle class

    :type providers: dict[str, dependency_injector.Provider]
    :param providers: Dict of all catalog providers, including inherited from
        parent catalogs

    :type cls_providers: dict[str, dependency_injector.Provider]
    :param cls_providers: Dict of current catalog providers

    :type inherited_providers: dict[str, dependency_injector.Provider]
    :param inherited_providers: Dict of providers, that are inherited from
        parent catalogs

    :type overridden_by: tuple[DeclarativeCatalog]
    :param overridden_by: Tuple of overriding catalogs

    :type is_overridden: bool
    :param is_overridden: Read-only, evaluated in runtime, property that is
        set to True if catalog is overridden

    :type last_overriding: DeclarativeCatalog | None
    :param last_overriding: Reference to the last overriding catalog, if any
    """

    Bundle = CatalogBundle

    name = str()

    cls_providers = dict()
    inherited_providers = dict()
    providers = dict()

    overridden_by = tuple()
    is_overridden = bool
    last_overriding = None

    catalog = DynamicCatalog

    __IS_CATALOG__ = True

    @classmethod
    def is_bundle_owner(cls, bundle):
        """Check if catalog is bundle owner."""
        return cls.catalog.is_bundle_owner(bundle)

    @classmethod
    def get_provider_bind_name(cls, provider):
        """Return provider's name in catalog."""
        return cls.catalog.get_provider_bind_name(provider)

    @classmethod
    def is_provider_bound(cls, provider):
        """Check if provider is bound to the catalog."""
        return cls.catalog.is_provider_bound(provider)

    @classmethod
    def filter(cls, provider_type):
        """Return dict of providers, that are instance of provided type."""
        return cls.catalog.filter(provider_type)

    @classmethod
    def override(cls, overriding):
        """Override current catalog providers by overriding catalog providers.

        :type overriding: DeclarativeCatalog | DynamicCatalog
        """
        cls.catalog.override(overriding)

    @classmethod
    def reset_last_overriding(cls):
        """Reset last overriding catalog."""
        cls.catalog.reset_last_overriding()

    @classmethod
    def reset_override(cls):
        """Reset all overridings for all catalog providers."""
        cls.catalog.reset_override()

    @classmethod
    def get(cls, name):
        """Return provider with specified name or raises error."""
        return cls.catalog.get_provider(name)

    @classmethod
    def has(cls, name):
        """Check if there is provider with certain name."""
        return cls.catalog.has_provider(name)


# Backward compatibility for versions < 0.11.*
AbstractCatalog = DeclarativeCatalog


def override(catalog):
    """Catalog overriding decorator."""
    def decorator(overriding_catalog):
        """Overriding decorator."""
        catalog.override(overriding_catalog)
        return overriding_catalog
    return decorator
