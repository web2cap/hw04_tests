from django import forms
from django.conf import settings

from .models import Post

POST_MIN_LEN = getattr(settings, "POST_MIN_LEN", None)


class PostForm(forms.ModelForm):
    """Форма добавления поста."""

    class Meta:
        model = Post
        fields = ["text", "group", "image"]

    def __init__(self, *args, **kwargs):
        """Задает css class полям формы"""

        super(PostForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(
                {"class": "form-control"}
            )

    def clean_text(self):
        data = self.cleaned_data["text"]

        if len(data) < POST_MIN_LEN:
            raise forms.ValidationError(
                f"Длинна поста должна быть не менее {POST_MIN_LEN} символов!"
            )

        return data
