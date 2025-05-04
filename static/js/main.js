/**
 * Opt-AI - Main JavaScript
 * Contains core functionality used across the site
 */

// Initialize on document ready
document.addEventListener('DOMContentLoaded', () => {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Mobile menu toggle
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
      const navbarMenu = document.getElementById('navbar-menu');
      navbarMenu.classList.toggle('show');
    });
  }

  // Handle URL validation
  const urlInputs = document.querySelectorAll('input[type="url"]');
  urlInputs.forEach(input => {
    input.addEventListener('blur', validateUrl);
  });

  // Handle analysis form submission
  const analysisForm = document.getElementById('analysis-form');
  if (analysisForm) {
    analysisForm.addEventListener('submit', function(event) {
      const urlInput = document.getElementById('url-input');
      if (!validateUrl(urlInput)) {
        event.preventDefault();
      }
      
      // Show loading indicator
      const submitButton = this.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        submitButton.disabled = true;
      }
    });
  }

  // Setup scroll reveal animations
  setupScrollReveal();
});

/**
 * Validates a URL input
 * @param {HTMLInputElement|Event} inputOrEvent - URL input element or event
 * @returns {Boolean} Whether URL is valid
 */
function validateUrl(inputOrEvent) {
  const input = inputOrEvent.target || inputOrEvent;
  const url = input.value.trim();
  const errorElement = document.getElementById(`${input.id}-error`);
  
  // Simple URL validation
  if (!url) {
    if (errorElement) errorElement.textContent = 'Please enter a URL';
    input.classList.add('is-invalid');
    return false;
  }
  
  // Check for protocol
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    if (errorElement) errorElement.textContent = 'URL must start with http:// or https://';
    input.classList.add('is-invalid');
    return false;
  }
  
  // More comprehensive URL validation with regex
  const urlPattern = /^(https?:\/\/)(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/;
  if (!urlPattern.test(url)) {
    if (errorElement) errorElement.textContent = 'Please enter a valid URL';
    input.classList.add('is-invalid');
    return false;
  }
  
  // Valid URL
  input.classList.remove('is-invalid');
  input.classList.add('is-valid');
  if (errorElement) errorElement.textContent = '';
  return true;
}

/**
 * Setup scroll reveal animations for elements
 */
function setupScrollReveal() {
  const revealElements = document.querySelectorAll('.reveal-on-scroll');
  
  const revealOnScroll = () => {
    const windowHeight = window.innerHeight;
    const revealPoint = 150;
    
    revealElements.forEach(element => {
      const elementTop = element.getBoundingClientRect().top;
      
      if (elementTop < windowHeight - revealPoint) {
        element.classList.add('active');
      } else {
        element.classList.remove('active');
      }
    });
  }
  
  // Initial check
  revealOnScroll();
  
  // Add scroll event listener
  window.addEventListener('scroll', revealOnScroll);
}

/**
 * Format a number with commas
 * @param {Number} num - Number to format
 * @returns {String} Formatted number
 */
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Create a progress bar element
 * @param {Number} score - Score (0-100)
 * @param {String} size - Size class (sm, md, lg)
 * @returns {HTMLElement} Progress bar element
 */
function createProgressBar(score, size = '') {
  // Determine status class based on score
  let statusClass = 'bg-danger';
  if (score >= 80) {
    statusClass = 'bg-success';
  } else if (score >= 60) {
    statusClass = 'bg-warning';
  } else if (score >= 40) {
    statusClass = 'bg-info';
  }
  
  // Create progress wrapper
  const progressWrapper = document.createElement('div');
  progressWrapper.className = `progress${size ? ' progress-' + size : ''}`;
  
  // Create progress bar
  const progressBar = document.createElement('div');
  progressBar.className = `progress-bar ${statusClass}`;
  progressBar.style.width = `${score}%`;
  progressBar.setAttribute('aria-valuenow', score);
  progressBar.setAttribute('aria-valuemin', 0);
  progressBar.setAttribute('aria-valuemax', 100);
  progressBar.textContent = `${score}%`;
  
  // Add progress bar to wrapper
  progressWrapper.appendChild(progressBar);
  
  return progressWrapper;
}

/**
 * Show an alert message
 * @param {String} message - Message to display
 * @param {String} type - Alert type (success, danger, warning, info)
 * @param {String} containerId - ID of container element
 * @param {Number} duration - Auto-dismiss duration in ms (0 to stay)
 */
function showAlert(message, type = 'info', containerId = 'alert-container', duration = 5000) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  // Create alert element
  const alertElement = document.createElement('div');
  alertElement.className = `alert alert-${type} alert-dismissible fade show`;
  alertElement.role = 'alert';
  
  // Add message
  alertElement.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Add to container
  container.appendChild(alertElement);
  
  // Auto-dismiss if duration is set
  if (duration > 0) {
    setTimeout(() => {
      alertElement.classList.remove('show');
      setTimeout(() => {
        alertElement.remove();
      }, 150);
    }, duration);
  }
}
