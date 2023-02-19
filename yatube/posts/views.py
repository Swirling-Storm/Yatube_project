from django.shortcuts import render


# Create your views here.
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'text': 'Это главная страница проекта Yatube'
    }
    return render(request, template, context)


def groups_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Лев Толстой – зеркало русской революции.'
    context = {
        'title': title,
        'text': 'Здесть будет информация о группах проекта'
    }
    return render(request, template, context)
