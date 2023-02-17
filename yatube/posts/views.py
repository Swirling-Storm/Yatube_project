from django.shortcuts import render, HttpResponse


# Create your views here.
def index(request):
    return HttpResponse('Тут типа главная страница')


def groups_posts(request, slug):
    return HttpResponse(f'А тут типа пост {slug}')
