---
name: Pulse Report
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1c1b1d'
  surface-container: '#201f21'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e5e1e4'
  on-surface-variant: '#bacac1'
  inverse-surface: '#e5e1e4'
  inverse-on-surface: '#313032'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#c0c1ff'
  on-secondary: '#1000a9'
  secondary-container: '#3131c0'
  on-secondary-container: '#b0b2ff'
  tertiary: '#d2d3d5'
  on-tertiary: '#2f3132'
  tertiary-container: '#b6b7b9'
  on-tertiary-container: '#46484a'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#e2e2e4'
  tertiary-fixed-dim: '#c6c6c8'
  on-tertiary-fixed: '#1a1c1d'
  on-tertiary-fixed-variant: '#454749'
  background: '#131315'
  on-background: '#e5e1e4'
  surface-variant: '#353437'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 32px
  gutter: 24px
  margin-mobile: 16px
  card-gap: 24px
---

## Brand & Style
The design system is engineered for "Pulse Report," a high-end analytics platform. It evokes a sense of precision, power, and technical sophistication through a **Modern Glassmorphic** aesthetic. The interface uses deep obsidian layers and vibrant accents to create a "command center" atmosphere, typical of premium fintech and data-intensive applications.

The target audience consists of data analysts and executives who require high legibility and a "wow" factor during high-stakes presentations. The emotional response is one of confidence and clarity—where complex data feels manageable and luminous against a dark, controlled environment.

## Colors
This design system utilizes a high-contrast dark palette to emphasize data visualization.

- **Background (Neutral):** The base is obsidian (#0a0a0c), providing a pure, deep canvas that minimizes eye strain and maximizes the "pop" of accent colors.
- **Primary (Emerald):** Used for growth metrics, success states, and primary calls to action.
- **Secondary (Indigo):** Used for trend lines, interactive elements, and secondary brand moments.
- **Surface Tints:** Use varying opacities of white (1% to 8%) over the obsidian base to create visual hierarchy and glass effects.

## Typography
The system relies on **Inter** for its systematic, utilitarian, and clean characteristics. 

High contrast is achieved through weight rather than size alone. Headlines utilize bold and extra-bold weights with negative letter-spacing for a modern, compact look. Labels and metadata use semi-bold or bold weights at smaller sizes, often in uppercase, to maintain readability against dark, translucent backgrounds.

## Layout & Spacing
The layout follows a **Fluid Grid** model optimized for wide-screen dashboards.

- **Desktop:** 12-column grid with 24px gutters. Content is housed in glass containers that reflow based on viewport width.
- **Tablet:** 8-column grid with 24px gutters. Sidebar collapses into a compact icon-only rail.
- **Mobile:** 4-column grid with 16px margins. Complex charts stack vertically, and glass cards utilize full-width minus margins.

Spacing follows an 8px rhythmic scale. Navigation is consistently placed on the left as a fixed sidebar to ground the fluid content area.

## Elevation & Depth
Depth is created through **Glassmorphism** rather than traditional drop shadows.

- **Base Layer:** Pure obsidian (#0a0a0c).
- **Surface Level:** Translucent white at 4% opacity with a 16px backdrop blur.
- **Border Treatment:** Every elevated surface features a 1px solid border. Use a linear gradient for the border (Top-Left: White 15% opacity to Bottom-Right: White 2% opacity) to simulate a light source reflecting off an edge.
- **Active State Glow:** Primary interactive elements (active tabs, selected cards) should emit a subtle, 20px Gaussian blur glow using the Primary or Secondary color at 20% opacity.

## Shapes
The design system uses a **Rounded** shape language to soften the high-tech aesthetic and make the interface feel modern and approachable.

- **Small Components:** Checkboxes and small buttons use a 0.5rem radius.
- **Medium Components:** Input fields and dropdowns use a 0.75rem radius.
- **Large Containers:** Dashboard cards and modal containers use a 1.5rem (rounded-xl) radius to emphasize the "glass pane" look.

## Components

- **Glass Cards:** The fundamental unit. 1.5rem corner radius, 1px gradient border, and 16px backdrop-blur. Background fill: `rgba(255, 255, 255, 0.04)`.
- **Buttons:**
    - *Primary:* Solid Emerald Green (#00d09c) with black text for maximum contrast.
    - *Secondary:* Ghost style with the 1px white border and Indigo text.
- **Tabs:** Minimalist underline style. The active tab uses a 2px Emerald Green bottom border with a matching soft glow.
- **Input Fields:** Obsidian fill, 1px white (10% opacity) border. On focus, the border transitions to Indigo with a subtle outer glow.
- **Horizontal Bar Charts:** Use rounded end-caps. Fills should be linear gradients (e.g., Indigo to Emerald) to represent data intensity.
- **Data Badges/Chips:** Semi-transparent fills (10% of accent color) with 100px pill radius and bold, high-contrast labels.
- **Segmented Controls:** Housed in a single glass container with a "sliding" frosted glass background to indicate the active selection.