Personal Hub (Apple Health–inspired)

A lightweight, static dashboard inspired by the Apple Health Summary view, with sections for Health, Finances, and Goals.

Quick start

- Open `index.html` in your browser, or
- Serve locally:

```bash
python3 -m http.server 5173
# then open http://localhost:5173
```

Structure

- `index.html`: Markup and section layout
- `styles.css`: Apple-like dark UI, card grid, accents
- `app.js`: Segmented control, sample charts (Chart.js via CDN)

Docs

- Health UI overview: `docs/HEALTH_UI.md`
- Integrations: `docs/INTEGRATIONS.md`

Notes

- This is an original implementation inspired by Apple’s design language, not a copy of proprietary assets. No Apple trademarks or assets are included.
- Replace sample data in `app.js` with your real sources (health exports, bank CSVs, habit trackers, etc.).

Customization ideas

- Add iCloud/Drive export imports for Health data
- Plaid or file-upload CSVs for finances
- Goals sync with Notion/Todoist APIs
- Light mode and accessibility tweaks


