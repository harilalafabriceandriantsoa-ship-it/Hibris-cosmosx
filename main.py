import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------

st.set_page_config(page_title="COSMOS X ANDR V12.2 AI", layout="wide")

st.markdown("""
<style>
    .stApp {
        background:#05050A;
        color:#00ffcc;
        font-family: monospace;
    }
    h1 {
        text-align:center;
        color:#00ffcc;
        text-shadow:0 0 10px #00ffcc;
    }
    .card {
        padding:20px;
        border:2px solid #00ffcc;
        border-radius:15px;
        background:rgba(0,255,204,0.05);
    }
</style>
""", unsafe_allow_html=True)

DB = "cosmos_v12_2.db"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT,
        h_tour TEXT,
        h_entry TEXT,
        cote REAL,
        signal TEXT,
        confidence REAL
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h, t, e, cote, sig, conf):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (hash, h_tour, h_entry, cote, signal, confidence)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (h, t, e, cote, sig, conf))
    conn.commit()
    conn.close()

def load_db():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df

# ---------------- HASH SCANNER ----------------

def hash_to_num(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10], 16) / 0xFFFFFFFFFF

def detect_hash_change(new_hash):
    if "last_hash" not in st.session_state:
        st.session_state.last_hash = new_hash
        return 1.0

    old = st.session_state.last_hash
    st.session_state.last_hash = new_hash

    # similarity scan
    diff = sum(a != b for a, b in zip(old, new_hash[:len(old)]))
    return min(1.5, 1 + diff * 0.05)

# ---------------- AUTO REF ----------------

def auto_ref(df):
    if len(df) < 5:
        return 1.7, "NEUTRAL"

    recent = df.head(10)

    weights = np.linspace(1, 2, len(recent))
    w_mean = np.average(recent["cote"], weights=weights)

    slope = np.polyfit(range(len(recent)), recent["cote"].values, 1)[0]

    if slope > 0.05:
        trend = "UP"
        ref = w_mean * 1.1
    elif slope < -0.05:
        trend = "DOWN"
        ref = w_mean * 0.9
    else:
        trend = "FLAT"
        ref = w_mean

    ref = float(np.clip(ref, 1.5, 2.5))
    return round(ref, 2), trend

# ---------------- TIME ENGINE ULTRA ----------------

def time_engine(now_sec, h_val, vol, mode):

    cycle = 120
    t = now_sec % cycle

    wave = np.sin(2 * np.pi * (t / cycle))
    entropy = np.sqrt(h_val)
    vol_norm = min(1.5, max(0.5, vol / 2))

    if mode == "SAFE":
        a, b, c, S = 8, 6, 10, 0.8
    else:
        a, b, c, S = 15, 12, 18, 1.2

    delay = (a * wave + b * entropy + c * vol_norm) * S

    # peak scan
    if abs(wave) > 0.85 and mode == "SNIPER":
        delay *= 0.75

    return int(np.clip(delay, 8, 110))

# ---------------- ENGINE ----------------

def compute(hash_input, last_time, cote_ref):

    now = datetime.now(pytz.timezone("Indian/Antananarivo"))
    now_sec = now.hour * 3600 + now.minute * 60 + now.second

    h_val = hash_to_num(hash_input)

    df = load_db()

    # ---------------- HASH SCAN ----------------
    hash_boost = detect_hash_change(hash_input)

    # ---------------- AUTO REF ----------------
    ref, trend = auto_ref(df)

    # ---------------- VOLATILITY ----------------
    vol = df["cote"].std() if len(df) > 5 else 1.0

    # ---------------- TIME ENGINE ----------------
    delay = time_engine(now_sec, h_val, vol, st.session_state.get("mode", "SNIPER"))

    entry = now + timedelta(seconds=delay)

    # ---------------- COTE ENGINE ----------------
    t_factor = (np.sin(now_sec / 120) + 1) / 2

    momentum = (h_val * 0.6) + (t_factor * 0.4)

    base = 1.2 + (h_val * 3.5) + (t_factor * 1.5) + (ref * 0.2)

    boost = np.random.uniform(1.05, 1.25)

    final = base * boost * hash_boost

    # ---------------- CONFIDENCE ----------------
    conf = min(99.9, (momentum ** 1.7) * 100)

    # ---------------- SIGNAL ENGINE (IMPROVED) ----------------

    if conf >= 88 and final >= 3:
        signal = "🔥 ULTRA X3+ SNIPER"
        color = "red"
    elif conf >= 75 and final >= 2.2:
        signal = "🟢 STRONG ENTRY"
        color = "green"
    elif conf >= 55:
        signal = "🟡 WAIT SIGNAL"
        color = "orange"
    else:
        signal = "🔴 NO ENTRY"
        color = "gray"

    # ---------------- SAVE ----------------
    save_db(hash_input, last_time, entry.strftime("%H:%M:%S"), round(final,2), signal, round(conf,1))

    return {
        "entry": entry.strftime("%H:%M:%S"),
        "cote": round(final,2),
        "conf": round(conf,1),
        "signal": signal,
        "ref": ref,
        "trend": trend,
        "hash_boost": round(hash_boost,2),
        "color": color
    }

# ---------------- UI ----------------

st.title("🚀 COSMOS X ANDR V12.2 AI")

mode = st.sidebar.radio("MODE", ["SNIPER", "SAFE"])
st.session_state.mode = mode

h = st.text_input("HASH")
t = st.text_input("LAST TIME")
c = st.number_input("REF", value=1.7)

if st.button("SCAN ENGINE"):
    if h:
        st.session_state.res = compute(h, t, c)

if "res" in st.session_state:
    r = st.session_state.res

    st.markdown(f"""
    <div class="card">
        <h2>{r['signal']}</h2>
        <p>ENTRY: {r['entry']}</p>
        <p>COTE: {r['cote']}</p>
        <p>CONF: {r['conf']}%</p>
        <p>REF: {r['ref']} | TREND: {r['trend']}</p>
        <p>HASH SCAN BOOST: {r['hash_boost']}</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("HISTORY")
st.dataframe(load_db())
