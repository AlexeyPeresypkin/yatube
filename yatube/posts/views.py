from django.http import HttpResponse
from django.shortcuts import render

from posts.models import Post
from yatube.settings import BASE_DIR


def index(request):
    latest = Post.objects.order_by('-pub_date')[:10]
    print(BASE_DIR)
    return render(request, "index.html", {"posts": latest})


