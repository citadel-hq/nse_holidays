# NSE Holidays & Macroeconomic Events

Standardized calendars of market holidays and high-impact macroeconomic events for Indian capital markets and quantitative trading strategies.

---

## 1. Datasets

### A. NSE Trading Holidays (`nse_holidays.csv`)
* **File**: [`nse_holidays.csv`](https://github.com/citadel-hq/nse_holidays/blob/main/nse_holidays.csv)
* **Description**: Official list of NSE F&O and equity trading holidays.
* **Format**: `DD-Mon-YYYY` (e.g. `26-Jan-2026`).

### B. High-Impact Macro Events Calendar (`nse_macro_events.csv`)
* **File**: [`nse_macro_events.csv`](https://github.com/citadel-hq/nse_holidays/blob/main/nse_macro_events.csv)
* **Description**: Confirmed and rolling high-impact macroeconomic and political events for India and major global market drivers:
  * **Union Budgets** (Annual February & post-election July budgets)
  * **RBI Monetary Policy Committee (MPC)** rate decisions
  * **US Federal Reserve FOMC** interest rate announcements and press conferences
  * **General & State Assembly Election** counting and result days
  * **High-impact inflation/macro releases** (CPI, GDP, NFP)
* **Schema**:
  | Column | Type | Example | Description |
  |---|---|---|---|
  | `date` | String (`YYYY-MM-DD`) | `2026-03-18` | Event date in ISO format |
  | `event` | String | `US Fed FOMC Rate Decision` | Official event description |
  | `category` | String | `CENTRAL_BANK`, `BUDGET`, `ELECTION`, `INFLATION` | Event classification |
  | `country` | String | `IN`, `US` | Origin country |
  | `impact` | String | `CRITICAL`, `HIGH` | Market volatility severity |

---

## 2. Automated Updates (GitHub Actions)

* **Execution Schedule**: Automatically synchronized **every day at 20:30 IST (15:00 UTC)** via GitHub Actions (`.github/workflows/main.yml`).
* **Workflow Tasks**:
  1. Executes `holidays.py` to synchronize official exchange holiday schedules.
  2. Executes `events.py` to reconcile confirmed annual schedules (2024–2026) with rolling live economic calendar releases via keyless API endpoints.
  3. Commits and pushes any newly detected dates.

---

## 3. Quickstart & Strategy Integration

### Installation
```bash
pip install -r requirements.txt
```

### Manual Synchronization
```bash
python holidays.py   # Updates nse_holidays.csv
python events.py     # Updates nse_macro_events.csv
```

### How Strategies Consume `nse_macro_events.csv`
Quantitative strategies (e.g. overnight strangles or credit spreads) can directly query the CSV to gate entry before scheduled event shocks:

```python
import pandas as pd
from datetime import date

# Load directly from local file or raw GitHub URL
URL = "https://raw.githubusercontent.com/citadel-hq/nse_holidays/main/nse_macro_events.csv"
df_events = pd.read_csv(URL)

today = date.today().isoformat()

# Check if today has a high-impact event
is_event_day = not df_events[(df_events["date"] == today) & (df_events["impact"].isin(["HIGH", "CRITICAL"]))].empty

if is_event_day:
    print(f"Skipping trade on {today} due to scheduled macro event risk.")
```
