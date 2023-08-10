const chat = $('#chat')
// cursors of other players have random colors from this list
// ordering of first eight colors is for bomb numbers on a cell
const colors = [
    'green', // 1 bomb around
    'blue', // 2 bombs around
    'darkorange', // 3 bombs around
    'red', // 4 bombs around
    'violet', // 5 bombs around
    'purple', // 6 bombs around 
    'pink', // 7 bombs around
    'darkblue', // 8 bombs around (is this real?)
    'green',
    'purple',
    'magenta',
    'lime',
    'teal',
    'violet',
    'fuchsia',
    'aqua',
    'gold',
    'mediumvioletred',
    'steelblue',
    'sandybrown',
    'mediumturquoise',
    'cadetblue',
];
const cursorsId = {};
const userColors = {}; 
const userCells = {};
const socket = new WebSocket(`ws://${window.location.host}/ws/game/${link}/`);
function disableContextMenu(event) {
    event.preventDefault();
}

board.addEventListener('contextmenu', disableContextMenu);

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data['start']){
        // Сообщение для чата "Игра началась". Запуск игры
        const chatMessage = $('<div class="text-success"></div>').text('Игра началась');
        $('#gameStatus').addClass('text-success').text('В игре')
        chat.append(chatMessage);
        // chat.scrollTop(chat[0].scrollHeight);
    }
    if (data.type === 'cursor') {
        const userId = data.user;
        const cursorColor = getRandomColor();
        // Создание курсора для всех кроме текущего пользователя
        if (userId !== user_key && !cursorsId[userId]) {
            addCursor(userId, cursorColor);
        }
        const boardRect = board.getBoundingClientRect();
        // Расстояние по горизонтали и вертикали до борда
        const xRelativeToBoard = (data.x / 100) * board.offsetWidth + boardRect.x;
        const yRelativeToBoard = (data.y / 100) * board.offsetHeight + boardRect.y;
        // Процентное вычисление положения курсора в окне игры
        const col = Math.floor((data.x / 100) * 32);
        const row = Math.floor((data.y / 100) * 32);
        // Поиск клетки, на которую пользователь навёл курсор
        let cell = $('.cell[data-row="' + row + '"][data-col="' + col + '"]');
        // Убрать ховер с предыдущей клеточки, если такая имеется
        if (userCells[userId] != cell) {
            try{
            userCells[userId].removeClass('hovered');} catch{}
        }
        if (userId != user_key){
            cell.addClass('hovered');
        }
        userCells[userId] = cell
        const cursorElement = cursorsId[userId];
        // Отклонение курсора по горизонтали и вертикали от граней дисплея
        if (cursorElement) {
            cursorElement.style.left = xRelativeToBoard + 'px'; 
            cursorElement.style.top = yRelativeToBoard + 'px';
        }
    }
    if (data.type == 'mark') {
        const col = data.y - 1
        const row = data.x - 1
        const state = data.state
        let cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
        if (data.user != user_key){
            toggleMark(cell)
        }
    }
    if (data.type == 'open') {
        const openedCells = data.opened_cells;
        for (const cellData of openedCells) {
            const col = cellData.y;
            const row = cellData.x;
            const cellValue = cellData.cell;
            openCell(col, row, cellValue);
        }
    }
};


let lastSentTime = 0;
board.addEventListener('mousemove', (event) => {
    // Передача информации о передвижении курсора на сервер раз в 50 мс
    const currentTime = Date.now();
    if (currentTime - lastSentTime >= 50) {
        lastSentTime = currentTime;
        let boardRect = board.getBoundingClientRect();
        // Вычисление положения курсора внутри игрового окна в процентном соотношении
        const x = ((event.clientX - boardRect.x) / board.offsetWidth) * 100;
        const y = ((event.clientY - boardRect.y) / board.offsetHeight) * 100;

        socket.send(JSON.stringify({
            type: 'cursor',
            user: user_key,
            x: x,
            y: y,
        }));
    }
});

function addCursor(userId, color) {
    const cursorElement = document.createElement('div');
    cursorElement.className = 'cursor';
    cursorElement.style.backgroundColor = color;
    cursorElement.style.transition = 'all 0.08s linear';

    const usernameElement = document.createElement('div');
    usernameElement.className = 'username';
    usernameElement.textContent = userId;

    cursorElement.appendChild(usernameElement);

    board.appendChild(cursorElement);
    cursorsId[userId] = cursorElement;
    userColors[userId] = color; 
}

function getRandomColor() {
    const randomIndex = Math.floor(Math.random() * colors.length);
    return colors[randomIndex];
}

socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event);
};

socket.onerror = (event) => {
    console.error('WebSocket error:', event);
};
