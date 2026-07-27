# Formie

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-blue)

**Visual HTML Form Builder** — Drag, drop, and export clean HTML forms. Zero install, zero dependencies, runs entirely in your browser.

> **Live demo:** [zwart04.github.io/formie](https://zwart04.github.io/formie/)

---

## The Problem

Non-technical people who use AI to generate websites almost always need forms — contact forms, signup forms, feedback forms, surveys. But they can't write proper HTML forms with the right input types, labels, validation, and accessibility. 

Existing solutions:
- **Google Forms / Typeform / Tally** — output is locked to their platform, you can't get clean HTML
- **Formeo / VvvebJs** — require setup, library integration, technical knowledge
- **HeyForm** — needs a full backend server
- **jQuery formBuilder** — requires jQuery

Formie is built for **one thing**: let anyone create a professional HTML form visually, then export clean, production-ready code.

---

## Features

- **Drag & Drop Building** — Drag field types from the palette onto the canvas
- **13 Field Types** — Text, Email, Textarea, Dropdown, Checkbox, Radio, Number, URL, Phone, Date, File Upload, Password, Submit Button
- **Properties Editor** — Click any field to edit its label, placeholder, options, required state, and more
- **Reorder Fields** — Drag fields on the canvas to rearrange them
- **Duplicate & Delete** — Clone or remove any field
- **Preview Mode** — See your form exactly as users will see it, with working validation
- **Export Clean HTML** — Download standalone HTML with proper form markup, labels, and responsive styles
- **Save / Load Form** — Export to JSON to save your work, import JSON to continue later
- **Sample Form** — Start with a pre-built contact form to see how it works
- **Undo / Redo** — 30-step undo history
- **Dark Theme** — Built-in dark mode for comfortable use
- **Zero Dependencies** — Single HTML file, works offline after first load

---

## How to Use

1. Go to [zwart04.github.io/formie](https://zwart04.github.io/formie/)
2. **Drag** a field type from the left palette onto the form canvas
3. **Click** any field to edit its properties (label, placeholder, options, etc.)
4. **Drag** fields on the canvas to reorder them
5. Click **Preview** to test your form
6. Click **Export** to download clean HTML code
7. Paste the exported HTML into your website

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` / `Ctrl+Y` | Redo |
| `Delete` / `Backspace` | Delete selected field |
| `Escape` | Deselect / close popovers |

---

## Why Formie?

| | Formie | Google Forms | Formeo | HeyForm |
|---|---|---|---|---|
| Price | Free | Free | Free (lib) | Freemium |
| Install | Zero — open browser | Requires Google account | Requires setup | Requires deploy |
| Output | Clean standalone HTML | Locked to Google | HTML (library-based) | Hosted forms |
| Dependencies | 0 | Heavy | Many | Node.js |
| File size | ~50KB (one file) | Full web app | Library | Full app |

Formie does **one thing well**: let non-technical people build HTML forms visually.

---

## Tech Stack

- Vanilla JavaScript (zero dependencies)
- Tailwind CSS v4 (via CDN — `@tailwindcss/browser`)
- Single HTML file — deploy anywhere
- Hosted on GitHub Pages

---

## Development

Formie is a single `index.html` file. To run locally:

```bash
# Clone the repo
git clone https://github.com/Zwart04/formie.git
cd formie

# Open in browser — that's it!
open index.html
# or: python3 -m http.server 8080
```

No build step. No Node.js. No npm install.

---

## Roadmap

- [x] Drag-drop field building
- [x] Properties editor (label, placeholder, options, required)
- [x] Preview mode with validation
- [x] Export clean HTML
- [x] Save/load JSON
- [x] Undo/Redo
- [x] Sample form template
- [x] Dark theme
- [ ] Conditional logic (show/hide fields)
- [ ] Multi-page / wizard forms
- [ ] File upload URL configuration
- [ ] Custom CSS theme export
- [ ] Email integration (Formspree, Web3Forms)

---

## License

MIT — see [LICENSE](LICENSE).

---

*Made for people who just want a form that works.*
