# 🚨 Agentic AI Disaster Alert System — Sri Lanka

<div align="center">

**Automated real-time flood & landslide monitoring system for Sri Lanka**

*Powered by live sensor data, AI-generated bilingual alerts, and Telegram delivery*

[![Disaster Alert Monitor](https://github.com/dinod001/Agentic-AI-Disaster-Alert-System-SL/actions/workflows/monitor.yml/badge.svg)](https://github.com/dinod001/Agentic-AI-Disaster-Alert-System-SL/actions/workflows/monitor.yml)
![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-orange?logo=google&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 📋 Overview

This system continuously monitors **39 flood stations** and **25 landslide-prone zones** across Sri Lanka using real-time data from the Irrigation Department and OpenWeatherMap. When risk conditions are detected, it uses **Google Gemini AI** to generate clear, bilingual alerts in **English and Sinhala (සිංහල)** and delivers them instantly via **Telegram**.

> ⚠️ **Disclaimer:** This is an AI-generated alert system. It is NOT an official government report. Always follow instructions from the **Disaster Management Centre (DMC)** of Sri Lanka.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Hourly Cron)               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌──────────────────┐                │
│  │ 📡 Irrigation    │    │ 🌧️ Weather API    │                │
│  │    Collector     │    │   (OpenWeather)   │                │
│  │  (39 stations)   │    │ (39 flood + 25    │                │
│  │                  │    │  landslide zones) │                │
│  └────────┬─────────┘    └────────┬──────────┘                │
│           │                       │                           │
│  ┌────────▼───────────────────────▼──────────┐               │
│  │          🔍  Risk Assessment Engines        │               │
│  │                                            │               │
│  │  Flood Engine          Landslide Engine     │               │
│  │  • Water level ratio   • Rainfall intensity │               │
│  │  • Rate of rise        • Humidity           │               │
│  │  • Current rainfall    • Wind speed         │               │
│  │                        • Cloud cover        │               │
│  │  Risk Score: 0-100     Risk Score: 0-100    │               │
│  └────────────────────┬──────────────────────┘               │
│                       │                                       │
│  ┌────────────────────▼──────────────────────┐               │
│  │     🔄  Alert State Deduplication          │               │
│  │  (Prevents duplicate hourly alerts)        │               │
│  │  • Compares (station, risk_level) vs last  │               │
│  │  • Auto-wipes daily at midnight            │               │
│  └────────────────────┬──────────────────────┘               │
│                       │ (only if state changed)               │
│  ┌────────────────────▼──────────────────────┐               │
│  │     🤖  Gemini 2.5 Flash (AI)             │               │
│  │  • Bilingual: English + Sinhala            │               │
│  │  • Tone adapts to risk level               │               │
│  └────────────────────┬──────────────────────┘               │
│                       │                                       │
│  ┌────────────────────▼──────────────────────┐               │
│  │     📱  Telegram Bot — Alert Delivery      │               │
│  └───────────────────────────────────────────┘               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚡ Features

| Feature | Details |
|---|---|
| **Real-time Data** | Irrigation water levels from ArcGIS + rainfall from OpenWeatherMap |
| **Dual Engines** | Separate flood & landslide risk scoring (0-100) |
| **Risk Levels** | `NORMAL` → `WATCH` → `WARNING` → `CRITICAL` |
| **AI Alerts** | Gemini 2.5 Flash generates bilingual English + Sinhala alerts |
| **Smart Tone** | WATCH = advisory, WARNING = urgent, CRITICAL = life-threatening |
| **Deduplication** | JSON state tracking prevents spam — alerts only when risk changes |
| **Telegram** | Auto-delivers to configured Telegram channel/chat |
| **Scheduled** | Runs every hour via GitHub Actions cron (free) |
| **Disclaimer** | Every alert clearly states this is AI-generated, not government-issued |

---

## 📁 Project Structure

```
├── .github/
│   └── workflows/
│       └── monitor.yml          # GitHub Actions hourly cron job
├── data/
│   └── alert_state.json         # Runtime state (auto-generated)
├── src/
│   ├── main.py                  # Entry point — single cycle runner
│   ├── config.py                # Central configuration loader
│   ├── agents/
│   │   ├── monitor_agent.py     # Orchestrator — ties everything together
│   │   └── llm.py               # Gemini AI alert generator
│   ├── collectors/
│   │   ├── irrigation_api.py    # Irrigation Department data collector
│   │   └── weather_api.py       # OpenWeatherMap API collector
│   ├── engine/
│   │   ├── flood_engine.py      # Flood risk scoring engine
│   │   └── landslide_engine.py  # Landslide risk scoring engine
│   ├── notifiers/
│   │   └── telegram_bot.py      # Telegram alert sender
│   └── utils/
│       ├── alert_state.py       # Deduplication state manager
│       └── logger.py            # Centralized logging
├── tests/
│   ├── test_collectors.py       # Data collector tests
│   └── test_engine.py           # Engine risk scoring tests
├── config.yaml                  # Station coordinates & model params
├── Dockerfile                   # Container deployment (optional)
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🔧 Risk Scoring

### Flood Engine (0-100 points)

| Factor | Points | Criteria |
|---|---|---|
| Water Level Ratio | 0-40 | Level vs alert/minor/major thresholds |
| Rate of Rise | 0-30 | Speed of water level increase (m/hr) |
| Current Rainfall | 0-30 | Rain intensity (mm/hr) |

### Landslide Engine (0-100 points)

| Factor | Points | Criteria |
|---|---|---|
| Rainfall Intensity | 0-40 | Current precipitation (mm/hr) |
| Humidity | 0-25 | Soil saturation proxy (%) |
| Wind Speed | 0-15 | Storm severity indicator (m/s) |
| Cloud Cover | 0-10 | Approaching storm indicator (%) |

### Classification

| Score | Level | Action |
|---|---|---|
| 70-100 | 🔴 CRITICAL | Immediate evacuation recommended |
| 45-69 | 🟠 WARNING | High alert — prepare for evacuation |
| 20-44 | 🟡 WATCH | Be vigilant — monitor conditions |
| 0-19 | 🟢 NORMAL | No action needed |

---

## 🌍 Coverage

- **39 Flood Monitoring Stations** across major river basins (Kelani, Kalu, Nilwala, Gin, Mahaweli, Walawe)
- **25 Landslide-Prone Zones** in hill country districts (Kandy, Matale, Nuwara Eliya, Badulla, Ratnapura, Kegalle)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- API keys for: OpenWeatherMap, Google Gemini, Telegram Bot

### 1. Clone & Install

```bash
git clone https://github.com/dinod001/Agentic-AI-Disaster-Alert-System-SL.git
cd Agentic-AI-Disaster-Alert-System-SL
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
OPENWEATHERMAP_API_KEY=your_openweathermap_key
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
IRRIGATION_DATA_URL=https://raw.githubusercontent.com/nuuuwan/lk_irrigation/main/data/alert_data.json
ARCGIS_URL=https://services3.arcgis.com/J7ZFXmR8rSmQ3FGf/arcgis/rest/services/gauges_2_view/FeatureServer/0/query
```

### 3. Run Locally

```bash
python src/main.py
```

### 4. Run Tests

```bash
python -m pytest tests/ -v
```

---

## ☁️ Deployment (GitHub Actions)

The system is designed to run as a **free serverless cron job** using GitHub Actions.

### Setup

1. Push the repo to GitHub
2. Go to **Settings → Secrets and variables → Actions**
3. Add 6 repository secrets:

| Secret | Description |
|---|---|
| `OPENWEATHERMAP_API_KEY` | OpenWeatherMap API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Target chat/channel ID |
| `IRRIGATION_DATA_URL` | Irrigation data source URL |
| `ARCGIS_URL` | ArcGIS feature service URL |

4. Go to **Actions** tab → **"Disaster Alert Monitor"** → **"Run workflow"** to test

The workflow runs automatically **every hour** and uses GitHub Actions cache to persist `alert_state.json` between runs for deduplication.

---

## 📱 Sample Telegram Alert

```
🕐 2026-02-19 11:30:00

A WATCH level flood alert HAS BEEN ISSUED for Weraganthota.
The water level is -1.78m and rising at 0.337m/hour.

There are no landslide warnings at this time.

---
⚠️ This is an AI-generated alert based on real-time sensor data.
This is NOT an official government report. Please also follow
instructions from the Disaster Management Centre (DMC) of Sri Lanka.

වෙරගන්තොට ප්‍රදේශයේ ගංවතුර අවදානමක් ඇති විය හැකි බැවින්
අවධානයෙන් සිටින්න. ජල මට්ටම -1.78m වන අතර
පැයකට 0.337m ක වේගයකින් ඉහළ යමින් පවතී.

මේ වන විට නායයෑම් අනතුරු ඇඟවීම් නොමැත.

---
⚠️ මෙය AI පද්ධතියක් මගින් සකස් කරන ලද අනතුරු ඇඟවීමකි.
මෙය රජයේ නිල දැනුම්දීමක් නොවේ. DMC ශ්‍රී ලංකාවේ උපදෙස් ද
අනුගමනය කරන්න.
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.11 |
| **AI Model** | Google Gemini 2.5 Flash (free tier) |
| **Weather Data** | OpenWeatherMap API |
| **Irrigation Data** | Sri Lanka Irrigation Dept (ArcGIS + GitHub) |
| **Notifications** | Telegram Bot API |
| **Scheduling** | GitHub Actions (cron) |
| **State Management** | JSON file with GitHub Actions cache |
| **Logging** | Python `logging` module |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ for Sri Lanka's safety**

*Protecting communities through real-time AI-powered disaster monitoring*

🇱🇰

</div>
