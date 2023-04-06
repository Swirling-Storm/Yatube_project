from django.test import Client, TestCase


class PostViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404_use_custom_template(self):
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
