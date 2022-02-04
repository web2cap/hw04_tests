from django.conf import settings
from django.core.paginator import Paginator

POST_PER_PAGE = getattr(settings, "POST_PER_PAGE", None)


def paginations(request, data_list):
    """Пагинация данных по страницам.
    Принимает на вход request и list с элементами данных.
    Возвращает объект страницы."""

    paginator = Paginator(data_list, POST_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return page_obj
