import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.const import POSTS_LIMITER
from posts.models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
PAGINATOR_POSTS = 11

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Tester')
        cls.group = Group.objects.create(
            slug='test-slug',
        )
        picture = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small_pic',
            content=picture,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='Tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_authorized_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон,
        если пользователь авторизован.
        """
        templates_pages_names = {
            'posts/index.html': ('posts:index',
                                 None),
            'posts/group_list.html': ('posts:group_list',
                                      {'slug': self.group.slug},),
            'posts/profile.html': ('posts:profile',
                                   {'username': self.post.author}),
            'posts/post_detail.html': ('posts:post_detail',
                                       {'post_id': self.post.id}),
            'posts/create_post.html': ('posts:post_create',
                                       None)
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                name, kwarg = reverse_name
                response = self.authorized_client.get(reverse(
                    name,
                    kwargs=kwarg
                ))
                self.assertTemplateUsed(response, template)

    def test_post_edit_pages_authorized_uses_correct_template(self):
        """
        URL-адрес использует шаблон posts/create_post.html,
        если пользователь авторизован.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_pages_guest_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон,
        если пользователь неавторизован.
        """
        templates_pages_names = {
            'posts/index.html': ('posts:index',
                                 None),
            'posts/group_list.html': ('posts:group_list',
                                      {'slug': self.group.slug},),
            'posts/profile.html': ('posts:profile',
                                   {'username': self.post.author}),
            'posts/post_detail.html': ('posts:post_detail',
                                       {'post_id': self.post.id}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                name, kwarg = reverse_name
                response = self.guest_client.get(reverse(
                    name,
                    kwargs=kwarg
                ))
                self.assertTemplateUsed(response, template)

    def post_context_checker(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text,
                             'Текст не совпадет с ожидаемым!')
            self.assertEqual(post.author, self.post.author,
                             'Автор  не совпадет с ожидаемым!')
            self.assertEqual(post.group, self.post.group,
                             'Группа не совпадет с ожидаемым!')
            self.assertTrue(post.image,
                            'Изображения нет в контексте')
            self.assertEqual(post.image, self.post.image,
                             'Изображение не совпадет с ожидаемым!')

    def test_index_page_show_correct_context_for_authorized_client(self):
        """
        Шаблон index сформирован с правильным контекстом
        для авторизованного пользователя.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.post_context_checker(response.context['page_obj'][0])

    def test_index_page_show_correct_context_for_guest_client(self):
        """
        Шаблон index сформирован с правильным контекстом
        для неавторизованного пользователя.
        """
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.post_context_checker(response.context['page_obj'][0])

    def test_groups_posts_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        responses = [
            self.authorized_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})),
            self.guest_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug}))
        ]
        for response in responses:
            with self.subTest(response=response):
                context_objects = [
                    'title',
                    'group',
                    'posts_count',
                    'page_obj'
                ]
                for object in context_objects:
                    self.assertIn(object, response.context)
                self.post_context_checker(response.context['page_obj'][0])
                test_group = response.context['group']
                self.assertEqual(test_group, self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        responses = [
            self.authorized_client.get(
                reverse('posts:profile',
                        kwargs={'username': self.post.author})),
            self.guest_client.get(
                reverse('posts:profile',
                        kwargs={'username': self.post.author}))
        ]
        for response in responses:
            with self.subTest(response=response):
                context_objects = [
                    'author',
                    'posts_count',
                    'page_obj',
                    'following'
                ]
                for object in context_objects:
                    self.assertIn(object, response.context)
                self.post_context_checker(response.context['page_obj'][0])
                test_profile = response.context['author']
                self.assertEqual(test_profile, self.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        responses = [
            self.authorized_client.get(reverse('posts:post_detail',
                                               kwargs={'post_id': self.post.id}
                                               )),
            self.guest_client.get(reverse('posts:post_detail',
                                          kwargs={'post_id': self.post.id}))
        ]
        for response in responses:
            with self.subTest(response=response):
                context_objects = [
                    'post',
                    'form',
                    'comments'
                ]
                for object in context_objects:
                    self.assertIn(object, response.context)
                post = response.context.get('post')
                self.post_context_checker(post)
                self.assertEqual(post, self.post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIn('form', response.context)
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                context_objects = [
                    'form',
                    'is_edit',
                    'post'
                ]
                for object in context_objects:
                    self.assertIn(object, response.context)
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Проверка работы кеша"""
        post = Post.objects.create(
            text='Test cache text',
            author=self.user)
        content_add = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_cache_clear)


class FollowViewTest(TestCase):
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
        self.follower = User.objects.create(username='Follower')
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        cache.clear()

    def test_follow(self):
        """Проверка подписки пользователя на пользователя."""
        follow_count = Follow.objects.count()
        self.follower_client.post(reverse('posts:profile_follow',
                                          kwargs={'username': self.author}))
        self.assertEqual(Follow.objects.count(),
                         follow_count + 1,
                         'Количество подписок не увеличилось!')

    def test_unfollow(self):
        """Проверка отписки пользователя от пользователя."""
        self.follower_client.post(reverse('posts:profile_follow',
                                          kwargs={'username': self.author}))
        follow_count = Follow.objects.count()
        self.follower_client.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author}))
        self.assertEqual(Follow.objects.count(),
                         follow_count - 1,
                         'Количество подписок не уменьшилось!')

    def test_post_in_follow_index(self):
        """Проверка появления поста на странице /follow/"""
        self.follower_client.post(reverse('posts:profile_follow',
                                          kwargs={'username': self.author}))
        response = self.follower_client.get('/follow/')
        post = response.context['page_obj'][0]
        self.assertEqual(post, self.post,
                         'Пост не появился в избранных авторах!')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Tester')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for count in range(PAGINATOR_POSTS):
            cls.post = Post.objects.create(
                text=f'Тестовый текст номер {count}',
                author=cls.user,
            )

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), POSTS_LIMITER)
