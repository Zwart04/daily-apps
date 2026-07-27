# Thema

[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](LICENSE)
![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-blue)

**Brand theme generator from images.** Upload any image — a logo, a photo, a mood board — and get a complete, accessible color theme system with CSS variables, Tailwind v4, and shadcn/ui exports. Zero install, zero dependencies, runs entirely in your browser.

> **Live demo:** [zwart04.github.io/thema](https://zwart04.github.io/thema/)

---

## The Problem

Every designer and developer knows this workflow: you find a beautiful image with the perfect color story for your project. Then you spend 30 minutes manually picking hex values, guessing accessible light/dark variants, and formatting them into framework-compatible code.

Existing color extraction tools (Coolors, PaletteLab) give you raw hex values — but not a complete **semantic theme system**. Thema bridges the gap: from one image to production-ready CSS variables, Tailwind config, and shadcn/ui theme, all in one click.

---

## Features

- **Color Extraction** — Paste or drop any image, get the 5-6 dominant colors instantly
- **Semantic Theme Mapping** — Colors automatically sorted into Primary, Secondary, Accent, Surface, and Text roles
- **Light & Dark Mode** — Perceptually uniform dark and light variants generated using OKLCH color math
- **Live UI Preview** — See your theme applied to buttons, cards, inputs, badges, and stat cards
- **Export Formats:**
  - CSS Custom Properties (`var(--primary)`)
  - Tailwind v4 `@theme` block
  - shadcn/ui format (OKLCH values)
- **One-Click Copy** — Copy any export format with a single click
- **Zero Dependencies** — Single HTML file, runs entirely in the browser, no server, no install
- **Privacy** — Your images never leave your device. All processing is local.

---

## How to Use

1. Open [zwart04.github.io/thema](https://zwart04.github.io/thema/)
2. Drop any image (logo, brand photo, mood board) onto the upload zone
3. Thema extracts the dominant colors instantly
4. A complete semantic theme is generated with light/dark variants
5. Preview it live on UI components
6. Copy your export format of choice (CSS, Tailwind, shadcn/ui)
7. Paste directly into your project

---

## Why Thema?

|                      | Thema | Coolors | PaletteLab | Adobe Color |
|----------------------|-------|---------|------------|-------------|
| Semantic roles       | Yes   | No      | No         | No          |
| Light/dark themes    | Yes   | No      | No         | No          |
| Tailwind v4 export   | Yes   | No      | No         | No          |
| shadcn/ui export     | Yes   | No      | No         | No          |
| Live UI preview      | Yes   | No      | Limited    | No          |
| Zero install         | Yes   | Yes     | Yes        | Yes         |
| Works offline        | Yes   | No      | Yes        | No          |
| Privacy (local only) | Yes   | No      | Yes        | No          |

Thema does what color tools should have done all along: not just show you colors, but package them into a production-ready theme system.

---

## Tech Stack

- Vanilla JavaScript (zero dependencies)
- [Culori](https://culorijs.org/) — color math in OKLCH space
- Tailwind CSS v4 (via CDN — `@tailwindcss/browser`)
- Canvas API — color extraction
- Single HTML file — deploy anywhere
- Hosted on GitHub Pages

---

## Development

Thema is a single `index.html` file. To run locally:

```bash
git clone https://github.com/Zwart04/thema.git
cd thema
python3 -m http.server 8080
# Open http://localhost:8080
```

No build step. No Node.js. No npm install.

---

## Roadmap

- [x] Color extraction from images
- [x] Semantic theme mapping (Primary, Secondary, Accent, Surface, Text)
- [x] Light and dark mode generation
- [x] Live UI component preview
- [x] CSS variables export
- [x] Tailwind v4 export
- [x] shadcn/ui export
- [ ] Contrast ratio report (WCAG AA/AAA)
- [ ] Color palette lock/edit (override specific roles)
- [ ] URL-based image loading
- [ ] Multiple export formats (SCSS, Less, JSON tokens)
- [ ] Palette history (localStorage)
- [ ] Multi-language (i18n)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Contributing

PRs welcome! This is a single-file app designed to stay simple. If you have an idea, open an issue first.

---

*Made for designers, developers, and anyone who wants their brand colors to look right in every mode.*
