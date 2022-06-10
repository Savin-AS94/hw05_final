import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.other_group = Group.objects.create(
            title='Тестовая группа2',
            slug='test2',
            description='Тестовое описание2',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовая пост',
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post_count = self.post.author.posts.count
        response = self.guest_client.get(reverse('posts:post_detail',
                                         kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post'), self.post)
        self.assertEqual(response.context.get('post_count'), post_count)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.guest_client.get(reverse('posts:profile',
                    kwargs={'username': self.user.username})))
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('post_count'),
                         Post.objects.count())

    def test_create_update_post_pages_show_correct_context(self):
        """Шаблоны create и update сформированы с правильным контекстом."""
        reverse_names = (
            reverse('posts:post_create'),
            reverse(
                'posts:update_post', kwargs={'post_id': self.post.id}),
        )
        for reverse_name in reverse_names:
            response = self.authorized_client.get(reverse_name)
            form_fields = {
                'form': PostForm,
            }
            self.assertIsInstance(response.context['form'],
                                  form_fields['form'])
        self.assertEqual(self.authorized_client.get(
            reverse('posts:update_post', kwargs={'post_id': self.post.id})
        ).context.get('form').instance.id, self.post.id)

    def test_post_no_group(self):
        """Пост не попадает в ненужную группу"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.other_group.slug}))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_post_on_pages(self):
        """Пост отображается на страницах"""
        reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username}),
        )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertIn(self.post,
                              response.context['page_obj'])

    def test_comment_on_page(self):
        """Комментарий отображается на странице поста"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertIn(self.comment, response.context.get('comments'))

    def test_comment_pages_show_correct_context(self):
        """В шаблон post_detail передается правильная форма коммента"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        form_fields = {
            'form': CommentForm,
        }
        self.assertIsInstance(response.context['form'],
                              form_fields['form'])

    def test_cache_index(self):
        """Тестирование работы кеша"""
        response_1 = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.first()
        post.text = 'wtf'
        post.save()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_1.content, response_3.content)
