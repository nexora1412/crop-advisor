# 🌾 CropAdvisor AI — किसान का डिजिटल साथी

An intelligent farming assistant powered by ASI:One AI that provides 
real-time agricultural advice to Indian farmers.

## Features
- 🌱 Real-time Farm Analysis (weather + soil + market data)
- 🤖 Personal Farming Assistant (pest control, desi nuskhe, diseases)
- 💰 Financial Guidance (government schemes, low-interest loans)
- ⚖️ Legal Rights (MSP, land rights, complaint filing)
- 🌐 Multi-language support (Hindi, Marathi, Tamil, Telugu & more)

## Tech Stack
- ASI:One API (AI reasoning)
- OpenWeatherMap API (live weather)
- Agromonitoring API (soil data)
- Python Flask (web framework)

## Setup Instructions
1. Clone this repository
2. Install dependencies:
   pip install flask openai python-dotenv requests
3. Copy .env.example to .env and add your API keys
4. Run: python agent.py
5. Open browser: http://localhost:5000

## API Keys Required
- ASI:One API key from asi1.ai
- OpenWeatherMap API key from openweathermap.org
- Agromonitoring API key from agromonitoring.com

## How It Works
Farmer enters crop, region, city and soil type. The system fetches 
live weather data, soil conditions and market prices, then sends 
everything to ASI:One AI which provides hyper-specific advice 
tailored to that exact farm.