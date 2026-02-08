// Global Sidebar State Management
let sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';

// Initialize sidebar state on page load
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.sidebar');
    const collapseBtn = document.getElementById('collapseBtn');

    // Apply saved state
    if (sidebarCollapsed && sidebar) {
        sidebar.classList.add('collapsed');
    }

    // Collapse button handler
    if (collapseBtn) {
        collapseBtn.addEventListener('click', function () {
            sidebarCollapsed = !sidebarCollapsed;
            localStorage.setItem('sidebarCollapsed', sidebarCollapsed);

            if (sidebar) {
                sidebar.classList.toggle('collapsed');
            }
        });
    }

    // Update active menu item based on current page
    updateActiveMenuItem();
});

// Update active menu item
function updateActiveMenuItem() {
    const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
    const navItems = document.querySelectorAll('.sidebar-nav-item');

    navItems.forEach(item => {
        item.classList.remove('active');
        const href = item.getAttribute('href');

        if (href && href.includes(currentPage)) {
            item.classList.add('active');
        }
    });
}

// Career Exploration Tab Switching
function initCareerTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const targetTab = this.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Show corresponding content
            tabContents.forEach(content => {
                if (content.dataset.tab === targetTab) {
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            });
        });
    });
}

// Initialize career tabs if on career exploration page
if (window.location.pathname.includes('career-exploration')) {
    document.addEventListener('DOMContentLoaded', initCareerTabs);
}
