from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

posts = [
    {
        'author': 'Sadrach Pierre',
        'title': 'Call of Duty',
        'review': 'This game is just ok.',
        'date_posted': 'March 23, 2020',
    },
    {
        'author': 'Sadrach Pierre',
        'title': 'Call of Duty',
        'review': 'This video game is amazing!',
        'date_posted': 'March 23, 2020',
    }]


def home(request):
    context = {
        'posts': posts
    }
    return render(request, "page1/home.html", {'context': context})


def base(request):
    context = {
        'posts': posts
    }
    return render(request, 'page1/base.html', {'context': context})
