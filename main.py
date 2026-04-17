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

st.set_page_config(page_title="COSMOS X ANDR V12.1 PRO", layout="wide")

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

DB = "cosmos_v12.db"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        h_actual TEXT,
        h_tour TEXT,
        h_entry TEXT,
        cote_moy REAL,
        signal TEXT,
        confidence REAL
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h_act, h_tour, h_entry, cote, sig, conf):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (h_actual, h_tour, h_entry, cote_moy, signal, confidence)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (h_act, h_tour, h_entry, cote, sig, conf))
    conn.commit()
    conn.close()

def load_db():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df

def reset_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS history")
    conn.commit()
    conn.close()
    init_db()

# ---------------- AUTH ----------------

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 SECURITY ACCESS")
    pwd = st.text_input("ENTER KEY", type="password")

    if st.button("ACTIVATE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("INVALID KEY")
    st.stop()

# ---------------- CORE ----------------

def now_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_to_float(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10], 16) / 0xFFFFFFFFFF

# ---------------- AUTO REF + TREND ----------------

def auto_ref(df):
    if len(df) < 5:
        return 1.7, 0, "NEUTRAL"

    recent = df.head(10)

    weights = np.linspace(1, 2, len(recent))
    w_mean = np.average(recent["cote_moy"], weights=weights)

    x = np.arange(len(recent))
    y = recent["cote_moy"].values
    slope = np.polyfit(x, y, 1)[0]

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
    return round(ref, 2), slope, trend

# ---------------- AI MODEL ----------------

def train_ai(df):
    if len(df) < 10:
        return None, None

    df = df.copy()
    df["h_val"] = df["h_actual"].apply(hash_to_float)

    X = df[["h_val", "confidence"]]
    y = df["cote_moy"]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=80, random_state=42)
    model.fit(Xs, y)

    return model, scaler

# ---------------- ENGINE ----------------

def compute(hash_input, last_time, cote_ref):

    now = now_time()
    now_sec = now.hour * 3600 + now.minute * 60 + now.second

    h_val = hash_to_float(hash_input)

    df = load_db()

    # -------- AUTO REF --------
    ref, slope, trend = auto_ref(df)

    # -------- VOLATILITY --------
    vol = df["cote_moy"].std() if len(df) > 5 else 1.0

    # -------- ULTRA TIME FORMULA --------
    cycle = 120
    t = now_sec % cycle

    wave = np.sin(2 * np.pi * (t / cycle))
    entropy = np.sqrt(h_val)
    v = min(1.5, max(0.5, vol / 2))

    mode = st.session_state.get("mode", "SNIPER")

    if mode == "SAFE":
        a, b, c, S = 8, 6, 10, 0.8
    else:
        a, b, c, S = 15, 12, 18, 1.2

    delay = (a * wave + b * entropy + c * v) * S

    if abs(wave) > 0.85 and mode == "SNIPER":
        delay *= 0.7

    delay = int(np.clip(delay, 8, 110))
    entry = now + timedelta(seconds=delay)

    # -------- COTE --------
    t_factor = (wave + 1) / 2
    momentum = (h_val * 0.6) + (t_factor * 0.4)

    base = 1.2 + (h_val * 3.5) + (t_factor * 1.5) + (ref * 0.2)

    boost = np.random.uniform(1.1, 1.3) if momentum > 0.7 else np.random.uniform(0.9, 1.05)

    cote = round(base * boost, 2)

    # -------- CONFIDENCE --------
    conf = round(min(99.9, (momentum ** 1.6) * 100), 1)

    # -------- SIGNAL --------
    if conf >= 85 and cote >= 2.8:
        sig = "🔥 ULTRA X3+ SNIPER"
    elif conf >= 70:
        sig = "🟢 STRONG ENTRY"
    elif conf >= 50:
        sig = "🟡 WAIT"
    else:
        sig = "🔴 NO ENTRY"

    save_db(hash_input, last_time, entry.strftime("%H:%M:%S"), cote, sig, conf)

    return {
        "entry": entry.strftime("%H:%M:%S"),
        "cote": cote,
        "conf": conf,
        "signal": sig,
        "ref": ref,
        "trend": trend,
        "slope": round(slope, 3)
    }

# ---------------- UI ----------------

st.title("🚀 COSMOS X ANDR V12.1 PRO")

st.sidebar.selectbox("MODE", ["SNIPER", "SAFE"], key="mode")

h = st.text_input("HASH")
t = st.text_input("LAST TIME")
c = st.number_input("REF", value=1.7)

if st.button("RUN"):
    if h and t:
        st.session_state.res = compute(h, t, c)

if "res" in st.session_state:
    r = st.session_state.res
    st.markdown(f"""
    <div class="card">
        <h2>{r['signal']}</h2>
        <p>ENTRY: {r['entry']}</p>
        <p>COTE: {r['cote']}</p>
        <p>CONF: {r['conf']}%</p>
        <p>REF: {r['ref']} | TREND: {r['trend']} | SLOPE: {r['slope']}</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("HISTORY")
st.dataframe(load_db())
