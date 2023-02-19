from django.shortcuts import render
from .models import Post


# Create your views here.
def index(request):
    title = 'Это главная страница проекта Yatube'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'title': title,
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def groups_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Лев Толстой – зеркало русской революции.'
    context = {
        'title': title,
        'text': 'Здесть будет информация о группах проекта'
    }
    return render(request, template, context)
