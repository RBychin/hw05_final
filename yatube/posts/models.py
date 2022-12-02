from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel
from django.urls import reverse

User = get_user_model()


class Group(models.Model):
    objects = None
    title = models.CharField(
        max_length=200,
        verbose_name='Название тематики',
    )
    slug = models.SlugField(
        unique=True, null=False,
        verbose_name='Slug-ссылка'
    )
    description = models.TextField(
        verbose_name='Описание', null=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('group', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(CreatedModel):
    objects = None
    text = models.TextField(
        verbose_name='Пост',
        help_text='Введите текст вашего сообщения.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу, необязательно.'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите картинку'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
