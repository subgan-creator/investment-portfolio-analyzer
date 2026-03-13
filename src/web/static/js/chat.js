/**
 * AI Chat Widget JavaScript
 * Handles chat functionality for the AI Investment Advisor
 */

// Portfolio data will be passed from the template
let portfolioData = {};

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initChat();
});

function initChat() {
    const chatBubble = document.getElementById('chatBubble');
    const chatPanel = document.getElementById('chatPanel');
    const closeChatBtn = document.getElementById('closeChatBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');

    // Toggle chat panel
    chatBubble.addEventListener('click', function() {
        chatPanel.classList.add('open');
        loadChatHistory();
        chatInput.focus();
    });

    closeChatBtn.addEventListener('click', function() {
        chatPanel.classList.remove('open');
    });

    // Clear chat
    clearChatBtn.addEventListener('click', function() {
        if (confirm('Clear conversation history?')) {
            clearChat();
        }
    });

    // Send message on button click
    chatSendBtn.addEventListener('click', sendMessage);

    // Send message on Enter (but allow Shift+Enter for new lines)
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 100) + 'px';
    });

    // Check API status on load
    checkApiStatus();
}

// Set portfolio data (called from template)
function setPortfolioData(data) {
    portfolioData = data;
}

// Check if API is configured
async function checkApiStatus() {
    try {
        const response = await fetch('/api/chat/status');
        const data = await response.json();

        if (!data.available) {
            showNotConfigured();
        }
    } catch (error) {
        console.error('Error checking API status:', error);
    }
}

// Show not configured message
function showNotConfigured() {
    const welcome = document.getElementById('chatWelcome');
    welcome.innerHTML = `
        <div class="chat-not-configured">
            <h4>API Key Required</h4>
            <p>To enable AI insights, add your OpenAI API key:</p>
            <p><code>OPENAI_API_KEY=sk-...</code></p>
            <p>Create a <code>.env</code> file in the project root.</p>
        </div>
    `;
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat');
        const data = await response.json();

        if (data.success && data.messages.length > 0) {
            const chatMessages = document.getElementById('chatMessages');
            const welcome = document.getElementById('chatWelcome');

            // Hide welcome, show messages
            welcome.style.display = 'none';

            // Clear existing messages (except welcome)
            const existingMessages = chatMessages.querySelectorAll('.chat-message');
            existingMessages.forEach(m => m.remove());

            // Add messages
            data.messages.forEach(msg => {
                appendMessage(msg.role, msg.content, msg.created_at_formatted);
            });

            scrollToBottom();
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Send message
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const message = chatInput.value.trim();

    if (!message) return;

    // Disable input while sending
    chatInput.disabled = true;
    chatSendBtn.disabled = true;

    // Hide welcome message
    const welcome = document.getElementById('chatWelcome');
    welcome.style.display = 'none';

    // Add user message to chat
    const time = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    appendMessage('user', message, time);

    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Show typing indicator
    showTyping();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                portfolio_data: portfolioData
            })
        });

        const data = await response.json();

        // Remove typing indicator
        hideTyping();

        if (data.success) {
            const responseTime = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
            appendMessage('assistant', data.response, responseTime);
        } else {
            showError(data.error || 'Failed to get response');
        }
    } catch (error) {
        hideTyping();
        showError('Network error. Please try again.');
        console.error('Error sending message:', error);
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        chatSendBtn.disabled = false;
        chatInput.focus();
    }

    scrollToBottom();
}

// Send suggestion message
function sendSuggestion(text) {
    const chatInput = document.getElementById('chatInput');
    chatInput.value = text;
    sendMessage();
}

// Get specific recommendations (primary CTA)
async function getSpecificRecommendations() {
    const chatSendBtn = document.getElementById('chatSendBtn');

    // Disable button while processing
    chatSendBtn.disabled = true;

    // Hide welcome message
    const welcome = document.getElementById('chatWelcome');
    welcome.style.display = 'none';

    // Add user message to chat
    const time = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    appendMessage('user', 'Give me specific investment recommendations for my portfolio', time);

    // Show typing indicator
    showTyping();

    try {
        const response = await fetch('/api/recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                portfolio_data: portfolioData
            })
        });

        const data = await response.json();

        // Remove typing indicator
        hideTyping();

        if (data.success) {
            const responseTime = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
            appendMessage('assistant', data.recommendations, responseTime);
        } else {
            showError(data.error || 'Failed to get recommendations');
        }
    } catch (error) {
        hideTyping();
        showError('Network error. Please try again.');
        console.error('Error getting recommendations:', error);
    } finally {
        chatSendBtn.disabled = false;
    }

    scrollToBottom();
}

// Append message to chat
function appendMessage(role, content, time) {
    const chatMessages = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.innerHTML = `
        <div class="chat-message-content">${escapeHtml(content).replace(/\n/g, '<br>')}</div>
        <span class="chat-message-time">${time}</span>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Show typing indicator
function showTyping() {
    const chatMessages = document.getElementById('chatMessages');

    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'chat-typing';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';

    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

// Hide typing indicator
function hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

// Show error message
function showError(message) {
    const chatMessages = document.getElementById('chatMessages');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'chat-error';
    errorDiv.textContent = message;

    chatMessages.appendChild(errorDiv);
    scrollToBottom();

    // Remove error after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
}

// Clear chat history
async function clearChat() {
    try {
        const response = await fetch('/api/chat', { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            // Clear messages from UI
            const chatMessages = document.getElementById('chatMessages');
            const messages = chatMessages.querySelectorAll('.chat-message, .chat-error');
            messages.forEach(m => m.remove());

            // Show welcome message again
            const welcome = document.getElementById('chatWelcome');
            welcome.style.display = 'block';
        }
    } catch (error) {
        console.error('Error clearing chat:', error);
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
