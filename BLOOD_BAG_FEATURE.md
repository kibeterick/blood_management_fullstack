# Blood Bag Visualization Feature

## Overview
Enhanced the admin dashboard with animated blood bag icons that visually represent blood inventory levels.

## Visual Design

### Blood Bag Structure
```
     ┌──┐          <- Red cap/tube at top
     │  │
   ┌──────┐
   │      │
   │ ~~~~ │        <- Wave animation (white overlay)
   │██████│        <- Blood level (fills based on units)
   │██████│           Gradient: #dc3545 (top) to #a71d2a (bottom)
   │██████│
   └──────┘        <- Rounded bottom
```

### Card Layout
```
┌─────────────────────┐
│       A+            │  <- Blood type label (red, bold)
│                     │
│     [Blood Bag]     │  <- Animated bag icon
│                     │
│        15           │  <- Unit count (large, bold)
│   units available   │  <- Description text
│                     │
│   ✓ Adequate        │  <- Status badge (green/red)
└─────────────────────┘
```

## Features

### 1. Dynamic Fill Level
- Blood level calculated as: `(units_available / 25) * 100%`
- Fills from bottom to top
- Smooth 1-second animation on page load
- Maximum capacity: 25 units = 100% full

### 2. Visual Indicators
- **Adequate Stock** (≥5 units):
  - Green badge with checkmark icon
  - Normal border color
  - White background

- **Low Stock** (<5 units):
  - Red pulsing badge with warning icon
  - Red border on card
  - Light red background gradient
  - Pulsing animation to draw attention

### 3. Animations
- **Wave Effect**: Continuous 2-second wave motion on blood surface
- **Pulse Effect**: Low stock badges pulse every 1.5 seconds
- **Fill Animation**: Blood level animates upward on page load (1 second)
- **Hover Effect**: Card scales up 5% and shows red shadow

### 4. Responsive Grid
- Auto-fit grid layout
- Minimum card width: 150px
- Adapts to screen size
- 20px gap between cards

## Technical Implementation

### CSS Classes
- `.inventory-grid` - Grid container for all blood type cards
- `.blood-type-card` - Individual card wrapper
- `.blood-bag-container` - Container for blood bag icon (80x120px)
- `.blood-bag` - The bag shape with border and cap
- `.blood-level` - The filled blood portion (dynamic height)
- `.stock-badge` - Status indicator badge

### Color Scheme
- Blood red: `#dc3545` (primary)
- Dark blood: `#a71d2a` (gradient bottom)
- Success green: `#d4edda` (background), `#155724` (text)
- Warning red: `#f8d7da` (background), `#721c24` (text)
- Border: `#e0e6ed` (normal), `#dc3545` (hover/low stock)

### Animations
```css
@keyframes wave {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
```

## Blood Type Initial Values

| Blood Type | Initial Units | Status    |
|------------|---------------|-----------|
| O+         | 20 units      | Adequate  |
| A+         | 15 units      | Adequate  |
| B+         | 12 units      | Adequate  |
| AB+        | 10 units      | Adequate  |
| A-         | 8 units       | Adequate  |
| O-         | 7 units       | Adequate  |
| B-         | 6 units       | Adequate  |
| AB-        | 5 units       | Adequate  |

## User Experience Benefits

1. **At-a-Glance Understanding**: Users can instantly see inventory levels without reading numbers
2. **Visual Hierarchy**: Low stock items immediately stand out with red borders and pulsing badges
3. **Engaging Interface**: Animations make the dashboard feel modern and alive
4. **Mobile-Friendly**: Responsive grid adapts to all screen sizes
5. **Intuitive**: Blood bag metaphor is universally understood in medical context

## Future Enhancements (Optional)

- Add click to view detailed history for each blood type
- Show trend arrows (increasing/decreasing)
- Add expiration date warnings
- Color-code by urgency (critical < 3 units, low < 5 units)
- Add sound alerts for critical low stock
- Show last donation date for each type
- Add export/print functionality for inventory reports

## Accessibility

- High contrast colors for readability
- Icon + text labels for status (not just color)
- Hover states for interactive feedback
- Semantic HTML structure
- Screen reader friendly with proper ARIA labels (can be added)

---

This feature transforms the blood inventory from a simple data table into an engaging, intuitive visual dashboard that helps administrators quickly assess stock levels and take action when needed.
