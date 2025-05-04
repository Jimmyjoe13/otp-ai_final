/**
 * Opt-AI - Profile JavaScript
 * Handle user profile functionality
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize form handlers
  initProfileForms();
  
  // Initialize subscription management
  initSubscriptionManagement();
  
  // Initialize account deletion
  initAccountDeletion();
});

/**
 * Initialize profile form handlers
 */
function initProfileForms() {
  // Edit profile form
  const editProfileForm = document.getElementById('edit-profile-form');
  const saveProfileButton = document.getElementById('save-profile');
  
  if (editProfileForm && saveProfileButton) {
    saveProfileButton.addEventListener('click', () => {
      // In a real implementation, this would submit the form via AJAX
      const formData = new FormData(editProfileForm);
      const username = formData.get('username');
      const email = formData.get('email');
      
      // Validate inputs
      if (!username || !email) {
        showAlert('Please fill in all required fields.', 'danger');
        return;
      }
      
      // Show loading state
      saveProfileButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
      saveProfileButton.disabled = true;
      
      // Simulate API call
      setTimeout(() => {
        // Reset button
        saveProfileButton.innerHTML = 'Save Changes';
        saveProfileButton.disabled = false;
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
        modal.hide();
        
        // Show success message
        showAlert('Profile updated successfully!', 'success');
      }, 1000);
    });
  }
  
  // Change password form
  const changePasswordForm = document.getElementById('change-password-form');
  const changePasswordButton = document.getElementById('change-password');
  
  if (changePasswordForm && changePasswordButton) {
    changePasswordButton.addEventListener('click', () => {
      // In a real implementation, this would submit the form via AJAX
      const formData = new FormData(changePasswordForm);
      const currentPassword = formData.get('current_password');
      const newPassword = formData.get('new_password');
      const confirmPassword = formData.get('confirm_password');
      
      // Validate inputs
      if (!currentPassword || !newPassword || !confirmPassword) {
        showAlert('Please fill in all password fields.', 'danger');
        return;
      }
      
      if (newPassword !== confirmPassword) {
        showAlert('New passwords do not match.', 'danger');
        return;
      }
      
      // Show loading state
      changePasswordButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
      changePasswordButton.disabled = true;
      
      // Simulate API call
      setTimeout(() => {
        // Reset button
        changePasswordButton.innerHTML = 'Update Password';
        changePasswordButton.disabled = false;
        
        // Reset form
        changePasswordForm.reset();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
        modal.hide();
        
        // Show success message
        showAlert('Password updated successfully!', 'success');
      }, 1000);
    });
  }
}

/**
 * Initialize subscription management
 */
function initSubscriptionManagement() {
  // Update payment method
  const updatePaymentButton = document.getElementById('update-payment');
  
  if (updatePaymentButton) {
    updatePaymentButton.addEventListener('click', () => {
      // Show loading state
      updatePaymentButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Redirecting...';
      updatePaymentButton.disabled = true;
      
      // In a real implementation, this would redirect to Stripe
      setTimeout(() => {
        // Reset button
        updatePaymentButton.innerHTML = 'Continue';
        updatePaymentButton.disabled = false;
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('updatePaymentModal'));
        modal.hide();
        
        // Show message
        showAlert('This would redirect to Stripe in a production environment.', 'info');
      }, 1000);
    });
  }
  
  // Cancel subscription
  const cancelSubscriptionButton = document.getElementById('confirm-cancel');
  
  if (cancelSubscriptionButton) {
    cancelSubscriptionButton.addEventListener('click', () => {
      // Show loading state
      cancelSubscriptionButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
      cancelSubscriptionButton.disabled = true;
      
      // Simulate API call
      setTimeout(() => {
        // Reset button
        cancelSubscriptionButton.innerHTML = 'Cancel Subscription';
        cancelSubscriptionButton.disabled = false;
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('cancelSubscriptionModal'));
        modal.hide();
        
        // Show success message
        showAlert('Your subscription has been cancelled. It will remain active until the end of your current billing period.', 'warning');
      }, 1000);
    });
  }
}

/**
 * Initialize account deletion
 */
function initAccountDeletion() {
  const deleteConfirmInput = document.getElementById('delete_confirmation');
  const confirmDeleteButton = document.getElementById('confirm-delete');
  
  if (deleteConfirmInput && confirmDeleteButton) {
    // Enable/disable button based on confirmation input
    deleteConfirmInput.addEventListener('input', () => {
      confirmDeleteButton.disabled = deleteConfirmInput.value !== 'DELETE';
    });
    
    // Handle delete confirmation
    confirmDeleteButton.addEventListener('click', () => {
      if (deleteConfirmInput.value !== 'DELETE') {
        return;
      }
      
      // Show loading state
      confirmDeleteButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
      confirmDeleteButton.disabled = true;
      
      // Simulate API call
      setTimeout(() => {
        // Reset button (for demo purposes)
        confirmDeleteButton.innerHTML = 'Delete Account';
        confirmDeleteButton.disabled = true;
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteAccountModal'));
        modal.hide();
        
        // Show message and redirect
        showAlert('Account scheduled for deletion. You will be logged out shortly.', 'warning');
        
        // Redirect to logout after a delay
        setTimeout(() => {
          window.location.href = '/logout';
        }, 3000);
      }, 1500);
    });
  }
}

/**
 * Show an alert message
 * @param {String} message - Message to display
 * @param {String} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
  // Create alert element
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.setAttribute('role', 'alert');
  
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Find the container after the h1 heading
  const container = document.querySelector('.container.py-4');
  const heading = document.querySelector('.mb-4');
  
  if (container && heading) {
    // Insert after heading
    heading.insertAdjacentElement('afterend', alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      alertDiv.classList.remove('show');
      setTimeout(() => {
        alertDiv.remove();
      }, 150);
    }, 5000);
  }
}

/**
 * Format a date string
 * @param {String} dateString - ISO date string
 * @returns {String} Formatted date
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}
