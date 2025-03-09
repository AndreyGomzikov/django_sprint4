from django import forms

from .models import User, Post, Comment


class UserUpdateForm(forms.ModelForm):
    """Форма обновления данных пользователя"""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class PostUpdateForm(forms.ModelForm):
    """Форма создания и обновления поста"""

    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'pub_date', 'location', 'category')


class CommentUpdateForm(forms.ModelForm):
    """Форма для создания комментария"""

    class Meta:
        model = Comment
        fields = ('text',)
