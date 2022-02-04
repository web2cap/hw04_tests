from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthor")
        cls.user_not_author = User.objects.create_user(
            username="TestNotAuthor"
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testslug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая запись",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_guest_urls_access(self):
        """Страницы доступные любому пользователю."""

        url_names = {
            "/",
            "/group/testslug/",
            "/profile/TestAuthor/",
            f"/posts/{self.post.pk}/",
        }
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_autorized_urls_access(self):
        """Страницы доступные авторизованному пользователю."""

        url_names = {
            "/",
            "/group/testslug/",
            "/profile/TestAuthor/",
            f"/posts/{self.post.pk}/",
            f"/posts/{self.post.pk}/edit/",
            f"/create/",
        }
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя
    def test_list_url_redirect_guest(self):
        """Страницы перенаправляют анонимного пользователя
        на страницу логина.
        """

        url_names_redirects = {
            f"/posts/{self.post.pk}/edit/": (
                f"/auth/login/?next=/posts/{self.post.pk}/edit/"
            ),
            f"/create/": "/auth/login/?next=/create/",
        }
        for address, redirect_address in url_names_redirects.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    # Редирект для не автора
    def test_redirect_not_author(self):
        """Редирект при попытке редактирования поста не авром"""

        response = self.authorized_client_not_author.get(
            f"/posts/{self.post.pk}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{self.post.pk}/")

    # Проверка вызываемых шаблонов для каждого адреса
    def test_task_list_url_corret_templates(self):
        """Страницы доступные авторизованному пользователю."""

        url_names_templates = {
            "/": "posts/index.html",
            "/group/testslug/": "posts/group_list.html",
            "/profile/TestAuthor/": "posts/profile.html",
            f"/posts/{self.post.pk}/": "posts/post_detail.html",
            f"/posts/{self.post.pk}/edit/": "posts/create_post.html",
            f"/create/": "posts/create_post.html",
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    # Страница не найденна
    def test_page_not_found(self):
        """Страница не найденна."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, 404)
