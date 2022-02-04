from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Главный автор
        cls.user = User.objects.create_user(username="TestAuthor")
        # Второй автор
        cls.user_second = User.objects.create_user(username="TestSecondAuthor")

        # Галвная группа (с 12 постами)
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testslug",
            description="Тестовое описание",
        )
        # Вторая группа (с 1 постом)
        cls.group_second = Group.objects.create(
            title="Тестовая группа",
            slug="testslugsecond",
            description="Тестовое описание второй группы",
        )

        # Добавляем 12 постов
        cls.post = []
        for i in range(12):
            cls.post.append(
                Post.objects.create(
                    author=cls.user,
                    text=f"Тестовая запись {i}",
                    group=cls.group,
                )
            )
        # Один потс со вторым автором во вторую групуу
        cls.post_second = Post.objects.create(
            author=cls.user_second,
            text="Тестовая запись 13",
            group=cls.group_second,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        page_name_template = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "testslug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "TestAuthor"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post[0].pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post[0].pk}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }

        for reverse_name, template in page_name_template.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Тесты для главной страницы
    def test_posts_index_page_show_correct_context(self):
        """Шаблон posts/index сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse("posts:index"))
        # Проверяем что первый элемент на странице соответствует
        # поледнему добавленному в БД
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовая запись 13")
        self.assertEqual(post_group_0, self.group_second)
        self.assertEqual(post_author_0, self.user_second)

    def test_posts_index_page_first_show_ten_items(self):
        """Шаблон posts/index первая страница содержит 10 результатов."""

        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_posts_index_page_second_show_three_items(self):
        """Шаблон posts/index вторая страница содержит 3 результата."""

        response = self.authorized_client.get(
            reverse("posts:index") + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3)

    # Тесты для страницы группы
    def test_posts_group_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом."""

        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "testslug"})
        )
        # Проверяем что первый элемент на странице соответствует
        # поледнему добавленному в БД
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовая запись 11")
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)

    def test_posts_group_page_first_show_ten_items(self):
        """Шаблон posts/group_list первая страница содержит 10 результатов."""

        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "testslug"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_posts_group_page_second_show_two_items(self):
        """Шаблон posts/group_list вторая страница содержит 2 результата."""

        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "testslug"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)

    # Тесты для страницы с постами пользователя
    def test_posts_user_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом."""

        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthor"})
        )
        # Проверяем что первый элемент на странице соответствует
        # поледнему добавленному в БД
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовая запись 11")
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)

    def test_posts_user_page_first_show_ten_items(self):
        """Шаблон posts/group_list первая страница содержит 10 результатов."""

        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthor"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_postsuser_page_second_show_two_items(self):
        """Шаблон posts/group_list вторая страница содержит 2 результата."""

        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthor"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)

    # Тесты для страницы детали поста
    def test_posts_detail_page_show_correct_context(self):
        """Шаблон posts/post_detail сформирован с правильным контекстом."""

        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post[0].pk})
        )
        self.assertEqual(response.context["post"].text, "Тестовая запись 0")
        self.assertEqual(response.context["post"].group, self.group)
        self.assertEqual(response.context["post"].author, self.user)

    # Тесты для создания поста
    def test_posts_create_page_show_correct_context(self):
        """Шаблон posts/index сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    # Тест что  пост не попал в группу, для которой не был предназначен.
    def test_posts_group_page_not_include_incorect_post(self):
        """Шаблон posts/group_list не содержит лишний пост."""

        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "testslugsecond"})
        )
        for secong_group_post in response.context["page_obj"]:
            self.assertNotEqual(secong_group_post.pk, self.post[0].pk)
