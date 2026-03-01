# Blueprint Dashboard - Visual Reference Guide

## Dashboard Layout Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                              HEADER                                  │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│ │   Blueprint  │  │ Classification│  │ Stats →      │  │          │ │
│ │   Dashboard  │  │  Dashboard    │  │              │  │          │ │
│ └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │
└────────────────────┬─────────────────────────────────────────────────┘
                     │
    ┌────────────────┴────────────────┐
    │                                 │
    ↓                                 ↓
┌──────────────┐              ┌──────────────────┐
│    SIDEBAR   │              │  DETAIL PANE     │
│ (340px wide) │              │  (Flex expand)   │
├──────────────┤              ├──────────────────┤
│              │              │                  │
│  NEW CAPTURE │              │  PLACEHOLDER     │
│  ─────────── │              │  (until selected)│
│              │              │                  │
│ [Drop Zone]  │              │  "Select an item │
│ [Title]      │              │   to review..."  │
│ [Content]    │              │                  │
│ [Category ▼] │              │                  │
│ [SUBMIT]     │              └──────────────────┘
│              │
│  PENDING     │              ┌──────────────────┐
│  ITEMS       │              │  ITEM DETAIL     │
│  ─────────── │              │  (when selected) │
│              │              ├──────────────────┤
│ • Action #1  │              │ Title + ID (close)
│   action     │              │                  │
│              │              │ CONTENT          │
│ • Thought    │              │ ─────────────    │
│   email task │              │ [Full item text] │
│              │              │                  │
│ • Idea       │              │ CLASSIFICATION   │
│   project    │              │ ─────────────    │
│              │              │ Label: action    │
│ • Emotion    │              │ Confidence: ████░
│   grateful   │              │ Status: Pending  │
│              │              │                  │
│ [Refresh]    │              │ OVERRIDE         │
│              │              │ ─────────────    │
│ (50 items)   │              │ Category: [▼]    │
│              │              │ Notes: [text]    │
│              │              │                  │
│              │              │ [√ Approve]      │
│              │              │ [✎ Modify]       │
│              │              │ [✕ Reject]       │
│              │              │                  │
│              │              │ AUDIT TRAIL      │
│              │              │ ─────────────    │
│              │              │ Approved         │
│              │              │ Now by user      │
│              │              │ Original: X      │
│              │              │                  │
└──────────────┘              └──────────────────┘
```

## Color Guide

### Primary Palette
```
████ #1e1e2e — Main background (dark primary)
████ #2d2d44 — Panel background (dark secondary)
████ #e0e0e0 — Primary text (light gray)
████ #888888 — Secondary text (muted gray)
```

### Action Palette
```
████ #00d4ff — Cyan (primary action, highlights)
████ #00d46e — Green (approve button)
████ #ffd700 — Yellow (modify button)
████ #ff6b6b — Red (reject button)
```

### Status Indicators
```
████ #404050 — Borders & dividers
████ #00d4ff — Active/selected (highlight)
████ #ffd700 — Pending (yellow)
████ #00d46e — Approved (green)
████ #ff6b6b — Rejected (red)
```

## UI Components

### Buttons

```
APPROVE BUTTON
┌─────────────────────────┐
│  ✓ APPROVE              │  ← Green (#00d46e)
│  (uppercase text)       │  ← Dark text on green
│  (12px font, bold)      │  ← Tight padding
└─────────────────────────┘

MODIFY BUTTON
┌─────────────────────────┐
│  ✎ MODIFY               │  ← Yellow (#ffd700)
│  (uppercase text)       │  ← Dark text on yellow
│  (12px font, bold)      │  ← Tight padding
└─────────────────────────┘

REJECT BUTTON
┌─────────────────────────┐
│  ✕ REJECT               │  ← Red (#ff6b6b)
│  (uppercase text)       │  ← White text on red
│  (12px font, bold)      │  ← Tight padding
└─────────────────────────┘

PRIMARY ACTION
┌─────────────────────────┐
│  ⬆ SUBMIT               │  ← Cyan (#00d4ff)
│  (or DROP FILE HERE)    │  ← Dark text on cyan
│  (12px font, bold)      │  ← Medium padding
└─────────────────────────┘
```

### Cards

```
CLASSIFICATION CARD
┌─────────────────────────────────────────────┐
│  Classification                 (section h3)│
├─────────────────────────────────────────────┤
│                                             │
│  Label:        [action]          (badge)   │
│  Confidence:   [████░] 80.5%                │
│  Status:       [NEEDS REVIEW]    (badge)   │
│                                             │
└─────────────────────────────────────────────┘

ITEM CARD (in list)
┌─────────────────────────────────────────────┐
│  Call mom about dentist appointment         │
│  (item-row-title - cyan, bold)              │
│  action                                     │
│  (item-row-class - muted, small)            │
└─────────────────────────────────────────────┘
← Hover: darker background
← Active: left cyan border + highlight
```

### Form Inputs

```
TEXT INPUT
┌─────────────────────────────────────────────┐
│ [Title of the item...................]      │  ← 8px padding
│ (12px font, dark bg, light border)         │
└─────────────────────────────────────────────┘
← On focus: cyan border + glow

TEXTAREA
┌─────────────────────────────────────────────┐
│ Content of the item, can be very long and  │
│ wrapped across multiple lines, with cursor │
│ blinking in the dark input area.           │
│ Minimum 60px height, max 120px height.     │
│                                             │
└─────────────────────────────────────────────┘
← On focus: cyan border + glow

SELECT DROPDOWN
┌─────────────────────────────────────────────┐
│ action ▼                                    │  ← Dark bg
│ (shows: auto, action, thought,             │
│  idea, emotion)                            │
└─────────────────────────────────────────────┘
← Cursor: pointer
← Dark styling to match theme
```

### Status Badges

```
PENDING
┌──────────────────┐
│ ⏳ NEEDS REVIEW  │  ← Yellow accent (#ffd700)
│ (semi-transparent)  ← #ffd700 at 10% opacity + 30% border
└──────────────────┘

APPROVED
┌──────────────────┐
│ ✓ APPROVED       │  ← Green accent (#00d46e)
│ (semi-transparent)  ← #00d46e at 10% opacity + 30% border
└──────────────────┘

REJECTED
┌──────────────────┐
│ ✕ REJECTED       │  ← Red accent (#ff6b6b)
│ (semi-transparent)  ← #ff6b6b at 10% opacity + 30% border
└──────────────────┘
```

### Confidence Indicator

```
Confidence Bar (Visual)
Label: Confidence
Bar: ████████░░ 80.5%
├─ Filled portion: linear gradient (#00d4ff → #00ff88)
├─ Empty portion: dark primary background
├─ Height: 6px, border-radius: 3px
└─ Animated on update: 0.3s transition

Color Meaning:
0-33%   : ████░░░░░░ Low confidence (pale)
34-66%  : ██████░░░░ Medium confidence (getting brighter)
67-100% : ██████████ High confidence (vibrant cyan→green)
```

### Audit Trail Entry

```
┌───────────────────────────────────┐
│ ███ APPROVED                      │ ← Cyan left border (3px)
│   Now · 14:35:42 · 2026-02-22    │ ← Timestamp (small text)
│   Original: needs-review (0.625)  │ ← Original classification
│   Notes: User approved via UI     │ ← Optional notes
└───────────────────────────────────┘
← Background: secondary panel color
← Font: small (11-12px), muted text
← Padding: 12px all around
```

### Drag & Drop Zone

```
Normal State:
┌─────────────────────────────────────┐
│  📎                                 │ ← Cyan icon
│  Paste or drop file here            │ ← Instructions
│  (12px muted text)                  │
└─────────────────────────────────────┘
← Dashed border (#404050)
← Dark primary background

Hover State:
┌─────────────────────────────────────┐
│  📎                                 │ ← Cyan icon (same)
│  Paste or drop file here            │ ← Instructions
│  (12px muted text)                  │
└─────────────────────────────────────┘
← Dashed border: CYAN (#00d4ff)
← Background: semi-transparent cyan glow

Drag Over State:
┌─────────────────────────────────────┐
│  📎                                 │ ← Cyan icon (brightened)
│  Paste or drop file here            │ ← Instructions
│  (12px muted text)                  │
└─────────────────────────────────────┘
← Dashed border: CYAN (solid)
← Background: rgba(0, 212, 255, 0.05)
← Ready to accept drop
```

## Spacing & Typography

### Typography Hierarchy

```
H1 — Page Title (Blueprint)
     └─ 24px, 700 weight, letter-spacing: -1px

H2 — Section Titles (New Capture, Pending Items)
     └─ 14px, 600 weight, uppercase, letter-spacing: 0.5px
     └─ Color: cyan accent

H3 — Card Titles (Classification, Override)
     └─ 12px, 600 weight, uppercase, letter-spacing: 0.5px
     └─ Color: cyan accent

Body — Main Text
     └─ 13px, 400 weight, line-height: 1.6
     └─ Color: light gray (#e0e0e0)

Small — Metadata, Labels
     └─ 11-12px, 400 weight, letter-spacing: 0.5px
     └─ Color: muted gray (#888)

Code — Item ID, Monospace
     └─ 12px, monospace font
     └─ Dark background pill
```

### Spacing Grid (8px base)

```
Card Padding:     16px (2 × 8px)
Section Padding:  20px (2.5 × 8px)
Header Padding:   24px (3 × 8px)
Gap Between Items: 12px (1.5 × 8px)
Gap Between Sections: 24px (3 × 8px)
Button Padding:   10px vertical, 16px horizontal
Border Radius:    6px (input/button), 12px (card)
```

## Responsive Behavior

### Desktop (1440px+)
```
Header: Full width
Sidebar: 340px fixed
Detail: Flex expand
All elements visible and optimal spacing
```

### Laptop (1024-1440px)
```
Header: Full width
Sidebar: 280px (narrower)
Detail: Flex expand
Header stats: 20px gap (tighter)
```

### Tablet (768-1024px)
```
Still side-by-side but with adjusted spacing
Sidebar: Full width (340px)
Detail: Full width
Everything readable
```

### Mobile (<768px)
```
Main becomes vertical flex
Sidebar: 100%, height: 40%
Detail: 100%, height: 60%
Header: Stacked layout
List: Smaller items
All buttons sized for touch (44px minimum)
```

## Animation & Transitions

```
All transitions: 0.2s ease

Button Hover:
├─ Background: slight darker shade
└─ Transform: translateY(-1px) [lift effect]

Input Focus:
├─ Border: cyan (#00d4ff)
└─ Box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1)

List Item Hover:
├─ Background: slightly lighter
└─ Instant (no transition)

List Item Active:
├─ Background: semi-transparent cyan
├─ Left border: 3px solid cyan
└─ Instant on click

Confidence Bar Fill:
├─ Width: animated 0.3s
└─ Uses CSS transition

Drag Over Zone:
├─ Border color: instant change
├─ Background: instant change
└─ Ready for file drop
```

## Message States

```
SUCCESS MESSAGE
┌─────────────────────────────────────┐
│ ✓ Item captured! Processing...      │  ← Green text
│ (green background with border)      │
└─────────────────────────────────────┘

ERROR MESSAGE
┌─────────────────────────────────────┐
│ ✕ Failed to load item: 500 error    │  ← Red text
│ (red background with border)        │
└─────────────────────────────────────┘

NEUTRAL MESSAGE
┌─────────────────────────────────────┐
│ Loading...                          │  ← Cyan text
│ (cyan background with border)       │
└─────────────────────────────────────┘
```

## Dark Mode Advantages

✓ **Reduced Eye Strain**: Better for prolonged use
✓ **Battery Efficient**: Less power on OLED screens
✓ **Professional Look**: Strava, Discord, Slack use dark themes
✓ **Focus**: Dark backgrounds enhance content visibility
✓ **Modern**: Current design trend in 2026
✓ **Consistency**: Matches system dark mode

## Accessibility Features

✓ **Color Contrast**: Cyan on dark meets WCAG AA standard
✓ **Font Size**: 12px minimum (readable without zoom)
✓ **Line Height**: 1.6 (easy to scan)
✓ **Click Targets**: Buttons 44px minimum (mobile-friendly)
✓ **Focus Indicators**: Cyan border on focus states
✓ **Status Badges**: Color + text (not color-only)
✓ **Error Messages**: Visible notification area

---

**Visual Reference Version**: 1.0  
**Last Updated**: February 22, 2026
