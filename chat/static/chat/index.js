current_user = JSON.parse(document.getElementById('current-username').textContent);
const add_button = document.querySelector('.create-room-button');
add_button.addEventListener('click', () => {
    const username_input = document.getElementById('username').value.trim();
    if (username_input) {
        fetch("/chat/add_user/" + encodeURIComponent(username_input) + "/", {
            method: 'POST',
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('User added successfully: ' + data.username);
                const div = document.createElement('div');
                div.className = "user-room"
                const btn = document.createElement('button')
                btn.className = "room-button"
                btn.textContent = data.username
                left_btn_room(btn);
                div.appendChild(btn);
                if (document.querySelector('.left-body').innerHTML.search('No chat history available.') !== -1) {
                    document.querySelector('.left-body').innerHTML = '';
                }
                document.querySelector('.left-body').appendChild(div);
            } else {
                alert('Username does not exist. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        alert('Please enter a username.');
    }
});

function getCookie(name) {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='))
        ?.split('=')[1];
}

function get_room_name(name) {
    const sorted_names = [name, current_user].sort();
    return sorted_names.join('_');
}


let chatSocket = null;
function setupRoomEvents(roomname) {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.close();
    }
    chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/private/chat/'
        + roomname
        + '/'
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        msg_panel = document.querySelector('.right-body');
        const messageElement = document.createElement('div');
        if (data.username === current_user) {
            messageElement.className = 'message-self';
        } else {
            messageElement.className = 'message-other';
        }
        messageElement.textContent = data.message;
        msg_panel.appendChild(messageElement);
        msg_panel.scrollTop = msg_panel.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    document.querySelector('.chat-message-input').focus();
    document.querySelector('.chat-message-input').onkeyup = function(e) {
        if (e.key === 'Enter') {
            document.querySelector('.send-message-button').click();
        }
    };

    document.querySelector('.send-message-button').onclick = function(e) {
        const messageInputDom = document.querySelector('.chat-message-input');
        const message = messageInputDom.value;
        if (message.trim() === '') {
            return;
        }
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        messageInputDom.value = '';
    };
}

document.querySelectorAll('.room-button').forEach(button => {
    left_btn_room(button);
});

function left_btn_room(button) {
    button.addEventListener('click', () => {
        const selectedname = button.textContent.trim();
        const roomname = get_room_name(selectedname)
        fetch(`/chat/room/${encodeURIComponent(roomname)}/`, {
            method: 'POST',
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        }).then(response => response.json())
        .then(data => {
            if (data.html) {
                document.querySelector('.right-panel').innerHTML = data.html;
                document.querySelector('.right-header h1').textContent = selectedname;
                setupRoomEvents(roomname);
            } else {
                alert('Failed to load chat room.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
}
