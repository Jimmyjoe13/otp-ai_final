/**
 * Opt-AI - Analyzer JavaScript
 * Handle analysis form and results
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize analysis type selector
  initAnalysisTypeSelector();
  
  // Set up URL validation
  const urlInput = document.getElementById('url-input');
  if (urlInput) {
    urlInput.addEventListener('input', validateUrlRealtime);
    urlInput.addEventListener('blur', validateUrl);
  }
  
  // Set up form submission
  const analysisForm = document.getElementById('analysis-form');
  if (analysisForm) {
    analysisForm.addEventListener('submit', handleAnalysisSubmit);
  }
});

/**
 * Initialize the analysis type selector
 */
function initAnalysisTypeSelector() {
  const analysisTypeButtons = document.querySelectorAll('.analysis-type-btn');
  const analysisTypeInput = document.getElementById('analysis_type');
  
  if (!analysisTypeButtons.length || !analysisTypeInput) return;
  
  // Set initial value
  const initialType = analysisTypeInput.value || 'meta';
  setActiveAnalysisType(initialType);
  
  // Add click handlers to buttons
  analysisTypeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const type = this.dataset.type;
      analysisTypeInput.value = type;
      setActiveAnalysisType(type);
    });
  });
}

/**
 * Set the active analysis type in the UI
 * @param {String} type - Analysis type (meta, partial, complete, deep)
 */
function setActiveAnalysisType(type) {
  const analysisTypeButtons = document.querySelectorAll('.analysis-type-btn');
  
  // Reset all buttons
  analysisTypeButtons.forEach(button => {
    button.classList.remove('active');
    button.classList.add('btn-outline-primary');
    button.classList.remove('btn-primary');
  });
  
  // Set active button
  const activeButton = document.querySelector(`.analysis-type-btn[data-type="${type}"]`);
  if (activeButton) {
    activeButton.classList.add('active');
    activeButton.classList.remove('btn-outline-primary');
    activeButton.classList.add('btn-primary');
  }
  
  // Update description
  updateAnalysisDescription(type);
}

/**
 * Update the analysis description based on selected type
 * @param {String} type - Analysis type
 */
function updateAnalysisDescription(type) {
  const descriptionElement = document.getElementById('analysis-description');
  if (!descriptionElement) return;
  
  let description = '';
  
  switch(type) {
    case 'meta':
      description = 'Meta Tags Analysis checks your title, description, and meta tags for SEO best practices.';
      break;
    case 'partial':
      description = 'Partial Analysis includes meta tags plus basic content analysis including headings and content structure.';
      break;
    case 'complete':
      description = 'Complete Analysis provides a comprehensive review of meta tags, content, and technical SEO aspects.';
      break;
    case 'deep':
      description = 'Deep Analysis includes everything in Complete Analysis plus AI-powered semantic analysis of your content.';
      break;
    default:
      description = 'Select an analysis type to begin.';
  }
  
  descriptionElement.textContent = description;
}

/**
 * Validate URL input in real-time (less strict than blur validation)
 */
function validateUrlRealtime() {
  const urlInput = document.getElementById('url-input');
  const errorElement = document.getElementById('url-input-error');
  
  if (!urlInput || !errorElement) return;
  
  const url = urlInput.value.trim();
  
  // Clear error if empty (will be caught on blur/submit)
  if (!url) {
    errorElement.textContent = '';
    urlInput.classList.remove('is-invalid');
    urlInput.classList.remove('is-valid');
    return;
  }
  
  // Simple validation for realtime feedback
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    errorElement.textContent = 'URL must start with http:// or https://';
    urlInput.classList.add('is-invalid');
    urlInput.classList.remove('is-valid');
    return;
  }
  
  // Basic pattern for realtime feedback
  const basicPattern = /^https?:\/\/\S+\.\S+/;
  if (!basicPattern.test(url)) {
    errorElement.textContent = 'Please enter a valid URL';
    urlInput.classList.add('is-invalid');
    urlInput.classList.remove('is-valid');
    return;
  }
  
  // Valid so far
  errorElement.textContent = '';
  urlInput.classList.remove('is-invalid');
  urlInput.classList.add('is-valid');
}

/**
 * Validate URL on blur (stricter validation)
 */
function validateUrl() {
  const urlInput = document.getElementById('url-input');
  const errorElement = document.getElementById('url-input-error');
  
  if (!urlInput || !errorElement) return;
  
  const url = urlInput.value.trim();
  
  // Check if empty
  if (!url) {
    errorElement.textContent = 'Please enter a URL';
    urlInput.classList.add('is-invalid');
    urlInput.classList.remove('is-valid');
    return false;
  }
  
  // Check for protocol
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    errorElement.textContent = 'URL must start with http:// or https://';
    urlInput.classList.add('is-invalid');
    urlInput.classList.remove('is-valid');
    return false;
  }
  
  // More comprehensive URL validation with regex
  const urlPattern = /^(https?:\/\/)(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/;
  if (!urlPattern.test(url)) {
    errorElement.textContent = 'Please enter a valid URL';
    urlInput.classList.add('is-invalid');
    urlInput.classList.remove('is-valid');
    return false;
  }
  
  // Valid URL
  errorElement.textContent = '';
  urlInput.classList.remove('is-invalid');
  urlInput.classList.add('is-valid');
  return true;
}

/**
 * Handle analysis form submission
 * @param {Event} event - Form submit event
 */
function handleAnalysisSubmit(event) {
  // Validate URL
  if (!validateUrl()) {
    event.preventDefault();
    return;
  }
  
  // Show loading state
  const submitButton = document.querySelector('#analysis-form button[type="submit"]');
  if (submitButton) {
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
    submitButton.disabled = true;
  }
  
  // Show loader overlay
  const loaderOverlay = document.getElementById('loader-overlay');
  if (loaderOverlay) {
    loaderOverlay.classList.remove('d-none');
  }
  
  // Form will submit normally to server
}

/**
 * Extract domain from URL
 * @param {String} url - Full URL
 * @returns {String} Domain
 */
function extractDomain(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch (e) {
    // If URL is invalid, just return the input
    return url;
  }
}
