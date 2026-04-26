# Cloud Kitchen Review Analytics

Automated topic classification + analytics dashboard for Zomato & Swiggy reviews.

## Quick Start (Windows)

1. **Drop your CSV file(s)** into the `data/` folder
2. **Double-click** `START_DASHBOARD.bat`
3. Browser opens automatically at **http://localhost:5000**

That's it. No manual install steps needed — the bat file handles everything.

---

## Requirements

- Python 3.10 or later — https://python.org (tick "Add Python to PATH" on install)
- Internet connection on first run (to install Flask & pandas)

---

## CSV Format

The dashboard auto-detects columns. Your CSV should have these headers
(exact names or close variants):

| Column | Example |
|--------|---------|
| Order_Id | 7844735518 |
| Res_name | Behrouz Biryani |
| Date | 01/03/2026 |
| Food_Rating | 4.0 |
| Comments | food was cold |

- **Multiple CSVs** are merged automatically — drop both Zomato and Swiggy files into `data/`
- Files with "swiggy" in the filename are tagged as Swiggy source; others default to Zomato

---

## Dashboard — 6 Views

| Tab | What it shows |
|-----|---------------|
| **Overview** | KPI tiles, topic donut, complaint bars, brand ratings, weekly trend |
| **Topic taxonomy** | Full 2-level topic → sub-topic hierarchy with counts |
| **Brand deep-dive** | Per-brand KPIs, topic/sub-topic bars, weekly trend chart |
| **Issue heatmap** | Cross-brand % rate per issue topic; cross-brand sub-topic compare |
| **Insights** | Auto-generated critical issues, watch list, positives, actions |
| **Review explorer** | Browse classified reviews; filter by brand, topic, rating |

---

## Topic Taxonomy (10 topics, 28 sub-topics)

| Topic | Sub-topics |
|-------|-----------|
| Food Quality | Taste - Bad · Taste - Good · Temperature - Cold Food · Freshness - Stale/Bad Smell · Cooking - Undercooked · Cooking - Overcooked/Hard · Foreign Object · Texture - Soggy |
| Quantity | Portion Too Small · Missing Items · Less Gravy/Sauce · Fewer Pieces |
| Wrong Order | Wrong Item Sent · Veg/Non-Veg Mix-up · Wrong Variant/Size |
| Packaging | Packaging Damaged · Beverage Issue |
| Delivery | Late Delivery · Not Delivered · Delivery Person |
| Value for Money | Overpriced/Not Worth · Good Value |
| Hygiene | Unhygienic |
| Positive Overall | Overall Positive · Specific Praise |
| App/Platform | Platform Issue · Offer/Promo Issue |
| Other Feedback | General Comment |

---

## Folder Structure

```
kitchen_analytics/
├── START_DASHBOARD.bat   ← double-click to launch
├── app.py                ← Flask server + API routes
├── classifier.py         ← topic/subtopic classification logic
├── requirements.txt      ← dependencies (flask, pandas)
├── data/                 ← put your CSV files here
│   └── your_file.csv
└── templates/
    └── index.html        ← dashboard UI
```

---

## Adding More Data

- Drop new CSV files into `data/` and restart the server (Ctrl+C then re-run bat)
- Add a `Region` or `City` column to your CSV → extend `app.py` groupBy for regional reports
- The classifier (`classifier.py`) is fully editable — add patterns to TAXONOMY for custom topics

---

## Stopping the Server

Press `Ctrl + C` in the terminal window, then close it.
