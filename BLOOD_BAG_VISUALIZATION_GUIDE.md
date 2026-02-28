# Blood Bag Visualization Guide

## Overview
The admin dashboard now displays blood inventory using animated blood bag icons that visually represent the available units for each blood type.

## Visual Features

### Blood Bag Design
```
     [Cap]
    ┌─────┐
    │     │ ← Empty space (white/gray)
    │~~~~~│ ← Wave animation
    │█████│ ← Blood level (red gradient)
    │█████│   Fills from bottom up
    └─────┘
```

### Blood Level Calculation
- Maximum capacity: 25 units (100% full)
- Formula: `height = (units_available / 25) * 100%`
- Examples:
  - 25 units = 100% full (bag completely filled)
  - 12-13 units = 50% full (half filled)
  - 6 units = 24% full (quarter filled)
  - 0 units = 0% full (empty bag)

### Color Scheme
- **Blood Fill**: Red gradient (#dc3545 to #a71d2a)
- **Bag Border**: Red (#dc3545)
- **Empty Space**: Light gray (#f8f9fa)
- **Low Stock Badge**: Pulsing red with warning icon
- **Adequate Badge**: Green with checkmark icon

## Current Inventory Levels

| Blood Type | Units | Fill Level | Status |
|------------|-------|------------|--------|
| O+         | 20    | 80%        | ✓ Adequate |
| A+         | 15    | 60%        | ✓ Adequate |
| B+         | 12    | 48%        | ✓ Adequate |
| AB+        | 10    | 40%        | ✓ Adequate |
| A-         | 8     | 32%        | ✓ Adequate |
| O-         | 7     | 28%        | ✓ Adequate |
| B-         | 6     | 24%        | ✓ Adequate |
| AB-        | 5     | 20%        | ✓ Adequate |

**Note**: Low stock threshold is 5 units. Any blood type with less than 5 units will show a pulsing red "Low Stock!" badge.

## 