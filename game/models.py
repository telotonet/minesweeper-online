from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.
STATUS_CHOICES = (
        ('1', 'Ожидание игрока'),
        ('2', 'В игре'),
        ('3', 'Игра окончена'),
    )
DIFFICULTY_CHOICES = [
        ('easy', 'Легкая'),
        ('medium', 'Средняя'),
        ('hard', 'Сложная'),
    ]
class GameRoom(models.Model):
    link         = models.CharField(max_length=25)
    is_open      = models.BooleanField(default=True)
    status       = models.CharField(max_length=1, choices=STATUS_CHOICES)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True, blank=True, null=True)
    difficulty   = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default='easy')
    lives        = models.PositiveIntegerField(default=1)
    board        = models.JSONField()
    game_state   = models.JSONField()

    def __str__(self):
        return self.link

    def get_absolute_url(self):
        return reverse('game_detail', args=[self.link, ])
    
    class Meta:
        ordering = ['-created_at', ]

class GameMember(models.Model):
    user = models.CharField(max_length=25)
    game = models.ForeignKey(GameRoom, related_name='members', on_delete=models.CASCADE)

    def __str__(self):
        return self.user