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

    // Store raw content for copy functionality
    messageDiv.setAttribute('data-raw-content', content);

    // Format content based on role
    let formattedContent;
    if (role === 'assistant') {
        formattedContent = formatMarkdown(content);
    } else {
        formattedContent = escapeHtml(content).replace(/\n/g, '<br>');
    }

    // Create message HTML with copy button for assistant messages
    let copyButtonHtml = '';
    if (role === 'assistant') {
        copyButtonHtml = `
            <button class="chat-copy-btn" onclick="copyMessage(this)" title="Copy response">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                <span class="copy-text">Copy</span>
            </button>
        `;
    }

    messageDiv.innerHTML = `
        <div class="chat-message-content">${formattedContent}</div>
        <div class="chat-message-footer">
            <span class="chat-message-time">${time}</span>
            ${copyButtonHtml}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Copy message content to clipboard
function copyMessage(button) {
    const messageDiv = button.closest('.chat-message');
    const rawContent = messageDiv.getAttribute('data-raw-content');

    navigator.clipboard.writeText(rawContent).then(() => {
        // Show success feedback
        const copyText = button.querySelector('.copy-text');
        const originalText = copyText.textContent;
        copyText.textContent = 'Copied!';
        button.classList.add('copied');

        setTimeout(() => {
            copyText.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        // Fallback for older browsers
        fallbackCopy(rawContent);
    });
}

// Fallback copy method for older browsers
function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.select();
    try {
        document.execCommand('copy');
    } catch (err) {
        console.error('Fallback copy failed:', err);
    }
    document.body.removeChild(textArea);
}

// Parse and format markdown-style content
function formatMarkdown(text) {
    // Escape HTML first
    let html = escapeHtml(text);

    // Headers: ## Header -> <h3>Header</h3>
    html = html.replace(/^### \*\*(.+?)\*\*$/gm, '<h4 class="md-h4">$1</h4>');
    html = html.replace(/^### (.+)$/gm, '<h4 class="md-h4">$1</h4>');
    html = html.replace(/^## \*\*(.+?)\*\*$/gm, '<h3 class="md-h3">$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h3 class="md-h3">$1</h3>');

    // Bold: **text** -> <strong>text</strong>
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text* -> <em>text</em> (but not inside bold)
    html = html.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '<em>$1</em>');

    // Numbered lists: 1. Item -> <li>Item</li>
    // First, wrap consecutive numbered items
    const numberedListRegex = /^(\d+)\. (.+)$/gm;
    let inNumberedList = false;
    let listBuffer = [];
    const lines = html.split('\n');
    const processedLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const numberedMatch = line.match(/^(\d+)\. (.+)$/);
        const bulletMatch = line.match(/^[-•] (.+)$/);

        if (numberedMatch) {
            if (!inNumberedList) {
                inNumberedList = true;
                processedLines.push('<ol class="md-list">');
            }
            processedLines.push(`<li>${numberedMatch[2]}</li>`);
        } else if (bulletMatch) {
            if (inNumberedList) {
                processedLines.push('</ol>');
                inNumberedList = false;
            }
            // Handle bullet points
            if (i === 0 || !lines[i-1].match(/^[-•] /)) {
                processedLines.push('<ul class="md-list">');
            }
            processedLines.push(`<li>${bulletMatch[1]}</li>`);
            if (i === lines.length - 1 || !lines[i+1].match(/^[-•] /)) {
                processedLines.push('</ul>');
            }
        } else {
            if (inNumberedList) {
                processedLines.push('</ol>');
                inNumberedList = false;
            }
            processedLines.push(line);
        }
    }

    if (inNumberedList) {
        processedLines.push('</ol>');
    }

    html = processedLines.join('\n');

    // Convert remaining newlines to <br> (but not after block elements)
    html = html.replace(/\n(?!<)/g, '<br>');
    html = html.replace(/<br>(<(?:h[34]|ol|ul|li|\/ol|\/ul))/g, '$1');
    html = html.replace(/(<\/(?:h[34]|li|ol|ul)>)<br>/g, '$1');

    // Clean up extra breaks
    html = html.replace(/<br><br>/g, '<br>');
    html = html.replace(/^<br>/, '');
    html = html.replace(/<br>$/, '');

    return html;
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
