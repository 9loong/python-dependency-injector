"""Objects injections unittests."""

import unittest2 as unittest

from objects.injections import Injection
from objects.injections import InitArg
from objects.injections import Attribute
from objects.injections import Method

from objects.providers import NewInstance


class InjectionTest(unittest.TestCase):

    """Injection test cases."""

    def test_init(self):
        """Test Injection creation and initialization."""
        injection = Injection('some_arg_name', 'some_value')
        self.assertEqual(injection.name, 'some_arg_name')
        self.assertEqual(injection.injectable, 'some_value')

    def test_value_with_scalar_injectable(self):
        """Test Injection value property with scalar value."""
        injection = Injection('some_arg_name', 'some_value')
        self.assertEqual(injection.value, 'some_value')

    def test_value_with_provider_injectable(self):
        """Test Injection value property with provider."""
        injection = Injection('some_arg_name', NewInstance(object))
        self.assertIsInstance(injection.value, object)


class InitArgTest(unittest.TestCase):

    """Init arg injection test cases."""

    def test_init(self):
        """Test InitArg creation and initialization."""
        injection = InitArg('some_arg_name', 'some_value')
        self.assertEqual(injection.name, 'some_arg_name')
        self.assertEqual(injection.injectable, 'some_value')


class AttributeTest(unittest.TestCase):

    """Attribute injection test cases."""

    def test_init(self):
        """Test Attribute creation and initialization."""
        injection = Attribute('some_arg_name', 'some_value')
        self.assertEqual(injection.name, 'some_arg_name')
        self.assertEqual(injection.injectable, 'some_value')


class MethodTest(unittest.TestCase):

    """Method injection test cases."""

    def test_init(self):
        """Test Method creation and initialization."""
        injection = Method('some_arg_name', 'some_value')
        self.assertEqual(injection.name, 'some_arg_name')
        self.assertEqual(injection.injectable, 'some_value')
