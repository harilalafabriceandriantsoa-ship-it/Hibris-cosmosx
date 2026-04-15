import streamlit as st        
import hashlib        
import statistics        
import random        
import numpy as np        
from datetime import datetime, timedelta    
from streamlit_autorefresh import st_autorefresh    

# ---------------- CONFIG ----------------    
st.set_page_config(page_title="COSMOS X ANDR", layout="wide")    

# ---------------- STYLE ----------------    
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#050505,#101820);
    color:#00ffcc;
    font-family: monospace;
}
h1,h2,h3 {text-align:center;}
.block {
    background:#0f0f0f;
    padding:15px;
    border-radius:12px;
    box-shadow:0 0 15px #00ffcc33;
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

    if st.button("ENTER"):        
        if pwd == "2026":        
            st.session_state.login = True        
            st.rerun()        
        else:        
            st.error("Wrong password")        
    st.stop()

# ---------------- HASH512 CORE ----------------    
def hash512(value):    
    return hashlib.sha512(value.encode()).hexdigest()    

# ---------------- TIME FACTOR ----------------    
def time_factor():    
    now = datetime.now()    
    return now.hour*3600 + now.minute*60 + now.second, now    

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

# ---------------- ENGINE ULTRA ----------------    
def analyse():    

    # 🔥 HASH ONLY (NO SEEDS)
    h = hash512(str(datetime.now()) + str(random.random()))    

    # ⏰ TIME
    t_seconds, now = time_factor()    

    # 🎲 base simulation
    base = int(h[:16], 16) % 1000
    noise = np.random.normal(base/100, 0.8, 25)

    series = np.abs(noise)

    mn = round(min(series),2)
    avg = round(statistics.mean(series),2)
    mx = round(max(series),2)

    acc = int((sum(1 for x in series if x >= 2) / len(series)) * 100)

    cote = cote_filter(avg, acc)

    confidence = int((acc * 0.65) + (avg * 18 * 0.35))

    # 🔥 HEURE D’ENTRÉE ULTRA DYNAMIQUE
    raw = int(h[8:24],16) + t_seconds + int(cote*100) + confidence
    delay = 20 + (raw % 45) + (int(h[-6:],16) % 10)

    entry_time = (now + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # 🎯 SIGNAL
    if acc > 85 and avg > 2:
        signal = "🟢 X3+ READY"
        emoji = "🔥🎯"
    elif acc > 65:
        signal = "🟡 WAIT"
        emoji = "⏳"
    else:
        signal = "🔴 SKIP"
        emoji = "❌"

    return {
        "hash": h[:12]+"...",
        "min": mn,
        "avg": avg,
        "max": mx,
        "accuracy": acc,
        "cote": cote,
        "confidence": confidence,
        "entry": entry_time,
        "signal": signal,
        "emoji": emoji
    }

# ---------------- UI ----------------    
st.title("🚀 COSMOS X ANDR SYSTEM")

if st.button("SCAN COSMOS X"):

    r = analyse()
    st.session_state.history.append(r)

    st.markdown(f"""
<div class="block">
<h2>{r['emoji']} {r['signal']}</h2>

⏰ ENTRY TIME: <b>{r['entry']}</b><br>
📊 ACCURACY: <b>{r['accuracy']}%</b><br>
💎 COTE: <b>x{r['cote']}</b><br>
🧠 CONFIDENCE: <b>{r['confidence']}</b><br>
📉 MIN: {r['min']} | 📊 AVG: {r['avg']} | 🚀 MAX: {r['max']}<br>
🔐 HASH: {r['hash']}
</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------    
st.subheader("📜 HISTORY")
for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | {h['signal']} | {h['accuracy']}% | x{h['cote']}")

# ---------------- GUIDE ----------------    
st.subheader("📖 GUIDE")
st.markdown("""
- 🔥 HASH ONLY SYSTEM (no seed)
- ⏰ TIME + HASH fusion entry
- 💎 COTE FILTER X3+
- 🧠 confidence-based decision
- ⚡ dynamic entry window (20–65s)
""")

# ---------------- AUTO REFRESH ----------------    
st_autorefresh(interval=10000, limit=None)
