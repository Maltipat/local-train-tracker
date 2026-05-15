# 🚂 local-train-tracker

A lightweight, self-hosted web app for checking **Indian Railways live running status** — arrival & departure times, delays, platform numbers, and current train location — all in one page, no external navigation.

---

## ✨ Features

- 🕐 Live **scheduled vs actual** arrival/departure times
- ⏱️ Delay badges (e.g. `+12 min late` or `On time`)
- 🚉 Platform number for your station
- 📍 Current GPS location of the train
- 🔍 Lookup by train number + station code
- 🖥️ Runs entirely on `localhost` — your data stays local

---

## ⚙️ Setup (one-time, ~3 minutes)

### 1. Get a free RailRadar API key
1. Sign up (free) at [railradar.in](https://railradar.in)
2. Copy your API key from the dashboard

### 2. Save your key

```bash
echo "YOUR_KEY_HERE" > .api_key
```

Or export it as an environment variable:

```bash
export RAILRADAR_KEY=YOUR_KEY_HERE
```

### 3. Install dependencies

```bash
python3 -m pip install --user flask requests
```

---

## ▶️ Run

```bash
python3 tracker_server.py
```

Then open: [http://localhost:5050](http://localhost:5050)

The status pill in the top-right should show **"Helper online · API key OK"**.

---

## 🔎 Usage

Fill in the **Station Time Lookup** form:

| Field | Example |
|-------|---------|
| Train number | `12951`, `22439` |
| Station code | `NDLS`, `BCT`, `BPL` |
| Date | Today / Yesterday / Tomorrow |

Click **Get Arrival / Departure** — results appear inline with times, delay, and platform.

> **Tip:** To inspect the raw API response, visit:  
> `http://localhost:5050/api/raw?train=12951`

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `API key missing` banner | Save key to `.api_key` in this folder and restart |
| `401 API key rejected` | Re-copy key from railradar.in (no extra spaces) |
| `429 quota exceeded` | Free tier is 1000 req/month — wait or upgrade |
| `Station not on route` | The response lists all valid station codes for that train |

---

## 📁 Project Structure

```
local-train-tracker/
├── tracker_server.py   # Flask backend — proxies RailRadar API
├── train-tracker.html  # Frontend UI (single file)
├── .api_key            # Your API key (gitignored)
└── README.md
```

---

## 🔒 Security Note

The `.api_key` file is listed in `.gitignore` and will **not** be pushed to GitHub. Never hardcode your key in source files.

---

## 📄 License

MIT — free to use, modify, and distribute.
