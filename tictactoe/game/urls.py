from django.contrib import admin
from django.urls import path
from .views import main_page, game_detail, create_game

urlpatterns = [
    path('', main_page, name='main_page'),
    path('game/create/', create_game, name='create_game'),
    path('game/<link>/', game_detail, name='game_detail'),
]
