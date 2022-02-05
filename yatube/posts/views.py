from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginations


def index(request):
    """Вывод POST_PER_PAGE объектов модели Post,
    отсортированных по полю pub_date по убыванию,
    с учетом номера страницы переданного в GET.
    """

    post_list = Post.objects.all()
    page_obj = paginations(request, post_list)

    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    """Страница список постов."""
    group = get_object_or_404(Group, slug=slug)

    post_list = group.posts.all()
    page_obj = paginations(request, post_list)

    template = "posts/group_list.html"
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Список постов пользователя, общее количество постов,
    инофрмация о пользователе."""

    author = get_object_or_404(User, username=username)

    post_list = author.posts.all()
    page_obj = paginations(request, post_list)

    template = "posts/profile.html"
    context = {
        "page_obj": page_obj,
        "author": author,
    }

    return render(request, template, context)


def post_detail(request, post_id):
    """Страница поста и количество постов пользователя."""

    post = get_object_or_404(Post, pk=post_id)

    template = "posts/post_detail.html"
    context = {"post": post}

    return render(request, template, context)


@login_required(login_url="users:login")
def post_create(request):
    """Добавления поста."""

    template = "posts/create_post.html"

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author_id = request.user.id
        instance.save()
        return redirect("posts:profile", request.user)

    return render(request, template, {"form": form})


@login_required(login_url="users:login")
def post_edit(request, post_id):
    """Редактирование поста. Доступно только автору."""

    template = "posts/create_post.html"

    post = get_object_or_404(Post, pk=post_id)

    # Если редактировать пытается не автор
    if request.user.id != post.author.id:
        return redirect("posts:post_detail", post.pk)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post.id)

    context = {
        "form": form,
        "is_edit": True,
    }
    return render(request, template, context)
