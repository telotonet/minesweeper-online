const boardSize = 32;
const board = document.getElementById('board');
let cells = [];
let firstClick = true;

function createBoard() {
    for (let i = 0; i < boardSize; i++) {
        cells[i] = [];
        for (let j = 0; j < boardSize; j++) {
            const cell = document.createElement('div');
            cell.classList.add('cell', 'hidden'); // Добавляем класс hidden
            cell.dataset.row = i;
            cell.dataset.col = j;
            cell.addEventListener('click', handleCellClick);
            board.appendChild(cell);
            cells[i][j] = cell;
        }
    }
}

function handleCellClick(event) {
    const row = parseInt(event.target.dataset.row);
    const col = parseInt(event.target.dataset.col);

    if (firstClick) {
        placeMines(row, col);
        firstClick = false;
    }

    openCell(row, col); // Открываем клетку

    event.target.removeEventListener('click', handleCellClick);
}

function openCell(row, col) {
    const cell = cells[row][col];
    cell.classList.remove('hidden'); // Убираем класс hidden
    cell.classList.add('opened'); // Добавляем класс opened

    const isMine = cell.classList.contains('mine');
    if (!isMine) {
        const minesCount = countAdjacentMines(row, col);
        if (minesCount === 0) {
            for (let i = Math.max(0, row - 1); i <= Math.min(row + 1, boardSize - 1); i++) {
                for (let j = Math.max(0, col - 1); j <= Math.min(col + 1, boardSize - 1); j++) {
                    if (i !== row || j !== col) {
                        const neighborCell = cells[i][j];
                        if (neighborCell.classList.contains('hidden')) {
                            openCell(i, j); // Рекурсивно открываем соседние пустые клетки
                        }
                    }
                }
            }
        } else {
            cell.innerHTML = minesCount;
        }
    } else {
        cell.innerHTML = '💣';
    }
}

// ... (остальной JavaScript код)
