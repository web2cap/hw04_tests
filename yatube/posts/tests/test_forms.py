from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthor")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testslug",
            description="Тестовое описание",
        )
        cls.group_after_edit = Group.objects.create(
            title="Тестовая группа заданная после редактирования",
            slug="testslug_after_edit",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая запись",
            group=cls.group,
        )
        cls.form_field_text = "Тестовая запись чезез форму"
        cls.form_field_text_edited = (
            "Отредактированный тестовая запись чезез форму"
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        post_count = Post.objects.count()
        form_data = {
            "text": self.form_field_text,
            "group": self.group.pk,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": "TestAuthor"}),
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        last_post = Post.objects.order_by("pk").last()
        self.assertEqual(last_post.text, self.form_field_text)
        self.assertEqual(last_post.group, self.group)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post.
        Изменяются текст записи и группа.
        """

        post_count = Post.objects.count()
        form_data = {
            "text": self.form_field_text_edited,
            "group": self.group_after_edit.pk,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": str(self.post.pk)}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail", kwargs={"post_id": str(self.post.pk)}
            ),
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                pk=self.post.pk,
                text=self.form_field_text_edited,
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                pk=self.post.pk,
                group=self.group_after_edit,
            ).exists()
        )
