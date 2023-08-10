const boardSize = 32;
const board = document.getElementById('board');
let cells = [];
let firstClick = true;


function createBoard(gameState) {
    for (let i = 0; i < boardSize; i++) {
        cells[i] = [];
        for (let j = 0; j < boardSize; j++) {
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
        console.log('hello')
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
    console.log(col, row)
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
    } else if (cellValue === '0') {
        cell.innerHTML = '';
    } else {
        cell.style.color = colors[parseInt(cellValue) - 1];
        cell.innerHTML = cellValue;
    }
}


// function countAdjacentMines(row, col) {
//     let count = 0;
//     for (let i = Math.max(0, row - 1); i <= Math.min(row + 1, boardSize - 1); i++) {
//         for (let j = Math.max(0, col - 1); j <= Math.min(col + 1, boardSize - 1); j++) {
//             if (i === row && j === col) continue;
//             if (cells[i][j].classList.contains('mine')) count++;
//         }
//     }
//     return count;
// }

// function revealMines() {
//     for (let i = 0; i < boardSize; i++) {
//         for (let j = 0; j < boardSize; j++) {
//             const cell = cells[i][j];
//             if (cell.classList.contains('mine') && cell.classList.contains('hidden')) {
//                 cell.innerHTML = '💣';
//             }
//         }
//     }
// }

// function gameOver() {
//     revealMines();
//     alert('Game Over!');
// }

// function checkWin() {
//     let allSafeCellsOpened = true;
//     for (let i = 0; i < boardSize; i++) {
//         for (let j = 0; j < boardSize; j++) {
//             const cell = cells[i][j];
//             const isMine = cell.classList.contains('mine');
//             const isOpened = cell.classList.contains('opened');
//             if (isMine && isOpened) {
//                 gameOver();
//                 return;
//             }
//             if (!isMine && !isOpened) {
//                 allSafeCellsOpened = false;
//             }
//         }
//     }
//     if (allSafeCellsOpened) {
//         alert('Congratulations! You won!');
//     }
// }

// Завершение хода игры при клике на бомбу
function handleMineClick(event) {
    event.preventDefault();
    gameOver();
}

function initGame() {
    createBoard(gameState);
    document.querySelectorAll('.mine').forEach((mine) => {
        mine.addEventListener('click', handleMineClick);
    });
}

initGame();

