from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import GameRoom, GameMember
from .utils import generate_random_link, member_num, generate_minesweeper, start_gamestate
from django.contrib import messages
from random import randint as ri
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pytils.translit import slugify


# Create your views here.
def main_page(request):
    return render(request, 'base.html', {})

def create_game(request):
    if request.method == 'POST':
        link = slugify(request.POST.get('link', None))
        print(link)
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
        board, cells_remain = generate_minesweeper(size, size)
        game_state, cells_remain = start_gamestate(board, cells_remain)
        game = GameRoom.objects.create(
                link=link,
                is_open=is_open, 
                status=1, 
                board=board, 
                game_state=game_state, 
                difficulty=difficulty, 
                lives=lives,
                cells_remain = cells_remain,
            )
    return redirect(reverse('game_detail', args=[game.link, ]))

def game_detail(request, link):
    game_obj = get_object_or_404(GameRoom, link=link)
    if request.user.is_anonymous and not request.session.get('user_key'):
        request.session['user_key'] = generate_random_link(game_link=False)
    user_key = request.user.username or request.session['user_key']
    if game_obj.members.count() < member_num:
        game_member, created = GameMember.objects.get_or_create(game=game_obj, user=user_key)
        game_obj.members.add(game_member)
        game_obj.save()
            
    return render(request, 'game_room.html', {'game_obj': game_obj, 'user_key': user_key})


def game_history(request):
    user_key = request.user.username or request.session.get('user_key')
    user_games = None
    if user_key:
        user_games = GameRoom.objects.filter(members__user=user_key).prefetch_related('members')
    
    paginator = Paginator(user_games, 20)
    page = request.GET.get('page')
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
    return render(request, 'history.html', {'games': games})