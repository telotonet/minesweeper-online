from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import GameRoom, GameMember
from .utils import generate_random_link, member_num, generate_minesweeper, start_gamestate
from django.contrib import messages
from random import randint as ri
from django.db import transaction
from django.utils.text import slugify

# Create your views here.
def main_page(request):
    return render(request, 'base.html', {})

def create_game(request):
    if request.method == 'POST':
        link = slugify(request.POST.get('link', None))
        is_open = bool(int(request.POST.get('isOpen', False)))
        difficulty = request.POST.get('difficulty', 'easy')
        if not link:
            link = generate_random_link()
        if GameRoom.objects.filter(link=link).exists():
            messages.error(request, "Игра с такой ссылкой уже существует", extra_tags="alert-danger")
            return redirect('main_page')
        lives = 1
        size = 10
        if difficulty == 'medium':
            lives = 2
            size = 16
        elif difficulty == 'hard':
            lives = 3
            size = 32
        game = GameRoom.objects.create(
                link=link,
                is_open=is_open, 
                status=1, 
                board=generate_minesweeper(size, size), 
                game_state=start_gamestate(size, size), 
                difficulty=difficulty, 
                lives=lives
            )
    return redirect(reverse('game_detail', args=[game.link, ]))

def game_detail(request, link):
    game_obj = get_object_or_404(GameRoom, link=link)
    if request.user.is_anonymous and not request.session.get('user_key'):
        request.session['user_key'] = generate_random_link(game_link=False)
    user_key = request.user.username or request.session['user_key']
    if game_obj.members.count() < member_num and game_obj.status == '1':
        game_member, created = GameMember.objects.get_or_create(game=game_obj, user=user_key)
        game_room_members = game_obj.members.add(game_member)
        if game_obj.members.count() == member_num:
            game_obj.status = '2'
        game_obj.save()
            
    return render(request, 'game_room.html', {'game_obj': game_obj, 'user_key': user_key})



