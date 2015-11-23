"""Providers module."""

import six

from .injections import _parse_args_injections
from .injections import _parse_kwargs_injections
from .injections import _get_injectable_args
from .injections import _get_injectable_kwargs

from .utils import ensure_is_provider
from .utils import is_attribute_injection
from .utils import is_method_injection
from .utils import GLOBAL_LOCK

from .errors import Error


class Provider(object):
    """Base provider class.

    :py:class:`Provider` is callable (implements ``__call__`` method). Every
    call to provider object returns provided result, according to the providing
    strategy of particular provider. This ``callable`` functionality is a
    regular part of providers API and it should be the same for all provider's
    subclasses.

    :py:class:`Provider` implements provider overriding logic that should be
    also common for all providers.

    Implementation of particular providing strategy should be done in
    :py:meth:`Provider._provide` of :py:class:`Provider` subclass. Current
    method is called every time when not overridden provider is called.

    All providers should extend this class.
    """

    __IS_PROVIDER__ = True
    __slots__ = ('overridden_by',)

    def __init__(self):
        """Initializer."""
        self.overridden_by = None

    def __call__(self, *args, **kwargs):
        """Return provided instance.

        Implementation of current method adds ``callable`` functionality for
        providers API and it should be common for all provider's subclasses.
        Also this method implements provider overriding logic that is also
        common for all providers. Implementation of particular providing
        strategy should be done in :py:meth:`Provider._provide` of
        :py:class:`Provider` subclass.
        """
        if self.overridden_by:
            return self.last_overriding(*args, **kwargs)
        return self._provide(*args, **kwargs)

    def _provide(self, *args, **kwargs):
        """Providing strategy implementation.

        Abstract protected method that implements providing strategy of
        particular provider. Current method is called every time when not
        overridden provider is called. Need to be overridden in subclasses.
        """
        raise NotImplementedError()

    @property
    def is_overridden(self):
        """Read-only property that is set to ``True`` if provider is overridden.

        :rtype: bool
        """
        return bool(self.overridden_by)

    @property
    def last_overriding(self):
        """Read-only reference to the last overriding provider, if any.

        :type: :py:class:`Provider`
        """
        try:
            return self.overridden_by[-1]
        except (TypeError, IndexError):
            raise Error('Provider {0} is not overridden'.format(str(self)))

    def override(self, provider):
        """Override provider with another provider.

        :param provider: overriding provider
        :type provider: :py:class:`Provider`

        :raise: :py:exc:`dependency_injector.errors.Error`
        """
        if provider is self:
            raise Error('Provider {0} could not be overridden '
                        'with itself'.format(self))
        if not self.is_overridden:
            self.overridden_by = (ensure_is_provider(provider),)
        else:
            self.overridden_by += (ensure_is_provider(provider),)

    def reset_last_overriding(self):
        """Reset last overriding provider.

        :rtype: None
        """
        if not self.is_overridden:
            raise Error('Provider {0} is not overridden'.format(str(self)))
        self.overridden_by = self.overridden_by[:-1]

    def reset_override(self):
        """Reset all overriding providers.

        :rtype: None
        """
        self.overridden_by = None

    def delegate(self):
        """Return provider's delegate.

        :rtype: :py:class:`Delegate`
        """
        return Delegate(self)


class Delegate(Provider):
    """Provider's delegate."""

    __slots__ = ('delegated',)

    def __init__(self, delegated):
        """Initializer.

        :type delegated: Provider
        """
        self.delegated = ensure_is_provider(delegated)
        super(Delegate, self).__init__()

    def _provide(self, *args, **kwargs):
        """Return provided instance.

        :param args: tuple of context positional arguments
        :type args: tuple[object]

        :param kwargs: dictionary of context keyword arguments
        :type kwargs: dict[str, object]

        :rtype: object
        """
        return self.delegated


class Factory(Provider):
    """:py:class:`Factory` provider creates new instance on every call.

    :py:class:`Factory` supports different syntaxes of passing injections:

    + simplified one syntax for passing positional and keyword argument
      injections only:

    .. code-block:: python

        factory = Factory(SomeClass, 'arg1', 'arg2', arg3=3, arg4=4)

    - extended (full) one syntax for passing any type of injections:

    .. code-block:: python

        factory = Factory(SomeClass,
                          injections.Arg(1),
                          injections.Arg(2),
                          injections.KwArg('some_arg', 3),
                          injections.KwArg('other_arg', 4),
                          injections.Attribute('some_attribute', 5))

    Retrieving of provided instance can be performed via calling
    :py:class:`Factory` object:

    .. code-block:: python

        factory = Factory(SomeClass,
                          some_arg1=1,
                          some_arg2=2)
        some_object = factory()
    """

    __slots__ = ('provides', 'args', 'kwargs', 'attributes', 'methods')

    def __init__(self, provides, *args, **kwargs):
        """Initializer.

        :param provides: Class or other callable that provides object
            for creation.
        :type provides: type | callable

        :param args: Tuple of injections.
        :type args: tuple

        :param kwargs: Dictionary of injections.
        :type kwargs: dict
        """
        if not callable(provides):
            raise Error('Factory provider expects to get callable, ' +
                        'got {0} instead'.format(str(provides)))
        self.provides = provides
        """Class or other callable that provides object for creation.

        :type: type | callable
        """

        self.args = _parse_args_injections(args)
        """Tuple of positional argument injections.

        :type: tuple[:py:class:`dependency_injector.injections.Arg`]
        """

        self.kwargs = _parse_kwargs_injections(args, kwargs)
        """Tuple of keyword argument injections.

        :type: tuple[:py:class:`dependency_injector.injections.KwArg`]
        """

        self.attributes = tuple(injection
                                for injection in args
                                if is_attribute_injection(injection))
        """Tuple of attribute injections.

        :type: tuple[:py:class:`dependency_injector.injections.Attribute`]
        """

        self.methods = tuple(injection
                             for injection in args
                             if is_method_injection(injection))
        """Tuple of method injections.

        :type: tuple[:py:class:`dependency_injector.injections.Method`]
        """

        super(Factory, self).__init__()

    @property
    def injections(self):
        """Read-only tuple of all injections.

        :rtype: tuple[:py:class:`dependency_injector.injections.Injection`]
        """
        return self.args + self.kwargs + self.attributes + self.methods

    def _provide(self, *args, **kwargs):
        """Return provided instance.

        :param args: tuple of context positional arguments
        :type args: tuple[object]

        :param kwargs: dictionary of context keyword arguments
        :type kwargs: dict[str, object]

        :rtype: object
        """
        instance = self.provides(*_get_injectable_args(args, self.args),
                                 **_get_injectable_kwargs(kwargs, self.kwargs))
        for attribute in self.attributes:
            setattr(instance, attribute.name, attribute.value)
        for method in self.methods:
            getattr(instance, method.name)(method.value)

        return instance


class Singleton(Provider):
    """Singleton provider.

    Singleton provider will create instance once and return it on every call.
    """

    __slots__ = ('instance', 'factory')

    def __init__(self, provides, *args, **kwargs):
        """Initializer."""
        self.instance = None
        self.factory = Factory(provides, *args, **kwargs)
        super(Singleton, self).__init__()

    def _provide(self, *args, **kwargs):
        """Return provided instance."""
        with GLOBAL_LOCK:
            if not self.instance:
                self.instance = self.factory(*args, **kwargs)
        return self.instance

    def reset(self):
        """Reset instance."""
        self.instance = None

    @property
    def injections(self):
        """Return tuple of all injections."""
        return self.factory.injections


class ExternalDependency(Provider):
    """External dependency provider.

    Those provider is used when dependency obviously have to be overridden by
    the client's code, but it's interface is known.
    """

    __slots__ = ('instance_of',)

    def __init__(self, instance_of):
        """Initializer."""
        if not isinstance(instance_of, six.class_types):
            raise Error('ExternalDependency provider expects to get class, ' +
                        'got {0} instead'.format(str(instance_of)))
        self.instance_of = instance_of
        super(ExternalDependency, self).__init__()

    def __call__(self, *args, **kwargs):
        """Return provided instance."""
        if not self.is_overridden:
            raise Error('Dependency is not defined')

        instance = self.last_overriding(*args, **kwargs)

        if not isinstance(instance, self.instance_of):
            raise Error('{0} is not an '.format(instance) +
                        'instance of {0}'.format(self.instance_of))

        return instance

    def provided_by(self, provider):
        """Set external dependency provider."""
        return self.override(provider)


class StaticProvider(Provider):
    """Static provider.

    Static provider is base implementation that provides exactly the same as
    it got on input.
    """

    __slots__ = ('provides',)

    def __init__(self, provides):
        """Initializer."""
        self.provides = provides
        super(StaticProvider, self).__init__()

    def _provide(self, *args, **kwargs):
        """Return provided instance."""
        return self.provides


class Class(StaticProvider):
    """Class provider provides class."""


class Object(StaticProvider):
    """Object provider provides object."""


class Function(StaticProvider):
    """Function provider provides function."""


class Value(StaticProvider):
    """Value provider provides value."""


class Callable(Provider):
    """Callable provider.

    Callable provider provides callable that is called on every provider call
    with some predefined dependency injections.
    """

    __slots__ = ('callback', 'args', 'kwargs')

    def __init__(self, callback, *args, **kwargs):
        """Initializer."""
        if not callable(callback):
            raise Error('Callable expected, got {0}'.format(str(callback)))
        self.callback = callback
        self.args = _parse_args_injections(args)
        self.kwargs = _parse_kwargs_injections(args, kwargs)
        super(Callable, self).__init__()

    def _provide(self, *args, **kwargs):
        """Return provided instance."""
        return self.callback(*_get_injectable_args(args, self.args),
                             **_get_injectable_kwargs(kwargs, self.kwargs))

    @property
    def injections(self):
        """Return tuple of all injections."""
        return self.args + self.kwargs


class Config(Provider):
    """Config provider.

    Config provider provides dict values. Also config provider creates
    child config objects for all undefined attribute calls. It makes possible
    to create deferred config value provider.
    """

    __slots__ = ('value',)

    def __init__(self, value=None):
        """Initializer."""
        if not value:
            value = dict()
        self.value = value
        super(Config, self).__init__()

    def __getattr__(self, item):
        """Return instance of deferred config."""
        return ChildConfig(parents=(item,), root_config=self)

    def _provide(self, paths=None):
        """Return provided instance."""
        value = self.value
        if paths:
            for path in paths:
                try:
                    value = value[path]
                except KeyError:
                    raise Error('Config key '
                                '"{0}" is undefined'.format('.'.join(paths)))
        return value

    def update_from(self, value):
        """Update current value from another one."""
        self.value.update(value)


class ChildConfig(Provider):
    """Child config provider.

    Child config provide an value from the root config object according to
    the current path in the config tree.
    """

    __slots__ = ('parents', 'root_config')

    def __init__(self, parents, root_config):
        """Initializer."""
        self.parents = parents
        self.root_config = root_config
        super(ChildConfig, self).__init__()

    def __getattr__(self, item):
        """Return instance of deferred config."""
        return ChildConfig(parents=self.parents + (item,),
                           root_config=self.root_config)

    def _provide(self, *args, **kwargs):
        """Return provided instance."""
        return self.root_config(self.parents)
