from django.contrib import admin
from django.urls import path
from .views import main_page, game_detail, create_game, game_history

urlpatterns = [
    path('', main_page, name='main_page'),
    path('game/create/', create_game, name='create_game'),
    path('game/<link>/', game_detail, name='game_detail'),
    path('history/', game_history, name='game_history'),
]
