# Jarvis Web — AI Voice Assistant with a Sci-Fi HUD

A browser-based personal voice assistant with a sci-fi HUD interface. This project includes real-time speech recognition, text-to-speech, live data widgets, and an optional AI mode powered by Google Gemini's function calling.


## Features

**Voice interaction**
- Continuous speech recognition via the browser's Web Speech API, with custom silence-detection so it waits for full sentences instead of cutting you off mid-thought
- Spoken responses via the browser's built-in SpeechSynthesis
- Clap detection — clap near your mic to wake Jarvis and get a spoken greeting
- Always-on listening mode with feedback-loop prevention (Jarvis pauses listening while it talks, so it can't hear itself)

**Two command modes**
- **Offline mode** — fast, free, keyword-based command matching (no API costs)
- **AI mode** — commands routed through Google Gemini's function-calling, so natural phrasing ("what's it like outside in Dubai right now?") works, not just exact phrases. Toggle between the two anytime with the AI MODE button.

**Commands**
- Time, web search (opens results in a new tab, with a clickable fallback link if the browser blocks the popup), weather by city, to-do list (add / list / clear / delete)

**Live HUD widgets**
- **Weather** — auto-detects your city via IP location, or shows a fixed city
- **Location** — IP, city, region, lat/lon via IP geolocation
- **Markets** — live US stock quotes (Finnhub), with a second toggleable page for PSX (mock data — no reliable free PSX API exists)
- **News** — live headlines (NewsAPI), styled with a red "breaking news" accent
- **Radar** — animated sweep with simulated target blips
- **Audio waveform** — real-time visualization of your live mic input

## Tech stack

- **Frontend:** Vanilla HTML/CSS/JS (no framework) — Web Speech API, Web Audio API, Canvas
- **Backend:** Flask (Python)
- **AI:** Google Gemini API (`google-generativeai`) with function calling
- **APIs:** OpenWeatherMap, Finnhub, NewsAPI, ip-api.com

## Setup

### 1. Clone and install backend dependencies
```bash
git clone https://github.com/ali4xk/jarvis-web.git
cd jarvis-web/backend
pip install -r requirements.txt
```

### 2. Set your API keys
This project needs a few free API keys, set as environment variables.

| Key | Get it from | Free? |
|---|---|---|
| `OPENWEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) | Yes |
| `FINNHUB_API_KEY` | [finnhub.io/register](https://finnhub.io/register) | Yes |
| `NEWS_API_KEY` | [newsapi.org/register](https://newsapi.org/register) | Yes (localhost only on free tier) |
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Yes, no card required |

Windows (PowerShell):
```powershell
setx OPENWEATHER_API_KEY "your_key"
setx FINNHUB_API_KEY "your_key"
setx NEWS_API_KEY "your_key"
setx GEMINI_API_KEY "your_key"
```
Restart your terminal after setting these for them to take effect.

### 3. Run the backend
```bash
python app.py
```
Runs on `http://localhost:5000`.

### 4. Open the frontend
Open `frontend/index.html` directly in **Chrome or Edge** (best Web Speech API support). Click "ACTIVATE VOICE MODE" to start.

## Notes

- Speech recognition and synthesis require Chrome or Edge. Firefox does not support the Web Speech API.
- The frontend talks to `localhost:5000`, so the backend must be running locally for anything to work.
- PSX market data is intentionally mocked (labeled in the UI) since no reliable free API exists for it.
- Local app control (opening desktop programs) isn't possible from a browser for security reasons — see the companion [desktop version](https://github.com/ali4xk/JarvisProject) for that feature.

## Related project

This is the web-based companion to [Jarvis-VoiceAssistant-DesktopVersion](https://github.com/ali4xk/Jarvis-VoiceAssistant-DesktopVersion), a fully offline Python desktop voice assistant with local app control, built with Whisper and pyttsx3.

## Developed by Muhammad Ali - @ali4xk
