# The Load Bench — Scraper Pipeline

Automated weekly digest generator for [The Load Bench](https://theloadbench.com) newsletter. Scrapes component availability (powder, primer, brass, bullets) and forum discussions (Reddit, Sniper's Hide) to produce a ready-to-edit markdown digest.

---

## What It Does

| Module | Purpose |
|--------|---------|
| `components.py` | Scrapes Powder Valley, Midsouth, Graf & Sons, Widener's, Lucky Gunner |
| `forums.py` | Pulls Reddit (r/reloading, r/longrange, r/6gt) + Sniper's Hide threads |
| `digest.py` | Combines results into a markdown weekly digest |
| `run.py` | Single entry point — runs everything |

---

## Quick Start

### 1. Install dependencies

```bash
cd scraper/
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the pipeline

From the repo root:

```bash
python scraper/run.py
```

Or from inside the `scraper/` directory:

```bash
cd scraper/
python run.py
```

**Optional flags:**

```bash
python scraper/run.py --skip-components    # forums only
python scraper/run.py --skip-forums        # components only
python scraper/run.py --output-dir /path/to/output
```

### 3. Find your digest

Output lands in `output/weekly-YYYY-MM-DD.md`. Open it, add your personal load bench notes in the **Next Steps** section, then paste into your newsletter tool (Beehiiv, Substack, etc.).

---

## Output Format

```markdown
# The Load Bench — Weekly Digest YYYY-MM-DD

## Component Availability
### In Stock This Week
- **H4350 1lb** — $32.99 | [Powder Valley](https://...)

### Watching (Out of Stock / Check for Restocks)
- **Varget 8lb** — price unknown | [Graf & Sons](https://...)

## From the Community
### Trending on Reddit
#### r/reloading
- **[H4350 finally back in stock at PV]** — ⬆️ 847 | 💬 143 comments

### Sniper's Hide Buzz
- **[6GT brass comparison thread]**

## Next Steps
- [ ] Current load development update
- [ ] Range trip results
...
```

---

## Cron Job Setup

To run automatically every Monday morning (9 AM):

```bash
crontab -e
```

Add:

```cron
0 9 * * 1 cd /path/to/theloadbench && python scraper/run.py >> logs/scraper.log 2>&1
```

Or with a virtual environment:

```cron
0 9 * * 1 cd /path/to/theloadbench && .venv/bin/python scraper/run.py >> logs/scraper.log 2>&1
```

### GitHub Actions (alternative)

You can also run this via GitHub Actions on a schedule — see `.github/workflows/` for a template (create one if needed).

---

## Notes on Scraping

- **Delays:** 1.5 seconds between requests. Be respectful.
- **Failures:** If a site blocks the scraper, it logs a warning and continues. The digest will note "check site manually."
- **Anti-bot:** Some sites (especially during high-demand periods) may return 403/captcha. The scraper handles this gracefully.
- **Reddit:** Uses the official public JSON API (no auth required). Just needs a proper User-Agent.
- **Sniper's Hide:** May require login for some forum sections. The scraper tries public URLs.

---

## Tracked Components

| Category | Items |
|----------|-------|
| Powders | H4350, Varget, N140, N150, IMR 4064, CFE 223, Hodgdon Extreme series |
| Primers | Federal 210M, 205M, CCI 400, CCI 450, BR4, BR2, Remington 9.5M |
| Brass | 6GT, .308 Win, .223 Rem, 9mm, .45 ACP (Lapua, Starline, Peterson, Alpha) |
| Bullets | 6GT 105-115gr, .308 175gr SMK, 185gr Juggernaut, .223 77gr SMK |

---

## File Structure

```
theloadbench/
├── scraper/
│   ├── components.py       # Site scrapers
│   ├── forums.py           # Reddit + Sniper's Hide
│   ├── digest.py           # Markdown generator
│   ├── run.py              # Entry point
│   ├── requirements.txt
│   └── README.md
└── output/                 # Gitignored — digests land here
    └── .gitkeep
```

---

*Built for [The Load Bench](https://theloadbench.com) by CrashFPV.*
