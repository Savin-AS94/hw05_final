from typing import Tuple

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название',
                             help_text='Напишите название группы',)
    slug = models.SlugField(unique=True)
    description = models.TextField(default='', verbose_name='Описание',
                                   help_text='Напишите описание группы',)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(default='', verbose_name='Сообщение',
                            help_text='О чём Вы думаете сейчас?',)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True)

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:settings.POST_STR]

    class Meta:
        ordering: Tuple[str] = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        null=True,
        verbose_name='Комментарий',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Ваш комментарий',
        help_text='Есть что ответить?'
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:settings.POST_STR]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Контент-мейкер'
    )

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
