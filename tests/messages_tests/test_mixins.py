from django.core.signing import decompress_b64
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .urls import ContactFormViewWithMsg


@override_settings(ROOT_URLCONF='messages_tests.urls')
class SuccessMessageMixinTests(SimpleTestCase):

    def test_set_messages_success(self):
        author = {'name': 'John Doe', 'slug': 'success-msg'}
        add_url = reverse('add_success_msg')
        req = self.client.post(add_url, author)
        self.assertIn(
            bytes(ContactFormViewWithMsg.success_message % author, 'utf-8'),
            decompress_b64(req.cookies['messages'].value))
