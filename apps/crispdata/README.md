# CrispData

**Smart Data Cleaner & Converter** — Paste messy data, get clean tables, Markdown, JSON, CSV, or HTML instantly.

[![GitHub Pages](https://img.shields.io/badge/demo-live-0ea5e9?style=flat-square)](https://zwart04.github.io/crispdata/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
![Zero Dependencies](https://img.shields.io/badge/dependencies-0-success?style=flat-square)
![100% Browser](https://img.shields.io/badge/privacy-client--side-blue?style=flat-square)

## The Problem

When you copy data from AI tools (ChatGPT, Claude, Gemini), databases, Slack, or emails, the format is almost always inconsistent:
- **Markdown tables** with misaligned pipes
- **JSON** with trailing commas, mixed quotes, or unquoted keys
- **CSV** with inconsistent quoting and invisible characters
- Invisible Unicode artifacts (zero-width spaces, BOM, soft hyphens)

Existing tools solve only part of this:
- **tableconvert.com** — manual format selection, no cleanup
- **cleanpaste.org** — removes invisible chars, no format conversion
- **OpenRefine** — powerful but requires installation

**CrispData** combines detection, cleaning, and conversion in one step. **100% browser, zero-install, zero-cost.**

## Features

- **Smart Paste** — paste any tabular data, auto-detects format
- **Auto-Clean** — removes invisible characters, normalizes quotes, fixes trailing commas
- **Multi-Format Output** — preview as Table, Markdown, JSON, CSV, or HTML table
- **Statistics** — row count, column count, cleaned character count
- **One-Click Copy** — copy any format with a single button
- **Dark Theme** — easy on the eyes, consistent with companion tools
- **Privacy** — everything runs in your browser, no data is sent anywhere

## Supported Input Formats

| Format | Auto-Detected |
|--------|:---:|
| Markdown table (pipe syntax) | Yes |
| JSON array of objects | Yes |
| JSON single object | Yes |
| CSV (comma-separated) | Yes |
| TSV (tab-separated) | Yes |
| HTML `<table>` | Yes |
| Pipe-delimited text | Yes |
| Semicolon-delimited | Partial |

## Quick Start

1. Open **[CrispData](https://zwart04.github.io/crispdata/)** (or clone and open `index.html`)
2. Paste your data into the left panel
3. Watch it auto-detect, clean, and preview as a table
4. Switch between Markdown / JSON / CSV / HTML tabs
5. Click **Copy** to grab the formatted output

Or load the **Sample** button to see it in action.

## Tech Stack

- **Vanilla JavaScript** — zero frameworks, zero dependencies
- **Tailwind CSS v4** — via CDN (`@tailwindcss/browser`)
- **Single HTML file** — open in any browser, no build step
- **GitHub Pages** — free, fast hosting

## Project Structure

```
crispdata/
├── index.html     # Complete application (JS + CSS + HTML)
├── PRD.md         # Product requirements document
└── README.md      # This file
```

## Roadmap

- [ ] **Excel/CSV file drag-and-drop** — drop .csv/.tsv files directly
- [ ] **Cell editing** — edit cells directly in the table preview
- [ ] **Sort by column** — click column headers to sort
- [ ] **Filter rows** — quick filter by value
- [ ] **Pagination** — for large datasets

## Why CrispData?

- **Bridges the gap** between AI-generated data and usable formats
- **Reduces friction** — no more opening multiple tabs for different conversions
- **Privacy-first** — your data never leaves your machine
- **Works offline** — save the HTML file and use anywhere

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Zwart04](https://github.com/Zwart04). Part of the daily-build series.
