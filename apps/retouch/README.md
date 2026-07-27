# Retouch

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-blue)

**Visual HTML editor for AI-generated code.** Paste any HTML from ChatGPT, Claude, v0, or Bolt — edit it visually with drag-and-drop, without writing a single line of code. Zero install, zero dependencies, runs entirely in your browser.

![Retouch Screenshot](docs/screenshot.png)

> **Live demo:** [zwart04.github.io/retouch](https://zwart04.github.io/retouch/)

---

## The Problem

Millions of people use AI to generate websites. But the output is raw HTML code. Non-technical users have no easy way to:

- Rearrange elements (move a section up/down)
- Change colors, fonts, and sizes
- Edit text content
- Preview on different screen sizes
- Export clean, production-ready HTML

Existing solutions like GrapesJS or Webstudio are powerful but complex. Retouch is designed for **one thing**: take HTML from any AI tool and let you edit it visually.

---

## Features

- ** Drag-and-Drop Reordering** — Click the dot handle and drag any element to a new position
- **Formatting Toolbar** — Bold, italic, underline, font size, font family (10 fonts)
- **Color Pickers** — Change text color and background color visually
- **Text Alignment** — Left, center, right
- **Padding & Margin Presets** — Quick presets for spacing (none, small, medium, large)
- **Width Presets** — Full width, contained (max 800px), half width, auto
- **Add Elements** — Insert div, h1, h2, p, img, link, button
- **Image URL Editor** — Double-click any image to change its source URL
- **Inline Text Editing** — Double-click any text to edit in-place
- **Undo / Redo** — 50-step undo history
- **Responsive Preview** — Toggle between Desktop, Tablet, and Mobile views
- **Grid Overlay** — Toggle alignment grid
- **Move Up / Down** — Fine-tune element position with buttons
- **Duplicate & Delete** — Clone or remove any element
- **Export Clean HTML** — Download a complete, production-ready HTML file
- **Open HTML Files** — Open existing HTML files from your computer
- **Dark Theme** — Easy on the eyes, built for focus

---

## How to Use

1. Go to [zwart04.github.io/retouch](https://zwart04.github.io/retouch/)
2. **Paste** your HTML code from ChatGPT, Claude, v0, or any AI tool into the left panel
3. Click **Render** to see it visually
4. **Click** any element to select it and show the formatting toolbar
5. **Drag** the dot handle to reorder elements
6. **Double-click** text to edit inline, or an image to change its URL
7. Click **Export** to download your edited HTML

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` / `Ctrl+Y` | Redo |
| `Ctrl+Enter` | Render |
| `Ctrl+S` | Export |
| `Ctrl+B` | Bold |
| `Ctrl+I` | Italic |
| `Ctrl+U` | Underline |
| `Delete` / `Backspace` | Delete selected element |
| `Escape` | Deselect / close popovers |

---

## Why Retouch?

| | Retouch | GrapesJS | Webstudio |
|---|---|---|---|
| Price | Free | Free (self-hosted) | Freemium |
| Install | Zero — open browser | Requires setup | Requires account |
| Dependencies | 0 | Many | Node.js |
| Focus | Edit AI-generated HTML | Full site builder | Full site builder |
| File size | ~45KB (one HTML file) | 1MB+ | Full app |

Retouch does **one thing well**: let non-technical people take AI-generated HTML and make it their own.

---

## Tech Stack

- Vanilla JavaScript (zero dependencies)
- Tailwind CSS v4 (via CDN — `@tailwindcss/browser`)
- Single HTML file — deploy anywhere
- Hosted on GitHub Pages

---

## Development

Retouch is a single `index.html` file. To run locally:

```bash
# Clone the repo
git clone https://github.com/Zwart04/retouch.git
cd retouch

# Open in browser — that's it!
open index.html
# or: python3 -m http.server 8080
```

No build step. No Node.js. No npm install.

---

## Roadmap

- [x] Drag-and-drop reordering
- [x] Image URL editor (double-click)
- [x] Margin presets
- [x] Width presets
- [x] Grid overlay
- [x] Responsive preview (Desktop / Tablet / Mobile)
- [ ] Copy/paste elements
- [ ] Undo/redo for drag operations
- [ ] Background image support
- [ ] Export with inline styles vs. CSS classes option
- [ ] i18n / multi-language

---

## License

MIT — see [LICENSE](LICENSE).

---

## Contributing

PRs welcome! This is a single-file app designed to stay simple. If you have an idea, open an issue first.

---

*Made with for people who just want their AI website to look right.*
