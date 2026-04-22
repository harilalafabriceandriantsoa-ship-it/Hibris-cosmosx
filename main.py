import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
import json
import os
from pathlib import Path

# ================= CONFIGURATION ULTRA =================
st.set_page_config(
    page_title="COSMOS X V17.0 OMEGA X3+", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ================= PERSISTENCE SYSTEM =================
# Ity fizarana ity no miantoka fa tsy ho voafafa ny data-nao
DATA_DIR = Path("cosmos_x_data")
DATA_DIR.mkdir(exist_ok=True)

DB_FILE = DATA_DIR / "cosmos_omega.db"

# ================= PREMIUM STYLING OMEGA =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #0d0033 0%, #000005 50%, #001a0d 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    .glass-ultra {
        background: rgba(5, 5, 20, 0.85);
        border: 2px solid rgba(0, 255, 204, 0.4);
        border-radius: 22px;
        padding: 28px;
        backdrop-filter: blur(16px);
        margin-bottom: 24px;
    }

    .glass-x3-result {
        background: rgba(2, 2, 15, 0.92);
        border: 3px solid #00ffcc;
        border-radius: 22px;
        padding: 32px;
        backdrop-filter: blur(20px);
        box-shadow: 0 0 60px rgba(0, 255, 204, 0.25);
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .entry-time-omega {
        font-family: 'Orbitron', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 30px #00ffcc88;
        margin: 20px 0;
    }

    .x3-prob-omega {
        font-size: 4.5rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        color: #ff00ff;
        margin: 15px 0;
    }

    .metric-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
    }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0088ff 100%) !important;
        color: #000 !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE FUNCTIONS =================
def db_init():
    conn = sqlite3.connect(str(DB_FILE))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            hash_input TEXT,
            time_input TEXT,
            entry_time TEXT,
            signal TEXT,
            x3_prob REAL,
            confidence REAL,
            min_target REAL,
            moy_target REAL,
            max_target REAL,
            result TEXT
        )
    """)
    conn.commit()
    return conn

def save_prediction(data):
    with db_init() as conn:
        conn.execute("""
            INSERT INTO predictions 
            (timestamp, hash_input, time_input, entry_time, signal, x3_prob, confidence, min_target, moy_target, max_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['timestamp'], data['hash'], data['time'], data['entry'], data['signal'],
            data['x3_prob'], data['conf'], data['min'], data['moy'], data['max']
        ))

def update_result(pred_id, result):
    with db_init() as conn:
        conn.execute("UPDATE predictions SET result = ? WHERE id = ?", (result, pred_id))

# ================= ENGINE OMEGA X3 =================
def run_engine_omega(hash_in, time_in, last_cote):
    hash_hex = hashlib.sha256(hash_in.encode()).hexdigest()
    hash_num = int(hash_hex[:16], 16)
    np.random.seed(hash_num & 0xFFFFFFFF)
    
    # Simulation ultra-précise (200,000 sims)
    sims = np.random.lognormal(np.log(2.1), 0.22, 200_000)
    x3_prob = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    # Targets
    moy = round(float(np.mean(sims)), 2)
    maxv = round(float(np.percentile(sims, 98)), 2)
    minv = round(float(np.percentile(sims, 2)), 2)
    conf = round(max(45, min(99, x3_prob * 1.2 + (hash_num % 15))), 2)

    # Entry Time logic
    try:
        base_t = datetime.strptime(time_in.strip(), "%H:%M:%S")
        entry_t = (base_t + timedelta(seconds=45 + (hash_num % 40))).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now().strftime("%H:%M:%S")

    signal = "💎 ULTRA X3+ (OMEGA)" if x3_prob > 42 else "🔥 STRONG X3+" if x3_prob > 35 else "⚠️ SKIP"
    
    res = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'hash': hash_in, 'time': time_in, 'entry': entry_t,
        'signal': signal, 'x3_prob': x3_prob, 'conf': conf,
        'min': minv, 'moy': moy, 'max': maxv
    }
    save_prediction(res)
    return res

# ================= MAIN APP =================
st.markdown("<h1 class='main-title'>COSMOS X V17.0 OMEGA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc99;'>VERSION FRANÇAISE • SYSTÈME PERSISTANT</p>", unsafe_allow_html=True)

if "last_res" not in st.session_state:
    st.session_state.last_res = None

col_in, col_res = st.columns([1, 2])

with col_in:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    st.subheader("📥 PARAMÈTRES")
    h_input = st.text_input("SERVER HASH")
    t_input = st.text_input("TIME (HH:MM:SS)")
    l_cote = st.number_input("LAST COTE", value=2.00, step=0.01)
    
    if st.button("🚀 ANALYSER", use_container_width=True):
        if h_input and t_input:
            st.session_state.last_res = run_engine_omega(h_input, t_input, l_cote)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_res:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-x3-result'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-omega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='x3-prob-omega'>{r['x3_prob']}%</div>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-box'>MIN<br><b>{r['min']}x</b></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-box'>MOYEN<br><b>{r['moy']}x</b></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-box'>MAX<br><b>{r['max']}x</b></div>", unsafe_allow_html=True)
        
        if st.button("✅ MARQUER COMME GAGNÉ (HIT)", use_container_width=True):
            with db_init() as conn:
                last_id = conn.execute("SELECT MAX(id) FROM predictions").fetchone()[0]
                update_result(last_id, "WIN ✅")
            st.success("Résultat enregistré !")
        st.markdown("</div>", unsafe_allow_html=True)

# ================= HISTORIQUE (PERSISTANT) =================
st.markdown("### 🕒 HISTORIQUE DES PRÉDICTIONS")
with db_init() as conn:
    df = pd.read_sql("SELECT timestamp, entry_time, signal, x3_prob, result FROM predictions ORDER BY id DESC LIMIT 15", conn)
    st.dataframe(df, use_container_width=True)

if st.sidebar.button("🗑️ RESET DATABASE"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        st.rerun()
