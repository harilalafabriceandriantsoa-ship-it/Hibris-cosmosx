import streamlit as st        
import hashlib        
import statistics        
import random        
import numpy as np        
from datetime import datetime, timedelta    
from streamlit_autorefresh import st_autorefresh    

# ---------------- CONFIG ----------------    
st.set_page_config(page_title="COSMOS X ANDR ⚡", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top,#0d0d0d,#000000);
    color:#00ffcc;
    font-family: monospace;
}
h1,h2,h3 {
    text-align:center;
    color:#00ffcc;
}
.block {
    background:#111;
    padding:15px;
    border-radius:12px;
    border:1px solid #00ffcc55;
    margin-bottom:10px;
}
.result {
    font-size:18px;
    padding:10px;
    border-left:4px solid #00ffcc;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------    
if "login" not in st.session_state:
    st.session_state.login = False

if "history" not in st.session_state:
    st.session_state.history = []

if "balance" not in st.session_state:
    st.session_state.balance = 1000

# ---------------- LOGIN ----------------    
if not st.session_state.login:
    st.title("🔐 COSMOS X ANDR ACCESS")
    pwd = st.text_input("Password", type="password")

    if st.button("ENTER SYSTEM"):
        if pwd == "2026":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

# ---------------- CORE HASH512 ----------------    
def hash512(server, client):
    return hashlib.sha512(f"{server}:{client}".encode()).hexdigest()

# ---------------- SIMULATION ENGINE ----------------    
def crash(server, client):
    h = hash512(server, client)
    dec = int(h[-8:], 16) or 1
    return round((4294967295 * 0.97) / dec, 2)

# ---------------- COTE FILTER ----------------    
def cote_filter(avg, acc):
    if acc > 90 and avg > 3:
        return 3.0
    elif acc > 80:
        return 2.5
    elif acc > 70:
        return 2.0
    elif acc > 60:
        return 1.8
    return 1.5

# ---------------- HEURE D’ENTRÉE ULTRA ----------------    
def entry_time(server, client, cote, confidence):

    h = hash512(server, client)
    now = datetime.now()

    seconds = now.hour*3600 + now.minute*60 + now.second

    seed = (
        int(h[:16],16) +
        int(h[16:32],16) +
        seconds +
        int(cote*100) +
        confidence
    )

    # 🔥 ULTRA DYNAMIC WINDOW (NOT FIXED)
    base = 15 + (seed % 45)
    micro = (int(h[-6:],16) % 10)

    delay = base + micro

    return (now + timedelta(seconds=delay)).strftime("%H:%M:%S")

# ---------------- ENGINE CORE ----------------    
def analyse(server, client):

    series = [crash(server, client) for _ in range(20)]

    mn = round(min(series),2)
    avg = round(statistics.mean(series),2)
    mx = round(max(series),2)

    acc = int(sum(1 for x in series if x >= 2) / len(series) * 100)

    cote = cote_filter(avg, acc)

    confidence = int((acc * 0.6) + (avg * 20 * 0.4))

    # 🎯 SIGNAL ENGINE
    if acc >= 85 and avg > 2:
        signal = "🟢 X3+ READY"
    elif acc >= 65:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    entry = entry_time(server, client, cote, confidence)

    return {
        "min": mn,
        "avg": avg,
        "max": mx,
        "acc": acc,
        "cote": cote,
        "confidence": confidence,
        "signal": signal,
        "entry": entry
    }

# ---------------- UI ----------------    
st.title("🌌 COSMOS X ANDR ⚡ ULTRA SYSTEM")

server = st.text_input("Server Seed")
client = st.text_input("Client Seed")

if st.button("🚀 SCAN COSMOS"):

    res = analyse(server, client)

    st.session_state.history.append(res)

    # 🎯 RESULT UI ULTRA STYLÉ
    st.markdown(f"""
<div class="block">
    <h2>⏰ ENTRY TIME: {res['entry']}</h2>
    <div class="result">🎯 SIGNAL: {res['signal']}</div>
    <div class="result">📊 ACCURACY: {res['acc']}%</div>
    <div class="result">💎 COTE: x{res['cote']}</div>
    <div class="result">🧠 CONFIDENCE: {res['confidence']}</div>
    <div class="result">📉 MIN: {res['min']} | 📊 AVG: {res['avg']} | 🚀 MAX: {res['max']}</div>
</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------    
st.subheader("📜 HISTORY")
for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | 🎯 {h['signal']} | 📊 {h['acc']}% | x{h['cote']}")

# ---------------- AUTO REFRESH ----------------    
st_autorefresh(interval=10000, limit=None)
