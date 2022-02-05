import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_username_value = "TestAuthor"
        cls.user = User.objects.create_user(username=cls.user_username_value)
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
        cls.post_small_gif_filename = "posts/small_gif.gif"
        cls.image_small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00"
            b"\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        image_small_gif_uploaded = SimpleUploadedFile(
            name=cls.post_small_gif_filename,
            content=cls.image_small_gif,
            content_type="image/gif",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая запись",
            group=cls.group,
            image=image_small_gif_uploaded,
        )
        cls.form_field_text = "Тестовая запись чезез форму"
        cls.form_field_text_edited = (
            "Отредактированный тестовая запись чезез форму"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""

        post_count = Post.objects.count()
        created_post_small_gif_filename = "posts/created_small_gif.gif"
        image_small_gif_uploaded = SimpleUploadedFile(
            name=created_post_small_gif_filename,
            content=self.image_small_gif,
            content_type="image/gif",
        )
        form_data = {
            "text": self.form_field_text,
            "group": self.group.pk,
            "image": image_small_gif_uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.user_username_value}
            ),
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        last_post = Post.objects.order_by("pk").last()
        self.assertEqual(last_post.text, self.form_field_text)
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.image, created_post_small_gif_filename)

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post.
        Изменяются текст записи и группа.
        """

        post_count = Post.objects.count()
        edited_post_small_gif_filename = "posts/edited_small_gif.gif"
        image_small_gif_uploaded = SimpleUploadedFile(
            name=edited_post_small_gif_filename,
            content=self.image_small_gif,
            content_type="image/gif",
        )
        form_data = {
            "text": self.form_field_text_edited,
            "group": self.group_after_edit.pk,
            "image": image_small_gif_uploaded,
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
        self.assertTrue(
            Post.objects.filter(
                pk=self.post.pk,
                image=edited_post_small_gif_filename,
            ).exists()
        )

    def test_comment_add_can_autorized(self):
        "Оставлять комментарии может авторизованный пользователь."
        comment_count = Comment.objects.filter(post=self.post).count()
        comment_text = f"Комментарий от {self.user_username_value}"
        form_data = {"text": comment_text}
        response = self.authorized_client.post(
            reverse(
                "posts:add_comment", kwargs={"post_id": str(self.post.pk)}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail", kwargs={"post_id": str(self.post.pk)}
            ),
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post).count(), comment_count + 1
        )
        self.assertTrue(
            Comment.objects.filter(post=self.post, text=comment_text).exists()
        )

    def test_comment_add_cant_guest(self):
        "Оставлять комментарии не может гость."
        comment_count = Comment.objects.filter(post=self.post).count()
        comment_text = f"Комментарий от гостя"
        form_data = {"text": comment_text}
        response = self.client.post(
            reverse(
                "posts:add_comment", kwargs={"post_id": str(self.post.pk)}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("users:login")
            + "?next="
            + reverse(
                "posts:add_comment", kwargs={"post_id": str(self.post.pk)}
            ),
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post).count(), comment_count
        )
        self.assertFalse(
            Comment.objects.filter(post=self.post, text=comment_text).exists()
        )
