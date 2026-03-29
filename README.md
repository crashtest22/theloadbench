# The Load Bench

> Precision handloading intelligence. Built by shooters, for shooters.

**theloadbench.com** — A newsletter and resource site for serious handloaders.

---

## What This Is

Static site for The Load Bench newsletter. Weekly precision handloading intel: component availability, load data, industry news. No beginner fluff.

## Stack

- Plain HTML5
- [Tailwind CSS](https://tailwindcss.com/) via CDN
- Vanilla JS (minimal)
- GitHub Pages hosting
- Beehiiv for newsletter

## Pages

| File | Description |
|------|-------------|
| `index.html` | Landing page with hero + email signup + feature overview |
| `about.html` | About CrashFPV and why this newsletter exists |
| `archive.html` | Past issues (placeholder until first issue ships) |

## Local Development

No build step required — it's static HTML.

```bash
# Option 1: Python simple server
python3 -m http.server 8080

# Option 2: Node http-server
npx http-server . -p 8080
```

Then open `http://localhost:8080`.

## Deployment

Auto-deploys to GitHub Pages on push to `main` via `.github/workflows/pages.yml`.

**Setup (one-time):**
1. Go to repo Settings → Pages
2. Set Source to **GitHub Actions**
3. Push to `main` — it deploys automatically

## Wiring Beehiiv

Newsletter forms currently use `action="#"` as a placeholder. To connect Beehiiv:

**Option A — Beehiiv embed form (simplest):**
1. In Beehiiv: Settings → Subscribe page → Embed
2. Replace the `<form>` in each HTML file with the Beehiiv embed code

**Option B — API (current JS stub):**
1. Get your API key and publication ID from Beehiiv
2. Uncomment and fill in the fetch block in `js/main.js`
3. Update CORS settings in Beehiiv dashboard if needed

**Option C — Direct POST:**
1. Set `form action="https://www.beehiiv.com/subscribe/YOUR_PUB_ID"` directly
2. Ensure `name="email"` is set on the input (it is)

## Directory Structure

```
theloadbench/
├── index.html              # Landing page
├── about.html              # About page
├── archive.html            # Issues archive (placeholder)
├── css/
│   └── style.css           # Custom styles (Tailwind supplement)
├── js/
│   └── main.js             # Form handling + Beehiiv stub
├── .github/
│   └── workflows/
│       └── pages.yml       # GitHub Pages auto-deploy
└── README.md               # This file
```

---

© 2026 The Load Bench | theloadbench.com
