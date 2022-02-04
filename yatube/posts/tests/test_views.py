from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


POST_PER_PAGE = getattr(settings, "POST_PER_PAGE", None)
POST_COUNT_ON_SECOND_PAGE = 2


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_username_value = "TestAuthor"
        cls.user = User.objects.create_user(username=cls.user_username_value)
        cls.user_second = User.objects.create_user(username="TestSecondAuthor")
        cls.group_slug_value = "testslug"
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=cls.group_slug_value,
            description="Тестовое описание",
        )
        cls.group_second_slug_value = "testslugsecond"
        cls.group_second = Group.objects.create(
            title="Тестовая группа",
            slug=cls.group_second_slug_value,
            description="Тестовое описание второй группы",
        )

        cls.post = []
        for i in range(POST_PER_PAGE + POST_COUNT_ON_SECOND_PAGE):
            cls.post.append(
                Post.objects.create(
                    author=cls.user,
                    text=f"Тестовая запись {i}",
                    group=cls.group,
                )
            )
        cls.post_second = Post.objects.create(
            author=cls.user_second,
            text="Тестовая запись созданная вторым автором",
            group=cls.group_second,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def db_vs_context_comparison(self, context_object, db_object):
        """Сравнивает объект контекста с объектом базы данных по полям:
        pk, text, group, author.
        """
        self.assertEqual(context_object.pk, db_object.pk)
        self.assertEqual(context_object.text, db_object.text)
        self.assertEqual(context_object.group, db_object.group)
        self.assertEqual(context_object.author, db_object.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        page_name_template = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": self.group_slug_value}
            ): "posts/group_list.html",
            reverse(
                "posts:profile",
                kwargs={"username": self.user_username_value},
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

    def test_posts_index_page_show_correct_context(self):
        """Шаблон posts/index сформирован с правильным контекстом."""

        response = self.client.get(reverse("posts:index"))
        context_first_object = response.context["page_obj"][0]
        db_first_post = Post.objects.first()
        self.db_vs_context_comparison(context_first_object, db_first_post)

    def test_posts_index_page_first_show_requared_number_items(self):
        """Шаблон posts/index первая страница содержит
        количество результатов в соответствии с настройками проекта.
        """

        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), POST_PER_PAGE)

    def test_posts_index_page_second_show_requared_number_items(self):
        """Шаблон posts/index вторая страница содержит
        POST_COUNT_ON_SECOND_PAGE плюс один результат.
        """

        response = self.authorized_client.get(
            reverse("posts:index") + "?page=2"
        )
        items_count = POST_COUNT_ON_SECOND_PAGE + 1
        self.assertEqual(len(response.context["page_obj"]), items_count)

    def test_posts_group_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом."""

        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": self.group_slug_value})
        )
        context_first_object = response.context["page_obj"][0]
        db_first_group_post = Post.objects.filter(group=self.group).first()
        self.db_vs_context_comparison(
            context_first_object, db_first_group_post
        )

    def test_posts_group_page_first_show_requared_number_items(self):
        """Шаблон posts/group_list первая страница содержит
        количество результатов в соответствии с настройками проекта.
        """

        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": self.group_slug_value})
        )
        self.assertEqual(len(response.context["page_obj"]), POST_PER_PAGE)

    def test_posts_group_page_second_show_requared_number_items(self):
        """Шаблон posts/group_list вторая страница содержит
        POST_COUNT_ON_SECOND_PAGE результатов.
        """

        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group_slug_value})
            + "?page=2"
        )
        self.assertEqual(
            len(response.context["page_obj"]), POST_COUNT_ON_SECOND_PAGE
        )

    def test_posts_user_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом."""

        response = self.client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user_username_value},
            )
        )
        context_first_object = response.context["page_obj"][0]
        db_first_user_post = Post.objects.filter(author=self.user).first()
        self.db_vs_context_comparison(context_first_object, db_first_user_post)

    def test_posts_user_page_first_show_requared_number_items(self):
        """Шаблон posts/group_list первая страница содержит
        количество результатов в соответствии с настройками проекта.
        """

        response = self.client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user_username_value},
            )
        )
        self.assertEqual(len(response.context["page_obj"]), POST_PER_PAGE)

    def test_postsuser_page_second_show_requared_number_items(self):
        """Шаблон posts/group_list вторая страница содержит
        POST_COUNT_ON_SECOND_PAGE результатов.
        """

        response = self.authorized_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user_username_value},
            )
            + "?page=2"
        )
        self.assertEqual(
            len(response.context["page_obj"]), POST_COUNT_ON_SECOND_PAGE
        )

    def test_posts_detail_page_show_correct_context(self):
        """Шаблон posts/post_detail сформирован с правильным контекстом."""

        response = self.client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post[0].pk})
        )
        context_object = response.context["post"]
        db_by_pk_post = Post.objects.filter(pk=self.post[0].pk).first()
        self.db_vs_context_comparison(context_object, db_by_pk_post)

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

    def test_posts_group_page_not_include_incorect_post(self):
        """Шаблон posts/group_list не содержит лишний пост."""

        response = self.client.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group_second_slug_value},
            )
        )
        for secong_group_post in response.context["page_obj"]:
            self.assertNotEqual(secong_group_post.pk, self.post[0].pk)
