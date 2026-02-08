// Main Application JavaScript

// Initialize app
document.addEventListener('DOMContentLoaded', function () {
    console.log('ASCEND App Initialized');

    // Check if user is logged in (for pages other than index.html)
    if (!window.location.pathname.endsWith('index.html') && !window.location.pathname.endsWith('/')) {
        const userEmail = localStorage.getItem('userEmail');
        if (!userEmail && !window.location.pathname.includes('index.html')) {
            // Redirect to login if not authenticated
            // window.location.href = 'index.html';
        }
    }
});

// Utility Functions
const utils = {
    // Format date
    formatDate: function (date) {
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'just now';
    },

    // Get user initials
    getInitials: function (name) {
        return name
            .split(' ')
            .map(word => word[0])
            .join('')
            .toUpperCase();
    },

    // Validate email
    validateEmail: function (email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Show notification
    showNotification: function (message, type = 'success') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? 'var(--accent-green)' : 'var(--accent-red)'};
            color: white;
            border-radius: 0.5rem;
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
};

// Export utils for use in other scripts
window.ascendUtils = utils;
