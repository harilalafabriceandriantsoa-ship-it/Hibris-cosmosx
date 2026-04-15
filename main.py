import streamlit as st
import hashlib
import statistics
import random
import numpy as np
from datetime import datetime, timedelta

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS X ANDR ⚡ ULTRA", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle,#0b0b0b,#000);
    color:#00ffcc;
    font-family: monospace;
}
.box {
    border:1px solid #00ffcc;
    padding:15px;
    border-radius:12px;
    margin-top:10px;
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
    pwd = st.text_input("PASSWORD", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("WRONG PASSWORD")
    st.stop()

# ---------------- HASH ENGINE ----------------
def make_hash(server, client):
    return hashlib.sha512(f"{server}:{client}".encode()).hexdigest()

# ---------------- ENTRY TIME ULTRA DYNAMIC ----------------
def entry_time(server, client):

    h = make_hash(server, client)
    now = datetime.now()

    h1 = int(h[:16], 16)
    h2 = int(h[16:32], 16)
    h3 = int(h[32:48], 16)

    seconds = now.hour * 3600 + now.minute * 60 + now.second

    volatility = abs((h1 % 97) - (h2 % 83)) + (h3 % 71)

    drift = (
        (h1 % 60) +
        (h2 % 45) +
        (h3 % 30) +
        ((seconds // 60) % 37) +
        int(volatility * 0.5)
    )

    micro = int((h1 ^ h2 ^ h3) % 19)

    delay = 18 + drift + micro

    delay = max(10, min(delay, 180))

    return (now + timedelta(seconds=delay)).strftime("%H:%M:%S")

# ---------------- SIMULATION ENGINE ----------------
def simulate(server, client):

    h = make_hash(server, client)

    base = int(h[:16], 16)
    mid = int(h[16:32], 16)

    random.seed(base + mid)

    series = [random.uniform(1.0, 4.8) for _ in range(25)]

    mn = round(min(series), 2)
    avg = round(statistics.mean(series), 2)
    mx = round(max(series), 2)

    success = sum(1 for x in series if x >= 3.0)
    prob = round(success / len(series) * 100, 1)

    # ---------------- NORMAL COTE (NO FIXE) ----------------
    if avg < 1.7:
        cote = round(random.uniform(1.3, 1.6), 2)
    elif avg < 2.2:
        cote = round(random.uniform(1.6, 2.0), 2)
    elif avg < 2.8:
        cote = round(random.uniform(2.0, 2.4), 2)
    else:
        cote = round(random.uniform(2.3, 2.8), 2)

    # ---------------- CONFIDENCE ----------------
    confidence = round((prob * 0.6) + (avg * 20 * 0.4), 1)

    # ---------------- SIGNAL ----------------
    if prob > 70 and avg > 2.2:
        signal = "🟢 X3+ READY"
    elif prob > 55:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    # ---------------- ENTRY ----------------
    entry = entry_time(server, client)

    return {
        "entry": entry,
        "signal": signal,
        "prob": prob,
        "avg": avg,
        "min": mn,
        "max": mx,
        "cote": cote,
        "confidence": confidence
    }

# ---------------- UI ----------------
st.title("🚀 COSMOS X ANDR ⚡ ULTRA SYSTEM")

server = st.text_input("SERVER SEED")
client = st.text_input("CLIENT SEED")

if st.button("ANALYSE"):

    if server and client:

        result = simulate(server, client)
        st.session_state.history.append(result)

        st.markdown(f"""
        <div class="box">

        ⏰ ENTRY TIME: <b>{result['entry']}</b><br>
        🎯 SIGNAL: <b>{result['signal']}</b><br><br>

        📊 PROB X3+: <b>{result['prob']}%</b><br>
        📈 MIN: <b>{result['min']}</b> | AVG: <b>{result['avg']}</b> | MAX: <b>{result['max']}</b><br><br>

        💎 COTE: <b>x{result['cote']}</b><br>
        🧠 CONFIDENCE: <b>{result['confidence']}</b>

        </div>
        """, unsafe_allow_html=True)

        # balance simulation
        if result["confidence"] > 75:
            bet = st.session_state.balance * 0.02
            st.session_state.balance += bet if random.random() > 0.5 else -bet

        st.write("💰 BALANCE:", round(st.session_state.balance, 2))

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")

for h in reversed(st.session_state.history[-10:]):
    st.write(f"⏰ {h['entry']} | {h['signal']} | {h['prob']}% | x{h['cote']}")

# ---------------- GUIDE ----------------
st.subheader("📖 GUIDE")

st.markdown("""
### ⚡ SYSTEM LOGIC
- HASH512 → entropy engine
- TIME → dynamic entry
- RANDOMIZED COTE → no fixed values

### 🎯 BEST ZONE
- x1.6 → x2.8

### ⏰ ENTRY
- fully dynamic (NOT FIXED)
- depends on hash + current time + volatility

### ⚠️ NOTE
Simulation system only, not guaranteed prediction.
""")
