import streamlit as st
import hashlib
import statistics
import random
import numpy as np
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS X ANDR ⚡", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle,#0d0d0d,#000);
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
    border:1px solid #00ffcc33;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "balance" not in st.session_state:
    st.session_state.balance = 1000

# ---------------- HASH512 ----------------
def hash512(value):
    return hashlib.sha512(value.encode()).hexdigest()

# ---------------- COTE FILTER ----------------
def compute_cote(avg, acc):
    if acc > 90 and avg > 3:
        return 3.0
    elif acc > 80:
        return 2.5
    elif acc > 70:
        return 2.0
    elif acc > 60:
        return 1.8
    return 1.5

# ---------------- CRASH SIM ----------------
def crash(seed):
    h = hash512(seed)
    dec = int(h[-8:],16) or 1
    return round((4294967295 * 0.97) / dec, 2)

# ---------------- HEURE MADAGASCAR ULTRA ENGINE ----------------
def entry_time(seed, cote, confidence):
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)

    # ⏰ TIME FACTOR (seconds of day)
    seconds = now.hour*3600 + now.minute*60 + now.second

    # 🔥 HASH FACTOR
    h = hash512(seed)
    h1 = int(h[:16],16)
    h2 = int(h[16:32],16)

    # ⚡ CORE FUSION (HASH + TIME + COTE FILTER)
    raw = h1 + h2 + seconds + int(cote*100) + confidence

    # 🎯 SNIPER WINDOW (5–55 sec dynamic)
    base_delay = 25 + (raw % 35)
    micro = int(h[-6:],16) % 7

    delay = base_delay + micro

    return (now + timedelta(seconds=delay)).strftime("%H:%M:%S")

# ---------------- ENGINE ----------------
def analyse(seed_input):

    series = [crash(seed_input + str(i)) for i in range(20)]

    mn = round(min(series),2)
    avg = round(statistics.mean(series),2)
    mx = round(max(series),2)

    acc = int(sum(1 for x in series if x >= 2) / len(series) * 100)

    cote = compute_cote(avg, acc)

    confidence = int((acc * 0.6) + (avg * 20 * 0.4))

    # 🧠 SIGNAL
    if acc >= 85 and avg > 2:
        signal = "🟢 X3+ READY"
    elif acc >= 65:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    entry = entry_time(seed_input, cote, confidence)

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
st.title("🚀 COSMOS X ANDR ⚡ ULTRA ENTRY SYSTEM")

seed = st.text_input("🔑 INPUT HASH SEED")

if st.button("SCAN X3+ ENTRY") and seed:

    result = analyse(seed)
    st.session_state.history.append(result)

    st.markdown(f"""
<div class="block">

## ⏰ ENTRY TIME (MADAGASCAR)
### 🎯 {result['entry']}

## 📊 SIGNAL
### {result['signal']}

## 📈 STATS
- MIN: {result['min']}
- AVG: {result['avg']}
- MAX: {result['max']}

## 🎯 COTE FILTER
x{result['cote']}

## 🧠 CONFIDENCE
{result['confidence']}%

</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")

for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | {h['signal']} | ACC {h['acc']}% | x{h['cote']}")

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=10000, limit=None)
