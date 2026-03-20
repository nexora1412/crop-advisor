from flask import Flask, request, jsonify, render_template_string
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

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CropAdvisor AI - किसान का डिजिटल साथी</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial; background: #f0f7f0; min-height: 100vh; }

        .header {
            background: linear-gradient(135deg, #1b4332, #2d6a4f);
            color: white;
            padding: 20px 40px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        .header h1 { font-size: 24px; }
        .header p { font-size: 12px; opacity: 0.85; margin-top: 4px; }

        .tabs {
            display: flex;
            background: #1b4332;
            padding: 0 40px;
            gap: 5px;
        }
        .tab {
            padding: 12px 20px;
            color: #95d5b2;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.2s;
        }
        .tab:hover { color: white; }
        .tab.active { color: white; border-bottom: 3px solid #95d5b2; }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .container { max-width: 1200px; margin: 25px auto; padding: 0 20px; }

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
        .full-width { grid-column: 1 / -1; }

        .card {
            background: white;
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        }
        .card h2 { color: #2d6a4f; margin-bottom: 15px; font-size: 17px; border-bottom: 2px solid #e8f5e9; padding-bottom: 10px; }

        label { font-weight: bold; color: #444; font-size: 13px; display: block; margin: 10px 0 4px; }
        input, select, textarea {
            width: 100%; padding: 9px 12px;
            border: 1px solid #ddd; border-radius: 6px;
            font-size: 14px; font-family: Arial;
        }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #2d6a4f; }

        .btn {
            background: #2d6a4f; color: white;
            padding: 11px; border: none; border-radius: 8px;
            cursor: pointer; font-size: 14px; width: 100%;
            margin-top: 14px; font-weight: bold; transition: background 0.2s;
        }
        .btn:hover { background: #1b4332; }
        .btn:disabled { background: #95d5b2; cursor: not-allowed; }
        .btn-outline {
            background: white; color: #2d6a4f;
            border: 2px solid #2d6a4f;
            padding: 9px; border-radius: 8px;
            cursor: pointer; font-size: 13px;
            margin: 4px; font-weight: bold;
            transition: all 0.2s;
        }
        .btn-outline:hover { background: #2d6a4f; color: white; }

        .result-box {
            background: #f8fdf8; border: 1px solid #95d5b2;
            border-radius: 8px; padding: 16px; margin-top: 15px;
            white-space: pre-wrap; font-size: 13.5px; line-height: 1.8;
            max-height: 500px; overflow-y: auto; display: none;
        }

        .loading {
            text-align: center; color: #2d6a4f;
            padding: 20px; display: none; font-size: 14px;
        }
        .spinner { font-size: 28px; animation: spin 1s linear infinite; display: inline-block; }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        /* CHAT */
        .chat-messages {
            height: 380px; overflow-y: auto;
            border: 1px solid #ddd; border-radius: 8px;
            padding: 15px; background: #fafafa; margin-bottom: 10px;
        }
        .msg { margin-bottom: 14px; overflow: hidden; }
        .msg.user .bubble {
            background: #2d6a4f; color: white;
            border-radius: 12px 12px 0 12px;
            padding: 10px 14px; display: inline-block;
            max-width: 80%; float: right; clear: both; font-size: 13px;
        }
        .msg.bot .bubble {
            background: #e8f5e9; color: #1b3a2a;
            border-radius: 12px 12px 12px 0;
            padding: 10px 14px; display: inline-block;
            max-width: 85%; float: left; clear: both;
            white-space: pre-wrap; font-size: 13px; line-height: 1.6;
        }
        .msg-name { font-size: 11px; color: #888; margin-bottom: 3px; }
        .user .msg-name { text-align: right; }
        .clearfix { clear: both; }

        .chat-row { display: flex; gap: 8px; margin-top: 10px; }
        .chat-row input { flex: 1; }
        .chat-send {
            background: #2d6a4f; color: white;
            border: none; padding: 10px 18px;
            border-radius: 6px; cursor: pointer; font-size: 14px;
        }
        .chat-send:hover { background: #1b4332; }

        .quick-btns { margin: 10px 0; }
        .quick-btns p { font-size: 12px; color: #888; margin-bottom: 6px; }
        .qq { 
            background: #e8f5e9; border: 1px solid #95d5b2;
            color: #2d6a4f; padding: 5px 11px; border-radius: 20px;
            cursor: pointer; font-size: 12px; margin: 3px;
            display: inline-block; transition: all 0.2s;
        }
        .qq:hover { background: #2d6a4f; color: white; }

        /* SCHEME CARDS */
        .scheme-card {
            background: #f8fdf8; border: 1px solid #95d5b2;
            border-radius: 10px; padding: 15px; margin-bottom: 12px;
        }
        .scheme-card h3 { color: #2d6a4f; font-size: 15px; margin-bottom: 6px; }
        .scheme-card p { font-size: 13px; color: #444; line-height: 1.6; }
        .badge {
            display: inline-block; padding: 3px 10px;
            border-radius: 20px; font-size: 11px; font-weight: bold;
            margin-bottom: 8px;
        }
        .badge-green { background: #d8f3dc; color: #1b4332; }
        .badge-blue { background: #dbeafe; color: #1e40af; }
        .badge-orange { background: #fef3c7; color: #92400e; }

        .stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
        .stat { background: #e8f5e9; border-radius: 10px; padding: 15px; text-align: center; }
        .stat .num { font-size: 22px; font-weight: bold; color: #2d6a4f; }
        .stat .lbl { font-size: 12px; color: #666; margin-top: 4px; }

        @media (max-width: 768px) {
            .grid-2, .grid-3 { grid-template-columns: 1fr; }
            .full-width { grid-column: 1; }
            .tabs { padding: 0 10px; overflow-x: auto; }
            .tab { font-size: 12px; padding: 10px 12px; white-space: nowrap; }
        }
    </style>
</head>
<body>

<div class="header">
    <div style="font-size:40px">🌾</div>
    <div>
        <h1>CropAdvisor AI — किसान का डिजिटल साथी</h1>
        <p>Real-time Farming • Personal Assistant • Government Schemes • Legal Rights • Powered by ASI:One AI</p>
    </div>
</div>

<div class="tabs">
    <div class="tab active" onclick="showTab('farm')">🌱 Farm Analysis</div>
    <div class="tab" onclick="showTab('assistant')">🤖 Personal Assistant</div>
    <div class="tab" onclick="showTab('finance')">💰 Financial Help</div>
    <div class="tab" onclick="showTab('legal')">⚖️ Legal Rights</div>
</div>

<!-- ═══════════════════════════════ TAB 1: FARM ANALYSIS ═══════════════════════════════ -->
<div id="tab-farm" class="tab-content active">
<div class="container">
<div class="grid-2">
    <div class="card">
        <h2>🌱 Farm Details</h2>

        <label>Language / भाषा</label>
        <select id="language" onchange="updateLangBadge()">
            <option value="english">English</option>
            <option value="hindi">Hindi (हिंदी)</option>
            <option value="marathi">Marathi (मराठी)</option>
            <option value="tamil">Tamil (தமிழ்)</option>
            <option value="telugu">Telugu (తెలుగు)</option>
            <option value="kannada">Kannada (ಕನ್ನಡ)</option>
            <option value="punjabi">Punjabi (ਪੰਜਾਬੀ)</option>
            <option value="gujarati">Gujarati (ગુજરાતી)</option>
            <option value="bengali">Bengali (বাংলা)</option>
        </select>

        <label>Crop / फसल</label>
        <input type="text" id="crop" placeholder="wheat, rice, cotton, sugarcane..." />

        <label>Region / State</label>
        <input type="text" id="region" placeholder="Vidarbha Maharashtra, Punjab..." />

        <label>Nearest City</label>
        <input type="text" id="city" placeholder="Nagpur, Amritsar, Pune..." />

        <label>Soil Type / मिट्टी</label>
        <select id="soil">
            <option value="black soil (Regur)">Black Soil - काली मिट्टी</option>
            <option value="red soil">Red Soil - लाल मिट्टी</option>
            <option value="alluvial soil">Alluvial Soil - जलोढ़ मिट्टी</option>
            <option value="sandy soil">Sandy Soil - रेतीली मिट्टी</option>
            <option value="clay soil">Clay Soil - चिकनी मिट्टी</option>
            <option value="laterite soil">Laterite Soil</option>
        </select>

        <label>Farm Size</label>
        <select id="farmsize">
            <option value="1 acre">1 Acre</option>
            <option value="2 acres">2 Acres</option>
            <option value="5 acres">5 Acres</option>
            <option value="10 acres">10 Acres</option>
            <option value="20+ acres">20+ Acres</option>
        </select>

        <button class="btn" onclick="getAdvice()" id="analyzeBtn">🔍 Get Farming Advice</button>

        <div class="loading" id="loading">
            <div class="spinner">🌀</div>
            <p style="margin-top:10px">Fetching live weather, soil & market data...<br>Analyzing with ASI:One AI...</p>
        </div>
    </div>

    <div class="card">
        <h2>📊 Live Analysis Result</h2>
        <div id="result" class="result-box" style="display:none; max-height:600px"></div>
        <div id="placeholder" style="color:#aaa; text-align:center; padding:40px 0; font-size:14px">
            <div style="font-size:50px">🌾</div>
            <p style="margin-top:10px">Fill in your farm details and click<br><b>Get Farming Advice</b></p>
        </div>
    </div>
</div>
</div>
</div>

<!-- ═══════════════════════════════ TAB 2: PERSONAL ASSISTANT ═══════════════════════════════ -->
<div id="tab-assistant" class="tab-content">
<div class="container">
<div class="grid-2">
    <div class="card">
        <h2>🤖 Personal Farm Assistant <span id="langBadge" style="font-size:12px;background:#e8f5e9;color:#2d6a4f;padding:3px 10px;border-radius:20px;margin-left:8px">🌐 English</span></h2>

        <div class="chat-messages" id="chatMessages">
            <div class="msg bot">
                <div class="msg-name">🌾 CropAdvisor AI</div>
                <div class="bubble">Namaste! 🙏 I am your personal farming assistant.

Ask me ANYTHING about your farm:
🐛 Insects & pests
🍂 Diseases & yellow leaves  
💧 Irrigation problems
🌿 Desi nuskhe (organic remedies)
🌾 Harvest timing
💰 Mandi prices & selling tips

I will answer in your chosen language!</div>
                <div class="clearfix"></div>
            </div>
        </div>

        <div class="quick-btns">
            <p>Quick questions:</p>
            <span class="qq" onclick="quickAsk('There are insects on my wheat field. They are in small numbers. What should I do? Give me both chemical and desi nuskha solution.')">🐛 Insects on field</span>
            <span class="qq" onclick="quickAsk('My crop leaves are turning yellow. What is the problem and how to fix it?')">🍂 Yellow leaves</span>
            <span class="qq" onclick="quickAsk('When should I irrigate my crop? What is the best time and how much water?')">💧 Irrigation help</span>
            <span class="qq" onclick="quickAsk('Give me best desi nuskha for pest control that I can make at home from kitchen items')">🌿 Desi nuskha</span>
            <span class="qq" onclick="quickAsk('There is fungal disease on my crop. White powder on leaves. What to do?')">🍄 Fungal disease</span>
            <span class="qq" onclick="quickAsk('What is the best time to harvest and how do I know my crop is ready?')">🌾 Harvest time</span>
            <span class="qq" onclick="quickAsk('Rats are destroying my field at night. How to get rid of them without poison?')">🐀 Rats in field</span>
            <span class="qq" onclick="quickAsk('My soil is looking dry and cracked. What should I do before sowing?')">🌍 Dry soil</span>
        </div>

        <div class="chat-row">
            <input type="text" id="chatInput" placeholder="Type your farming question..." onkeypress="if(event.key==='Enter') sendChat()" />
            <button class="chat-send" onclick="sendChat()">Send ➤</button>
        </div>
    </div>

    <div class="card">
        <h2>📋 Common Problems Guide</h2>
        <div style="font-size:13px; line-height:1.9; color:#333">

            <div style="background:#fff8e1;border-left:4px solid #f59e0b;padding:12px;border-radius:6px;margin-bottom:12px">
                <b>🐛 Few insects on field?</b><br>
                • Desi nuskha: Spray neem oil (5ml) + soap (2ml) in 1L water<br>
                • Also try: Garlic + chili paste diluted in water<br>
                • Chemical: Use only if infestation spreads to 30%+ plants
            </div>

            <div style="background:#fef2f2;border-left:4px solid #ef4444;padding:12px;border-radius:6px;margin-bottom:12px">
                <b>🍂 Yellow leaves?</b><br>
                • Nitrogen deficiency → Apply Urea 10kg/acre<br>
                • Waterlogging → Improve drainage immediately<br>
                • Fungal → Spray Mancozeb 2g/L water
            </div>

            <div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:12px;border-radius:6px;margin-bottom:12px">
                <b>💧 Irrigation timing?</b><br>
                • Best time: Early morning (6-8 AM) or evening (5-7 PM)<br>
                • Never irrigate during peak heat (11AM-3PM)<br>
                • Check soil: Insert finger 2 inches — if dry, irrigate
            </div>

            <div style="background:#eff6ff;border-left:4px solid #3b82f6;padding:12px;border-radius:6px">
                <b>🌿 Universal Desi Pest Spray</b><br>
                • 250g neem leaves + boil in 5L water<br>
                • Cool, strain, add 10ml soap liquid<br>
                • Spray on leaves morning or evening<br>
                • Repeat every 7 days — works for most insects!
            </div>
        </div>
    </div>
</div>
</div>
</div>

<!-- ═══════════════════════════════ TAB 3: FINANCIAL HELP ═══════════════════════════════ -->
<div id="tab-finance" class="tab-content">
<div class="container">

    <div class="stat-row">
        <div class="stat"><div class="num">₹6,000</div><div class="lbl">PM-KISAN annual benefit</div></div>
        <div class="stat"><div class="num">4%</div><div class="lbl">KCC loan interest rate</div></div>
        <div class="stat"><div class="num">85%</div><div class="lbl">Crop insurance subsidy</div></div>
    </div>

    <div class="grid-2">
        <div class="card">
            <h2>🏦 Get Personalized Financial Advice</h2>

            <label>Your State / राज्य</label>
            <input type="text" id="finState" placeholder="Maharashtra, Punjab, UP..." />

            <label>Land Size</label>
            <select id="finLand">
                <option value="less than 1 acre (marginal farmer)">Less than 1 acre (Marginal)</option>
                <option value="1-2 acres (small farmer)">1-2 acres (Small)</option>
                <option value="2-5 acres (medium farmer)">2-5 acres (Medium)</option>
                <option value="5+ acres (large farmer)">5+ acres (Large)</option>
            </select>

            <label>What do you need help with?</label>
            <select id="finNeed">
                <option value="crop loan at low interest">Low Interest Crop Loan</option>
                <option value="government subsidy for seeds and fertilizer">Seeds & Fertilizer Subsidy</option>
                <option value="crop insurance">Crop Insurance</option>
                <option value="equipment subsidy for tractor or pump">Equipment Subsidy</option>
                <option value="all available government schemes">All Available Schemes</option>
                <option value="emergency financial help after crop loss">Emergency Help After Crop Loss</option>
            </select>

            <label>Language / भाषा</label>
            <select id="finLang">
                <option value="english">English</option>
                <option value="hindi">Hindi (हिंदी)</option>
                <option value="marathi">Marathi (मराठी)</option>
                <option value="tamil">Tamil</option>
                <option value="telugu">Telugu</option>
            </select>

            <button class="btn" onclick="getFinancialAdvice()" id="finBtn">💰 Get Financial Guidance</button>
            <div class="loading" id="finLoading"><div class="spinner">🌀</div><p style="margin-top:8px">Finding best schemes for you...</p></div>
            <div class="result-box" id="finResult"></div>
        </div>

        <div class="card">
            <h2>📋 Key Government Schemes</h2>

            <div class="scheme-card">
                <span class="badge badge-green">✅ All Farmers</span>
                <h3>PM-KISAN Samman Nidhi</h3>
                <p>₹6,000/year directly in your bank account in 3 installments. Register at pmkisan.gov.in with Aadhaar + land records.</p>
            </div>

            <div class="scheme-card">
                <span class="badge badge-blue">🏦 Loan</span>
                <h3>Kisan Credit Card (KCC)</h3>
                <p>Crop loans up to ₹3 lakh at only 4% interest (7% - 3% govt subsidy). Apply at any bank with land documents + Aadhaar.</p>
            </div>

            <div class="scheme-card">
                <span class="badge badge-orange">🛡️ Insurance</span>
                <h3>PM Fasal Bima Yojana</h3>
                <p>Crop insurance with only 1.5-2% premium (govt pays 85%+). Covers drought, flood, pest damage. Apply through bank or CSC center.</p>
            </div>

            <div class="scheme-card">
                <span class="badge badge-green">⚙️ Equipment</span>
                <h3>PM Kisan Mandhan Yojana</h3>
                <p>Pension scheme for farmers — ₹55/month contribution gives ₹3,000/month pension after age 60. Register at CSC center.</p>
            </div>
        </div>
    </div>
</div>
</div>

<!-- ═══════════════════════════════ TAB 4: LEGAL RIGHTS ═══════════════════════════════ -->
<div id="tab-legal" class="tab-content">
<div class="container">
<div class="grid-2">
    <div class="card">
        <h2>⚖️ Know Your Legal Rights</h2>

        <label>Your State</label>
        <input type="text" id="legalState" placeholder="Maharashtra, Punjab..." />

        <label>What legal issue do you face?</label>
        <select id="legalIssue">
            <option value="MSP - Minimum Support Price rights">MSP Rights (Minimum Price)</option>
            <option value="land rights and protection from illegal acquisition">Land Rights Protection</option>
            <option value="mandi and APMC rules - where I can sell my crop">Where Can I Sell My Crop</option>
            <option value="crop loan waiver eligibility">Loan Waiver Eligibility</option>
            <option value="rights when crop is damaged by someone">Crop Damage by Others</option>
            <option value="water rights and irrigation disputes">Water & Irrigation Rights</option>
            <option value="tenant farmer rights if I farm someone else land">Tenant Farmer Rights</option>
            <option value="how to file complaint against corrupt officials">File Complaint Against Officials</option>
        </select>

        <label>Language / भाषा</label>
        <select id="legalLang">
            <option value="english">English</option>
            <option value="hindi">Hindi (हिंदी)</option>
            <option value="marathi">Marathi (मराठी)</option>
            <option value="tamil">Tamil</option>
            <option value="telugu">Telugu</option>
        </select>

        <button class="btn" onclick="getLegalAdvice()" id="legalBtn">⚖️ Get Legal Guidance</button>
        <div class="loading" id="legalLoading"><div class="spinner">🌀</div><p style="margin-top:8px">Researching your legal rights...</p></div>
        <div class="result-box" id="legalResult"></div>
    </div>

    <div class="card">
        <h2>📜 Important Farmer Laws</h2>

        <div class="scheme-card">
            <span class="badge badge-green">💰 Price Protection</span>
            <h3>MSP - Minimum Support Price</h3>
            <p>Government must buy your crop at MSP price. If trader pays less, you can complain to District Collector. Current wheat MSP: ₹2,275/quintal (2024-25).</p>
        </div>

        <div class="scheme-card">
            <span class="badge badge-blue">🏡 Land Rights</span>
            <h3>Land Acquisition Act 2013</h3>
            <p>No one can take your farm land without proper notice and 4x market rate compensation. You can challenge illegal acquisition in court. Free legal aid available.</p>
        </div>

        <div class="scheme-card">
            <span class="badge badge-orange">🛒 Selling Rights</span>
            <h3>Freedom to Sell</h3>
            <p>You can sell your produce directly to any buyer, company, or online platform. You are NOT forced to sell only at APMC mandi. Get best price.</p>
        </div>

        <div class="scheme-card">
            <span class="badge badge-green">📞 Helplines</span>
            <h3>Important Contacts</h3>
            <p>
            • Kisan Call Center: <b>1800-180-1551</b> (Free, 24/7)<br>
            • PM-KISAN Helpline: <b>155261</b><br>
            • Soil Health: <b>1800-180-1551</b><br>
            • Crop Insurance: <b>1800-200-7710</b>
            </p>
        </div>
    </div>
</div>
</div>
</div>

<script>
let farmContext = "";
let chatHistory = [];

function showTab(name) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    event.target.classList.add('active');
}

function updateLangBadge() {
    const labels = {
        english:'English', hindi:'Hindi (हिंदी)', marathi:'Marathi (मराठी)',
        tamil:'Tamil', telugu:'Telugu', kannada:'Kannada',
        punjabi:'Punjabi', gujarati:'Gujarati', bengali:'Bengali'
    };
    const val = document.getElementById('language').value;
    document.getElementById('langBadge').innerText = '🌐 ' + labels[val];
}

async function getAdvice() {
    const crop = document.getElementById('crop').value;
    const region = document.getElementById('region').value;
    const city = document.getElementById('city').value;
    const soil = document.getElementById('soil').value;
    const farmsize = document.getElementById('farmsize').value;
    const language = document.getElementById('language').value;
    if (!crop || !region || !city) { alert('Please fill Crop, Region and City!'); return; }

    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    document.getElementById('placeholder').style.display = 'none';

    const res = await fetch('/analyze', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ crop, region, city, soil, farmsize, language })
    });
    const data = await res.json();
    document.getElementById('loading').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('result').style.display = 'block';
    document.getElementById('result').innerText = data.advice;
    farmContext = `Farmer grows ${crop} in ${region} (${city}), ${soil}, ${farmsize}`;
}

function quickAsk(q) {
    document.getElementById('chatInput').value = q;
    sendChat();
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    const language = document.getElementById('language').value;
    if (!msg) return;
    input.value = '';
    addMessage('user', msg, 'You');
    chatHistory.push({ role: 'user', content: msg });
    const tid = 'typing_' + Date.now();
    addTyping(tid);
    const res = await fetch('/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: chatHistory, farmContext, language })
    });
    const data = await res.json();
    removeTyping(tid);
    addMessage('bot', data.reply, '🌾 CropAdvisor AI');
    chatHistory.push({ role: 'assistant', content: data.reply });
}

function addMessage(role, text, name) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.innerHTML = `<div class="msg-name">${name}</div><div class="bubble">${text}</div><div class="clearfix"></div>`;
    const c = document.getElementById('chatMessages');
    c.appendChild(div); c.scrollTop = c.scrollHeight;
}
function addTyping(id) {
    const div = document.createElement('div');
    div.className = 'msg bot'; div.id = id;
    div.innerHTML = '<div class="bubble">⏳ Thinking...</div><div class="clearfix"></div>';
    const c = document.getElementById('chatMessages');
    c.appendChild(div); c.scrollTop = c.scrollHeight;
}
function removeTyping(id) { const el = document.getElementById(id); if(el) el.remove(); }

async function getFinancialAdvice() {
    const state = document.getElementById('finState').value;
    const land = document.getElementById('finLand').value;
    const need = document.getElementById('finNeed').value;
    const language = document.getElementById('finLang').value;
    if (!state) { alert('Please enter your state!'); return; }
    document.getElementById('finBtn').disabled = true;
    document.getElementById('finLoading').style.display = 'block';
    document.getElementById('finResult').style.display = 'none';
    const res = await fetch('/financial', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state, land, need, language })
    });
    const data = await res.json();
    document.getElementById('finLoading').style.display = 'none';
    document.getElementById('finBtn').disabled = false;
    document.getElementById('finResult').style.display = 'block';
    document.getElementById('finResult').innerText = data.advice;
}

async function getLegalAdvice() {
    const state = document.getElementById('legalState').value;
    const issue = document.getElementById('legalIssue').value;
    const language = document.getElementById('legalLang').value;
    if (!state) { alert('Please enter your state!'); return; }
    document.getElementById('legalBtn').disabled = true;
    document.getElementById('legalLoading').style.display = 'block';
    document.getElementById('legalResult').style.display = 'none';
    const res = await fetch('/legal', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state, issue, language })
    });
    const data = await res.json();
    document.getElementById('legalLoading').style.display = 'none';
    document.getElementById('legalBtn').disabled = false;
    document.getElementById('legalResult').style.display = 'block';
    document.getElementById('legalResult').innerText = data.advice;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

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

    lang_line = f"CRITICAL: Respond ENTIRELY in {language} language only. Every word must be in {language}." if language != 'english' else ""

    response = client.chat.completions.create(
        model="asi1",
        max_tokens=750,
        messages=[{
            "role": "user",
            "content": f"""You are an expert agricultural advisor for Indian farmers. {lang_line}

FARM DETAILS (give advice SPECIFIC to these exact details - DO NOT give generic advice):
- Crop: {crop}
- Region: {region} — tailor advice to THIS region's specific climate, rainfall pattern, and local farming practices
- City: {city}
- Soil: {soil} — address THIS soil's specific properties (water retention, nutrients, problems)
- Farm Size: {farmsize} — calculate ALL quantities for THIS exact farm size

LIVE REAL-TIME DATA RIGHT NOW:
- Temperature in {city}: {weather['temperature']}°C
- Humidity: {weather['humidity']}%
- Rainfall today: {weather['rainfall_mm']}mm
- Sky condition: {weather['condition']}
- Soil moisture: {soil_data['soil_moisture']}
- Market price of {crop}: {market['current_price']} (Trend: {market['trend']})
- Best selling month: {market['best_sell_month']}

Based on THIS SPECIFIC combination of crop+region+soil+weather, provide:

1. 🌱 FERTILIZER SCHEDULE
   - Calculate exact kg needed for {farmsize} total
   - Name specific fertilizers available in {region} markets
   - Exact timing based on {weather['temperature']}°C current temperature

2. 💧 IRRIGATION ADVICE
   - Based on {weather['humidity']}% humidity and {weather['rainfall_mm']}mm rain today
   - How {soil} specifically retains or drains water
   - Next irrigation: when and how much

3. 💰 BEST SELLING WINDOW
   - Price trend is {market['trend']} — should farmer sell now or wait?
   - Specific mandis in {region} that give best price for {crop}

4. ⚠️ RISK ALERTS
   - Pests/diseases SPECIFIC to {region} at {weather['temperature']}°C and {weather['humidity']}% humidity
   - What to watch for in next 7 days

5. ✅ TODAY'S SINGLE ACTION
   - Based on all live data, ONE most important thing to do TODAY"""
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

    lang_line = f"CRITICAL: You MUST respond entirely in {language} language only." if language != 'english' else ""

    system = f"""You are a knowledgeable, friendly personal farming assistant for Indian farmers. {lang_line}

{f"Farmer context: {farm_context}" if farm_context else ""}

You help with ALL farming problems:
- Pest & insect identification and treatment
- Plant disease diagnosis  
- Fertilizer and nutrition advice
- Irrigation guidance
- Harvest timing
- Market and mandi advice
- Organic/desi remedies

PEST/INSECT RESPONSE FORMAT:
1. Identify the pest from description
2. Assess severity (small/large infestation)
3. If SMALL infestation → give DESI NUSKHA first (home remedy with kitchen items)
4. Also give chemical option with exact product name and quantity
5. Prevention for future

DESI NUSKHE you know:
- Neem oil spray (5ml + 2ml soap in 1L water)
- Garlic-chili spray (crush 10 garlic + 5 chilies, boil, strain, dilute 1:10)
- Wood ash on soil for ants/crawling insects
- Buttermilk spray for fungal issues
- Turmeric water for soil treatment

Always be practical, specific, and give advice a rural farmer can implement TODAY with locally available materials."""

    messages = [{"role": "system", "content": system}]
    for h in history[-8:]:
        messages.append(h)

    response = client.chat.completions.create(
        model="asi1",
        max_tokens=450,
        messages=messages
    )
    return jsonify({"reply": response.choices[0].message.content})


@app.route('/financial', methods=['POST'])
def financial():
    data = request.json
    state = data.get('state', 'Maharashtra')
    land = data.get('land', '2 acres')
    need = data.get('need', 'all available government schemes')
    language = data.get('language', 'english')

    lang_line = f"CRITICAL: Respond ENTIRELY in {language} language only." if language != 'english' else ""

    response = client.chat.completions.create(
        model="asi1",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": f"""You are a government scheme expert for Indian farmers. {lang_line}

Farmer Details:
- State: {state}
- Land: {land}
- Need: {need}

Give SPECIFIC and ACTIONABLE financial guidance:

1. ELIGIBLE SCHEMES
   - List all central + {state} state schemes this farmer qualifies for
   - Exact benefit amount in rupees
   - Eligibility criteria they meet

2. HOW TO APPLY
   - Exact documents needed (Aadhaar, land records, bank passbook etc.)
   - Where to apply (which office, website, or app)
   - Step by step process

3. LOAN OPTIONS
   - Best low-interest loan schemes for {land} farmer in {state}
   - Interest rate, loan amount, repayment period
   - Which bank or institution to approach

4. SUBSIDY AVAILABLE
   - Seeds, fertilizer, equipment subsidy specific to {state}
   - How to claim it

5. IMMEDIATE ACTION
   - What to do THIS WEEK to start getting benefits
   - Most important scheme to apply for first

Be specific with amounts, websites, phone numbers, and office names."""
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
            "content": f"""You are a legal rights expert specifically for Indian farmers. {lang_line}

Farmer is from: {state}
Legal issue: {issue}

Provide clear, practical legal guidance:

1. YOUR RIGHTS
   - Exact legal rights in this situation under Indian law
   - Specific law name and section number
   - What {state} state law says additionally

2. WHAT YOU CAN DO
   - Step by step actions to protect your rights
   - Which authority/office to approach first
   - Documents to keep ready

3. HOW TO FILE COMPLAINT (if needed)
   - Exact office name and address type
   - Online portal if available
   - What to write in complaint

4. FREE LEGAL HELP
   - District Legal Services Authority (DLSA) — free lawyer
   - Farmer helpline numbers specific to {state}
   - NGOs that help farmers with legal issues

5. IMPORTANT WARNINGS
   - Common traps/scams to avoid
   - Things NOT to sign without reading
   - Your rights if someone tries to cheat you

Use simple language. This farmer may not be educated in legal terms."""
        }]
    )
    return jsonify({"advice": response.choices[0].message.content})


if __name__ == '__main__':
    print("🌾 CropAdvisor AI is running!")
    print("👉 Open browser: http://localhost:5000")
    app.run(debug=True, port=5000)
