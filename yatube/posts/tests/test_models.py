from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая запись",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей поста корректно работает __str__."""

        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях поста совпадает с ожидаемым."""

        post = PostModelTest.post
        field_verboses = {
            "text": "Текст записи",
            "pub_date": "Дата публикации",
            "author": "Автор публикации",
            "group": "Группа",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях поста совпадает с ожидаемым."""

        post = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст поста",
            "group": "Выберите группу",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Заголовок тестовой группы",
            slug="testslug",
            description="Тестовое описание",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей группы корректно работает __str__."""

        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_name(self):
        """verbose_name в полях модели совпадает с ожидаемым."""

        group = GroupModelTest.group
        field_verboses = {
            "title": "Название",
            "slug": "Ссылка на группу",
            "description": "Описание",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях модели совпадает с ожидаемым."""

        group = GroupModelTest.group
        field_help_texts = {
            "title": "Введите название группы",
            "slug": "Укажите ссылку на группу",
            "description": "Введите описание группы",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected
                )
