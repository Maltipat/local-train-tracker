#!/usr/bin/env python3
"""
Train Tracker — local helper server.
Uses RailRadar API for real-time live train data.

SETUP
=====
1. Sign up free at https://railradar.in
2. Save your API key:  echo "YOUR_KEY" > .api_key

Run:  python3 tracker_server.py
Open: http://localhost:5050
"""

from __future__ import annotations

import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from flask import Flask, jsonify, request, send_from_directory
    import requests
except ImportError as exc:
    sys.stderr.write(
        "\nMissing dependency: {}\n"
        "Install with:\n"
        "    python3 -m pip install --user flask requests\n\n"
        .format(exc.name)
    )
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("train-tracker")

HERE = Path(__file__).resolve().parent
app  = Flask(__name__, static_folder=None)
IST  = timezone(timedelta(hours=5, minutes=30))
API  = "https://api.railradar.org/api/v1"


def _read_key() -> str | None:
    key = os.environ.get("RAILRADAR_KEY", "").strip()
    if key:
        return key
    fp = HERE / ".api_key"
    return fp.read_text().strip() if fp.exists() else None

API_KEY: str | None = _read_key()


def load_key() -> str | None:
    return API_KEY


def unix_to_time(ts) -> str | None:
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=IST).strftime("%H:%M")
    except Exception:
        return None


def fmt_delay(mins) -> str | None:
    if mins is None:
        return None
    if mins == 0:
        return "On time"
    return f"+{mins} min late" if mins > 0 else f"{mins} min"


def fetch_train(train_no: str) -> dict:
    key = load_key()
    if not key:
        raise RuntimeError("No API key. Save your RailRadar key to '.api_key'.")
    r = requests.get(f"{API}/trains/{train_no}",
                     headers={"X-API-Key": key}, timeout=20)
    if r.status_code == 401: raise RuntimeError("API key rejected.")
    if r.status_code == 429: raise RuntimeError("Free quota exceeded (1000/month). Upgrade at railradar.in.")
    if r.status_code == 404: raise RuntimeError(f"Train {train_no} not found.")
    r.raise_for_status()
    return r.json()


@app.route("/")
def index():
    return send_from_directory(str(HERE), "train-tracker.html")


@app.route("/api/health")
def api_health():
    return jsonify({
        "ok": True,
        "time": datetime.now().isoformat(),
        "api_key_configured": load_key() is not None,
    })


@app.route("/api/station-time")
def api_station_time():
    train_no     = (request.args.get("train") or "").strip()
    station_code = (request.args.get("station") or "").strip().upper()

    if not re.match(r"^\d{4,5}$", train_no):
        return jsonify({"error": "Invalid train number (must be 4-5 digits)."}), 400
    if not re.match(r"^[A-Z]{2,5}$", station_code):
        return jsonify({"error": "Invalid station code (2-5 letters, e.g. NDLS, BCT)."}), 400

    try:
        data = fetch_train(train_no)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except requests.RequestException as e:
        return jsonify({"error": f"API request failed: {e}"}), 502

    train_info  = data.get("data", {}).get("train", {})
    live        = data.get("data", {}).get("liveData", {})
    route       = live.get("route", [])
    current_loc = live.get("currentLocation", {})

    all_codes = [(s.get("stationCode") or "").upper() for s in route]
    station   = next((s for s in route
                      if (s.get("stationCode") or "").upper() == station_code), None)

    if not station:
        return jsonify({
            "error": f"Station {station_code} is not on this train's route.",
            "available_stations": all_codes,
            "train": train_no, "station": station_code,
        }), 404

    return jsonify({
        "train":                train_no,
        "train_name":           train_info.get("trainName", ""),
        "station":              station_code,
        "date":                 live.get("journeyDate", ""),
        "scheduled_arrival":    unix_to_time(station.get("scheduledArrival")),
        "scheduled_departure":  unix_to_time(station.get("scheduledDeparture")),
        "actual_arrival":       unix_to_time(station.get("actualArrival")),
        "actual_departure":     unix_to_time(station.get("actualDeparture")),
        "delay_arrival":        fmt_delay(station.get("delayArrivalMinutes")),
        "delay_departure":      fmt_delay(station.get("delayDepartureMinutes")),
        "platform":             station.get("platform"),
        "current_station":      current_loc.get("stationCode", ""),
        "gps_lat":              current_loc.get("latitude"),
        "gps_lng":              current_loc.get("longitude"),
        "data_source":          live.get("dataSource", "OFFICIAL"),
        "last_updated":         live.get("lastUpdatedAt", ""),
    })


@app.route("/api/raw")
def api_raw():
    train_no = (request.args.get("train") or "22439").strip()
    try:
        return jsonify(fetch_train(train_no))
    except Exception as e:
        return jsonify({"error": str(e)}), 502


if __name__ == "__main__":
    port    = 5050
    key_set = load_key() is not None
    print()
    print("=" * 60)
    print(" Train Tracker — Live Running Status")
    print("=" * 60)
    print(f" Open in browser:    http://localhost:{port}")
    print(f" API key configured: {'YES' if key_set else 'NO  ⚠'}")
    print(" Press Ctrl+C to stop.")
    print("=" * 60)
    print()
    app.run(host="127.0.0.1", port=port, debug=False)
