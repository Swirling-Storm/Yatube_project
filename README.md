# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

# Yatube project

## Обо мне

Это первый большой проект,
выполненный на платформе Яндекс.Практикум 

Чтобы написать этот проект, мне нужно было:
* разобраться в основах HTML и вёрстки для бэкенд-разработчика;
* создать основу для Django-проекта и добавить в него новые приложения;
* применить MVC на практике;
* использовать шаблонизатор Django;
* освоить Django ORM;
* написать тесты;
* задеплоить проект в облако.

Инструменты и стек: #python #HTML #CSS #Django #Bootstrap #Unittest #Pythonanywhere

## Использованные технологии

* Django==2.2.16
* Pillow==8.3.1
* sorl-thumbnail==12.7.0
* django-debug-toolbar==3.2.4

## Dev режим

Установите и активируйте виртуальное окружение.

```bash
python -m venv venv

source venv/Scripts/activate
```

Используйте пакетный менеджер [pip](https://pip.pypa.io/en/stable/) для установки использованных расширений.

```bash
pip install -r requirements.txt
```

Для запуска проекта используйте

```bash
python manage.py runserver
```