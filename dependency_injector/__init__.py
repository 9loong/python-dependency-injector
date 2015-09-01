"""Dependency injector."""

from .catalog import AbstractCatalog
from .catalog import override

from .providers import Provider
from .providers import Delegate
from .providers import Factory
from .providers import Singleton
from .providers import ExternalDependency
from .providers import Class
from .providers import Object
from .providers import Function
from .providers import Value
from .providers import Callable
from .providers import Config

from .injections import Injection
from .injections import KwArg
from .injections import Attribute
from .injections import Method
from .injections import inject

from .utils import is_provider
from .utils import ensure_is_provider
from .utils import is_injection
from .utils import ensure_is_injection
from .utils import is_kwarg_injection
from .utils import is_attribute_injection
from .utils import is_method_injection

from .errors import Error


__all__ = (
    # Catalogs
    'AbstractCatalog',
    'override',

    # Providers
    'Provider',
    'Delegate',
    'Factory',
    'Singleton',
    'ExternalDependency',
    'Class',
    'Object',
    'Function',
    'Value',
    'Callable',
    'Config',

    # Injections
    'Injection',
    'KwArg',
    'Attribute',
    'Method',
    'inject',

    # Utils
    'is_provider',
    'ensure_is_provider',
    'is_injection',
    'ensure_is_injection',
    'is_kwarg_injection',
    'is_attribute_injection',
    'is_method_injection',

    # Errors
    'Error',
)
