
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import GameRoom
from .utils import member_num
from random import choice
import time
import asyncio
from channels.db import database_sync_to_async
from django.utils.html import escape, strip_tags


class GameConsumer(AsyncWebsocketConsumer):
    connected_users = dict()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_cursor_time = 0
        self.last_cell_time = 0
    async def connect(self):
        self.game_link = self.scope['url_route']['kwargs']['link']
        self.game_group_name = f'game_group_{self.game_link}'
        session = self.scope['session']['user_key']
        user = self.scope['user']
        self.user_key = user.username or session

        await self._setup_game()
        if self.game_obj.status == '3':
            await self.close()

        await self._add_to_game_group(user)

        await self.accept()

        if self.count == member_num and self.user_key in self.player_list and self.game_obj.status == '1':
            await self.start_handle_message()
    
    @database_sync_to_async
    def save_game(self):
        self.game_obj.save()
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        cursor_time = time.time()
        if message_type == 'cursor' and cursor_time - self.last_cursor_time >= 0.05 and self.user_key in self.player_list:
            x = text_data_json.get('x')
            y = text_data_json.get('y')
            user = text_data_json.get('user')
            self.last_cursor_time = cursor_time
            await self.cursor_handle_message(x, y, user)
            
        if message_type == 'mark' and self.user_key in self.player_list:
            x = text_data_json.get('x')
            y = text_data_json.get('y')
            user = text_data_json.get('user')
            state_var = text_data_json.get('state')
            state = state_var if state_var in ['c', 'f', 'q'] else 'c'
            await self.mark_handle_message(x, y, user, state)

        if message_type == 'open' and self.user_key in self.player_list:
            x = text_data_json.get('x')
            y = text_data_json.get('y')
            user = text_data_json.get('user')
            opened_cells = []
            await self.open_handle_message(x, y, user, opened_cells)
        if message_type == 'message':
            message = text_data_json.get('message')
            user = self.user_key
            await self.chat_handle_message(message, user)    
    # Логика курсора
    async def cursor_handle_message(self, x, y, user):
         await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'send_cursor',
                    'user': user,
                    'x': x,
                    'y': y,
                }
            )
    # Логика отметки клеток
    async def mark_handle_message(self, x, y, user, state):
        self.game_obj.game_state[x-1][y-1] = state

        await self.save_game()
        
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_mark',
                'state': state,
                'user': user,
                'x': x,
                'y': y,
            }
        )
    # Логика открытия клеток
    async def open_handle_message(self, x, y, user, opened_cells):
        if self.game_obj.game_state[x][y] in ['q', 'c', 'f']:
            if self.game_obj.board[x][y] == '0':
                self.open_adjacent_cells(x, y, opened_cells)
            else:
                if self.game_obj.board[x][y] == 'M' and self.game_obj.lives > 0:
                    self.game_obj.lives -= 1
                opened_cells.append({'x': x, 'y': y, 'cell': self.game_obj.board[x][y]})
            
            self.game_obj.game_state[x][y] = self.game_obj.board[x][y]

            await self.save_game()
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'send_open',
                    'user': user,
                    'opened_cells': opened_cells
                }
            )
            await self.check_game_status()
    # Отправка старт сообщения в группу
    async def start_handle_message(self):
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_start_message',
            }
        )
    # Логика чата
    async def chat_handle_message(self, message, user):
        stripped_message = strip_tags(message)
        sanitized_message = escape(stripped_message)
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_chat_message',
                'message': sanitized_message,
                'user': user
            }
        )

    async def send_open(self, event):
        user = event['user']
        opened_cells = event['opened_cells']
        await self.send(text_data=json.dumps({
            'type': 'open',
            'user': user,
            'opened_cells': opened_cells,
            'lives': self.game_obj.lives
        }))

    async def send_mark(self, event):
        x = event['x']
        y = event['y']
        user = event['user']
        state = event['state']
        await self.send(text_data=json.dumps({
            'type': 'mark',
            'state': state,
            'user': user,
            'x': x,
            'y': y,
        }))

    async def send_cursor(self, event):
        x = event['x']
        y = event['y']
        user = event['user']
        await self.send(text_data=json.dumps({
            'type': 'cursor',
            'user': user,
            'x': x,
            'y': y,
        }))
    # Общение в чате
    async def send_chat_message(self, event):
        message = event['message']
        user = event['user']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'user': user,
        }))
    # Отправка сообщения о начале игры
    async def send_start_message(self, event):
        await self.send(text_data=json.dumps({
            'start': True,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )
        if self.user_key in self.connected_users_dict:
            self.connected_users_dict.remove(self.user_key)
            if not self.connected_users_dict and self.game_obj.status == '2':
                self.game_obj.status = '3'  # Устанавливаем статус игры 'Игра окончена'
                await self.save_game()
            else:
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'send_chat_message',
                        'message': f'отключился от игры',
                        'user': self.user_key,
                    }
                )

    async def _setup_game(self):
        self.game_obj = await sync_to_async(GameRoom.objects.get)(link=self.game_link)
        self.count = await sync_to_async(self.game_obj.members.count)()
        players = await sync_to_async(list)(self.game_obj.members.all().values_list('user'))
        self.player_list = [player[0] for player in players]

    async def _add_to_game_group(self, user):
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        if self.user_key in self.player_list:
            self.connected_users_dict = self.connected_users.get(f'{self.game_link}')
            if self.connected_users_dict:
                self.connected_users_dict.append(self.user_key)
            else:
                self.connected_users_dict = self.connected_users[f'{self.game_link}'] = []
                self.connected_users_dict.append(self.user_key)
            await self._send_connect_message()

    async def _send_connect_message(self):
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_chat_message',
                'message': f'присоединился к игре',
                'user': self.user_key
            }
        )
    
    # Логика открытия смежных нулевых клеток
    def open_adjacent_cells(self, x, y, opened_cells):
        if x < 0 or x >= len(self.game_obj.game_state) or y < 0 or y >= len(self.game_obj.game_state[0]):
            return
        if self.game_obj.game_state[x][y] not in ['q', 'c', 'f']:
            return
        
        self.game_obj.game_state[x][y] = self.game_obj.board[x][y]
        opened_cells.append({'x': x, 'y': y, 'cell': self.game_obj.board[x][y]})
        
        if self.game_obj.board[x][y] == '0':
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x = x + dx
                    new_y = y + dy
                    self.open_adjacent_cells(new_x, new_y, opened_cells)
    
    async def check_game_status(self):
        if self.game_obj.lives <= 0 or 'c' not in [cell for row in self.game_obj.game_state for cell in row]:
            self.game_obj.status = '3'
            await self.save_game()
            # await self.channel_layer.group_send(
            #     self.game_group_name,
            #     {
            #         'type': 'close_connections',
            #     }
            # )

    async def close_connections(self, event):
        await self.close()








