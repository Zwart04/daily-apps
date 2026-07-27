# Thema — Brand Theme Generator from Images

## Problem Statement
When people use AI (ChatGPT, Claude, v0) to design websites, the default aesthetic is terrible — AI-purple gradients, mismatched palettes, zero accessibility. Existing color extraction tools (Coolors, PaletteLab) only give raw hex values, not a complete semantic theme system with light/dark modes and framework exports.

## Target Users
1. Non-technical people generating websites with AI who want professional-looking color schemes
2. Developers needing instant theme scaffolding from a brand logo/image
3. Designers who want accessible color system variants quickly

## Core Features (MVP)
1. Upload image via drag-drop or click → extract 5 dominant colors
2. Auto-map colors to semantic roles (primary, secondary, accent, surface, text)
3. Generate light AND dark mode themes with WCAG AA contrast
4. Export formats: CSS variables, Tailwind v4 @theme, shadcn/ui format
5. Live preview: theme applied to example UI components (button, card, badge, input, form)
6. One-click copy per export format

## Out of Scope
- Login/user accounts
- Server-side processing
- Saving/loading palettes (SSR/localStorage future)
- Image generation
- Full website builder (this is a theme scaffold tool)

## Tech Stack
- Vanilla JavaScript (zero build step)
- Tailwind CSS v4 (via CDN — @tailwindcss/browser)
- culori library (via CDN — color math in OKLCH)
- Canvas API (color extraction)
- Single HTML file — deploy on GitHub Pages
