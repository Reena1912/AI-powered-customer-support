// app.js

const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/chat'
  : 'https://ai-powered-customer-support.onrender.com/chat';
const messagesContainer = document.getElementById('messagesContainer');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Add a message to the chat viewport
function appendMessage(text, sender) {
  const messageEl = document.createElement('div');
  messageEl.classList.add('message', sender);

  const bubbleEl = document.createElement('div');
  bubbleEl.classList.add('message-bubble');
  bubbleEl.innerText = text;

  const metaEl = document.createElement('div');
  metaEl.classList.add('message-meta');
  const now = new Date();
  metaEl.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  messageEl.appendChild(bubbleEl);
  messageEl.appendChild(metaEl);
  messagesContainer.appendChild(messageEl);
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show/hide typing indicator
let typingIndicatorEl = null;

function showTypingIndicator() {
  if (typingIndicatorEl) return;
  
  typingIndicatorEl = document.createElement('div');
  typingIndicatorEl.classList.add('message', 'bot', 'typing-message');
  
  const bubbleEl = document.createElement('div');
  bubbleEl.classList.add('message-bubble');
  
  const indicatorEl = document.createElement('div');
  indicatorEl.classList.add('typing-indicator');
  
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('div');
    dot.classList.add('typing-dot');
    indicatorEl.appendChild(dot);
  }
  
  bubbleEl.appendChild(indicatorEl);
  typingIndicatorEl.appendChild(bubbleEl);
  messagesContainer.appendChild(typingIndicatorEl);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
  if (typingIndicatorEl) {
    typingIndicatorEl.remove();
    typingIndicatorEl = null;
  }
}

// Send user question to backend API
async function askQuestion(questionText) {
  if (!questionText.trim()) return;
  
  // Disable inputs during request
  chatInput.value = '';
  chatInput.disabled = true;
  sendBtn.disabled = true;
  
  appendMessage(questionText, 'user');
  showTypingIndicator();
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: questionText })
    });
    
    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }
    
    const data = await response.json();
    removeTypingIndicator();
    appendMessage(data.answer, 'bot');
  } catch (error) {
    console.error('Error contacting chatbot:', error);
    removeTypingIndicator();
    appendMessage(`Unable to connect to the chatbot server. Please ensure the backend is running at ${API_URL}`, 'bot');
  } finally {
    // Re-enable inputs
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

// Handle Form Submit
chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = chatInput.value;
  askQuestion(text);
});

// Setup click handlers for suggestion buttons
document.querySelectorAll('.suggestion-btn').forEach(button => {
  button.addEventListener('click', () => {
    const questionText = button.getAttribute('data-question');
    askQuestion(questionText);
  });
});

// Welcome Message
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    appendMessage("Hello! I'm The Padel Company assistant. Ask me anything about courts, coaches, tournament listings, marketplace rackets, or booking information in India!", 'bot');
  }, 300);
});
