import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor

# ---------------- CONFIG ----------------

st.set_page_config(page_title="COSMOS X V13 QUANT FINAL", layout="wide")

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

DB = "v13_quant_final.db"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT,
        time TEXT,
        entry TEXT,
        cote REAL,
        prob REAL,
        signal TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h, t, e, cote, p, s):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (hash, time, entry, cote, prob, signal)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (h, t, e, cote, p, s))
    conn.commit()
    conn.close()

def load_db():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 200", conn)
    conn.close()
    return df

def reset_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS history")
    conn.commit()
    conn.close()
    init_db()

# ---------------- LOGIN ----------------

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 COSMOS X ACCESS")

    pwd = st.text_input("PASSWORD", type="password")

    if st.button("LOGIN"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("WRONG PASSWORD")

    st.stop()

# ---------------- HASH ----------------

def hash_to_float(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10], 16) / 0xFFFFFFFFFF

def hash_scanner(new_hash):
    if "last_hash" not in st.session_state:
        st.session_state.last_hash = new_hash
        return 1.0

    old = st.session_state.last_hash
    st.session_state.last_hash = new_hash

    diff = sum(a != b for a, b in zip(old, new_hash))
    return 1 + (diff * 0.03)

# ---------------- AUTO REF ----------------

def auto_ref(df):
    if len(df) < 5:
        return 1.7, "NEUTRAL"

    recent = df.head(10)

    weights = np.linspace(1, 2, len(recent))
    wmean = np.average(recent["cote"], weights=weights)

    slope = np.polyfit(range(len(recent)), recent["cote"].values, 1)[0]

    if slope > 0.05:
        return round(wmean * 1.1, 2), "UP"
    elif slope < -0.05:
        return round(wmean * 0.9, 2), "DOWN"
    else:
        return round(wmean, 2), "FLAT"

# ---------------- ML MODEL ----------------

def train_model(df):
    if len(df) < 10:
        return None

    X = []
    y = []

    for i in range(len(df)):
        h = hash_to_float(df.iloc[i]["hash"])
        X.append([h])
        y.append(df.iloc[i]["cote"])

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

# ---------------- TIME ENGINE ----------------

def time_engine(now_sec, h_val, vol):

    wave1 = np.sin(2 * np.pi * (now_sec % 120) / 120)
    wave2 = np.cos(2 * np.pi * (now_sec % 180) / 180)

    entropy = np.sqrt(h_val)

    delay = 10 + wave1 * 25 + wave2 * 20 + entropy * 30 + vol * 10

    return int(np.clip(delay, 8, 120))

# ---------------- ENGINE ----------------

def compute(hash_input, last_time):

    now = datetime.now(pytz.timezone("Indian/Antananarivo"))
    now_sec = now.hour * 3600 + now.minute * 60 + now.second

    h_val = hash_to_float(hash_input)

    df = load_db()

    # VOLATILITY
    vol = df["cote"].std() if len(df) > 5 else 1.0

    # HASH SCAN
    hash_boost = hash_scanner(hash_input)

    # AUTO REF
    ref, trend = auto_ref(df)

    # TIME ENGINE
    delay = time_engine(now_sec, h_val, vol)
    entry = now + timedelta(seconds=delay)

    # MODEL
    model = train_model(df)

    if model:
        pred = model.predict([[h_val]])[0]
    else:
        pred = 1.5 + h_val * 3

    # PROBABILITY
    prob = min(0.99, (h_val * 0.6 + (vol / 2) * 0.4))

    # SIGNAL
    if prob > 0.85 and pred > 2.8:
        signal = "🔥 ULTRA X3+"
    elif prob > 0.70:
        signal = "🟢 STRONG ENTRY"
    elif prob > 0.50:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 NO ENTRY"

    final_cote = pred * hash_boost

    save_db(hash_input, last_time, entry.strftime("%H:%M:%S"), round(final_cote,2), round(prob,2), signal)

    return {
        "entry": entry.strftime("%H:%M:%S"),
        "cote": round(final_cote,2),
        "prob": round(prob,2),
        "signal": signal,
        "ref": ref,
        "trend": trend,
        "vol": round(vol,2)
    }

# ---------------- UI ----------------

st.title("🚀 COSMOS X ANDR V13 QUANT FINAL")

col1, col2 = st.columns(2)

with col1:
    h = st.text_input("HASH INPUT")
    t = st.text_input("LAST TIME")

    if st.button("RUN ENGINE"):
        if h:
            st.session_state.res = compute(h, t)

with col2:
    if st.button("🗑️ RESET DATA"):
        reset_db()
        st.success("RESET DONE")

if "res" in st.session_state:
    r = st.session_state.res

    st.markdown(f"""
    <div class="card">
        <h2>{r['signal']}</h2>
        <p>ENTRY: {r['entry']}</p>
        <p>COTE: {r['cote']}</p>
        <p>PROB: {r['prob']}</p>
        <p>REF: {r['ref']} | TREND: {r['trend']}</p>
        <p>VOL: {r['vol']}</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("HISTORY")
st.dataframe(load_db())
