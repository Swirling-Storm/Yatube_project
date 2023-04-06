import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='Tester')
        cls.group = Group.objects.create(
            title='test-title',
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
            name='pic.jpg',
            content=picture,
            content_type='image/jpg'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_forms_create_post_with_authorized_client(self):
        """
        Проверка, будет ли создан пост в базе авторизованным пользователем.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст для теста',
            'group': self.group.id,
            'image': self.uploaded
        }
        self.authorized_client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    )
        self.assertEqual(Post.objects.count(),
                         post_count + 1, 'Количество постов не изменилось!')
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста',
                group=self.group.id,
                image='posts/pic.jpg'
            ).exists()
        )

    def test_posts_forms_post_edit_with_authorized_client(self):
        """
        Проверка будет ли редактирован существующий пост
        авторизованным пользователем.
        """
        form_data = {
            'text': 'Тестовый новый текст',
            'group': self.group.id,
        }
        self.authorized_client.post(reverse('posts:post_edit',
                                    kwargs={'post_id': self.post.id}),
                                    data=form_data,
                                    follow=True
                                    )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый новый текст',
                group=self.group.id,
            ).exists())

    def test_posts_forms_create_post_with_guest_client(self):
        """
        Проверка, будет ли создан пост в базе неавторизованным пользователем.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст для теста',
            'group': self.group.id,
            'image': self.uploaded
        }
        self.guest_client.post(reverse('posts:post_create'),
                               data=form_data,
                               )
        self.assertEqual(Post.objects.count(),
                         post_count, 'Количество постов изменилось!')
        self.assertFalse(
            Post.objects.filter(
                text='Текст для теста',
                group=self.group.id,
                image='posts/pic.jpg'
            ).exists()
        )

    def test_posts_forms_post_edit_with_guest_client(self):
        """
        Проверка будет ли редактирован существующий пост
        неавторизованным пользователем.
        """
        form_data = {
            'text': 'Тестовый новый текст',
            'group': self.group.id,
        }
        self.guest_client.post(reverse('posts:post_edit',
                               kwargs={'post_id': self.post.id}),
                               data=form_data,
                               follow=True
                               )
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый новый текст',
                group=self.group.id,
            ).exists())

    def test_posts_forms_create_post_not_valid_form(self):
        """
        Проверка, будет ли создан пост в базе авторизованным пользователем
        с невалидными данными.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': ' ',
            'group': self.group.id,
        }
        self.authorized_client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    )
        self.assertEqual(Post.objects.count(),
                         post_count, 'Количество постов изменилось!')
        self.assertFalse(
            Post.objects.filter(
                text='',
                group=self.group.id,
            ).exists()
        )

    def test_posts_forms_post_edit_not_valid_form(self):
        """
        Проверка будет ли редактирован существующий пост
        авторизованным пользователем с невалидными данными.
        """
        form_data = {
            'text': ' ',
            'group': self.group.id,
        }
        self.authorized_client.post(reverse('posts:post_edit',
                                    kwargs={'post_id': self.post.id}),
                                    data=form_data,
                                    follow=True
                                    )
        self.assertFalse(
            Post.objects.filter(
                text=' ',
                group=self.group.id,
            ).exists()
        )

    def test_posts_forms_create_post_with_not_picture(self):
        """
        Проверка, будет ли создан пост с не-картинкой.
        """
        not_picture_docx = b'not picture file'
        not_pic_uploaded = SimpleUploadedFile(
            name='not_picture.docx',
            content=not_picture_docx,
            content_type='not_picture'
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст для теста',
            'group': self.group.id,
            'image': not_pic_uploaded,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_create'),
            data=form_data
        )
        self.assertEqual(Post.objects.count(),
                         post_count,
                         'Количество постов изменилось!'
                         )
        image_error = ('Загрузите правильное изображение.'
                       ' Файл, который вы загрузили,'
                       ' поврежден или не является изображением.')
        self.assertFormError(
            response,
            'form',
            'image',
            image_error
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='Tester')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_client_create_comment(self):
        """
        Проверка, что авторизированный пользователь может
        создавать комментарии.
        """
        comments_count = Comment.objects.count()
        form_data = {
            'post_id': self.post.id,
            'text': 'Test comment',
            'author': self.user
        }
        self.authorized_client.post(reverse('posts:add_comment',
                                    kwargs={'post_id': self.post.id}),
                                    data=form_data,
                                    follow=True
                                    )
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            'Количество комментариев не изменилось!'
        )
        self.assertTrue(
            Comment.objects.filter(
                post_id=self.post.id,
                text='Test comment',
                author=self.user
            ).exists()
        )

    def test_guest_client_create_comment(self):
        """
        Проверка, что неавторизированный пользователь  не может
        создавать комментарии.
        """
        comments_count = Comment.objects.count()
        form_data = {
            'post_id': self.post.id,
            'text': 'Test comment',
            'author': self.user
        }
        self.guest_client.post(reverse('posts:add_comment',
                               kwargs={'post_id': self.post.id}),
                               data=form_data,
                               follow=True
                               )
        self.assertEqual(Comment.objects.count(),
                         comments_count,
                         'Количество комментариев изменилось!')
        self.assertFalse(
            Comment.objects.filter(
                post_id=self.post.id,
                text='Test comment',
                author=self.user
            ).exists()
        )

    def test_not_valid_form_create_comment(self):
        """
        Проверка будет ли создан комментарий
        с невалидными данными.
        """
        comments_count = Comment.objects.count()
        form_data = {
            'post_id': self.post.id,
            'text': ' ',
            'author': self.user
        }
        self.authorized_client.post(reverse('posts:add_comment',
                                    kwargs={'post_id': self.post.id}),
                                    data=form_data,
                                    follow=True
                                    )
        self.assertEqual(Comment.objects.count(),
                         comments_count,
                         'Количество комментариев изменилось!')
        self.assertFalse(
            Comment.objects.filter(
                post_id=self.post.id,
                text=' ',
                author=self.user
            ).exists()
        )
