from flask import Flask, request, jsonify, render_template
import os, json
from dotenv import load_dotenv
from openai import OpenAI
from weather_tool import get_weather
from soil_tool import get_soil_data
from market_tool import get_market_price

load_dotenv()
app = Flask(__name__)
client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key=os.getenv("ASI_API_KEY"),
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    crop = data.get('crop', 'wheat')
    region = data.get('region', 'Maharashtra')
    city = data.get('city', 'Pune')
    soil = data.get('soil', 'black soil')
    farmsize = data.get('farmsize', '2 acres')
    language = data.get('language', 'english')

    weather = get_weather(city)
    soil_data = get_soil_data(20.5, 78.9)
    market = get_market_price(crop)

    lang_line = f"CRITICAL: Respond ENTIRELY in {language} language only." if language != 'english' else ""

    response = client.chat.completions.create(
        model="asi1",
        max_tokens=750,
        messages=[{
            "role": "user",
            "content": f"""You are an expert agricultural advisor for Indian farmers. {lang_line}

FARM DETAILS:
- Crop: {crop}
- Region: {region}
- City: {city}
- Soil: {soil}
- Farm Size: {farmsize}

LIVE REAL-TIME DATA:
- Temperature: {weather['temperature']}°C
- Humidity: {weather['humidity']}%
- Rainfall today: {weather['rainfall_mm']}mm
- Sky: {weather['condition']}
- Soil moisture: {soil_data['soil_moisture']}
- {crop} market price: {market['current_price']} (Trend: {market['trend']})
- Best selling month: {market['best_sell_month']}

Give HYPER-SPECIFIC advice for THIS exact farm:

1. 🌱 FERTILIZER SCHEDULE - exact kg for {farmsize}, specific products available in {region}
2. 💧 IRRIGATION ADVICE - based on {weather['humidity']}% humidity and {weather['rainfall_mm']}mm rain
3. 💰 BEST SELLING WINDOW - price trend is {market['trend']}, advise accordingly
4. ⚠️ RISK ALERTS - pests/diseases specific to {region} at current weather conditions
5. ✅ TODAY'S SINGLE ACTION - ONE most important thing to do today"""
        }]
    )
    return jsonify({"advice": response.choices[0].message.content})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    history = data.get('history', [])
    farm_context = data.get('farmContext', '')
    language = data.get('language', 'english')

    lang_line = f"CRITICAL: Respond entirely in {language} language only." if language != 'english' else ""

    system = f"""You are a knowledgeable friendly farming assistant for Indian farmers. {lang_line}
{f"Farmer context: {farm_context}" if farm_context else ""}

Help with pests, diseases, fertilizers, irrigation, harvest, markets.

For pests/insects:
1. Identify pest from description
2. If SMALL infestation: give DESI NUSKHA first (neem oil, garlic-chili spray, ash)
3. Give chemical option with exact product and quantity
4. Prevention tips

Desi nuskhe: neem oil spray, garlic-chili paste, wood ash, buttermilk spray, turmeric water.
Always give practical advice with locally available materials."""

    messages = [{"role": "system", "content": system}]
    for h in history[-8:]:
        messages.append(h)

    response = client.chat.completions.create(
        model="asi1", max_tokens=450, messages=messages
    )
    return jsonify({"reply": response.choices[0].message.content})


@app.route('/financial', methods=['POST'])
def financial():
    data = request.json
    state = data.get('state', 'Maharashtra')
    land = data.get('land', '2 acres')
    need = data.get('need', 'all schemes')
    language = data.get('language', 'english')

    lang_line = f"CRITICAL: Respond ENTIRELY in {language} language only." if language != 'english' else ""

    response = client.chat.completions.create(
        model="asi1",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": f"""You are a government scheme expert for Indian farmers. {lang_line}

Farmer: {state} state, {land} land, needs: {need}

Provide:
1. ELIGIBLE SCHEMES - central + {state} state schemes with exact benefit amounts
2. HOW TO APPLY - documents needed, where to apply, step by step
3. LOAN OPTIONS - best low-interest loans, interest rate, which bank
4. SUBSIDY AVAILABLE - seeds, fertilizer, equipment for {state}
5. IMMEDIATE ACTION - what to do THIS WEEK

Be specific with amounts, websites, phone numbers."""
        }]
    )
    return jsonify({"advice": response.choices[0].message.content})


@app.route('/legal', methods=['POST'])
def legal():
    data = request.json
    state = data.get('state', 'Maharashtra')
    issue = data.get('issue', 'MSP rights')
    language = data.get('language', 'english')

    lang_line = f"CRITICAL: Respond ENTIRELY in {language} language only." if language != 'english' else ""

    response = client.chat.completions.create(
        model="asi1",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": f"""You are a legal rights expert for Indian farmers. {lang_line}

Farmer from: {state}
Issue: {issue}

Provide:
1. YOUR RIGHTS - exact legal rights, law name and section
2. WHAT YOU CAN DO - step by step actions, which office to approach
3. HOW TO FILE COMPLAINT - exact office, online portal if available
4. FREE LEGAL HELP - DLSA, farmer helplines for {state}, NGOs
5. WARNINGS - scams to avoid, things not to sign

Use simple language for rural farmer."""
        }]
    )
    return jsonify({"advice": response.choices[0].message.content})


if __name__ == '__main__':
    print("🌾 CropAdvisor AI is running!")
    print("👉 Open browser: http://localhost:5000")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
