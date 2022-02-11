from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Comment, Follow, User


@cache_page(60 * 20)
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    # показывать по 10 записей на странице.

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
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
            # return redirect('post', username=request.user, post_id=30)
        return render(request, 'new_post.html',
                      {'form': form, 'context_dict': context_dict})
    form = PostForm()
    return render(request, 'new_post.html',
                  {'form': form, 'context_dict': context_dict})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = Post.objects.filter(group=group) \
        .order_by('-pub_date').all()
    paginator = Paginator(group_posts_list, 10)
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
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=author, user=user).exists()
        context['following'] = following

    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    user_auth = request.user
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = Comment.objects.filter(post=post.pk)
    form = CommentForm()
    return render(request, 'post.html',
                  {'author': post.author, 'post': post,
                   'user_auth': user_auth,
                   'comments': comments,
                   'form': form})


@login_required
def post_edit(request, username, post_id):
    context_dict = {'title': 'Редактировать запись', 'button': 'Изменить'}
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    if request.user != author:
        return redirect(
            "post",
            username=request.user.username,
            post_id=post.pk
        )
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=request.user, post_id=post_id)
    return render(request, 'new_post.html',
                  {
                      'form': form,
                      'context_dict': context_dict,
                      'post': post
                  })

    # тут тело функции. Не забудьте проверить,
    # что текущий пользователь — это автор записи.
    # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
    # который вы создали раньше (вы могли назвать шаблон иначе)
    # return render(request, 'new_post.html',
    #               {'form': form, 'context_dict': context_dict})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    # if request.method == 'POST':
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = post.author
        comment.save()
    return redirect('post', username=username, post_id=post_id)
    # return render(request, 'post.html', {'form': form})


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    posts = Post.objects.filter(author__following__user=request.user).order_by(
        '-pub_date')
    paginator = Paginator(posts, 10)
    # показывать по 10 записей на странице.
    page_number = request.GET.get(
        'page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(
        page_number)  # получить записи с нужным смещением
    return render(request, "follow.html",
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author or Follow.objects.filter(author=author,
                                                       user=request.user).exists():
        return redirect('profile', username=username)
    follower = Follow.objects.create(user=request.user, author=author)
    follower.save()
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('profile', username=username)
