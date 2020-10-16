from django.urls import path
from . import views

urlpatterns = [
    # path('base.html', views.base, name='page1-base'),
    path('', views.index),
]