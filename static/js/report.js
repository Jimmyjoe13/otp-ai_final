/**
 * Opt-AI - Report JavaScript
 * Handle SEO analysis report functionality
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize the AI recommendations section if present
  initAIRecommendations();
  
  // Add event listener to the chat bot button
  const chatBotButton = document.getElementById('open-chat-bot');
  if (chatBotButton) {
    chatBotButton.addEventListener('click', openChatBot);
  }
});

/**
 * Initialize the AI recommendations section
 */
function initAIRecommendations() {
  const aiRecommendationsContainer = document.getElementById('ai-recommendations');
  const analysisId = document.getElementById('analysis-id')?.value;
  
  if (!aiRecommendationsContainer || !analysisId) return;
  
  // Show loading state
  aiRecommendationsContainer.innerHTML = `
    <div class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Generating AI-powered recommendations...</p>
    </div>
  `;
  
  // Fetch AI recommendations
  fetch(`/api/ai-recommendations/${analysisId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load AI recommendations');
      }
      return response.json();
    })
    .then(data => {
      renderAIRecommendations(data, aiRecommendationsContainer);
    })
    .catch(error => {
      aiRecommendationsContainer.innerHTML = `
        <div class="alert alert-danger">
          <i class="fas fa-exclamation-circle me-2"></i> Error loading AI recommendations: ${error.message}
          <button class="btn btn-outline-danger btn-sm mt-2" onclick="initAIRecommendations()">Try Again</button>
        </div>
      `;
    });
}

/**
 * Render AI recommendations
 * @param {Object} data - Recommendations data
 * @param {HTMLElement} container - Container element
 */
function renderAIRecommendations(data, container) {
  let html = `
    <div class="mb-4">
      <h5 class="fw-bold">Summary</h5>
      <p>${data.summary}</p>
    </div>
    
    <div class="mb-4">
      <h5 class="fw-bold">Top Priorities</h5>
      <ul class="list-group">
  `;
  
  // Add priorities
  data.priorities.forEach(priority => {
    html += `<li class="list-group-item"><i class="fas fa-arrow-right text-primary me-2"></i> ${priority}</li>`;
  });
  
  html += `
      </ul>
    </div>
    
    <div class="mb-4">
      <h5 class="fw-bold">Detailed Recommendations</h5>
  `;
  
  // Add recommendations
  data.recommendations.forEach(rec => {
    html += `
      <div class="card mb-3">
        <div class="card-header bg-light">
          <h6 class="mb-0">${rec.title}</h6>
        </div>
        <div class="card-body">
          <p>${rec.description}</p>
          <h6>Action Steps:</h6>
          <ol>
    `;
    
    rec.steps.forEach(step => {
      html += `<li>${step}</li>`;
    });
    
    html += `
          </ol>
        </div>
      </div>
    `;
  });
  
  html += `
    </div>
    
    <div>
      <h5 class="fw-bold">Additional Insights</h5>
      <p>${data.insights}</p>
    </div>
  `;
  
  container.innerHTML = html;
}

/**
 * Open the chat bot
 */
function openChatBot() {
  const chatToggle = document.getElementById('chat-toggle');
  if (chatToggle) {
    chatToggle.click();
    
    // Check if there's a current analysis context to add to the first message
    const analysisId = document.getElementById('analysis-id')?.value;
    const analysisUrl = document.querySelector('h5.text-muted.text-break')?.textContent;
    
    if (analysisId && analysisUrl) {
      // Wait a bit for the chat to open and then add a context message
      setTimeout(() => {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
          chatInput.value = `I'm looking at the SEO report for ${analysisUrl}. Can you help me understand what I should focus on improving first?`;
          // Trigger the chat form submission
          const chatForm = document.getElementById('chat-form');
          if (chatForm) {
            chatForm.dispatchEvent(new Event('submit'));
          }
        }
      }, 500);
    }
  }
}

/**
 * Format a score value as a status class
 * @param {Number} score - The score value (0-100)
 * @returns {String} Status class
 */
function getScoreStatusClass(score) {
  if (score >= 80) return 'success';
  if (score >= 60) return 'warning';
  return 'danger';
}

/**
 * Format a score value as a text status
 * @param {Number} score - The score value (0-100)
 * @returns {String} Status text
 */
function getScoreStatusText(score) {
  if (score >= 80) return 'Good';
  if (score >= 60) return 'Fair';
  return 'Poor';
}
