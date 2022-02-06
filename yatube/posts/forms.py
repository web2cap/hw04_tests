from django import forms
from django.conf import settings

from .models import Comment, Post

POST_MIN_LEN = getattr(settings, "POST_MIN_LEN", None)
COMMENT_MIN_LEN = getattr(settings, "COMMENT_MIN_LEN", None)


class PostForm(forms.ModelForm):
    """Форма добавления поста."""

    class Meta:
        model = Post
        fields = ["text", "group", "image"]

    def clean_text(self):
        data = self.cleaned_data["text"]

        if len(data) < POST_MIN_LEN:
            raise forms.ValidationError(
                f"Длинна поста должна быть не менее {POST_MIN_LEN} символов!"
            )

        return data


class CommentForm(forms.ModelForm):
    """Форма добавления комментария."""

    class Meta:
        model = Comment
        fields = ["text"]

    def clean_text(self):
        data = self.cleaned_data["text"]

        if len(data) < COMMENT_MIN_LEN:
            raise forms.ValidationError(
                f"Длинна комментария должна быть не менее {COMMENT_MIN_LEN} символов!"
            )

        return data
