import { sidebarState, isActiveMenuItem } from './sidebarState.js';

export function createSidebar() {
    const sidebar = document.createElement('aside');
    sidebar.className = 'sidebar';
    if (sidebarState.isCollapsed()) {
        sidebar.classList.add('collapsed');
    }

    sidebar.innerHTML = `
        <!-- Logo -->
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">⚡</div>
            <div class="sidebar-logo-text">ASCEND</div>
        </div>

        <!-- Navigation -->
        <nav class="sidebar-nav">
            <a href="dashboard.html" class="sidebar-nav-item ${isActiveMenuItem('dashboard.html') ? 'active' : ''}">
                <i data-lucide="layout-dashboard" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>
                <span>Dashboard</span>
            </a>
            <a href="ask-question.html" class="sidebar-nav-item ${isActiveMenuItem('ask-question.html') ? 'active' : ''}">
                <i data-lucide="message-circle-question" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>
                <span>Ask Question</span>
            </a>
            <a href="career-exploration.html" class="sidebar-nav-item ${isActiveMenuItem('career-exploration.html') ? 'active' : ''}">
                <i data-lucide="compass" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>
                <span>Career Exploration</span>
            </a>
            <a href="discussion.html" class="sidebar-nav-item ${isActiveMenuItem('discussion.html') ? 'active' : ''}">
                <i data-lucide="message-square" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>
                <span>Discussion</span>
            </a>
        </nav>

        <!-- Footer -->
        <div class="sidebar-footer">
            <div class="sidebar-nav-item" id="sidebar-collapse-btn">
                <i data-lucide="chevron-left" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>
                <span>Collapse</span>
            </div>
            <a href="index.html" class="sidebar-nav-item">
                <i data-lucide="log-out" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>
                <span>Sign Out</span>
            </a>
        </div>
    `;

    // Add collapse button listener
    const collapseBtn = sidebar.querySelector('#sidebar-collapse-btn');
    collapseBtn.addEventListener('click', () => {
        sidebarState.toggle();
    });

    // Subscribe to state changes
    sidebarState.subscribe((collapsed) => {
        if (collapsed) {
            sidebar.classList.add('collapsed');
        } else {
            sidebar.classList.remove('collapsed');
        }
    });

    return sidebar;
}
