import random
import string
from .models import GameRoom

member_num = 2 # tictactoe max player number

# game_link parameter is for separate 'game link' and 'user session key'
def generate_random_link(length=random.randint(3,10), game_link=True):
    characters = string.ascii_letters + string.digits
    link = ''.join(random.choice(characters) for _ in range(length))
    if GameRoom.objects.filter(link=link).exists() and game_link:
        return generate_random_link()
    return link

def generate_minesweeper(rows=32, cols=32):
    # M - mine
    # 0 - void cell without any mines around it
    # 1-8 - bomb number around cells
    size = int(rows*cols)
    mines = int(size*0.2) # 20% mines 
    cells_remain = size - mines
    board = [['0' for _ in range(cols)] for _ in range(rows)]
    for _ in range(mines):
        row, col = random.randint(0, rows - 1), random.randint(0, cols - 1)
        while board[row][col] == 'M':
            row, col = random.randint(0, rows - 1), random.randint(0, cols - 1)
        board[row][col] = 'M'
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 'M':
                continue
            count = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = i + dx, j + dy
                    if 0 <= nx < rows and 0 <= ny < cols and board[nx][ny] == 'M':
                        count += 1
            board[i][j] = str(count)
    return board, cells_remain



def open_adjacent_cells(x, y, opened_cells, board, game_state):
    if x < 0 or x >= len(game_state) or y < 0 or y >= len(game_state[0]):
        return
    if game_state[x][y] != 'c':
        return
    
    game_state[x][y] = board[x][y]
    opened_cells.append({'x': x, 'y': y, 'cell': board[x][y]})
    
    if board[x][y] == '0':
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x = x + dx
                new_y = y + dy
                open_adjacent_cells(new_x, new_y, opened_cells, board, game_state)

def start_gamestate(board):
    rows = len(board)
    cols = len(board[0])
    
    game_state = [['c' for _ in range(cols)] for _ in range(rows)]
    
    zero_cells = [(i, j) for i in range(rows) for j in range(cols) if board[i][j] == '0']
    random_zero_cell = random.choice(zero_cells)
    x, y = random_zero_cell
    
    opened_cells = []
    open_adjacent_cells(x, y, opened_cells, board, game_state)
    
    return game_state

