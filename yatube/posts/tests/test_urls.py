from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.no_auth = User.objects.create_user(username='No_auth')
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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_equal_name(self):
        """URL-адрес соответствует reverse"""
        url_pages = {
            '/': reverse('posts:index'),
            f'/posts/{self.post.id}/': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            f'/profile/{self.post.author}/': (
                reverse('posts:profile',
                        kwargs={'username': self.user.username})
            ),
            f'/group/{self.group.slug}/': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            '/create/': reverse('posts:post_create'),
        }
        for url, reverse_name in url_pages.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse_name, url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/profile.html': (
                reverse('posts:profile',
                        kwargs={'username': self.user.username})
            ),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test'})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_update_redirects_access_error(self):
        """Тестирование редиректа не автора поста при редактировании"""
        self.authorized_client.force_login(self.no_auth)
        response = self.authorized_client.post(
            reverse('posts:update_post', kwargs={'post_id': self.post.id}),
        )
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.id})
        )

    def test_exist_url(self):
        """Тестирование доступности страниц."""
        reverse_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse('posts:update_post',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            '/unextisting/': HTTPStatus.NOT_FOUND,
        }
        for reverse_name, status in reverse_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, status)

    def test_unexisting_template(self):
        response = self.guest_client.get('/unsexisting/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_create_update_comment_post_redirects_guest_client(self):
        """Тестирование редиректа анонимных пользователей"""
        reverse_names = {
            reverse('posts:post_create'): (
                reverse('users:login') + '?next='
                + reverse('posts:post_create')
            ),
            reverse('posts:update_post', kwargs={'post_id': self.post.id}): (
                reverse('users:login') + '?next='
                + reverse('posts:update_post',
                          kwargs={'post_id': self.post.id})
            ),
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}): (
                reverse('users:login') + '?next='
                + reverse('posts:add_comment',
                          kwargs={'post_id': self.post.id})
            )
        }
        for reverse_name, redirect in reverse_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertRedirects(response, redirect)

    def test_delete_post_template(self):
        """Тестирование удаления поста не автором"""
        self.authorized_client.force_login(self.no_auth)
        response = self.authorized_client.get(
            reverse('posts:post_delete', kwargs={'post_id': self.post.id}),
        )
        self.assertTemplateUsed(response, 'core/403csrf.html')
