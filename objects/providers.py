"""
Standard providers.
"""

from .injections import InitArg, Attribute, Method


class Provider(object):
    """
    Base provider class.
    """

    __is_objects_provider__ = True

    def __call__(self, *args, **kwargs):
        """
        Returns provided instance.
        """
        raise NotImplementedError()


def prepare_injections(injections):
    """
    Prepares injections list to injection.
    """
    return [(injection.name, injection.value) for injection in injections]


def fetch_injections(injections, injection_type):
    """
    Fetches injections of injection type from list.
    """
    return tuple([injection
                  for injection in injections
                  if isinstance(injection, injection_type)])


class NewInstance(Provider):
    """
    New instance providers will create and return new instance on every call.
    """

    def __init__(self, provides, *injections):
        """
        Initializer.
        """
        self.provides = provides
        self.init_injections = fetch_injections(injections, InitArg)
        self.attribute_injections = fetch_injections(injections, Attribute)
        self.method_injections = fetch_injections(injections, Method)

    def __call__(self, *args, **kwargs):
        """
        Returns provided instance.
        """
        init_injections = prepare_injections(self.init_injections)
        init_injections = dict(init_injections)
        init_injections.update(kwargs)

        provided = self.provides(*args, **init_injections)

        attribute_injections = prepare_injections(self.attribute_injections)
        for name, injectable in attribute_injections:
            setattr(provided, name, injectable)

        method_injections = prepare_injections(self.method_injections)
        for name, injectable in method_injections:
            getattr(provided, name)(injectable)

        return provided


class Singleton(NewInstance):
    """
    Singleton provider will create instance once and return it on every call.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializer.
        """
        self.instance = None
        super(Singleton, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Returns provided instance.
        """
        if not self.instance:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance


class _StaticProvider(Provider):
    """
    Static provider is base implementation that provides exactly the same as
    it got on input.
    """

    def __init__(self, provides):
        """
        Initializer.
        """
        self.provides = provides

    def __call__(self):
        """
        Returns provided instance.
        """
        return self.provides


class Class(_StaticProvider):
    """
    Class provider provides class.
    """


class Object(_StaticProvider):
    """
    Object provider provides object.
    """


class Function(_StaticProvider):
    """
    Function provider provides function.
    """


class Value(_StaticProvider):
    """
    Value provider provides value.
    """
