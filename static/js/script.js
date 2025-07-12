// F319 Crawler Web Interface - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initAnimations();
    
    // Initialize form enhancements
    initFormEnhancements();
    
    // Initialize tooltips (if Bootstrap is loaded)
    initTooltips();
    
    console.log('🚀 F319 Crawler Web Interface loaded!');
});

// Animation utilities
function initAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // Animate hero icon on page load
    const heroIcon = document.querySelector('.hero-icon');
    if (heroIcon) {
        setTimeout(() => {
            heroIcon.style.animation = 'pulse 2s infinite';
        }, 500);
    }
}

// Form enhancements
function initFormEnhancements() {
    // Auto-format username input
    const usernameInput = document.getElementById('username_id');
    // if (usernameInput) {
    //     usernameInput.addEventListener('input', function() {
    //         // Remove spaces and invalid characters
    //         // this.value = this.value.replace(/[^a-zA-Z0-9._]/g, '');
            
    //         // Validate format
    //         // validateUsernameFormat(this);
    //     });
        
    //     usernameInput.addEventListener('blur', function() {
    //         // validateUsernameFormat(this);
    //     });
    // }
    
    // Enhanced form submission
    const crawlForm = document.getElementById('crawlForm');
    if (crawlForm) {
        crawlForm.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            showLoadingState();
        });
    }
}

// // Username format validation
// function validateUsernameFormat(input) {
//     const value = input.value.trim();
//     const isValid = value.includes('.') && value.split('.').length === 2;
    
//     // Visual feedback
//     if (value && !isValid) {
//         input.classList.add('is-invalid');
//         showFormError(input, 'Format phải là username.userid');
//     } else {
//         input.classList.remove('is-invalid');
//         hideFormError(input);
//     }
    
//     return isValid;
// }

// Form validation
function validateForm() {
    const usernameInput = document.getElementById('username_id');
    const value = usernameInput.value.trim();
    
    if (!value) {
        showFormError(usernameInput, 'Vui lòng nhập username.userid');
        usernameInput.focus();
        return false;
    }
    
    // if (!validateUsernameFormat(usernameInput)) {
    //     usernameInput.focus();
    //     return false;
    // }
    
    return true;
}

// Show form error
function showFormError(input, message) {
    // Remove existing error
    hideFormError(input);
    
    // Create error element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-error-for', input.id);
    
    // Insert after input
    input.parentNode.insertBefore(errorDiv, input.nextSibling);
}

// Hide form error
function hideFormError(input) {
    const errorDiv = input.parentNode.querySelector(`[data-error-for="${input.id}"]`);
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Loading state
function showLoadingState() {
    const submitBtn = document.querySelector('#crawlForm button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang chuẩn bị...';
        submitBtn.disabled = true;
        
        // Store original text for potential restore
        submitBtn.setAttribute('data-original-text', originalText);
    }
}

// Restore button state
function restoreButtonState() {
    const submitBtn = document.querySelector('#crawlForm button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.getAttribute('data-original-text');
        if (originalText) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
}

// Initialize tooltips
function initTooltips() {
    // Bootstrap tooltips
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Utility functions

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show notification-alert`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.maxWidth = '400px';
    
    alertDiv.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Get icon for notification type
function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'danger': 'exclamation-triangle'
    };
    return icons[type] || 'info-circle';
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Đã copy vào clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

// Fallback copy function
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Đã copy vào clipboard!', 'success');
    } catch (err) {
        showNotification('Không thể copy vào clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format duration
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Add loading overlay
function showLoadingOverlay(message = 'Đang xử lý...') {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-primary fw-bold">${message}</p>
        </div>
    `;
    
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        backdrop-filter: blur(5px);
    `;
    
    document.body.appendChild(overlay);
}

// Remove loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Network status checker
function checkNetworkStatus() {
    return navigator.onLine;
}

// Add network status listeners
window.addEventListener('online', function() {
    showNotification('Kết nối mạng đã được khôi phục', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Mất kết nối mạng', 'warning');
});

// Error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showNotification('Đã xảy ra lỗi JavaScript', 'error');
});

// Prevent form resubmission on page refresh
window.addEventListener('beforeunload', function(e) {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && submitBtn.disabled) {
            e.preventDefault();
            e.returnValue = 'Crawler đang chạy. Bạn có chắc muốn thoát?';
        }
    });
});

// Global utility object
window.F319Crawler = {
    showNotification,
    copyToClipboard,
    formatFileSize,
    formatDuration,
    scrollToElement,
    showLoadingOverlay,
    hideLoadingOverlay,
    checkNetworkStatus
}; 