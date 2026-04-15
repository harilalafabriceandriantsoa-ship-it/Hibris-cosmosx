import streamlit as st
import hashlib
import statistics
import numpy as np
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS X ANDR ⚡ ENTRY AI", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#050505,#0d0d0d,#1a1a1a);
    color:#00ffcc;
    font-family: monospace;
}
h1,h2,h3 {text-align:center; color:#00ffcc;}
.box {
    background:#0a0a0a;
    padding:15px;
    border-radius:12px;
    border:1px solid #00ffcc33;
    box-shadow:0 0 10px #00ffcc22;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- TIME MADAGASCAR ----------------
def now_mg():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ---------------- HASH512 ----------------
def hash512(data):
    return hashlib.sha512(data.encode()).hexdigest()

# ---------------- CRASH SIMULATION ----------------
def crash_from_hash(h):
    dec = int(h[-10:], 16) or 1
    return round((4294967295 * 0.97) / dec, 2)

# ---------------- COTE FILTER ----------------
def cote_filter(avg, accuracy):
    if accuracy > 90 and avg > 3:
        return 3.0
    elif accuracy > 80:
        return 2.5
    elif accuracy > 70:
        return 2.0
    elif accuracy > 60:
        return 1.8
    return 1.5

# ---------------- IA ENGINE ----------------
def ai_score(series, avg, mn, accuracy):
    trend = series[-1] - series[0]
    volatility = np.std(series)

    trend_factor = 1.15 if trend > 0 else 0.9
    stability = 1 / (1 + volatility)

    base = (avg * 0.5) + (accuracy / 100 * 3 * 0.3) + (mn * 0.2)

    return base * trend_factor * (1 + stability)

# ---------------- ENTRY TIME ULTRA ----------------
def entry_time(h, cote, confidence, now):

    seed1 = int(h[:16], 16)
    seed2 = int(h[16:32], 16)

    seconds = now.hour * 3600 + now.minute * 60 + now.second

    raw = seed1 + seed2 + seconds + int(cote * 100) + confidence

    delay = 15 + (raw % 50) + (int(h[-6:],16) % 10)

    return (now + timedelta(seconds=delay)).strftime("%H:%M:%S"), delay

# ---------------- ENGINE CORE ----------------
def run_engine():

    now = now_mg()

    # HASH basé sur time
    h = hash512(str(now.timestamp()))

    series = [crash_from_hash(hash512(h + str(i))) for i in range(20)]

    mn = round(min(series), 2)
    avg = round(statistics.mean(series), 2)
    mx = round(max(series), 2)

    accuracy = int(sum(1 for x in series if x >= 2) / len(series) * 100)

    cote = cote_filter(avg, accuracy)

    confidence = int((accuracy * 0.6) + (avg * 20 * 0.4))

    score = ai_score(series, avg, mn, accuracy)

    entry, delay = entry_time(h, cote, confidence, now)

    if accuracy >= 85 and avg > 2:
        signal = "🟢 X3+ READY"
    elif accuracy >= 65:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    return {
        "time": now.strftime("%H:%M:%S"),
        "entry": entry,
        "delay": delay,
        "min": mn,
        "avg": avg,
        "max": mx,
        "accuracy": accuracy,
        "cote": cote,
        "confidence": confidence,
        "score": round(score, 2),
        "signal": signal
    }

# ---------------- UI ----------------
st.title("🌌 COSMOS X ANDR ⚡ ULTRA ENTRY AI")

if st.button("🚀 SCAN ENTRY WINDOW"):

    res = run_engine()
    st.session_state.history.append(res)

    st.markdown(f"""
<div class="box">

⏰ TIME MG: <b>{res['time']}</b><br>
🎯 ENTRY: <b>{res['entry']}</b> (+{res['delay']}s)<br><br>

📊 MIN: {res['min']} | MOY: {res['avg']} | MAX: {res['max']}<br>
📈 ACCURACY: {res['accuracy']}%<br>
💎 COTE: x{res['cote']}<br>
🧠 CONFIDENCE: {res['confidence']}<br>
⚡ SCORE AI: {res['score']}<br><br>

🔥 SIGNAL: {res['signal']}

</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")

for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | 🎯 {h['signal']} | 📊 {h['accuracy']}% | x{h['cote']}")

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=10000, limit=None)
