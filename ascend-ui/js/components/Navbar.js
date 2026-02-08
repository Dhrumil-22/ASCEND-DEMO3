import { sidebarState } from './sidebarState.js';

export function createNavbar() {
    const navbar = document.createElement('header');
    navbar.className = 'header';

    navbar.innerHTML = `
        <!-- Left: Sidebar Toggle -->
        <button class="sidebar-toggle-btn" id="navbar-sidebar-toggle">
            <i data-lucide="menu" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>
        </button>

        <!-- Center: Search Bar -->
        <div class="header-search">
            <div class="input-icon">
                <i data-lucide="search" style="width: 18px; height: 18px; stroke-width: 1.5; position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary);"></i>
                <input type="text" class="input" placeholder="Search..." style="padding-left: 42px;">
            </div>
        </div>

        <!-- Right: Actions -->
        <div class="header-actions">
            <button class="btn btn-secondary btn-sm">
                <i data-lucide="bell" style="width: 18px; height: 18px; stroke-width: 1.5;"></i>
            </button>
            <button class="btn btn-primary" onclick="window.location.href='ask-question.html'">
                <i data-lucide="zap" style="width: 18px; height: 18px; stroke-width: 1.5;"></i>
                Ask Question
            </button>
            <div class="header-user">
                <div class="header-user-info">
                    <div class="header-user-name">Alex Johnson</div>
                    <div class="header-user-role">Student</div>
                </div>
                <div class="avatar avatar-md">
                    <i data-lucide="user" style="width: 18px; height: 18px; stroke-width: 1.5;"></i>
                </div>
            </div>
        </div>
    `;

    // Add toggle button listener
    const toggleBtn = navbar.querySelector('#navbar-sidebar-toggle');
    toggleBtn.addEventListener('click', () => {
        sidebarState.toggle();
    });

    return navbar;
}
