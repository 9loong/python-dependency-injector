"""Dependency injector catalog unittests."""

import unittest2 as unittest
import dependency_injector as di


class CatalogA(di.DeclarativeCatalog):
    """Test catalog A."""

    p11 = di.Provider()
    p12 = di.Provider()


class CatalogB(CatalogA):
    """Test catalog B."""

    p21 = di.Provider()
    p22 = di.Provider()


class CatalogC(CatalogB):
    """Test catalog C."""

    p31 = di.Provider()
    p32 = di.Provider()


class CatalogsInheritanceTests(unittest.TestCase):
    """Catalogs inheritance tests."""

    def test_cls_providers(self):
        """Test `di.DeclarativeCatalog.cls_providers` contents."""
        self.assertDictEqual(CatalogA.cls_providers,
                             dict(p11=CatalogA.p11,
                                  p12=CatalogA.p12))
        self.assertDictEqual(CatalogB.cls_providers,
                             dict(p21=CatalogB.p21,
                                  p22=CatalogB.p22))
        self.assertDictEqual(CatalogC.cls_providers,
                             dict(p31=CatalogC.p31,
                                  p32=CatalogC.p32))

    def test_inherited_providers(self):
        """Test `di.DeclarativeCatalog.inherited_providers` contents."""
        self.assertDictEqual(CatalogA.inherited_providers, dict())
        self.assertDictEqual(CatalogB.inherited_providers,
                             dict(p11=CatalogA.p11,
                                  p12=CatalogA.p12))
        self.assertDictEqual(CatalogC.inherited_providers,
                             dict(p11=CatalogA.p11,
                                  p12=CatalogA.p12,
                                  p21=CatalogB.p21,
                                  p22=CatalogB.p22))

    def test_providers(self):
        """Test `di.DeclarativeCatalog.inherited_providers` contents."""
        self.assertDictEqual(CatalogA.providers,
                             dict(p11=CatalogA.p11,
                                  p12=CatalogA.p12))
        self.assertDictEqual(CatalogB.providers,
                             dict(p11=CatalogA.p11,
                                  p12=CatalogA.p12,
                                  p21=CatalogB.p21,
                                  p22=CatalogB.p22))
        self.assertDictEqual(CatalogC.providers,
                             dict(p11=CatalogA.p11,
                                  p12=CatalogA.p12,
                                  p21=CatalogB.p21,
                                  p22=CatalogB.p22,
                                  p31=CatalogC.p31,
                                  p32=CatalogC.p32))


class CatalogProvidersBindingTests(unittest.TestCase):
    """Catalog providers binding test cases."""

    def test_provider_is_bound(self):
        """Test that providers are bound to the catalogs."""
        self.assertIs(CatalogA.p11.bind.catalog, CatalogA)
        self.assertEquals(CatalogA.p11.bind.name, 'p11')

        self.assertIs(CatalogA.p12.bind.catalog, CatalogA)
        self.assertEquals(CatalogA.p12.bind.name, 'p12')

    def test_provider_rebinding(self):
        """Test that provider could not be bound twice."""
        self.assertRaises(di.Error, type, 'TestCatalog',
                          (di.DeclarativeCatalog,),
                          dict(some_name=CatalogA.p11))


class CatalogBundleTests(unittest.TestCase):
    """Catalog bundle test cases."""

    def setUp(self):
        """Set test environment up."""
        self.bundle = CatalogC.Bundle(CatalogC.p11,
                                      CatalogC.p12)

    def test_get_attr_from_bundle(self):
        """Test get providers (attribute) from catalog bundle."""
        self.assertIs(self.bundle.p11, CatalogC.p11)
        self.assertIs(self.bundle.p12, CatalogC.p12)

    def test_get_attr_not_from_bundle(self):
        """Test get providers (attribute) that are not in bundle."""
        self.assertRaises(di.Error, getattr, self.bundle, 'p21')
        self.assertRaises(di.Error, getattr, self.bundle, 'p22')
        self.assertRaises(di.Error, getattr, self.bundle, 'p31')
        self.assertRaises(di.Error, getattr, self.bundle, 'p32')

    def test_get_method_from_bundle(self):
        """Test get providers (get() method) from bundle."""
        self.assertIs(self.bundle.get('p11'), CatalogC.p11)
        self.assertIs(self.bundle.get('p12'), CatalogC.p12)

    def test_get_method_not_from_bundle(self):
        """Test get providers (get() method) that are not in bundle."""
        self.assertRaises(di.Error, self.bundle.get, 'p21')
        self.assertRaises(di.Error, self.bundle.get, 'p22')
        self.assertRaises(di.Error, self.bundle.get, 'p31')
        self.assertRaises(di.Error, self.bundle.get, 'p32')

    def test_has(self):
        """Test checks of providers availability in bundle."""
        self.assertTrue(self.bundle.has('p11'))
        self.assertTrue(self.bundle.has('p12'))

        self.assertFalse(self.bundle.has('p21'))
        self.assertFalse(self.bundle.has('p22'))
        self.assertFalse(self.bundle.has('p31'))
        self.assertFalse(self.bundle.has('p32'))

    def test_create_bundle_with_unbound_provider(self):
        """Test that bundle is not created with unbound provider."""
        self.assertRaises(di.Error, CatalogC.Bundle, di.Provider())

    def test_create_bundle_with_another_catalog_provider(self):
        """Test that bundle can not contain another catalog's provider."""
        class TestCatalog(di.DeclarativeCatalog):
            """Test catalog."""

            provider = di.Provider()

        self.assertRaises(di.Error,
                          CatalogC.Bundle, CatalogC.p31, TestCatalog.provider)

    def test_create_bundle_with_another_catalog_provider_with_same_name(self):
        """Test that bundle can not contain another catalog's provider."""
        class TestCatalog(di.DeclarativeCatalog):
            """Test catalog."""

            p31 = di.Provider()

        self.assertRaises(di.Error,
                          CatalogC.Bundle, CatalogC.p31, TestCatalog.p31)

    def test_is_bundle_owner(self):
        """Test that catalog bundle is owned by catalog."""
        self.assertTrue(CatalogC.is_bundle_owner(self.bundle))
        self.assertFalse(CatalogB.is_bundle_owner(self.bundle))
        self.assertFalse(CatalogA.is_bundle_owner(self.bundle))

    def test_is_bundle_owner_with_not_bundle_instance(self):
        """Test that check of bundle ownership raises error with not bundle."""
        self.assertRaises(di.Error, CatalogC.is_bundle_owner, object())


class CatalogTests(unittest.TestCase):
    """Catalog test cases."""

    def test_get(self):
        """Test getting of providers using get() method."""
        self.assertIs(CatalogC.get('p11'), CatalogC.p11)
        self.assertIs(CatalogC.get('p12'), CatalogC.p12)
        self.assertIs(CatalogC.get('p22'), CatalogC.p22)
        self.assertIs(CatalogC.get('p22'), CatalogC.p22)
        self.assertIs(CatalogC.get('p32'), CatalogC.p32)
        self.assertIs(CatalogC.get('p32'), CatalogC.p32)

    def test_get_undefined(self):
        """Test getting of undefined providers using get() method."""
        self.assertRaises(di.Error, CatalogC.get, 'undefined')

    def test_has(self):
        """Test checks of providers availability in catalog."""
        self.assertTrue(CatalogC.has('p11'))
        self.assertTrue(CatalogC.has('p12'))
        self.assertTrue(CatalogC.has('p21'))
        self.assertTrue(CatalogC.has('p22'))
        self.assertTrue(CatalogC.has('p31'))
        self.assertTrue(CatalogC.has('p32'))
        self.assertFalse(CatalogC.has('undefined'))

    def test_filter_all_providers_by_type(self):
        """Test getting of all catalog providers of specific type."""
        self.assertTrue(len(CatalogC.filter(di.Provider)) == 6)
        self.assertTrue(len(CatalogC.filter(di.Value)) == 0)


class OverrideTests(unittest.TestCase):
    """Catalog overriding and override decorator test cases."""

    class Catalog(di.DeclarativeCatalog):
        """Test catalog."""

        obj = di.Object(object())
        another_obj = di.Object(object())

    def tearDown(self):
        """Tear test environment down."""
        self.Catalog.reset_override()

    def test_overriding(self):
        """Test catalog overriding with another catalog."""
        @di.override(self.Catalog)
        class OverridingCatalog(self.Catalog):
            """Overriding catalog."""

            obj = di.Value(1)
            another_obj = di.Value(2)

        self.assertEqual(self.Catalog.obj(), 1)
        self.assertEqual(self.Catalog.another_obj(), 2)

    def test_is_overridden(self):
        """Test catalog is_overridden property."""
        self.assertFalse(self.Catalog.is_overridden)

        @di.override(self.Catalog)
        class OverridingCatalog(self.Catalog):
            """Overriding catalog."""

        self.assertTrue(self.Catalog.is_overridden)

    def test_last_overriding(self):
        """Test catalog last_overriding property."""
        @di.override(self.Catalog)
        class OverridingCatalog1(self.Catalog):
            """Overriding catalog."""

        @di.override(self.Catalog)
        class OverridingCatalog2(self.Catalog):
            """Overriding catalog."""

        self.assertIs(self.Catalog.last_overriding, OverridingCatalog2)

    def test_last_overriding_on_not_overridden(self):
        """Test catalog last_overriding property on not overridden catalog."""
        with self.assertRaises(di.Error):
            self.Catalog.last_overriding

    def test_reset_last_overriding(self):
        """Test resetting last overriding catalog."""
        @di.override(self.Catalog)
        class OverridingCatalog1(self.Catalog):
            """Overriding catalog."""

            obj = di.Value(1)
            another_obj = di.Value(2)

        @di.override(self.Catalog)
        class OverridingCatalog2(self.Catalog):
            """Overriding catalog."""

            obj = di.Value(3)
            another_obj = di.Value(4)

        self.Catalog.reset_last_overriding()

        self.assertEqual(self.Catalog.obj(), 1)
        self.assertEqual(self.Catalog.another_obj(), 2)

    def test_reset_last_overriding_when_not_overridden(self):
        """Test resetting last overriding catalog when it is not overridden."""
        with self.assertRaises(di.Error):
            self.Catalog.reset_last_overriding()

    def test_reset_override(self):
        """Test resetting all catalog overrides."""
        @di.override(self.Catalog)
        class OverridingCatalog1(self.Catalog):
            """Overriding catalog."""

            obj = di.Value(1)
            another_obj = di.Value(2)

        @di.override(self.Catalog)
        class OverridingCatalog2(self.Catalog):
            """Overriding catalog."""

            obj = di.Value(3)
            another_obj = di.Value(4)

        self.Catalog.reset_override()

        self.assertIsInstance(self.Catalog.obj(), object)
        self.assertIsInstance(self.Catalog.another_obj(), object)


class AbstractCatalogCompatibilityTest(unittest.TestCase):
    """Test backward compatibility with di.AbstractCatalog."""

    def test_compatibility(self):
        """Test that di.AbstractCatalog is available."""
        self.assertIs(di.DeclarativeCatalog, di.AbstractCatalog)
