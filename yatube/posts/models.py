from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Введите название группы",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Ссылка на группу",
        help_text="Укажите ссылку на группу",
    )
    description = models.TextField(
        verbose_name="Описание", help_text="Введите описание группы"
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст записи", help_text="Введите текст поста"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор публикации",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите группу",
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return self.text[:15]
