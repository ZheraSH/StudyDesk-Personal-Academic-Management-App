# StudyDesk Design System

## 1. Design Identity

StudyDesk uses a visual style called:

# Muted Royal Purple Skeuomorphism

The interface should resemble a physical study desk translated into digital form.

Visual references:

```text
Academic Planner
Notebook
Desk Organizer
Paper
Physical Buttons
Soft Plastic
Desktop Utility
```

The aesthetic should be nostalgic without looking outdated.

The design must not resemble:

```text
Gaming UI
Cyberpunk
Neon Dashboard
Corporate SaaS
Generic Material Design
Glassmorphism
```

---

# 2. Color Philosophy

The purple palette should feel:

```text
Elegant
Muted
Academic
Calm
Warm
Professional
```

Avoid saturated royal purple.

The main purple should look slightly faded.

---

# 3. Color Tokens

## Primary

```text
--color-primary: #6F5A8E
```

Main action color.

Used for:

* primary button,
* selected navigation,
* active state,
* important labels.

---

## Primary Dark

```text
--color-primary-dark: #514568
```

Used for:

* pressed buttons,
* strong headings,
* dark decorative elements.

---

## Primary Light

```text
--color-primary-light: #9B89B8
```

Used for:

* highlights,
* secondary accents,
* selected backgrounds.

---

## Background

```text
--color-background: #F4F1F7
```

Main application background.

Should feel like soft paper rather than pure white.

---

## Surface

```text
--color-surface: #E8E1EF
```

Used for:

* cards,
* panels,
* sections,
* input areas.

---

## Text

```text
--color-text: #302A38
```

Main text.

Never use pure black.

---

## Muted Text

```text
--color-muted: #746B7D
```

Secondary text.

---

## Border

```text
--color-border: #C8BDD4
```

Used subtly.

Avoid heavy borders.

---

## Success

```text
--color-success: #748A77
```

Muted green.

---

## Warning

```text
--color-warning: #AD8E61
```

Muted amber.

---

## Danger

```text
--color-danger: #A66F78
```

Muted red.

Danger must remain readable but not visually aggressive.

---

# 4. Typography

Use a clean modern font.

Recommended:

```text
Inter
Segoe UI
System UI
```

Typography hierarchy:

```text
Page Title
24-28px
Semibold

Section Title
18-20px
Semibold

Card Title
15-17px
Semibold

Body
14-15px

Metadata
12-13px

Caption
11-12px
```

Do not use excessive bold text.

---

# 5. Skeuomorphic Principles

Skeuomorphism should be subtle.

The UI can simulate physical depth using:

```text
Soft Shadow
Inner Shadow
Bevel
Highlight
Gradient
Inset Surface
Raised Surface
```

Example button:

```text
Normal:
Raised surface

Hover:
Slightly brighter

Pressed:
Inset surface

Disabled:
Flat and muted
```

Do not use giant shadows.

Do not use heavy 3D effects.

The goal is:

```text
"Feels physical"
```

not:

```text
"Looks like a game UI from 2009"
```

---

# 6. Card Style

Cards should feel like physical planner sections.

Properties:

```text
Radius: 12-16px
Border: 1px subtle
Shadow: low blur
Padding: 16-20px
```

Recommended visual structure:

```text
┌─────────────────────────────┐
│ TASK                        │
│                             │
│ Database Report             │
│                             │
│ Due tomorrow                │
│                             │
│ ● High Priority             │
└─────────────────────────────┘
```

Cards should have strong hierarchy.

Do not place everything into cards.

Some content can sit directly on the background.

---

# 7. Task Status Visuals

Use restrained visual indicators.

```text
Inbox
Neutral

Planned
Purple

In Progress
Muted Blue/Purple

Completed
Muted Green

Archived
Gray
```

Overdue:

```text
Muted Red
```

Do not make overdue tasks neon red.

---

# 8. Deadline Visual Hierarchy

Deadline urgency:

```text
> 7 days
Normal

3-7 days
Moderate

1-3 days
Important

< 24 hours
High Attention

Overdue
Danger
```

The actual remaining time should always be visible.

Example:

```text
Database Assignment

Due tomorrow
18h 23m remaining
```

Avoid showing only:

```text
17/09/2026
```

because humans apparently enjoy mentally calculating deadlines at 1 AM.

---

# 9. Dashboard Layout

Desktop:

```text
┌───────────────────────────────────────────────────────┐
│ StudyDesk                              18 Sep 2026   │
├────────────┬──────────────────────────────────────────┤
│            │                                          │
│ Dashboard  │  Good Evening                           │
│ Schedule   │                                          │
│ Tasks      │  ┌───────────────────────────────────┐   │
│ Focus      │  │ NEXT CLASS                       │   │
│ Statistics │  │ Web Programming                  │   │
│ Settings   │  │ 13:00 - 15:00                   │   │
│            │  └───────────────────────────────────┘   │
│            │                                          │
│            │  TODAY                                   │
│            │  ┌───────────────┐ ┌────────────────┐   │
│            │  │ 3 Classes     │ │ 4 Tasks        │   │
│            │  └───────────────┘ └────────────────┘   │
│            │                                          │
│            │  UPCOMING DEADLINES                      │
│            │  Task A             Tomorrow             │
│            │  Task B             2 days               │
└────────────┴──────────────────────────────────────────┘
```

---

# 10. Mobile Layout

Mobile should prioritize actions.

```text
┌──────────────────────────┐
│ StudyDesk        🔔      │
│ Friday, 18 September     │
│                          │
│ NEXT CLASS               │
│ ┌──────────────────────┐ │
│ │ Web Programming      │ │
│ │ 13:00 - 15:00        │ │
│ │ Lab 2                │ │
│ └──────────────────────┘ │
│                          │
│ DUE SOON                 │
│ ┌──────────────────────┐ │
│ │ Database Report      │ │
│ │ Due tomorrow         │ │
│ └──────────────────────┘ │
│                          │
│ [+ Add Task]             │
│                          │
├──────────────────────────┤
│ Home Schedule Tasks Focus│
└──────────────────────────┘
```

---

# 11. Navigation

Desktop:

```text
Sidebar
```

Mobile:

```text
Bottom Navigation
```

Navigation:

```text
Home
Schedule
Tasks
Focus
Settings
```

Statistics may be accessible through Home or Settings rather than becoming another permanent mobile tab.

---

# 12. Quick Add Button

The most important action should be visually accessible.

Use:

```text
+ Add Task
```

The button should look slightly raised.

On mobile:

```text
Floating Action Button
```

On desktop:

```text
Top-right action
```

---

# 13. Input Design

Inputs should resemble paper slots or soft inset panels.

Normal:

```text
Light surface
Subtle border
Soft inset shadow
```

Focused:

```text
Purple border
Subtle purple glow/highlight
```

Avoid strong neon focus rings.

---

# 14. Buttons

Primary:

```text
Purple raised button
White/light text
```

Secondary:

```text
Light purple surface
Dark purple text
```

Danger:

```text
Muted red
```

Ghost:

```text
Transparent
```

Pressed state:

```text
Slight inward shadow
```

---

# 15. Icons

Use simple line icons.

Preferred visual language:

```text
Calendar
Book
Clipboard
Clock
Bell
Check
Paperclip
Play
Settings
```

Do not use emoji as the core interface icon system.

Emoji may be used inside user-generated content.

---

# 16. Empty States

Empty states should be useful.

Example:

```text
No tasks today.

Your academic battlefield is
currently suspiciously peaceful.
```

But humor should be optional and subtle.

---

# 17. Motion

Animations should be minimal.

Recommended:

```text
150-250ms
```

Use for:

* page transitions,
* button press,
* expanding sections,
* notification feedback.

Do not animate every card on page load.

---

# 18. Accessibility

Maintain:

* readable contrast,
* scalable text,
* touch-friendly controls,
* clear status labels,
* icons combined with text when meaning is important.

Do not communicate critical information through color alone.

Example:

Bad:

```text
Red = overdue
```

Better:

```text
OVERDUE
```

with muted red visual support.

---

# 19. Dark Mode

Dark mode is optional for MVP.

When implemented, do not simply invert colors.

Use a dedicated dark palette:

```text
Dark Background
Dark Surface
Muted Purple
Light Text
Soft Borders
```

Purple should remain muted.

No neon purple.

---

# 20. Design Rule

Every screen should answer:

```text
What do I need to know?
What do I need to do?
How quickly can I do it?
```

StudyDesk should feel like a personal academic desk, not a database administration panel.

The interface exists to reduce mental load, not demonstrate how many components the developer knows how to create.
