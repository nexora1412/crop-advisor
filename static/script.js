let farmContext = "";
let chatHistory = [];

function showTab(name, el) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    el.classList.add('active');
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

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

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