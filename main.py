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

# ---------------- ENGINE ----------------
def hash512(seed: str):
    h = hashlib.sha512(seed.encode()).hexdigest()
    val = int(h[:16], 16)
    return val / 10**12

def get_time():
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    sec = now.hour * 3600 + now.minute * 60 + now.second
    return now, sec

# ---------------- CORE CALC ----------------
def compute_engine(hash_input, cote_ref):

    now, sec = get_time()

    h_val = hash512(hash_input)
    time_factor = (sec % 60) / 60

    # 🎯 COTE FILTER
    if cote_ref < 1.5:
        cote_factor = 0.75
    elif cote_ref < 2.0:
        cote_factor = 1.0
    elif cote_ref <= 2.5:
        cote_factor = 1.25
    else:
        cote_factor = 0.85

    # 📊 BASE ENGINE
    base = (h_val * 2.4) * cote_factor * (1 + time_factor)

    # 📊 NORMAL COTE MIN / MOY / MAX
    cote_min = round(base * 0.78, 2)
    cote_moy = round(base, 2)
    cote_max = round(base * 1.32, 2)

    # 🧠 CONFIDENCE
    confidence = round((h_val * 60) + (cote_moy * 20), 2)

    # ⏰ ENTRY TIME (DYNAMIC NON FIXE)
    delay = int(20 + (h_val * 40) + (time_factor * 30) + (cote_factor * 15))
    entry_time = now + timedelta(seconds=delay)

    # 🎯 SIGNAL LOGIC
    if cote_moy >= 2.2 and confidence >= 70:
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
        "time": now.strftime("%H:%M:%S")
    }

# ---------------- UI ----------------
st.title("🌌 COSMOS X ANDR SYSTEM ⚡")

hash_in = st.text_input("🔑 HASH INPUT")
cote_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5)

if st.button("🚀 SCAN ENTRY"):

    if hash_in:
        res = compute_engine(hash_in, cote_ref)

        st.session_state.history.append(res)

        st.markdown(f"""
# 🎯 RESULT COSMOS

⏰ CURRENT TIME: `{res['time']}`  
🚀 ENTRY TIME: `{res['entry']}`  

🔥 SIGNAL: **{res['signal']}**  

📊 COTE MIN: `{res['min']}`  
📊 COTE MOY: `{res['moy']}`  
📊 COTE MAX: `{res['max']}`  

🧠 CONFIDENCE: `{res['confidence']}%`  
🔑 HASH: `{res['hash']}`
""")

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")
for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | 🎯 {h['signal']} | 📊 {h['moy']}x | 🧠 {h['confidence']}%")

# ---------------- GUIDE ----------------
st.subheader("📖 GUIDE")
st.markdown("""
### 🎯 SYSTEM LOGIC
- HASH512 → base probability
- TIME → dynamic entry window
- COTE REF → trend filter

### ⏰ ENTRY RULE
- 🔥 X3+ ENTRY = strong zone
- ⏳ WAIT = medium zone
- ❌ SKIP = avoid

### 📊 BEST ZONE
- 1.8 → 2.5 cote = optimal range
""")
