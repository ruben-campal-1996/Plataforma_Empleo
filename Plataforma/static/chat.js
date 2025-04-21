document.addEventListener('DOMContentLoaded', function() {
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');

    // Añadir evento de clic a la burbuja
    if (chatBubble) {
        chatBubble.addEventListener('click', function() {
            console.log('Chat bubble clicked'); // Depuración
            toggleChat();
        });
    }

    // Función para alternar visibilidad del chat
    function toggleChat() {
        console.log('toggleChat called'); // Depuración
        chatWindow.classList.toggle('d-none');
        if (!chatWindow.classList.contains('d-none')) {
            chatInput.focus();
            loadChatHistory();
        }
    }

    // Resto del código sin cambios...
    function loadChatHistory() {
        fetch('/recomendacion_ia/get_chat_history/')
            .then(response => response.json())
            .then(data => {
                chatBody.innerHTML = '';
                data.chat_history.forEach(message => {
                    addMessageToChat(message.text, message.is_user ? 'user' : 'bot');
                });
                chatBody.scrollTop = chatBody.scrollHeight;
            });
    }

    function addMessageToChat(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        messageDiv.textContent = text;
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    window.sendMessage = function() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessageToChat(message, 'user');
        chatInput.value = '';

        fetch('/recomendacion_ia/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                addMessageToChat(data.response, 'bot');
            } else if (data.error) {
                addMessageToChat('Error: ' + data.error, 'bot');
            }
        })
        .catch(error => {
            addMessageToChat('Error al conectar con el servidor.', 'bot');
        });
    };

    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return null;
    }

    chatInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});