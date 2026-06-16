---
name: Executive Grooming System
colors:
  surface: '#121414'
  surface-dim: '#121414'
  surface-bright: '#38393a'
  surface-container-lowest: '#0d0e0f'
  surface-container-low: '#1a1c1c'
  surface-container: '#1e2020'
  surface-container-high: '#282a2b'
  surface-container-highest: '#333535'
  on-surface: '#e2e2e2'
  on-surface-variant: '#d0c5af'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#2f3131'
  outline: '#99907c'
  outline-variant: '#4d4635'
  surface-tint: '#e9c349'
  primary: '#f2ca50'
  on-primary: '#3c2f00'
  primary-container: '#d4af37'
  on-primary-container: '#554300'
  inverse-primary: '#735c00'
  secondary: '#c8c6c5'
  on-secondary: '#303030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b5b4'
  tertiary: '#d0cecd'
  on-tertiary: '#313030'
  tertiary-container: '#b5b2b2'
  on-tertiary-container: '#454545'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffe088'
  primary-fixed-dim: '#e9c349'
  on-primary-fixed: '#241a00'
  on-primary-fixed-variant: '#574500'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1b1b1c'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1c1b1b'
  on-tertiary-fixed-variant: '#474646'
  background: '#121414'
  on-background: '#e2e2e2'
  surface-variant: '#333535'
typography:
  display-lg:
    fontFamily: Montserrat
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Montserrat
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1.0'
    letterSpacing: 0.1em
  button:
    fontFamily: Montserrat
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.0'
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
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  container-max: 1280px
  gutter: 24px
---

## Brand & Style
The design system for this elegant barbershop blends the traditional luxury of a high-end salon with a sharp, modern digital edge. It targets a discerning clientele who values precision, craftsmanship, and a premium service experience.

The visual style is **Corporate Modern with a hint of Glassmorphism**. It utilizes a deep, dark-mode-first approach to evoke an atmosphere of exclusivity and sophistication. The interface should feel like a high-end physical space: dark surfaces, polished metallic accents, and a focus on clarity. The emotional response is one of trust, prestige, and meticulous attention to detail.

## Colors
The palette is centered on a high-contrast, dark-mode aesthetic. 
- **Deep Charcoal (#121212):** Used for the primary background, providing a rich, void-like depth.
- **Graphite Grey (#1F1F1F):** Used for containers, cards, and secondary surfaces to create subtle hierarchy.
- **Metallic Gold (#D4AF37):** The signature primary color. Used sparingly for calls to action, active states, and premium highlights.
- **Neutral Silver (#E0E0E0):** Used for primary typography to ensure high readability against dark backgrounds without the harshness of pure white.

## Typography
The system uses a pairing of **Montserrat** for headings and **Inter** for functional body text. 
- Montserrat provides a geometric, bold confidence necessary for a brand focused on "style" and "cuts."
- Inter ensures maximum legibility in data-heavy admin views and booking flows.
- Use uppercase styling for labels and small headers to mimic high-fashion editorial layouts.

## Layout & Spacing
The layout employs a **Fluid Grid** for the client-facing mobile app and a **Structured Fixed Grid** for the admin dashboard.
- **Mobile:** Uses a single-column flow with 20px side margins and generous vertical breathing room between service categories.
- **Desktop/Admin:** A 12-column grid with a fixed left-hand navigation sidebar. 
- **Rhythm:** All spacing is based on an 8px baseline to ensure mathematical harmony across components.

## Elevation & Depth
Depth is achieved through **Tonal Layering** supplemented by subtle **Metallic Outlines**.
- **Level 0 (Base):** #121212 for the main app canvas.
- **Level 1 (Cards):** #1F1F1F with a 1px border of #2A2A2A.
- **Level 2 (Popovers/Modals):** #2A2A2A with a soft, 20% opacity black shadow (blur: 15px, Y: 8px).
- **Glassmorphism:** Navigation bars and floating headers should use a backdrop filter (blur: 20px) with a 60% opaque #121212 background to maintain context while scrolling.

## Shapes
The shape language is **Rounded**, utilizing a 0.5rem (8px) base radius. This softens the "industrial" feel of the dark theme, making the interface feel more approachable and modern. Larger containers (like service cards or promotional banners) should use `rounded-xl` (24px) to create a soft, high-end look.

## Components
- **Buttons:** 
  - *Primary:* Solid Gold (#D4AF37) with black text. 
  - *Secondary:* Transparent with a 1px Gold border and Gold text. 
  - *Ghost:* No border, silver text, gold hover state.
- **Cards:** Graphite grey background. When a card is "Selected" (e.g., choosing a barber), it gains a 2px Gold border.
- **Inputs:** Darker background than the card surface. The focus state must glow with a subtle Gold outer shadow.
- **Chips:** Used for "Available Times" or "Service Tags." Pill-shaped with a dark grey fill and silver text.
- **Admin Specifics:** Data tables should use zebra-striping with #121212 and #1F1F1F, with Gold used exclusively for status indicators (e.g., "Confirmed") and primary action icons.
- **Status Indicators:** Use Gold for "Pending," Emerald for "Completed," and a deep Crimson for "Canceled," ensuring they are muted enough to fit the dark aesthetic.