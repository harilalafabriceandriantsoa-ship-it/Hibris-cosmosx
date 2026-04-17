import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & STYLE PREMIUM ----------------

st.set_page_config(page_title="COSMOS X ANDR V12.1 AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');
    
    .stApp {
        background-color: #05050A;
        background-image: radial-gradient(circle at 50% 0%, #002222 0%, #05050A 70%);
        color: #00ffcc;
        font-family: 'Share Tech Mono', monospace;
    }
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00ffcc;
        text-shadow: 0 0 15px rgba(0,255,204,0.5);
        text-align: center;
        letter-spacing: 2px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #004d4d, #00ffcc) !important;
        color: black !important;
        font-weight: bold !important;
        font-family: 'Orbitron', sans-serif;
        border: none;
        height: 50px;
        border-radius: 12px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px #00ffcc;
        transform: translateY(-2px);
    }
    .prediction-card {
        padding: 25px;
        border: 2px solid #00ffcc;
        border-radius: 20px;
        background: rgba(0, 20, 20, 0.8);
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);
        margin-bottom: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

DB = "cosmos_v12.db"

# ---------------- DATABASE SYSTEM ----------------

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

def load_db_full():
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

# ---------------- SECURITY ----------------

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1>🔐 SECURITY ACCESS</h1>", unsafe_allow_html=True)
    pwd = st.text_input("ENTER TERMINAL KEY", type="password")
    if st.button("ACTIVATE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("INVALID KEY")
    st.stop()

# ---------------- CORE LOGIC ----------------

def get_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_to_num(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    # Logarithmic normalization base
    return int(h[:10], 16) / 0xFFFFFFFFFF

def train_ai():
    df = load_db_full()
    if len(df) < 5:
        return None, None
    df_copy = df.copy()
    df_copy['h_val'] = df_copy['h_actual'].apply(hash_to_num)
    X = df_copy[['h_val', 'confidence']]
    y = df_copy['cote_moy']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    return model, scaler

# ---------------- MATH & ENGINE ----------------

def compute_engine(hash_input, last_tour_time, cote_ref):
    now = get_now()
    now_sec = now.hour * 3600 + now.minute * 60 + now.second
    
    h_hex = hashlib.sha256(hash_input.encode()).hexdigest()
    h_int = int(h_hex[:10], 16)
    h_val = h_int / 0xFFFFFFFFFF
    
    # 1. VOLATILITY ANALYSIS (Standard Deviation)
    df_hist = load_db_full()
    volatility = 1.0
    if len(df_hist) >= 10:
        volatility = df_hist['cote_moy'].head(10).std()
        if np.isnan(volatility): volatility = 1.0

    # 2. LOGARITHMIC DISTRIBUTION (Scaling)
    # Ampiasaina ny log mba hampihenana ny dispersion ny cotes ambony be
    base_prediction = 1.1 + (np.log1p(h_val * 10) * 1.5)
    
    # AI Integration
    model, scaler = train_ai()
    if model and scaler:
        X_input = np.array([[h_val, 75.0]])
        X_input_scaled = scaler.transform(X_input)
        ai_val = model.predict(X_input_scaled)[0]
        final_cote = (base_prediction * 0.3) + (ai_val * 0.7)
    else:
        final_cote = base_prediction

    # 3. ULTRA TIME ENGINE (V13 Layering)
    h_parts = [int(h_hex[i:i+6], 16) for i in range(8, 32, 6)]
    base_delay = 12 + (h_int % 25)
    layers_sum = sum([p % (14 - i) for i, p in enumerate(h_parts)])
    
    mode_val = st.session_state.get('mode', 'SNIPER')
    mode_bias = 12 if mode_val == "SAFE" else 3
    
    final_delay = base_delay + layers_sum + (now_sec % 15) + mode_bias
    entry_time = now + timedelta(seconds=max(8, min(115, final_delay)))
    
    # Confidence Score with Volatility filter
    raw_conf = (h_val * 100) - (volatility * 2)
    conf = round(max(5.0, min(99.8, raw_conf + (len(df_hist)/2))), 1)
    
    # Signal Logic
    if conf >= 82 and final_cote >= 3:
        sig, col = "🔥 ULTRA X3+ SNIPER 🎯", "#ff00cc"
    elif conf >= 60 and final_cote >= 2:
        sig, col = "🟢 STRONG ENTRY ⚡", "#00ffcc"
    elif conf >= 40:
        sig, col = "🟡 WAITING SIGNAL ⏳", "#ffcc00"
    else:
        sig, col = "🔴 RISK HIGH / NO ENTRY ❌", "#ff4444"

    res = {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "min": round(final_cote * 0.85, 2),
        "moy": round(final_cote, 2),
        "max": round(final_cote * 1.7, 2),
        "conf": conf,
        "sig": sig,
        "color": col,
        "vol": round(volatility, 2)
    }
    
    save_db(hash_input, last_tour_time, res['entry'], res['moy'], sig, conf)
    return res

# ---------------- UI ----------------

st.sidebar.markdown("### ⚙️ SETTINGS")
st.session_state.mode = st.sidebar.radio("ANALYSIS MODE", ["SNIPER", "SAFE"])

if st.sidebar.button("🗑️ CLEAR DATA"):
    reset_db()
    st.sidebar.success("History Purged")
    st.rerun()

st.markdown("<h1>🚀 COSMOS X ANDR V12.1 AI ⚡</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### 📥 INPUT DATA")
    with st.form("main_form"):
        h_in = st.text_input("SERVER HASH")
        t_in = st.text_input("LAST TIME (HH:MM:SS)")
        c_ref = st.number_input("REF COTE", value=2.0)
        if st.form_submit_button("🚀 RUN AI ENGINE"):
            if h_in and t_in:
                st.session_state.prediction = compute_engine(h_in, t_in, c_ref)
            else:
                st.error("Fill all fields")

with col2:
    if "prediction" in st.session_state:
        p = st.session_state.prediction
        st.markdown(f"""
        <div class="prediction-card" style="border-color: {p['color']};">
            <h2 style="color: {p['color']};">{p['sig']}</h2>
            <p>VOLATILITY: {p['vol']} | CONF: {p['conf']}%</p>
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 12px; margin: 15px 0;">
                <small>NEXT ENTRY TIME</small><br>
                <b style="font-size: 2.5rem; color: #fff;">{p['entry']}</b>
            </div>
            <div style="display: flex; justify-content: space-around;">
                <div><small>MIN</small><br><b>{p['min']}x</b></div>
                <div style="color:#00ffcc;"><small>TARGET</small><br><b>{p['moy']}x</b></div>
                <div><small>MAX</small><br><b>{p['max']}x</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("### 📜 PREDICTION HISTORY")
history = load_db_full()
if not history.empty:
    st.dataframe(history[['h_entry', 'cote_moy', 'confidence', 'signal']], use_container_width=True)
