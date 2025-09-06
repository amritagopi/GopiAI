import unittest

class TestAPIImports(unittest.TestCase):

    def test_authorization_import(self):
        try:
            from api.authorization import Authorization
        except ImportError:
            self.fail("Authorization import failed")

    def test_application_import(self):
        try:
            from api.application import app, start
        except ImportError:
            self.fail("Application import failed")

    def test_base_import(self):
        try:
            from api.base import API
        except ImportError:
            self.fail("Base import failed")

    def test_factory_import(self):
        try:
            from api.factory import APIFactory
        except ImportError:
            self.fail("Factory import failed")

    def test_route_import(self):
        try:
            from api.route import EncodingAPIRoute
        except ImportError:
            self.fail("Route import failed")