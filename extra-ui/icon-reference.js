// Script to update all HTML files with Lucide icons
// This file documents the icon replacements needed

const iconReplacements = {
    // Sidebar Navigation
    dashboard: 'layout-dashboard',
    askQuestion: 'message-circle',
    careerExploration: 'compass',
    discussion: 'users',
    collapse: 'chevron-left',
    signOut: 'log-out',

    // Dashboard Icons
    target: 'target',
    mail: 'mail',
    bookOpen: 'book-open',
    activity: 'activity',

    // Discussion Icons
    messageSquare: 'message-square',

    // Profile Icons
    user: 'user',

    // Search
    search: 'search',

    // Notifications
    bell: 'bell'
};

// Icon HTML template
const iconTemplate = (name) => `<i data-lucide="${name}" style="width: 20px; height: 20px; stroke-width: 1.5;"></i>`;

// Remember to add this script tag before </head>:
// <script src="https://unpkg.com/lucide@latest"></script>

// And this before </body>:
// <script>lucide.createIcons();</script>
