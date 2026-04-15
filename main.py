import streamlit as st
import hashlib
import numpy as np
import statistics
import random
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS X ANDR ⚡ ULTRA ENTRY", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle,#0a0a0a,#000);
    color:#00ffcc;
    font-family: monospace;
}
h1,h2,h3 {text-align:center;}
.box {
    padding:15px;
    border:1px solid #00ffcc;
    border-radius:12px;
    margin:10px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- TIME MADAGASCAR ----------------
def get_time():
    tz = pytz.timezone("Indian/Antananarivo")
    return datetime.now(tz)

# ---------------- HASH512 ONLY ----------------
def hash512():
    now = get_time().strftime("%Y-%m-%d %H:%M:%S")
    return hashlib.sha512(now.encode()).hexdigest()

# ---------------- CORE SIMULATION ----------------
def simulate():

    h = hash512()

    # TIME FACTOR
    t = get_time()
    seconds = t.hour*3600 + t.minute*60 + t.second

    hash_int = int(h[:16],16)
    time_factor = seconds % 500

    # COTE FILTER BASE
    base = (hash_int % 1000) / 100 + 1.2
    cycle = 1 + (time_factor / 500)

    # FINAL ENGINE
    values = np.random.lognormal(
        mean=np.log(base * cycle),
        sigma=0.35,
        size=12000
    )

    success = [x for x in values if x >= 3]

    prob = round(len(success)/len(values)*100,2)

    # MIN / MOYEN / MAX
    logv = np.log(values + 1)

    mn = round(np.exp(np.min(logv)) / 1.3, 2)
    avg = round(np.exp(np.mean(logv)) / 1.2, 2)
    mx = round(np.exp(np.percentile(logv, 95)), 2)

    # CONFIDENCE IA
    confidence = round((prob * avg) / 10, 2)

    # ---------------- HEURE D'ENTRÉE ULTRA ----------------
    risk = int((avg * 10) + confidence)
    seed = hash_int + seconds + risk

    delay = 20 + (seed % 45)   # 20s → 65s dynamic window

    entry_time = (t + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # ---------------- SIGNAL ----------------
    if prob > 60 and avg > 2.3:
        signal = "🟢 X3+ READY"
    elif prob > 40:
        signal = "⏳ WAIT"
    else:
        signal = "🔴 SKIP"

    return {
        "entry": entry_time,
        "prob": prob,
        "min": mn,
        "avg": avg,
        "max": mx,
        "confidence": confidence,
        "signal": signal
    }

# ---------------- UI ----------------
st.title("🚀 COSMOS X ANDR — ULTRA ENTRY SYSTEM")

if st.button("⚡ SCAN ENTRY SIGNAL"):

    res = simulate()
    st.session_state.history.append(res)

    st.markdown(f"""
<div class='box'>
<h2>⏰ ENTRY TIME: {res['entry']}</h2>
<h2>{res['signal']}</h2>
🎯 PROB X3+: <b>{res['prob']}%</b><br>
📉 MIN: {res['min']}<br>
📊 MOYEN: {res['avg']}<br>
🚀 MAX: {res['max']}<br>
🧠 CONFIDENCE: {res['confidence']}<br>
</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")
for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | {h['signal']} | {h['prob']}% | x{h['avg']}")

# ---------------- LIVE CLOCK ----------------
st_autorefresh(interval=10000, limit=None)
