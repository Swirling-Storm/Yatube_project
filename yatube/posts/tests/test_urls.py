from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Tester')
        cls.group = Group.objects.create(
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='Tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_general_pages_url_exists_at_desired_location(self):
        """Страницы "/", "/group/<slug:slug>/", "/profile/<str:username>/",
        "/posts/<int:post_id>/" доступны любому пользователю."""
        addresses = [
            '/',
            '/group/test-slug/',
            '/profile/Tester/',
            f'/posts/{self.post.id}/',
        ]
        for address in addresses:
            with self.subTest(address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизированному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_exists_at_desired_location(self):
        """Страница /posts/<int:post_id>/edit/ доступна только автору."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location(self):
        """
        Страница /'posts/<int:post_id>/comment/ доступна
        авторизированному пользователю.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page_edit_url_exists_at_desired_location(self):
        """Страница /unexisting_page/ недоступна."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/Tester/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
