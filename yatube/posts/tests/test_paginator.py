import math

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовая пост',
        )
        cls.POST_NUM_CHECK = 29
        for post_num in range(cls.POST_NUM_CHECK):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {post_num}',
                group=cls.group
            )
            cls.post_count = cls.POST_NUM_CHECK + 1

    def setUp(self):
        self.guest_client = Client()

    def test_first_pages_contains_ten_records(self):
        """Тестирование количества постов на 1(0) странице"""
        reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.POST_LIM)

    def test_other_page_contains_num_records(self):
        """Тестирование количества постов на страницах"""
        num_pages = math.ceil(self.post_count / settings.POST_LIM)
        response = self.guest_client.get(reverse('posts:index')
                                         + f'?page={num_pages}')
        self.assertEqual(len(response.context['page_obj']),
                         self.post_count - settings.POST_LIM * (num_pages - 1))
