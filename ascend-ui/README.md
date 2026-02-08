# ASCEND - Career Mentorship Platform UI

A modern, responsive web application for career mentorship and guidance built with vanilla HTML, CSS, and JavaScript.

## 🎨 Features

- **Dark Modern Design**: Professional dark theme with blue accents
- **Fully Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- **5 Complete Pages**:
  - Sign In/Authentication
  - Dashboard with stats and mentor recommendations
  - Ask a Question form
  - Career Exploration (Companies, Paths, Experiences, Roadmaps)
  - Discussion Forum

## 🚀 Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, or Edge)
- No build tools or dependencies required!

### Installation

1. Clone or download this repository
2. Navigate to the `ascend-ui` folder
3. Open `index.html` in your web browser

That's it! The application runs entirely in the browser.

## 📁 Project Structure

```
ascend-ui/
├── index.html              # Sign-in page
├── dashboard.html          # Main dashboard
├── ask-question.html       # Question submission
├── career-exploration.html # Career exploration
├── discussion.html         # Discussion forum
├── css/
│   ├── variables.css      # Design system variables
│   ├── reset.css          # CSS reset
│   ├── global.css         # Global styles
│   ├── components.css     # Reusable components
│   └── pages.css          # Page-specific styles
└── js/
    ├── app.js            # Main application logic
    └── navigation.js     # Navigation handling
```

## 🎯 Usage

### Sign In
1. Open `index.html`
2. Select your role (Student/Mentor/Admin)
3. Enter email and password
4. Click "Sign In"

### Navigate the Platform
- **Dashboard**: View your stats, recommended mentors, and recent activity
- **Ask Question**: Submit career questions with skills and target role
- **Career Exploration**: Browse companies, career paths, experiences, and roadmaps
- **Discussion**: Participate in community discussions

## 🎨 Design System

### Colors
- **Primary**: `#4c7cf5` (Blue)
- **Background**: `#0f1419` (Dark)
- **Cards**: `#1e2738` (Dark Blue-Gray)
- **Success**: `#10b981` (Green)
- **Warning**: `#fbbf24` (Yellow)

### Typography
- **Font**: System fonts (Inter, Roboto, Segoe UI)
- **Sizes**: 12px - 30px
- **Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## 📱 Responsive Breakpoints

- **Desktop**: > 1024px
- **Tablet**: 768px - 1024px
- **Mobile**: < 768px

## 🔧 Customization

### Changing Colors
Edit `css/variables.css` to customize the color scheme:

```css
:root {
  --primary: #4c7cf5;        /* Change primary color */
  --bg-primary: #0f1419;     /* Change background */
  /* ... more variables */
}
```

### Adding New Pages
1. Create a new HTML file
2. Include the CSS files in the `<head>`
3. Copy the sidebar and header structure
4. Add your content in the `<main>` section

## 🌟 Key Features

### Interactive Components
- **Role Selector**: Choose between Student, Mentor, or Admin
- **Stats Cards**: Display key metrics with icons
- **Mentor Cards**: Show mentor profiles with trust scores
- **Activity Feed**: Timeline of recent interactions
- **Tab Navigation**: Switch between different content views
- **Tag Input**: Add/remove skills dynamically
- **Form Validation**: Client-side validation for all forms

### Animations
- Smooth page transitions
- Hover effects on cards and buttons
- Fade-in animations on load
- Transform effects on interactive elements

## 🔒 Security Note

This is a **frontend-only demo**. In a production environment, you would need:
- Backend API for authentication
- Database for storing user data
- Proper security measures (HTTPS, CSRF protection, etc.)
- Server-side validation

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork this project and customize it for your needs!

## 📧 Support

For questions or issues, please open an issue in the repository.

---

**Built with ❤️ using vanilla HTML, CSS, and JavaScript**
