const board = document.getElementById('board');
board.style.gridTemplateColumns = `repeat(${size}, ${cellSize}px)`
board.style.gridTemplateRows = `repeat(${size}, ${cellSize}px)`;
let cells = [];
let firstClick = true;


function createBoard(gameState) {
    for (let i = 0; i < size; i++) {
        cells[i] = [];
        for (let j = 0; j < size; j++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.row = i;
            cell.dataset.col = j;
            const state = gameState[i][j];
            board.appendChild(cell);
            cells[i][j] = cell; // Извлекаем состояние из массива
            if (state === 'c') {
                cell.classList.add('hidden');
            } else if (state === 'f') {
                cell.classList.add('mine-marked');
                cell.classList.add('hidden');
                cell.innerHTML = '🚩';
            } else if (state === 'q') {
                cell.classList.add('mine-question');
                cell.classList.add('hidden');
                cell.innerHTML = '❓';
            } else {
                openCell(j, i, state)
            }
            cell.addEventListener('click', handleCellClick);
            cell.addEventListener('contextmenu', handleCellContextmenu);

        }
    }
}


function handleCellContextmenu(event) {
    event.preventDefault();
    state = toggleMark(event.target);
    socket.send(JSON.stringify({
        type: 'mark',
        state: state,
        user: user_key,
        y: parseInt(event.target.dataset.col)+1,
        x: parseInt(event.target.dataset.row)+1,
    }));
}

function handleCellClick(event) {
    if (!event.target.classList.contains('opened')){
        event.preventDefault();
        const col = parseInt(event.target.dataset.col)
        const row = parseInt(event.target.dataset.row)

        socket.send(JSON.stringify({
            type: 'open',
            user: user_key,
            y: col,
            x: row,
        }));
    }
}
    

function toggleMark(cell) {
    let state = 'c';
    if (cell.classList.contains('hidden')) {
        if (cell.classList.contains('mine-marked')) {
            cell.classList.remove('mine-marked');
            cell.classList.add('mine-question');
            cell.innerHTML = '❓'
            state = 'q'
        } else if (cell.classList.contains('mine-question')) {
            cell.classList.remove('mine-question');
            cell.innerHTML = '';
            state = 'c'
        } else {
            if (cell.innerHTML === '') {
                cell.classList.add('mine-marked');
                cell.innerHTML = '🚩'; // Метка миной
                state = 'f'
            }
        }
    }
    return state
}   

function openCell(col, row, cellValue) {
    const cell = cells[row][col];
    cell.classList.remove('hidden'); // Убираем класс hidden
    cell.classList.add('opened'); // Добавляем класс opened
    const isF = cell.classList.contains('mine-marked');
    const isQ = cell.classList.contains('mine-question');
    if (isF || isQ) {
        cell.classList.remove('mine-marked');
        cell.classList.remove('mine-question');
        cell.innerHTML = '';
    }
    if (cellValue === 'M') {
        cell.style.transition = 'all 0.5s linear';
        cell.style.backgroundColor = 'red';
        cell.innerHTML = '💣';
        cell.style.transition = 'box-shadow 0.7s linear';
        cell.style.boxShadow = `0 0 ${cellSize-0.2*cellSize}px ${cellSize-0.8*cellSize}px red`;
        cell.style.zIndex = '99';
        setTimeout(() => {
            cell.style.boxShadow = 'none'; // Убираем тени
            cell.style.zIndex = '0';
        }, 700);
    } else if (cellValue === '0') {
        cell.innerHTML = '';
    } else {
        cell.style.color = colors[parseInt(cellValue) - 1];
        cell.innerHTML = cellValue;
    }
}
createBoard(gameState)
