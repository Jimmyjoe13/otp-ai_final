/**
 * Opt-AI - Chatbot JavaScript
 * Handles the AI chatbot functionality
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize chatbot
  initializeChatbot();
});

/**
 * Initialize the chatbot UI and functionality
 */
function initializeChatbot() {
  const chatToggle = document.getElementById('chat-toggle');
  const chatContainer = document.getElementById('chat-container');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');
  
  // If elements don't exist, chatbot is not available on this page
  if (!chatToggle || !chatContainer || !chatForm || !chatInput || !chatMessages) {
    return;
  }
  
  // Toggle chat window
  chatToggle.addEventListener('click', () => {
    chatContainer.classList.toggle('chat-hidden');
    chatToggle.classList.toggle('active');
    
    // If opening chat for first time, add welcome message
    if (!chatContainer.classList.contains('chat-hidden') && chatMessages.children.length === 0) {
      addBotMessage("👋 Hi there! I'm Opty-bot, your SEO assistant. Ask me anything about SEO or how to improve your website's performance!");
    }
    
    // Focus input when opening
    if (!chatContainer.classList.contains('chat-hidden')) {
      chatInput.focus();
    }
  });
  
  // Handle chat form submission
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    
    // Get bot response
    getBotResponse(message);
  });
  
  // Handle pressing Enter to submit
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });
}

/**
 * Add a user message to the chat
 * @param {String} message - User message text
 */
function addUserMessage(message) {
  const chatMessages = document.getElementById('chat-messages');
  
  const messageElement = document.createElement('div');
  messageElement.className = 'chat-message user-message';
  messageElement.innerHTML = `
    <div class="message-content">
      <p>${escapeHTML(message)}</p>
    </div>
    <div class="message-avatar">
      <div class="avatar user-avatar">
        <i class="fas fa-user"></i>
      </div>
    </div>
  `;
  
  chatMessages.appendChild(messageElement);
  
  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Add a bot message to the chat
 * @param {String} message - Bot message text/HTML
 */
function addBotMessage(message) {
  const chatMessages = document.getElementById('chat-messages');
  
  const messageElement = document.createElement('div');
  messageElement.className = 'chat-message bot-message';
  messageElement.innerHTML = `
    <div class="message-avatar">
      <div class="avatar bot-avatar">
        <i class="fas fa-robot"></i>
      </div>
    </div>
    <div class="message-content">
      <p>${message}</p>
    </div>
  `;
  
  chatMessages.appendChild(messageElement);
  
  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Add a loading message while waiting for bot response
 * @returns {HTMLElement} The loading message element
 */
function addLoadingMessage() {
  const chatMessages = document.getElementById('chat-messages');
  
  const messageElement = document.createElement('div');
  messageElement.className = 'chat-message bot-message';
  messageElement.innerHTML = `
    <div class="message-avatar">
      <div class="avatar bot-avatar">
        <i class="fas fa-robot"></i>
      </div>
    </div>
    <div class="message-content">
      <p><span class="typing-indicator"><span>.</span><span>.</span><span>.</span></span></p>
    </div>
  `;
  
  chatMessages.appendChild(messageElement);
  
  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  return messageElement;
}

/**
 * Get a response from the bot
 * @param {String} message - User message
 */
function getBotResponse(message) {
  // Add loading message
  const loadingMessage = addLoadingMessage();
  
  // Get context if available
  const analysisId = document.getElementById('analysis-id')?.value;
  let apiUrl = '/api/chatbot';
  
  if (analysisId) {
    apiUrl += `?analysis_id=${analysisId}`;
  }
  
  // Send request to API
  fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: message }),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      return response.json();
    })
    .then(data => {
      // Remove loading message
      loadingMessage.remove();
      
      // Add bot response
      addBotMessage(data.response);
    })
    .catch(error => {
      // Remove loading message
      loadingMessage.remove();
      
      // Add error message
      addBotMessage(`I'm sorry, I encountered an error: ${error.message}. Please try again later.`);
    });
}

/**
 * Escape HTML to prevent XSS
 * @param {String} unsafe - Unsafe string
 * @returns {String} Escaped string
 */
function escapeHTML(unsafe) {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
