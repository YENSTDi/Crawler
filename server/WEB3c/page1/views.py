# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import plotly.express as px
from pymongo import MongoClient

df = px.data.gapminder().query("continent=='Oceania'")
fig = px.line(df, x="year", y="lifeExp", color='country')

graph = fig.to_html(full_html=False)
plots = {'graph': graph}

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
    ld = loader.get_template('page1/base.html')
    client = MongoClient()
    db = client.crawler
    coll = db.main3c
    res = coll.find({'date': '2020-05-23'})
    context = {
        'context': res, 'graph': plots
    }
    return render(request, 'page1/base.html', context)
    # return HttpResponse(ld.render(context, request))
