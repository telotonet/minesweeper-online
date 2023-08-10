// const board = document.getElementById('board');
// const cells = board.getElementsByClassName('cell');
// let currentPlayer = 'X';
// let isGameOver = false;
// let movesCount = 0;

// function makeMove(cell) {
//     if (isGameOver || cell.textContent !== '') {
//         return;
//     }
//     socket.send(JSON.stringify({
//         'type': 'make_move',
//         'move': cell.id
//     }));
//     if (checkWinner()) {
//         isGameOver = true;
//         return;
//     }

//     if (movesCount === cells.length) {
//         announceDraw();
//         return;
//     }

//     currentPlayer = (currentPlayer === 'X') ? 'O' : 'X';
    
// }

// function checkWinner() {
//     const winningCombos = [
//         [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
//         [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
//         [0, 4, 8], [2, 4, 6] // Diagonals
//     ];

//     for (const combo of winningCombos) {
//         const [a, b, c] = combo;
//         if (cells[a].textContent && cells[a].textContent === cells[b].textContent && cells[a].textContent === cells[c].textContent) {
//             highlightWinningCombo([a, b, c]);
//             return true;
//         }
//     }

//     return false;
// }

// function highlightWinningCombo(combo) {
//     combo.forEach(index => {
//         cells[index].classList.add('bg-success');
//     });
// }

// function announceDraw() {
//     for (const cell of cells) {
//         cell.classList.add('bg-danger');
//     }
//     isGameOver = true;
// }
