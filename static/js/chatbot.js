// AI Medical Chatbot JavaScript
// Handles chat functionality for the health assistant

// Toggle chatbot modal
function toggleChatbot() {
    const modal = document.getElementById('chatbot-modal');
    const toggleBtn = document.getElementById('chatbot-toggle');

    if (modal.classList.contains('show')) {
        modal.classList.remove('show');
        toggleBtn.style.transform = 'scale(1)';
    } else {
        modal.classList.add('show');
        toggleBtn.style.transform = 'scale(1.05)';
        // Focus on input when opening
        setTimeout(() => {
            const chatInput = document.getElementById('chat-input');
            if (chatInput) chatInput.focus();
        }, 300);
    }
}

// Close chatbot when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('chatbot-modal');
    const toggleBtn = document.getElementById('chatbot-toggle');
    const chatbotWidget = document.getElementById('chatbot-widget');

    if (!modal.contains(event.target) && !toggleBtn.contains(event.target) && !chatbotWidget.contains(event.target)) {
        if (modal.classList.contains('show')) {
            toggleChatbot();
        }
    }
});

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');

    // Clear input
    input.value = '';

    // Disable send button
    const sendButton = document.getElementById('send-button');
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';

    // Show typing indicator
    showTypingIndicator();

    // Send to server
    fetch('/api/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();

        if (data.error) {
            addMessage(data.error, 'bot', true);
        } else {
            addMessage(data.reply, 'bot');
        }
    })
    .catch(error => {
        hideTypingIndicator();
        addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'bot', true);
        console.error('Chatbot error:', error);
    })
    .finally(() => {
        // Re-enable send button
        sendButton.disabled = false;
        sendButton.innerHTML = '<i class="bi bi-send"></i> Send';
    });
}

function addMessage(text, sender, isError = false) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const avatar = sender === 'user' ?
        '<i class="bi bi-person-circle-fill text-white"></i>' :
        '<img src="/static/images/Chatbot_logo.jpg" alt="AI Health Assistant" class="chatbot-logo-avatar">';

    messageDiv.innerHTML = `
        <div class="message-avatar">
            ${avatar}
        </div>
        <div class="message-content">
            <div class="message-text ${isError ? 'text-danger' : ''}">
                ${text.replace(/\n/g, '<br>')}
            </div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'typing-indicator';
    indicator.innerHTML = `
        <div class="message bot-message">
            <div class="message-avatar">
                <img src="/static/images/Chatbot_logo.jpg" alt="AI Health Assistant" class="chatbot-logo-avatar">
            </div>
            <div class="message-content">
                <div class="message-text">
                    <i class="bi bi-three-dots"></i> Thinking...
                </div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(indicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});