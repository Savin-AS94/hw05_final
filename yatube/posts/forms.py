from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {'group': 'Группа', 'text': 'Сообщение'}
        fields = ("group", "text", "image")


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Комментарий'}
        fields = ("text",)
