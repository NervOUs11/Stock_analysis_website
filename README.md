# 📈 Stock Valuation Dashboard

A financial analysis dashboard built with Dash and Plotly. Search any stock ticker to view key financial statements and run an interactive intrinsic value model.

---

## Project Structure

```
├── app.py                  # Entry point
├── server.py               # Dash app instance
├── layout.py               # App layout
├── callbacks.py            # All callback logic
├── components.py           # Reusable UI components (cards, charts)
├── utils.py                # Shared helpers (safe_format)
├── getData.py              # Yahoo Finance data fetching
├── dcf_valuation.py        # DCF / PE / FCF valuation calculations
├── pages/
│   ├── financials.py       # Financials tab
│   └── valuation.py        # Valuation tab
└── assets/
    ├── Logo_black.png
    └── Logo_white.png
```

---

## Getting Started

**1. Create and activate a virtual environment**
```commandline
python -m venv .venv
source .venv/bin/activate
```

> On Windows use: `.venv\Scripts\activate`

**2. Install dependencies**
```commandline
pip install -r requirements.txt
```

**3. Run the app**
```commandline
python app.py
```

Then open [http://localhost:8050](http://localhost:8050) in your browser.

---

## Features

- **Financials Tab** — Income statement, EPS, CAPEX, FCF, retained earnings, and long-term debt charts
- **Valuation Tab** — Interactive intrinsic value model with two methods:
  - **PE-Based** — Projects EPS growth and applies an exit PE multiple
  - **FCF-Based** — Projects FCF growth and applies an exit P/FCF multiple
- **Dark Mode** — Full dark/light theme toggle