# coding: utf-8

from django.test import TestCase
from django.test.client import RequestFactory

from .middlewares import ApplicationMiddleware


class ApplicationMiddlewareTest(TestCase):
    def setUp(self):
        self.middleware = ApplicationMiddleware()
        self.request_factory = RequestFactory()

    def test_headers_in_request(self):
        request = self.request_factory.get('/')
        self.middleware.process_request(request)

        if not hasattr(request, '_HEADERS'):
            self.fail('request does not have attribute "_HEADERS"')

        self.assertIsInstance(request._HEADERS, dict)