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
        cls.user_second_follow = User.objects.create_user(username='second')
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
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_follow,
        )

    def setUp(self):
        self.follow_client = Client()
        self.follow_second_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_following_list(self):
        """Записи пользователя появляются при подписке"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_follow.username})
        )
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.post, response_follow.context['page_obj'])

    def test_user_unfollowing_list(self):
        """Записи автора пропадают при отписке"""
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_follow.username})
        )
        response_unfollow = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response_unfollow.context['page_obj'])

    def test_user_able_to_follow(self):
        """Тестирование редиректа при подписке"""
        response_follow = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_follow.username})
        )
        self.assertRedirects(
            response_follow,
            reverse('posts:profile',
                    kwargs={'username': self.user_follow.username})
        )

    def test_follow_and_unfollow(self):
        """Тестирование подписки и отписки на автора"""
        follow_count = Follow.objects.count()
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_follow
            ).exists()
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_second_follow.username}
            )
        )
        follow_count_after = Follow.objects.count()
        self.assertEqual(follow_count + 1, follow_count_after)

        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_second_follow.username}
            )
        )
        self.assertEqual(follow_count, Follow.objects.count())
