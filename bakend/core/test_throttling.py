from types import SimpleNamespace
from django.test import SimpleTestCase
from django.core.cache import cache
from rest_framework.exceptions import Throttled
from core.throttling import BurstRateThrottle, SustainedRateThrottle
from core.exceptions import custom_exception_handler

class ThrottleTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.user = SimpleNamespace(is_authenticated=True, id=9851)

    def request(self, method='GET', data=None):
        return SimpleNamespace(user=self.user, method=method, data=data or {})

    def test_navigation_and_saves_do_not_consume_model_budget(self):
        for cls in [BurstRateThrottle, SustainedRateThrottle]:
            throttle = type('TestThrottle', (cls,), {'rate':'2/min'})()
            for _ in range(15):
                self.assertTrue(throttle.allow_request(self.request(), type('DocumentListView', (), {})()))
                self.assertTrue(throttle.allow_request(self.request('PUT'), type('PaperDetailView', (), {})()))
            view = type('ChatStreamView', (), {})()
            self.assertTrue(throttle.allow_request(self.request('POST'), view))
            self.assertTrue(throttle.allow_request(self.request('POST'), view))
            self.assertFalse(throttle.allow_request(self.request('POST'), view))

    def test_throttle_error_is_localized(self):
        response = custom_exception_handler(Throttled(wait=21), {})
        self.assertEqual(response.status_code,429)
        self.assertEqual(response.data['retry_after'],21)
        self.assertIn('21 秒', response.data['detail'])
