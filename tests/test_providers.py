"""Objects providers unittests."""

import unittest2 as unittest
from collections import namedtuple

from objects.providers import Provider
from objects.providers import Delegate
from objects.providers import NewInstance
from objects.providers import Singleton
from objects.providers import Scoped
from objects.providers import ExternalDependency
from objects.providers import Class
from objects.providers import Object
from objects.providers import Function
from objects.providers import Value
from objects.providers import Callable
from objects.providers import Config

from objects.injections import Injection
from objects.injections import InitArg
from objects.injections import Attribute
from objects.injections import Method

from objects.utils import is_provider

from objects.errors import Error


class ProviderTests(unittest.TestCase):

    """Provider test cases."""

    def setUp(self):
        """Set test cases environment up."""
        self.provider = Provider()

    def test_is_provider(self):
        """Test `is_provider` check."""
        self.assertTrue(is_provider(self.provider))

    def test_call(self):
        """Test call."""
        self.assertRaises(NotImplementedError, self.provider.__call__)

    def test_delegate(self):
        """Test creating of provider delegation."""
        delegate1 = self.provider.delegate()

        self.assertIsInstance(delegate1, Delegate)
        self.assertIs(delegate1.delegated, self.provider)

        delegate2 = self.provider.delegate()

        self.assertIsInstance(delegate2, Delegate)
        self.assertIs(delegate2.delegated, self.provider)

        self.assertIsNot(delegate1, delegate2)

    def test_override(self):
        """Test provider overriding."""
        overriding_provider = Provider()
        self.provider.override(overriding_provider)
        self.assertTrue(self.provider.overridden)

    def test_override_with_not_provider(self):
        """Test provider overriding with not provider instance."""
        self.assertRaises(Error, self.provider.override, object())

    def test_last_overriding(self):
        """Test getting last overriding provider."""
        overriding_provider1 = Provider()
        overriding_provider2 = Provider()

        self.provider.override(overriding_provider1)
        self.assertIs(self.provider.last_overriding, overriding_provider1)

        self.provider.override(overriding_provider2)
        self.assertIs(self.provider.last_overriding, overriding_provider2)

    def test_last_overriding_of_not_overridden_provider(self):
        """Test getting last overriding from not overridden provider."""
        try:
            self.provider.last_overriding
        except Error:
            pass
        else:
            self.fail('Got en error in {}'.format(
                str(self.test_last_overriding_of_not_overridden_provider)))


class DelegateTests(unittest.TestCase):

    """Delegate test cases."""

    def setUp(self):
        """Set test cases environment up."""
        self.delegated = Provider()
        self.delegate = Delegate(delegated=self.delegated)

    def test_is_provider(self):
        """Test `is_provider` check."""
        self.assertTrue(is_provider(self.delegate))

    def test_init_with_not_provider(self):
        """Test that delegate accepts only another provider as delegated."""
        self.assertRaises(Error, Delegate, delegated=object())

    def test_call(self):
        """ Test returning of delegated provider."""
        delegated1 = self.delegate()
        delegated2 = self.delegate()

        self.assertIs(delegated1, self.delegated)
        self.assertIs(delegated2, self.delegated)


class NewInstanceTests(unittest.TestCase):

    """NewInstance test cases."""

    class Example(object):

        """Example class for NewInstance provider tests."""

        def __init__(self, init_arg1=None, init_arg2=None):
            """Initializer.

            :param init_arg1:
            :param init_arg2:
            :return:
            """
            self.init_arg1 = init_arg1
            self.init_arg2 = init_arg2

            self.attribute1 = None
            self.attribute2 = None

            self.method1_value = None
            self.method2_value = None

        def method1(self, value):
            """Setter method 1."""
            self.method1_value = value

        def method2(self, value):
            """Setter method 2."""
            self.method2_value = value

    def test_is_provider(self):
        """Test `is_provider` check."""
        self.assertTrue(is_provider(NewInstance(self.Example)))

    def test_init_with_not_class(self):
        """Test creation of provider with not a class."""
        self.assertRaises(Error, NewInstance, 123)

    def test_call(self):
        """Test creation of new instances."""
        provider = NewInstance(self.Example)
        instance1 = provider()
        instance2 = provider()

        self.assertIsNot(instance1, instance2)
        self.assertIsInstance(instance1, self.Example)
        self.assertIsInstance(instance2, self.Example)

    def test_call_with_init_args(self):
        """Test creation of new instances with init args injections."""
        provider = NewInstance(self.Example,
                               InitArg('init_arg1', 'i1'),
                               InitArg('init_arg2', 'i2'))

        instance1 = provider()
        instance2 = provider()

        self.assertEqual(instance1.init_arg1, 'i1')
        self.assertEqual(instance1.init_arg2, 'i2')

        self.assertEqual(instance2.init_arg1, 'i1')
        self.assertEqual(instance2.init_arg2, 'i2')

        self.assertIsNot(instance1, instance2)
        self.assertIsInstance(instance1, self.Example)
        self.assertIsInstance(instance2, self.Example)

    def test_call_with_attributes(self):
        """Test creation of new instances with attribute injections."""
        provider = NewInstance(self.Example,
                               Attribute('attribute1', 'a1'),
                               Attribute('attribute2', 'a2'))

        instance1 = provider()
        instance2 = provider()

        self.assertEqual(instance1.attribute1, 'a1')
        self.assertEqual(instance1.attribute2, 'a2')

        self.assertEqual(instance2.attribute1, 'a1')
        self.assertEqual(instance2.attribute2, 'a2')

        self.assertIsNot(instance1, instance2)
        self.assertIsInstance(instance1, self.Example)
        self.assertIsInstance(instance2, self.Example)

    def test_call_with_methods(self):
        """Test creation of new instances with method injections."""
        provider = NewInstance(self.Example,
                               Method('method1', 'm1'),
                               Method('method2', 'm2'))

        instance1 = provider()
        instance2 = provider()

        self.assertEqual(instance1.method1_value, 'm1')
        self.assertEqual(instance1.method2_value, 'm2')

        self.assertEqual(instance2.method1_value, 'm1')
        self.assertEqual(instance2.method2_value, 'm2')

        self.assertIsNot(instance1, instance2)
        self.assertIsInstance(instance1, self.Example)
        self.assertIsInstance(instance2, self.Example)

    def test_call_with_context_args(self):
        """Test creation of new instances with context args."""
        provider = NewInstance(self.Example)
        instance = provider(11, 22)

        self.assertEqual(instance.init_arg1, 11)
        self.assertEqual(instance.init_arg2, 22)

    def test_call_with_context_kwargs(self):
        """Test creation of new instances with context kwargs."""
        provider = NewInstance(self.Example,
                               InitArg('init_arg1', 1))

        instance1 = provider(init_arg2=22)
        self.assertEqual(instance1.init_arg1, 1)
        self.assertEqual(instance1.init_arg2, 22)

        instance1 = provider(init_arg1=11, init_arg2=22)
        self.assertEqual(instance1.init_arg1, 11)
        self.assertEqual(instance1.init_arg2, 22)

    def test_call_overridden(self):
        """Test creation of new instances on overridden provider."""
        provider = NewInstance(self.Example)
        overriding_provider1 = NewInstance(dict)
        overriding_provider2 = NewInstance(list)

        provider.override(overriding_provider1)
        provider.override(overriding_provider2)

        instance1 = provider()
        instance2 = provider()

        self.assertIsNot(instance1, instance2)
        self.assertIsInstance(instance1, list)
        self.assertIsInstance(instance2, list)


class SingletonTests(unittest.TestCase):

    """Singleton test cases."""

    def test_call(self):
        """Test creation and returning of single object."""
        provider = Singleton(object)

        instance1 = provider()
        instance2 = provider()

        self.assertIsInstance(instance1, object)
        self.assertIsInstance(instance2, object)
        self.assertIs(instance1, instance2)

    def test_reset(self):
        """Test creation and reset of single object."""
        provider = Singleton(object)

        instance1 = provider()
        self.assertIsInstance(instance1, object)

        provider.reset()

        instance2 = provider()
        self.assertIsInstance(instance1, object)

        self.assertIsNot(instance1, instance2)


class ScopedTests(unittest.TestCase):

    """Scoped test cases."""

    APPLICATION_SCOPE = 'application'
    REQUEST_SCOPE = 'request'

    def setUp(self):
        """Set test cases environment up."""
        self.provider = Scoped(object)

    def test_call(self):
        """Test creation and returning of scope single object."""
        self.provider.in_scope(self.APPLICATION_SCOPE)

        instance1 = self.provider()
        instance2 = self.provider()

        self.assertIsInstance(instance1, object)
        self.assertIsInstance(instance2, object)
        self.assertIs(instance1, instance2)

    def test_call_several_scopes(self):
        """Test creation of several scopes instances."""
        self.provider.in_scope(self.APPLICATION_SCOPE)
        app_instance1 = self.provider()
        app_instance2 = self.provider()

        self.provider.in_scope(self.REQUEST_SCOPE)
        request_instance1 = self.provider()
        request_instance2 = self.provider()

        self.assertIsInstance(app_instance1, object)
        self.assertIsInstance(app_instance2, object)
        self.assertIs(app_instance1, app_instance2)

        self.assertIsInstance(request_instance1, object)
        self.assertIsInstance(request_instance2, object)
        self.assertIs(request_instance1, request_instance2)

        self.provider.in_scope(self.APPLICATION_SCOPE)
        app_instance3 = self.provider()
        self.assertIsInstance(app_instance3, object)
        self.assertIs(app_instance3, app_instance1)
        self.assertIs(app_instance3, app_instance2)

        self.provider.in_scope(self.REQUEST_SCOPE)
        request_instance3 = self.provider()
        self.assertIsInstance(request_instance3, object)
        self.assertIs(request_instance3, request_instance1)
        self.assertIs(request_instance3, request_instance2)

    def test_call_not_in_scope(self):
        """Test creation of instance with no active scope."""
        self.assertRaises(Error, self.provider)

    def test_call_in_out_scope(self):
        """Test creation of instances within in and out of scope."""
        self.provider.in_scope(self.REQUEST_SCOPE)
        instance1 = self.provider()
        instance2 = self.provider()
        self.provider.out_of_scope(self.REQUEST_SCOPE)

        self.provider.in_scope(self.REQUEST_SCOPE)
        instance3 = self.provider()
        instance4 = self.provider()
        self.provider.out_of_scope(self.REQUEST_SCOPE)

        self.assertIs(instance1, instance2)
        self.assertIs(instance3, instance4)

        self.assertIsNot(instance1, instance3)
        self.assertIsNot(instance2, instance3)

        self.assertIsNot(instance1, instance4)
        self.assertIsNot(instance2, instance4)

    def test_out_of_scope(self):
        """Test call `out_of_scope()` on provider that has no such scope."""
        self.assertRaises(Error,
                          self.provider.out_of_scope,
                          self.REQUEST_SCOPE)


class ExternalDependencyTests(unittest.TestCase):

    """ExternalDependency test cases."""

    def test_call_satisfied(self):
        """Test call of satisfied external dependency."""
        provider = ExternalDependency(instance_of=object)
        provider.satisfy(NewInstance(object))
        self.assertIsInstance(provider(), object)

    def test_call_satisfied_but_not_instance_of(self):
        """Test call of satisfied external dependency, but not instance of."""
        provider = ExternalDependency(instance_of=list)
        provider.satisfy(NewInstance(dict))
        self.assertRaises(Error, provider)

    def test_call_not_satisfied(self):
        """Test call of not satisfied external dependency."""
        provider = ExternalDependency(instance_of=object)
        self.assertRaises(Error, provider)


class StaticProvidersTests(unittest.TestCase):

    """Static providers test cases."""

    def test_is_provider(self):
        """Test `is_provider` check."""
        self.assertTrue(is_provider(Class(object)))
        self.assertTrue(is_provider(Object(object())))
        self.assertTrue(is_provider(Function(map)))
        self.assertTrue(is_provider(Value(123)))

    def test_call_class_provider(self):
        """Test Class provider call."""
        self.assertIs(Class(dict)(), dict)

    def test_call_object_provider(self):
        """Test Object provider call."""
        obj = object()
        self.assertIs(Object(obj)(), obj)

    def test_call_function_provider(self):
        """Test Function provider call."""
        self.assertIs(Function(map)(), map)

    def test_call_value_provider(self):
        """Test Value provider call."""
        self.assertEqual(Value(123)(), 123)

    def test_call_overridden_class_provider(self):
        """Test overridden Class provider call."""
        cls_provider = Class(dict)
        cls_provider.override(Object(list))
        self.assertIs(cls_provider(), list)

    def test_call_overridden_object_provider(self):
        """Test overridden Object provider call."""
        obj1 = object()
        obj2 = object()
        obj_provider = Object(obj1)
        obj_provider.override(Object(obj2))
        self.assertIs(obj_provider(), obj2)

    def test_call_overridden_function_provider(self):
        """Test overridden Function provider call."""
        function_provider = Function(map)
        function_provider.override(Function(reduce))
        self.assertIs(function_provider(), reduce)

    def test_call_overridden_value_provider(self):
        """Test overridden Value provider call."""
        value_provider = Value(123)
        value_provider.override(Value(321))
        self.assertEqual(value_provider(), 321)


class CallableTests(unittest.TestCase):

    """Callable test cases."""

    def example(self, arg1, arg2, arg3):
        """Example callback."""
        return arg1, arg2, arg3

    def setUp(self):
        """Set test cases environment up."""
        self.provider = Callable(self.example,
                                 Injection('arg1', 'a1'),
                                 Injection('arg2', 'a2'),
                                 Injection('arg3', 'a3'))

    def test_is_provider(self):
        """Test `is_provider` check."""
        self.assertTrue(is_provider(Callable(map)))

    def test_call(self):
        """Test provider call."""
        self.assertEqual(self.provider(), ('a1', 'a2', 'a3'))

    def test_call_with_args(self):
        """Test provider call with kwargs priority."""
        provider = Callable(self.example,
                            Injection('arg3', 'a3'))
        self.assertEqual(provider(1, 2), (1, 2, 'a3'))

    def test_call_with_kwargs_priority(self):
        """Test provider call with kwargs priority."""
        self.assertEqual(self.provider(arg1=1, arg3=3), (1, 'a2', 3))

    def test_call_overridden(self):
        """Test overridden provider call."""
        overriding_provider1 = Value((1, 2, 3))
        overriding_provider2 = Value((3, 2, 1))

        self.provider.override(overriding_provider1)
        self.provider.override(overriding_provider2)

        result1 = self.provider()
        result2 = self.provider()

        self.assertEqual(result1, (3, 2, 1))
        self.assertEqual(result2, (3, 2, 1))
