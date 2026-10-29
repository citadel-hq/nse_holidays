"""NSE Macro Events Generator
Fetches and maintains a standardized calendar of high-impact macroeconomic events
for India (RBI MPC, Union Budget, Elections) and key global spillovers (US Fed FOMC, US CPI/NFP)
that directly impact market volatility and quantitative options strategies.
"""

import csv
import json
import logging
import os
import urllib.request
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nse_macro_events.csv")

# Baseline confirmed scheduled events (2023 - 2026)
STATIC_SEED_EVENTS: List[Dict[str, str]] = [
    # --- 2023 Union Budget ---
    {"date": "2023-02-01", "event": "Union Budget 2023", "category": "BUDGET", "country": "IN", "impact": "CRITICAL"},

    # --- 2023 Elections & Summits ---
    {"date": "2023-05-13", "event": "Karnataka Assembly Election Results", "category": "ELECTION", "country": "IN", "impact": "HIGH"},
    {"date": "2023-09-08", "event": "G20 New Delhi Leaders Summit", "category": "OTHER_HIGH_IMPACT", "country": "IN", "impact": "HIGH"},
    {"date": "2023-12-03", "event": "State Assembly Elections Results (MP, RJ, CG, TS)", "category": "ELECTION", "country": "IN", "impact": "HIGH"},

    # --- 2023 RBI Monetary Policy Committee (MPC) Decisions ---
    {"date": "2023-02-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2023-04-06", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2023-06-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2023-08-10", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2023-10-06", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2023-12-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},

    # --- 2023 US Fed FOMC Rate Decisions ---
    {"date": "2023-02-01", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2023-03-22", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2023-05-03", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2023-06-14", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2023-07-26", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2023-09-20", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2023-11-01", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2023-12-13", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    # --- 2024 Union Budgets ---
    {"date": "2024-02-01", "event": "Union Interim Budget 2024", "category": "BUDGET", "country": "IN", "impact": "CRITICAL"},
    {"date": "2024-07-23", "event": "Union Full Budget 2024", "category": "BUDGET", "country": "IN", "impact": "CRITICAL"},
    # --- 2025 & 2026 Union Budgets ---
    {"date": "2025-02-01", "event": "Union Budget 2025", "category": "BUDGET", "country": "IN", "impact": "CRITICAL"},
    {"date": "2026-02-01", "event": "Union Budget 2026", "category": "BUDGET", "country": "IN", "impact": "CRITICAL"},

    # --- 2024 Elections ---
    {"date": "2024-06-04", "event": "Lok Sabha Election 2024 Counting Day", "category": "ELECTION", "country": "IN", "impact": "CRITICAL"},
    {"date": "2024-10-08", "event": "Haryana & J&K Assembly Election Results", "category": "ELECTION", "country": "IN", "impact": "HIGH"},
    {"date": "2024-11-23", "event": "Maharashtra & Jharkhand Assembly Election Results", "category": "ELECTION", "country": "IN", "impact": "HIGH"},
    # --- 2025 Elections ---
    {"date": "2025-02-08", "event": "Delhi Assembly Election Results", "category": "ELECTION", "country": "IN", "impact": "HIGH"},
    {"date": "2025-11-20", "event": "Bihar Assembly Election Results", "category": "ELECTION", "country": "IN", "impact": "HIGH"},

    # --- 2024 RBI Monetary Policy Committee (MPC) Decisions ---
    {"date": "2024-02-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2024-04-05", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2024-06-07", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2024-08-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2024-10-09", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2024-12-06", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    # --- 2025 RBI MPC Decisions ---
    {"date": "2025-02-07", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2025-04-09", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2025-06-06", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2025-08-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2025-10-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2025-12-05", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    # --- 2026 RBI MPC Decisions ---
    {"date": "2026-02-06", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2026-04-08", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2026-06-05", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2026-08-07", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2026-10-07", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},
    {"date": "2026-12-04", "event": "RBI MPC Interest Rate Decision", "category": "CENTRAL_BANK", "country": "IN", "impact": "HIGH"},

    # --- 2024 US Fed FOMC Rate Decisions ---
    {"date": "2024-01-31", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2024-03-20", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2024-05-01", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2024-06-12", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2024-07-31", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2024-09-18", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2024-11-07", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2024-12-18", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    # --- 2025 US Fed FOMC Rate Decisions ---
    {"date": "2025-01-29", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2025-03-19", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2025-05-07", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2025-06-18", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2025-07-30", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2025-09-17", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2025-10-29", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2025-12-10", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    # --- 2026 US Fed FOMC Rate Decisions ---
    {"date": "2026-01-28", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2026-03-18", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2026-05-06", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2026-06-17", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2026-07-29", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2026-09-16", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2026-11-04", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
    {"date": "2026-12-16", "event": "US Fed FOMC Rate Decision", "category": "CENTRAL_BANK", "country": "US", "impact": "HIGH"},
]


def classify_category(event_name: str) -> str:
  """Categorize macro event based on event title keywords."""
  name = event_name.lower()
  if any(k in name for k in ["rate", "fomc", "fed", "rbi", "monetary policy"]):
    return "CENTRAL_BANK"
  if "budget" in name:
    return "BUDGET"
  if any(k in name for k in ["election", "vote", "poll"]):
    return "ELECTION"
  if any(k in name for k in ["cpi", "inflation", "pce", "ppi"]):
    return "INFLATION"
  if any(k in name for k in ["gdp", "growth"]):
    return "MACRO_GROWTH"
  if any(k in name for k in ["payroll", "unemployment", "jobless"]):
    return "LABOR_MARKET"
  return "OTHER_HIGH_IMPACT"


def fetch_api_events() -> List[Dict[str, str]]:
  """Fetch live upcoming high-impact economic events from biquote API with fallback."""
  url = "https://biquote.io/api/calendar?importance=high&countries=US,IN"
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

  fetched_events: List[Dict[str, str]] = []
  try:
    logging.info("Querying live economic calendar API...")
    with urllib.request.urlopen(req, timeout=10) as resp:
      data = json.loads(resp.read().decode())
      logging.info("API returned %d events.", len(data))

      for item in data:
        # Extract ISO date from UTC timestamp (e.g., '2026-10-28T18:00:00Z' -> '2026-10-28')
        raw_time = item.get("time", "")
        if not raw_time:
          continue
        date_str = raw_time[:10]

        event_name = item.get("name", "").strip()
        country = item.get("countryCode", "US").upper()
        impact = item.get("importance", "high").upper()

        if not event_name:
          continue

        category = classify_category(event_name)

        fetched_events.append({
            "date": date_str,
            "event": event_name,
            "category": category,
            "country": country,
            "impact": impact,
        })
  except Exception as e:
    logging.warning("API fetch encountered error: %s. Using static seed.", e)

  return fetched_events


def load_existing_csv() -> List[Dict[str, str]]:
  """Load existing records if CSV exists to ensure persistence."""
  if not os.path.exists(CSV_FILE_PATH):
    return []

  existing: List[Dict[str, str]] = []
  try:
    with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as f:
      reader = csv.DictReader(f)
      for row in reader:
        existing.append(row)
  except Exception as e:
    logging.warning("Failed to read existing CSV: %s", e)
  return existing


def update_macro_events():
  """Consolidates seeds, existing entries, and newly fetched API events,

  deduplicating and saving sorted records to CSV.
  """
  logging.info("Starting macro events synchronization...")

  # 1. Existing events
  existing = load_existing_csv()

  # 2. Static verified seeds
  seeds = STATIC_SEED_EVENTS

  # 3. Live API events
  api_events = fetch_api_events()

  # Combine and deduplicate
  seen_keys: Set[Tuple[str, str]] = set()
  combined: List[Dict[str, str]] = []

  # Priority: seeds first (canonical names), then existing, then api events
  for item in seeds + existing + api_events:
    key = (item["date"].strip(), item["event"].strip().lower())
    if key not in seen_keys:
      seen_keys.add(key)
      combined.append({
          "date": item["date"].strip(),
          "event": item["event"].strip(),
          "category": item["category"].strip().upper(),
          "country": item["country"].strip().upper(),
          "impact": item["impact"].strip().upper(),
      })

  # Sort chronologically by date, then country, then event name
  combined.sort(key=lambda x: (x["date"], x["country"], x["event"]))

  # Write back to CSV
  fieldnames = ["date", "event", "category", "country", "impact"]
  with open(CSV_FILE_PATH, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined)

  logging.info(
      "Successfully updated %s with %d total high-impact events.",
      CSV_FILE_PATH,
      len(combined),
  )


if __name__ == "__main__":
  update_macro_events()
