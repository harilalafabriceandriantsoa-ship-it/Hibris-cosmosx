import streamlit as st
import hashlib
import numpy as np
from datetime import datetime, timedelta
import pytz

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS X ANDR V4", layout="wide")

st.markdown("""
<style>
.stApp {background:#0b0b0b;color:#00ffcc;font-family:monospace;}
h1 {text-align:center;color:#00ffcc;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "login" not in st.session_state:
    st.session_state.login = False

# ---------------- LOGIN ----------------
if not st.session_state.login:
    st.title("🔐 COSMOS X ANDR ACCESS")
    pwd = st.text_input("Password", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

# ---------------- ENGINE ----------------

def hash512(seed: str):
    h = hashlib.sha512(seed.encode()).hexdigest()
    return int(h[:16], 16) / 10**12

def get_time():
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    sec = now.hour * 3600 + now.minute * 60 + now.second
    return now, sec

# ---------------- HEURE DU TOUR (V4 FIXED MODULE) ----------------
def tour_engine(sec, h_val):
    base_cycle = sec % 120                     # 2 min cycle
    micro_cycle = int((h_val * 100) % 60)      # hash influence
    return (base_cycle + micro_cycle) / 180    # normalized 0–1

# ---------------- CORE ENGINE ----------------
def compute_engine(hash_input, cote_ref):

    now, sec = get_time()
    h_val = hash512(hash_input)

    time_factor = (sec % 60) / 60
    tour = tour_engine(sec, h_val)

    # 🎯 COTE FILTER
    if cote_ref < 1.5:
        cote_factor = 0.75
    elif cote_ref < 2.0:
        cote_factor = 1.0
    elif cote_ref <= 2.5:
        cote_factor = 1.25
    else:
        cote_factor = 0.85

    # 📊 BASE ENGINE (V4 IMPROVED STABILITY)
    base = (h_val * 2.4) * cote_factor * (1 + time_factor + tour * 0.6)

    # 📉 MIN / MOY / MAX NORMAL
    cote_min = round(base * 0.78, 2)
    cote_moy = round(base, 2)
    cote_max = round(base * 1.32, 2)

    # 🧠 CONFIDENCE (TOUR BOOST INCLUDED)
    confidence = round(
        (h_val * 55) +
        (cote_moy * 18) +
        (tour * 30),
        2
    )

    # ⏰ ENTRY TIME ULTRA STABLE
    delay = int(
        20 +
        (h_val * 35) +
        (time_factor * 25) +
        (tour * 45) +
        (cote_factor * 10)
    )

    entry_time = now + timedelta(seconds=delay)

    # 🎯 SIGNAL LOGIC
    if cote_moy >= 2.2 and confidence >= 70 and tour > 0.45:
        signal = "🔥 X3+ ENTRY"
    elif cote_moy >= 1.8:
        signal = "⏳ WAIT"
    else:
        signal = "❌ SKIP"

    return {
        "hash": hash_input[:12] + "...",
        "min": cote_min,
        "moy": cote_moy,
        "max": cote_max,
        "confidence": confidence,
        "entry": entry_time.strftime("%H:%M:%S"),
        "signal": signal,
        "time": now.strftime("%H:%M:%S"),
        "tour": round(tour, 3),
        "version": "V4"
    }

# ---------------- UI ----------------
st.title("🌌 COSMOS X ANDR SYSTEM ⚡ V4")

hash_in = st.text_input("🔑 HASH INPUT")
cote_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5)

if st.button("🚀 SCAN ENTRY"):

    if hash_in:

        result = compute_engine(hash_in, cote_ref)

        st.session_state.history.append(result)

        st.markdown(f"""
# 🌌 COSMOS RESULT ⚡ V4

🕒 TIME NOW: `{result['time']}`  
🚀 ENTRY TIME: `{result['entry']}`  
🔄 TOUR ENGINE: `{result['tour']}`  

🔥 SIGNAL: **{result['signal']}**

📉 MIN: `{result['min']}`
📊 MOY: `{result['moy']}`
📈 MAX: `{result['max']}`

🧠 CONFIDENCE: `{result['confidence']}%`
🔑 HASH: `{result['hash']}`
⚡ VERSION: `{result['version']}`
""")

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")
for h in reversed(st.session_state.history[-10:]):
    st.write(
        f"⏰ {h['entry']} | 🎯 {h['signal']} | "
        f"📊 {h['moy']}x | 🧠 {h['confidence']}% | 🔄 {h['tour']}"
    )

# ---------------- GUIDE ----------------
st.subheader("📖 GUIDE V4")
st.markdown("""
### ⚙️ SYSTEM V4 LOGIC
- HASH512 → base engine
- TIME → Madagascar real time
- TOUR ENGINE → cycle + hash fusion
- COTE REF → trend filter

### 🎯 SIGNAL RULE
- 🔥 X3+ ENTRY = strong zone
- ⏳ WAIT = medium zone
- ❌ SKIP = avoid entry

### ⏰ ENTRY WINDOW
- fully dynamic
- depends on hash + time + tour engine
""")
