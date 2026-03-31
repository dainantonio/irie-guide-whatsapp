# IrieGuide 🇯🇲 – Jamaica WhatsApp Tourism Concierge

A warm, knowledgeable WhatsApp bot powered by Gemini 1.5 Flash that serves as your personal Jamaica tourism concierge. Ask about any of Jamaica's 14 parishes and IrieGuide will share top attractions, food tips, and local secrets.

## Features

- **AI-powered** with Google Gemini 1.5 Flash + function calling
- **All 14 Jamaican parishes** with curated attraction data
- **WhatsApp delivery** via Twilio Messaging API
- **Persistent sessions** — remembers last 10 turns per user
- **Caribbean personality** — warm, friendly island concierge vibes
- **Free deployment** on Render.com

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/irie-guide-whatsapp.git
cd irie-guide-whatsapp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

**Get your keys:**
- **GEMINI_API_KEY** → [Google AI Studio](https://aistudio.google.com/app/apikey)
- **TWILIO_ACCOUNT_SID / AUTH_TOKEN** → [Twilio Console](https://console.twilio.com)
- **TWILIO_WHATSAPP_FROM** → Your Twilio WhatsApp sender (sandbox: `whatsapp:+14155238886`)

### 3. Run locally

```bash
uvicorn main:app --reload
```

Server starts at `http://localhost:8000`

### 4. Test with ngrok (local Twilio webhook)

```bash
ngrok http 8000
```

Copy the `https://xxxx.ngrok.io` URL and set it as your Twilio WhatsApp webhook:
`https://xxxx.ngrok.io/webhook`

## Twilio WhatsApp Sandbox Setup

1. Go to [Twilio Console → Messaging → Try it out → Send a WhatsApp message](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Join the sandbox by sending `join <sandbox-word>` to `+1 415 523 8886`
3. Set the webhook URL: `https://YOUR_DOMAIN/webhook` (POST)
4. Send a message — IrieGuide responds!

## Deploy to Render.com (Free)

### Option A: Connect GitHub (recommended)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — click **Deploy**
5. Add environment variables in the Render dashboard under **Environment**
6. Your webhook URL: `https://irie-guide-whatsapp.onrender.com/webhook`

### Option B: render.yaml auto-deploy

The included `render.yaml` defines the free-tier web service. Render will:
- Install Python dependencies via `pip install -r requirements.txt`
- Start the server with `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Note:** Free Render instances spin down after 15 minutes of inactivity. First message after sleep may take ~30 seconds.

## Project Structure

```
irie-guide-whatsapp/
├── main.py              # FastAPI app, Gemini AI, Twilio webhook
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com deployment config
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Example Conversations

> **You:** What should I do in Portland?
>
> **IrieGuide:** Irie, mon! Portland is Jamaica's lush garden parish — pure paradise! 🌿 You MUST visit the Blue Lagoon, a mystical 180-ft deep spring where fresh and saltwater meet — the colour is unreal. Then head to Reach Falls for a stunning jungle waterfall adventure. And before you leave, stop at Boston Bay — the birthplace of Jamaican jerk cooking — and taste the real thing! Walk good and enjoy every moment! 🔥

---

> **You:** Best beaches in Negril?
>
> **IrieGuide:** No worries, mon — Negril is pure vibes! 🏖️ Seven Mile Beach in Westmoreland is one of the Caribbean's most beautiful stretches of white sand — just endless sunshine and calm turquoise water. For sunset, head to the Negril Cliffs and Rick's Café where brave souls cliff-jump into the sea. The golden hour there is legendary. Big up your trip! ☀️

## Contributing

Pull requests welcome! Ideas: hotel recommendations, restaurant bookings API, Google Maps links, multi-language support.

## License

MIT
