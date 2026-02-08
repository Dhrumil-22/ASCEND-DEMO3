// Sidebar State Management
class SidebarState {
    constructor() {
        this.collapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        this.listeners = [];
    }

    toggle() {
        this.collapsed = !this.collapsed;
        localStorage.setItem('sidebarCollapsed', this.collapsed);
        this.notifyListeners();
    }

    isCollapsed() {
        return this.collapsed;
    }

    subscribe(listener) {
        this.listeners.push(listener);
    }

    notifyListeners() {
        this.listeners.forEach(listener => listener(this.collapsed));
    }
}

// Export singleton instance
export const sidebarState = new SidebarState();

// Get current page for active menu highlighting
export function getCurrentPage() {
    const path = window.location.pathname;
    const page = path.split('/').pop() || 'dashboard.html';
    return page;
}

// Active menu item helper
export function isActiveMenuItem(href) {
    const currentPage = getCurrentPage();
    return href && href.includes(currentPage);
}
