from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from posts.forms import PostForm
from posts.models import Post, Group

from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list,
                          10)  # показывать по 10 записей на странице.

    page_number = request.GET.get(
        'page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(
        page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    context_dict = {'title': 'Добавить запись', 'button': 'Добавить'}
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(author=request.user,
                                group=form.cleaned_data['group'],
                                text=form.cleaned_data['text'])
            return redirect('index')
        return render(request, 'new_post.html',
                      {'form': form, 'context_dict': context_dict})
    form = PostForm()
    return render(request, 'new_post.html',
                  {'form': form, 'context_dict': context_dict})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = Post.objects.filter(group=group) \
        .order_by('-pub_date').all()
    paginator = Paginator(group_posts_list, 2)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html',
                  {'page': page, 'paginator': paginator, 'group': group})


def profile(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related(
        'author',
        'group',
    ).filter(author=author).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        'user': user,
        "author": author,
        "page": page,
        "paginator": paginator,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    user_auth = request.user
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'post.html',
                  {'user': user, 'post': post, 'user_auth': user_auth})


@login_required
def post_edit(request, username, post_id):
    context_dict = {'title': 'Редактировать запись', 'button': 'Изменить'}
    post = get_object_or_404(Post, pk=post_id)
    user = get_object_or_404(User, username=username)
    if request.user != post.author:
        return redirect("post", username=post.author, post_id=post.pk)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("post", username=post.author, post_id=post.pk)
    return render(request, 'new_post.html',
                  {'form': form, 'context_dict': context_dict})
# тут тело функции. Не забудьте проверить,
# что текущий пользователь — это автор записи.
# В качестве шаблона страницы редактирования укажите шаблон создания новой записи
# который вы создали раньше (вы могли назвать шаблон иначе)
# return render(request, 'new_post.html',
#               {'form': form, 'context_dict': context_dict})
