# ASCEND Design System Update

## Typography

### Fonts Used

**Headings**: Neue Montreal (fallback to system fonts)
**Body Text**: Inter (loaded from Google Fonts)

### Font Setup

The Inter font is automatically loaded from Google Fonts in all HTML pages. 

**Note about Neue Montreal**: This is a premium font that requires a license or custom hosting. The CSS currently falls back to system fonts if Neue Montreal is not available. To use Neue Montreal:

1. Purchase a license from [Pangram Pangram](https://pangrampangram.com/products/neue-montreal) or similar source
2. Download the font files (.woff2, .woff)
3. Create a `fonts` folder in your project
4. Add this CSS to `variables.css`:

```css
@font-face {
  font-family: 'Neue Montreal';
  src: url('../fonts/NeueMontreal-Regular.woff2') format('woff2'),
       url('../fonts/NeueMontreal-Regular.woff') format('woff');
  font-weight: 400;
  font-style: normal;
}

@font-face {
  font-family: 'Neue Montreal';
  src: url('../fonts/NeueMontreal-Medium.woff2') format('woff2'),
       url('../fonts/NeueMontreal-Medium.woff') format('woff');
  font-weight: 500;
  font-style: normal;
}

@font-face {
  font-family: 'Neue Montreal';
  src: url('../fonts/NeueMontreal-Bold.woff2') format('woff2'),
       url('../fonts/NeueMontreal-Bold.woff') format('woff');
  font-weight: 700;
  font-style: normal;
}
```

### Typography Scale

- **Page Titles**: 32px, weight 700 (Neue Montreal)
- **Section Titles**: 24px, weight 600 (Neue Montreal)
- **Card Titles**: 18px, weight 600 (Neue Montreal)
- **Body Text**: 14px, weight 400 (Inter)
- **Labels/Sidebar**: 13px, weight 500 (Inter)
- **Buttons**: Inter, weight 500

## Color System

### Background Colors
- `--bg-main`: #0B0F14 (main background)
- `--bg-dashboard`: #0E131A (dashboard background)
- `--bg-sidebar`: #121821 (sidebar background)

### Surface Colors
- `--card-bg`: #1A2230 (card background)
- `--card-hover`: #202A3A (card hover state)
- `--bg-input`: #141B24 (input fields)

### Borders
- `--border-color`: #2A3547 (primary borders)
- `--divider-color`: #1F2735 (dividers)
- `--input-border`: #2C374A (input borders)

### Primary Accent (Gradient)
- Gradient: `linear-gradient(135deg, #4DA3FF 0%, #6C7BFF 100%)`
- `--accent-blue`: #4DA3FF
- `--accent-blue-soft`: #5AA8FF
- `--input-focus`: #4DA3FF

### Accent Colors
- `--success-green`: #3DDC97
- `--warning-yellow`: #FFC857
- `--accent-red`: #ef4444
- `--accent-purple`: #8b5cf6

### Text Colors
- `--text-primary`: #E6EDF3 (primary text)
- `--text-secondary`: #9FB0C3 (secondary text)
- `--text-muted`: #6B7A90 (muted text)
- `--text-sidebar`: #8A97AA (sidebar text)

## Design Elements

### Border Radius
- Cards: 16px (`--radius-lg`)
- Buttons: 12px (`--radius-md`)
- Inputs: 12px (`--radius-md`)

### Shadows
- Soft, subtle shadows for depth
- Cards: `0 4px 12px rgba(0, 0, 0, 0.1)`
- Buttons: `0 4px 12px rgba(77, 163, 255, 0.25)`
- Glow effect: `0 0 20px rgba(77, 163, 255, 0.15)`

### Buttons
- Primary: Blue gradient with glow on hover
- Secondary: Transparent with border
- Smooth transitions and transform effects

### Cards
- Background: `--card-bg`
- Border: 1px solid `--border-color`
- Border radius: 16px
- Soft shadow for depth
- Hover state with subtle background change

## Implementation Notes

All design system changes have been applied to:
- ✅ CSS Variables (`variables.css`)
- ✅ Global Styles (`global.css`)
- ✅ Components (`components.css`)
- ✅ Page Styles (`pages.css`)
- ✅ All HTML pages (font imports)

The layout and component structure remain unchanged - only colors, typography, and visual styling have been updated.
