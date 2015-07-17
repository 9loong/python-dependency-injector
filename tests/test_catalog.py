"""Objects catalog unittests."""

import unittest2 as unittest

from objects.catalog import AbstractCatalog

from objects.providers import Object
from objects.providers import Value

from objects.errors import Error


class CatalogTests(unittest.TestCase):

    """Catalog test cases."""

    class Catalog(AbstractCatalog):

        """Test catalog."""

        obj = Object(object())
        another_obj = Object(object())

    def test_get_used(self):
        """Test retrieving used provider."""
        catalog = self.Catalog(self.Catalog.obj)
        self.assertIsInstance(catalog.obj(), object)

    def test_get_unused(self):
        """Test retrieving unused provider."""
        catalog = self.Catalog()
        self.assertRaises(Error, getattr, catalog, 'obj')

    def test_all_providers(self):
        """Test getting of all catalog providers."""
        self.assertTrue(len(self.Catalog.providers) == 2)

        self.assertIn('obj', self.Catalog.providers)
        self.assertIn(self.Catalog.obj, self.Catalog.providers.values())

        self.assertIn('another_obj', self.Catalog.providers)
        self.assertIn(self.Catalog.another_obj,
                      self.Catalog.providers.values())

    def test_all_providers_by_type(self):
        """Test getting of all catalog providers of specific type."""
        self.assertTrue(len(self.Catalog.filter(Object)) == 2)
        self.assertTrue(len(self.Catalog.filter(Value)) == 0)

    def test_metaclass_with_several_catalogs(self):
        """Test that metaclass work well with several catalogs."""
        class Catalog1(AbstractCatalog):

            """Catalog1."""

            provider = Object(object())

        class Catalog2(AbstractCatalog):

            """Catalog2."""

            provider = Object(object())

        self.assertTrue(len(Catalog1.providers) == 1)
        self.assertIs(Catalog1.provider, Catalog1.providers['provider'])

        self.assertTrue(len(Catalog2.providers) == 1)
        self.assertIs(Catalog2.provider, Catalog2.providers['provider'])

        self.assertIsNot(Catalog1.provider, Catalog2.provider)
