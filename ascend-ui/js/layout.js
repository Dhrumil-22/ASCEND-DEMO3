// Layout.js - Reusable Layout System
// Handles component loading, sidebar collapse, and active menu detection

// Load HTML component into target container
async function loadComponent(url, targetId) {
    try {
        const response = await fetch(url);
        const html = await response.text();
        document.getElementById(targetId).innerHTML = html;
    } catch (error) {
        console.error(`Failed to load component: ${url}`, error);
    }
}

// Main layout initialization - CORRECT ORDER
async function initLayout() {
    // 1. Load components
    await loadComponent("components/sidebar.html", "sidebar-container");
    await loadComponent("components/navbar.html", "navbar-container");

    // 2. Apply collapse state from localStorage
    initSidebarState();

    // 3. Bind events (AFTER components are loaded)
    initSidebarCollapse();
    initNavbarToggle();

    // 4. Set active menu item
    updateActiveMenuItem();

    // 5. Initialize Lucide icons (CRITICAL)
    if (window.lucide) {
        lucide.createIcons();
    }
}

// Initialize sidebar collapse state from localStorage
function initSidebarState() {
    const sidebar = document.querySelector(".sidebar");
    const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true";

    if (isCollapsed && sidebar) {
        sidebar.classList.add("collapsed");
    }
}

// Bind sidebar collapse button event (AFTER component load)
function initSidebarCollapse() {
    const collapseBtn = document.querySelector(".sidebar-toggle");

    if (collapseBtn) {
        collapseBtn.addEventListener("click", toggleSidebar);
    }
}

// Bind navbar toggle button event (AFTER component load)
function initNavbarToggle() {
    const toggleBtn = document.querySelector(".sidebar-toggle-btn");

    if (toggleBtn) {
        toggleBtn.addEventListener("click", toggleSidebar);
    }
}

// Toggle sidebar collapse
function toggleSidebar() {
    const sidebar = document.querySelector(".sidebar");

    if (sidebar) {
        sidebar.classList.toggle("collapsed");

        const isCollapsed = sidebar.classList.contains("collapsed");
        localStorage.setItem("sidebarCollapsed", isCollapsed);
    }
}

// URL-based active menu detection
function updateActiveMenuItem() {
    const path = window.location.pathname;

    document.querySelectorAll(".sidebar-nav-item").forEach(item => {
        item.classList.remove("active");

        const page = item.dataset.page;
        if (page && path.includes(page)) {
            item.classList.add("active");
        }
    });
}

// Export for use in pages
window.initLayout = initLayout;
