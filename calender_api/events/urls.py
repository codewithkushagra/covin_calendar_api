from django.urls import path

from .views import init_view, redirect_view

app_name = 'events'

urlpatterns = [
    path('init/', init_view, name='init'),
    path('redirect', redirect_view, name='redirect'),
]