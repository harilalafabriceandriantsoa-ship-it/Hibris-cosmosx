import streamlit as st
import hashlib
import numpy as np
from datetime import datetime, timedelta
import pytz

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS X ANDR", layout="wide")

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

# ---------------- TIME ENGINE ----------------
def get_time():
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    sec = now.hour * 3600 + now.minute * 60 + now.second
    return now, sec

def tour_factor(sec):
    return (sec % 120) / 120  # 2 min cycle

# ---------------- HASH ENGINE ----------------
def hash512(seed):
    h = hashlib.sha512(seed.encode()).hexdigest()
    return int(h[:16], 16) / 10**12

# ---------------- CORE ENGINE ----------------
def compute_engine(hash_input, cote_ref):

    now, sec = get_time()

    h_val = hash512(hash_input)

    time_factor = (sec % 60) / 60
    tour = tour_factor(sec)

    # 🎯 COTE FILTER
    if cote_ref < 1.5:
        cote_factor = 0.75
    elif cote_ref < 2.0:
        cote_factor = 1.0
    elif cote_ref <= 2.5:
        cote_factor = 1.25
    else:
        cote_factor = 0.85

    # 📊 BASE
    base = (h_val * 2.4) * cote_factor * (1 + time_factor + (tour * 0.5))

    # 📉 MIN / MOY / MAX
    cote_min = round(base * 0.78, 2)
    cote_moy = round(base, 2)
    cote_max = round(base * 1.32, 2)

    # 🧠 CONFIDENCE
    confidence = round((h_val * 55) + (cote_moy * 18) + (tour * 25), 2)

    # ⏰ ENTRY TIME
    delay = int(18 + (h_val * 35) + (time_factor * 25) + (tour * 40) + (cote_factor * 10))
    entry_time = now + timedelta(seconds=delay)

    # 🎯 SIGNAL
    if cote_moy >= 2.2 and confidence >= 70 and tour > 0.4:
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
        "tour": round(tour, 2),
        "cote_ref": cote_ref
    }

# ---------------- UI ----------------
st.title("🌌 COSMOS X ANDR SYSTEM ⚡ ULTRA V4")

hash_in = st.text_input("🔑 HASH INPUT")
cote_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5)

# ⏰ LIVE TOUR DISPLAY
now, sec = get_time()
tour_live = round(tour_factor(sec), 2)

st.markdown(f"""
### ⏰ STATUS LIVE
- HASH INPUT: `{hash_in if hash_in else '---'}`
- TOUR ACTUEL: `{tour_live}`
- TIME MADAGASCAR: `{now.strftime('%H:%M:%S')}`
""")

if st.button("🚀 SCAN ENTRY"):

    if hash_in:

        result = compute_engine(hash_in, cote_ref)

        st.session_state.history.append(result)

        # 🎯 RESULT
        st.markdown(f"""
# 🌌 COSMOS RESULT ULTRA V4

⏰ TIME NOW: `{result['time']}`  
🔄 TOUR: `{result['tour']}`  
📊 COTE REF: `{result['cote_ref']}`  

🚀 ENTRY TIME: `{result['entry']}`  

🔥 SIGNAL: **{result['signal']}**

📉 MIN: `{result['min']}`
📊 MOY: `{result['moy']}`
📈 MAX: `{result['max']}`

🧠 CONFIDENCE: `{result['confidence']}%`
🔑 HASH: `{result['hash']}`
""")

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY (LAST 10)")
for h in reversed(st.session_state.history[-10:]):
    st.write(
        f"⏰ {h['entry']} | 🔄 TOUR {h['tour']} | "
        f"📊 {h['moy']}x | 🧠 {h['confidence']}% | 🎯 {h['signal']}"
    )

# ---------------- GUIDE ----------------
st.subheader("📖 GUIDE ULTRA V4")

st.markdown("""
### 🧠 INPUTS REQUIRED
- 🔑 HASH (required)
- 📊 COTE RÉFÉRENCE
- ⏰ HEURE AUTO (Madagascar)

### 🔄 CORE SYSTEM
- HASH512 → base signal
- TOUR (0 → 1 cycle 2 min)
- TIME (real seconds cycle)
- COTE FILTER → stability zone

### 🎯 ENTRY LOGIC
- 🔥 X3+ ENTRY → strong zone
- ⏳ WAIT → medium zone
- ❌ SKIP → avoid

### ⏰ ENTRY TIME
- dynamic (hash + time + tour)
- NOT FIXED
""")
