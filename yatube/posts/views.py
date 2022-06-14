from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User


def pagination(page_number, posts_list):
    return Paginator(posts_list, settings.POST_LIM).get_page(page_number)


def index(request):
    posts = Post.objects.select_related('author', 'group')
    title = 'Это главная страница проекта Yatube'
    header = 'Последние обновления на сайте'
    templates = 'posts/index.html'
    context = {
        'title': title,
        'header': header,
        'page_obj': pagination(request.GET.get('page'), posts),
    }
    return render(request, templates, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    templates = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': pagination(request.GET.get('page'), posts),
    }
    return render(request, templates, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    templates = 'posts/profile.html'
    page_obj = pagination(request.GET.get('page'), posts)
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists())
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_count': page_obj.paginator.count,
        'following': following,
    }
    return render(request, templates, context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id)
    templates = 'posts/post_detail.html'
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'post_count': post.author.posts.count,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, templates, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html',
                  {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True, }
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.pk)
        return render(request, 'posts/create_post.html', context)
    return redirect('posts:post_detail', post.pk)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_delete(request, post_id):
    post_delete = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    if post_delete.author == request.user:
        post_delete.delete()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'core/403csrf.html')


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Посты контент-мейкера'
    posts = Post.objects.select_related('author').filter(
        author__following__user=request.user
    )
    context = {
        'page_obj': pagination(request.GET.get('page'), posts),
        'title': title,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:profile', username=username)
