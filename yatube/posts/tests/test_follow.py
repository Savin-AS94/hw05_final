from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post


User = get_user_model()


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_follow = User.objects.create_user(username='follow')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_follow,
            group=cls.group,
            text='Тестовая пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_can_follow_author(self):
        """Тестирование подписки на автора"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_follow.username}
            )
        )
        follow_count_after = Follow.objects.count()
        self.assertEqual(follow_count + 1, follow_count_after)
        # Редирект при подписке
        response_follow = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_follow.username},
                    ), follow=True
        )
        self.assertRedirects(
            response_follow,
            reverse('posts:profile',
                    kwargs={'username': self.user_follow.username})
        )
        # Подписка активна
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.user_follow,
        ).exists())

    def test_user_can_follow_author_once(self):
        """На автора можно подписаться только один раз"""
        Follow.objects.create(
            user=self.user,
            author=self.user_follow,
        )
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_follow.username},
                    )
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_user_can_unfollow_author(self):
        """Тестирование отписки от автора"""
        follow_count = Follow.objects.count()
        Follow.objects.create(
            user=self.user,
            author=self.user_follow,
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_follow.username}
            )
        )
        # Количество подписок не изменилось
        self.assertEqual(follow_count, Follow.objects.count())
        # Подписка как объект удалена
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user_follow,
        ).exists())
