from django import forms
from django.conf import settings

from .models import Post

POST_MIN_LEN = getattr(settings, "POST_MIN_LEN", None)


class PostForm(forms.ModelForm):
    """Форма добавления поста."""

    class Meta:
        model = Post
        fields = ("group", "text", "image")

    def clean_text(self):
        data = self.cleaned_data["text"]

        if len(data) < POST_MIN_LEN:
            raise forms.ValidationError(
                f"Длинна поста должна быть не менее {POST_MIN_LEN} символов!"
            )

        return data
