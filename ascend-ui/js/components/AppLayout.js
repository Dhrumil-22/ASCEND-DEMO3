import { createSidebar } from './Sidebar.js';
import { createNavbar } from './Navbar.js';
import { sidebarState } from './sidebarState.js';

export function createAppLayout(pageContent) {
    // Create main layout container
    const appLayout = document.createElement('div');
    appLayout.className = 'app-layout';

    // Create sidebar
    const sidebar = createSidebar();

    // Create content wrapper
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'app-content-wrapper';
    if (sidebarState.isCollapsed()) {
        contentWrapper.classList.add('sidebar-collapsed');
    }

    // Create navbar
    const navbar = createNavbar();

    // Create page content area
    const pageContentArea = document.createElement('main');
    pageContentArea.className = 'app-page-content';
    pageContentArea.innerHTML = pageContent;

    // Assemble layout
    contentWrapper.appendChild(navbar);
    contentWrapper.appendChild(pageContentArea);
    appLayout.appendChild(sidebar);
    appLayout.appendChild(contentWrapper);

    // Subscribe to sidebar state changes
    sidebarState.subscribe((collapsed) => {
        if (collapsed) {
            contentWrapper.classList.add('sidebar-collapsed');
        } else {
            contentWrapper.classList.remove('sidebar-collapsed');
        }
    });

    return appLayout;
}

// Initialize app layout
export function initAppLayout() {
    // Get page content from the page-content div
    const pageContentDiv = document.getElementById('page-content');
    if (!pageContentDiv) {
        console.error('No #page-content element found');
        return;
    }

    const pageContent = pageContentDiv.innerHTML;
    pageContentDiv.remove(); // Remove the placeholder

    // Create and mount app layout
    const appLayout = createAppLayout(pageContent);
    document.body.appendChild(appLayout);

    // Initialize Lucide icons
    if (window.lucide) {
        window.lucide.createIcons();
    }
}
