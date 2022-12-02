import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from ..models import Group, Post, Comment
from django.urls import reverse
from django import forms

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestContext(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='RBychin',
            first_name='Роман',
            last_name='Бычин',
            email='rbychin@ya.ru',
            password='UTkgE7jv4x',
        )
        cls.another_user = User.objects.create_user(username='Antony')
        Group.objects.bulk_create(
            [Group(
                title=f'Группа {i}',
                description=f'Описание {i}',
                slug=f'test_slug_{i}'
            ) for i in range(1, 3)]
        )
        cls.group_1 = Group.objects.get(slug='test_slug_1')
        cls.group_2 = Group.objects.get(slug='test_slug_2')
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
        Post.objects.bulk_create([
            Post(
                text='Тестовый пост 1',
                author=cls.user,
                group=cls.group_1,
                image=uploaded
            ),
            Post(
                text='Тестовый пост 2',
                author=cls.another_user,
                group=cls.group_2
            )
        ])
        cls.post = Post.objects.get(author=cls.user)
        Comment.objects.create(
            text='Мой комментарий',
            author=cls.user,
            post_id=cls.post.pk
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cache.clear()

    def setUp(self):
        cache.clear()
        self.rbychin = Client()
        self.rbychin.force_login(self.user)
        self.antony = Client().force_login(self.another_user)
        self.guest = Client()

    def test_index_a_context(self):
        """Получаем контекст в index,
        проверяем количество постов в контексте."""
        posts_count = Post.objects.all().count()
        index = 1
        addresses = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for address in addresses:
            with self.subTest(addresse=address):
                response = self.guest.get(address)
                self.assertIsNotNone(
                    response.context['page_obj'],
                    'В контекст не передан ни один пост.'
                )
                if 'group' in address:
                    posts_count = Post.objects.filter(
                        group=self.group_1).count()
                    index = 0
                elif 'profile' in address:
                    posts_count = Post.objects.filter(
                        author=self.user).count()
                    index = 0
                self.assertEqual(
                    response.context['object_list'].count(),
                    posts_count)
                self.assertIsNotNone(
                    response.context['object_list'][index].image,
                    'Картинка не найдена')

    def test_context_edit_post(self):
        """Проверяет, что в контексте форма вызванного поста"""
        response = self.rbychin.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form = response.context['post']
        form_fields = {
            form.text: self.post.text,
            form.author.username: self.user.username,
            form.group.slug: self.group_1.slug
        }
        for field, value in form_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)

    def test_context_create_post(self):
        """Тест контекста формы при создании поста"""
        response = self.rbychin.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        form = response.context['form']
        for field, value in form_fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], value)

    def test_context_post_detail(self):
        """Тест контекста для post_detail"""
        response = self.rbychin.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        post = response.context['post']
        self.assertEqual(post.text, 'Тестовый пост 1')
        response.context.get('post')
        self.assertIsNotNone(
            response.context['post'].image,
            'Картинка не найдена')

    def test_index_cache(self):
        """Тест кеша страницы index"""
        new_post = Post.objects.create(
            author=self.user,
            text='Пост теста кеширования',
            group=self.group_1
        )
        response_first = self.rbychin.get(
            reverse('posts:index')
        )
        response_content_first = response_first.content
        new_post.delete()
        response_second = self.rbychin.get(
            reverse('posts:index')
        )
        response_content_second = response_second.content
        self.assertEqual(response_content_first, response_content_second)
        cache.clear()
        response_third = self.rbychin.get(
            reverse('posts:index')
        )
        response_content_third = response_third.content
        self.assertNotEqual(response_content_second, response_content_third)

    def test_comment_context(self):
        response = self.rbychin.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        self.assertEqual(
            response.context['comments'].first().text, 'Мой комментарий'
        )
