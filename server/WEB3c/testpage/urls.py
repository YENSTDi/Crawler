from django.urls import path
from . import views

urlpatterns = [
    path('home.html', views.home, name=''),
    path('getv/', views.get_value),
    path('file/', views.file),
]