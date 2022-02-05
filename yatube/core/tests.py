from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.url_unexisting_page = "/unexisting_page/"
        cls.template_not_found = "core/404.html"

    def test_not_found_page(self):
        """Проверка, статуса ответа сервера = 404, когда страница не найденна.
        Проверка, что используется шаблон для страницы 404."""

        response = self.client.get(self.url_unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, self.template_not_found)
