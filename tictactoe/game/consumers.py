
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import GameRoom
from .utils import member_num
from random import choice
import time
import asyncio
class GameConsumer(AsyncWebsocketConsumer):
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
        
        self.game_obj = await sync_to_async(GameRoom.objects.get)(link=self.game_link)
        self.count = await sync_to_async(self.game_obj.members.count)()
        players = await sync_to_async(list)(self.game_obj.members.all().values_list('user'))
        self.player_list = [player[0] for player in players]

        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        if self.user_key in self.player_list or user.username in self.player_list:
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'chat_message',
                    'connect': True,
                    'message': f'{self.user_key} connected'
                }
            )

        await self.accept()
        if self.count == member_num and self.user_key in self.player_list:
            await self.channel_layer.group_send(
                self.game_group_name,
                    {
                        'type': 'start_message',
                        'message': True
                    }
                )
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


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'cursor':
            cursor_time = time.time()
            if cursor_time - self.last_cursor_time >= 0.05:
                x = text_data_json.get('x')
                y = text_data_json.get('y')
                user = text_data_json.get('user')
                self.last_cursor_time = cursor_time
                
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'send_cursor',
                        'user': user,
                        'x': x,
                        'y': y,
                    }
                )
        if message_type == 'cell':
            cell_time = time.time()
            if cell_time - self.last_cell_time >= 0.05:
                user = text_data_json.get('user')
                cell = text_data_json.get('cell')
                self.last_cell_time = cell_time
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'send_cell',
                        'user': user,
                        'cell': cell,
                    }
                )
        if message_type == 'mark':
            x = text_data_json.get('x')
            y = text_data_json.get('y')
            user = text_data_json.get('user')
            state_var = text_data_json.get('state')
            state = state_var if state_var in ['c', 'o', 'f', 'q'] else 'o'
            
            self.game_obj.game_state[x-1][y-1] = state
            await sync_to_async(self.game_obj.save)()
            
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
        if message_type == 'open':
            x = text_data_json.get('x')
            y = text_data_json.get('y')
            user = text_data_json.get('user')
            state = 'o'
            opened_cells = []

            if self.game_obj.game_state[x][y] in ['q', 'c', 'f']:
                if self.game_obj.board[x][y] == '0':
                    self.open_adjacent_cells(x, y, opened_cells)
                else:
                    opened_cells.append({'x': x, 'y': y, 'cell': self.game_obj.board[x][y]})
                
                self.game_obj.game_state[x][y] = self.game_obj.board[x][y]
                await sync_to_async(self.game_obj.save)()
                
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'send_open',
                        'state': state,
                        'user': user,
                        'opened_cells': opened_cells
                    }
                )

    async def send_open(self, event):
        state = event['state']
        user = event['user']
        opened_cells = event['opened_cells']
        await self.send(text_data=json.dumps({
            'type': 'open',
            'state': state,
            'user': user,
            'opened_cells': opened_cells,
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

    async def send_cell(self, event):
        cell = event['cell']
        user = event['user']
        await self.send(text_data=json.dumps({
            'type': 'cell',
            'user': user,
            'cell': cell
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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )
        user = self.scope['user']
        if self.user_key in self.player_list or user.username in self.player_list:
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'chat_message',
                    'connect': False,
                    'message': f'{self.user_key} disconnected'
                }
        )

    async def chat_message(self, event):
        message = event['message']
        connect = event['connect']
        await self.send(text_data=json.dumps({
            'chat_message': message,
            'connect': connect,
        }))

    async def start_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'start': message,
        }))
