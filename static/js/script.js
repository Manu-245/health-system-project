console.log("JavaScript loaded successfully!");  // Debugging check

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded!");

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.emit('join_chat');

    var chatForm = document.getElementById('chat-form');
    if (!chatForm) {
        console.error("Chat form not found!");
        return;
    }

    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log("Send button clicked!");

        var messageInput = document.getElementById('message');
        var message = messageInput.value.trim();
        var recipientId = "{{ recipient.id }}";

        if (recipientId && message) {
            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recipient_id: recipientId, message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log("Message sent successfully!");

                    var chatMessages = document.getElementById('chat-messages');
                    var newMessage = document.createElement('div');
                    newMessage.classList.add("message", "sent");
                    newMessage.innerHTML = "<p><strong>You:</strong> " + data.message + "</p>";
                    chatMessages.appendChild(newMessage);
                    messageInput.value = '';  // Clear input
                    chatMessages.scrollTop = chatMessages.scrollHeight;  // Auto-scroll
                } else {
                    alert("Message failed to send. Try again.");
                }
            })
            .catch(error => console.error("Fetch Error:", error));
        } else {
            console.warn("Recipient ID or message is missing!");
        }
    });

    socket.on('receive_message', function(data) {
        console.log("New message received!");

        var chatMessages = document.getElementById('chat-messages');
        var newMessage = document.createElement('div');
        newMessage.classList.add("message", "received");
        newMessage.innerHTML = "<p><strong>" + data.sender + ":</strong> " + data.message + "</p>";
        chatMessages.appendChild(newMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;  // Auto-scroll
    });
});
