from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': ('Текст поста', 'Текст нового поста'),
            'group': ('Группа', 'Группа, к которой будет относиться пост'),
            'image': ('Картинка', 'Загрузите ваше изображение')
        }


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
