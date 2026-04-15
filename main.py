import streamlit as st
import hashlib
import statistics
import random
import numpy as np
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import pytz

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS ULTRA AI V4 ⚡", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(circle,#0f0f0f,#050505); color:#00ffcc;}
h1,h2,h3 {color:#00ffcc; text-align:center;}
.block {padding:15px;border-radius:12px;background:#111;margin:10px 0;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "memory" not in st.session_state:
    st.session_state.memory = []

# ---------------- HASH ENGINE ----------------
def hash512(data):
    return hashlib.sha512(data.encode()).hexdigest()

def crash_value(hash_str):
    dec = int(hash_str[-10:], 16) or 1
    return (4294967295 * 0.97) / dec

# ---------------- AI LEARNING ----------------
def ai_learning(avg, acc, mn):
    if len(st.session_state.memory) < 5:
        return 1.0

    recent = st.session_state.memory[-20:]
    avg_mem = np.mean([m[0] for m in recent])

    trend = avg - avg_mem
    stability = 1 / (1 + np.std([m[1] for m in recent]))

    return 1 + (trend * 0.2) + stability

# ---------------- COTE NORMALISÉE ----------------
def cote_engine(avg, acc):
    base = (avg * acc) / 100

    if base > 3:
        return 3.2
    elif base > 2.2:
        return 2.5
    elif base > 1.6:
        return 2.0
    else:
        return 1.5

# ---------------- ULTRA ENTRY TIME ENGINE ----------------
def entry_time(hash_val, now, cote, confidence):

    h_int = int(hash_val[:16], 16)

    # entropy from hash
    entropy = (h_int % 97)

    # time entropy (madagascar time)
    t_sec = now.hour*3600 + now.minute*60 + now.second

    # dynamic risk weight
    risk = int(cote * 10 + confidence)

    # NON FIXED CORE (IMPORTANT)
    seed = entropy + t_sec + risk
    random.seed(seed)

    base_delay = random.randint(10, 60)

    micro_shift = (h_int % 11)

    final_delay = base_delay + micro_shift

    return (now + timedelta(seconds=final_delay)), final_delay

# ---------------- MAIN ENGINE ----------------
def analyse(hash_input):

    now = datetime.now(pytz.timezone("Indian/Antananarivo"))

    h = hash512(hash_input)

    base = crash_value(h)

    # simulation
    series = np.random.lognormal(mean=np.log(abs(base)+1), sigma=0.35, size=2000)

    avg = round(np.mean(series),2)
    mn = round(np.min(series),2)
    mx = round(np.max(series),2)

    success = sum(1 for x in series if x >= 2.0)
    acc = int(success/len(series)*100)

    cote = cote_engine(avg, acc)

    confidence = int((acc * 0.7) + (avg * 15))

    ai_boost = ai_learning(avg, acc, mn)

    confidence = int(confidence * ai_boost)

    entry, delay = entry_time(h, now, cote, confidence)

    signal = "🔴 SKIP"
    if acc > 80 and confidence > 120:
        signal = "🟢 STRONG ENTRY"
    elif acc > 65:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    result = {
        "hash": h[:12],
        "avg": avg,
        "min": mn,
        "max": mx,
        "accuracy": acc,
        "cote": cote,
        "confidence": confidence,
        "entry": entry.strftime("%H:%M:%S"),
        "delay": delay,
        "signal": signal
    }

    st.session_state.history.append(result)
    st.session_state.memory.append((avg, acc, mn))

    return result

# ---------------- UI ----------------
st.title("🌌 COSMOS ULTRA AI V4 ⚡")

hash_input = st.text_input("🔑 HASH INPUT")

if st.button("SCAN COSMOS") and hash_input:

    res = analyse(hash_input)

    st.markdown(f"""
<div class='block'>
<h2>{res['signal']}</h2>

⏰ ENTRY TIME: <b>{res['entry']}</b> (delay {res['delay']}s)  
📊 ACCURACY: {res['accuracy']}%  
📉 MIN: {res['min']} | 📊 AVG: {res['avg']} | 🚀 MAX: {res['max']}  
💎 COTE: x{res['cote']}  
🧠 CONFIDENCE: {res['confidence']}  
🔑 HASH: {res['hash']}  
</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")
for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | {h['signal']} | x{h['cote']} | {h['accuracy']}%")

# ---------------- GUIDE ----------------
st.subheader("📖 GUIDE")

st.markdown("""
### ⚡ INPUTS
- HASH = base entropy

### 🧠 ENGINE
- HASH512 entropy
- TIME entropy (Madagascar)
- COTE filter
- AI learning memory

### ⏰ ENTRY WINDOW
- Dynamic 10s → 70s (NON FIXE)
- Depends on:
  - hash entropy
  - current time
  - confidence
  - cote risk

### 🎯 SIGNAL
- 🟢 STRONG ENTRY = best X3+ zone
- 🟡 WAIT = unstable
- 🔴 SKIP = avoid
""")

st_autorefresh(interval=8000)
