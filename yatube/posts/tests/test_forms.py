import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Post, Group, Comment
from django.test import TestCase, Client, override_settings


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm
        cls.user = User.objects.create_user(
            username='roman'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Ля ля ля',
            group=cls.group,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorize_client = Client()
        self.authorize_client.force_login(self.user)

    def test_post_create_valid_form(self):
        """Проверка добавление поста с валидной формой."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Созданный пост',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorize_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Созданный пост',
                image='posts/small.gif',
                group=self.group.pk
            ).exists()
        )

    def test_post_edit_form(self):
        """Проверка работы изменения поста с валидной формой."""
        response = self.authorize_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk
            }),
            data={'text': 'Измененный пост',
                  'group': self.group.pk}
        )
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Измененный пост',
                group=self.group,
            ).exists()
        )

    def test_post_create_not_valid_form(self):
        """Проверка работы добавления поста с невалидной формой."""
        post_count = Post.objects.count()
        response = self.authorize_client.post(
            reverse('posts:post_create'),
            data={'text': ' '}
        )
        self.assertFormError(response, 'form', 'text', 'Обязательное поле.')
        self.assertEqual(Post.objects.count(),
                         post_count, 'Пост не должен быть добавлен')
        self.assertEqual(response.status_code, HTTPStatus.OK, 'Сервер упал')

    def test_comment_add_valid_form(self):
        """Комментарий появится на странице поста"""
        form_data = {
            'text': 'Мой комментарий',
            'post_id': self.post.pk
        }
        Comment.objects.create(
            text='Мой комментарий',
            post_id=self.post.pk,
            author=self.user
        )
        self.authorize_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.pk}
            ), data=form_data, follow=True
        )
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        self.assertEqual(
            response.context['comments'].first().text, 'Мой комментарий'
        )
