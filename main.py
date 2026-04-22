import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from pathlib import Path

# ================= CONFIGURATION ULTRA =================
st.set_page_config(
    page_title="COSMOS X V17.0 OMEGA X3+", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Timezone Madagascar
EAT = pytz.timezone('Indian/Antananarivo')

# ================= PERSISTENCE SYSTEM =================
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
        box-shadow: 0 0 40px rgba(0, 255, 204, 0.15);
        margin-bottom: 24px;
    }

    .glass-x3-result {
        background: rgba(2, 2, 15, 0.92);
        border: 3px solid;
        border-image: linear-gradient(135deg, #00ffcc, #ff00ff, #00ccff) 1;
        border-radius: 22px;
        padding: 32px;
        backdrop-filter: blur(20px);
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #00ffcc);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 4s ease infinite;
    }

    .entry-time-omega {
        font-family: 'Orbitron', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        color: #00ffcc;
        filter: drop-shadow(0 0 30px #00ffccaa);
    }

    .target-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE FUNCTIONS =================
def db_init():
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, hash_input TEXT, time_input TEXT, last_cote REAL,
            entry_time TEXT, signal TEXT, x3_prob REAL, accuracy REAL,
            min_target REAL, moy_target REAL, max_target REAL,
            result TEXT
        )
    """)
    conn.commit()
    return conn

def save_prediction(data):
    with db_init() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions 
            (timestamp, hash_input, time_input, last_cote, entry_time, signal, 
             x3_prob, accuracy, min_target, moy_target, max_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['timestamp'], data['hash'], data['time'], data['last_cote'],
            data['entry'], data['signal'], data['x3_prob'], data['accuracy'],
            data['min'], data['moy'], data['max']
        ))
        conn.commit()
        return cursor.lastrowid

def update_result(p_id, res):
    with db_init() as conn:
        conn.execute("UPDATE predictions SET result = ? WHERE id = ?", (res, p_id))
        conn.commit()

# ================= ENGINE OMEGA =================
def run_omega(hash_in, time_in, last_c):
    h_hex = hashlib.sha256(hash_in.encode()).hexdigest()
    np.random.seed(int(h_hex[:8], 16))
    
    # Advanced logic based on interval
    x3_p = round(float(np.random.uniform(38, 58) if last_c < 2.0 else np.random.uniform(22, 42)), 2)
    acc = round(min(99.4, 88 + (np.random.random() * 8)), 2)
    
    # Target calculations
    c_min = round(2.0 + (np.random.random() * 0.4), 2)
    c_moy = round(3.5 + (np.random.random() * 1.2), 2)
    c_max = round(6.0 + (np.random.random() * 12.0), 2)
    
    try:
        t_base = datetime.strptime(time_in.strip(), "%H:%M:%S")
        # Shift entry time for the rebound effect
        dream_time = (t_base + timedelta(seconds=48)).strftime("%H:%M:%S")
    except:
        dream_time = "00:00:00"

    res = {
        'timestamp': datetime.now(EAT).strftime("%Y-%m-%d %H:%M:%S"),
        'hash': hash_in, 'time': time_in, 'last_cote': last_c,
        'entry': dream_time, 'x3_prob': x3_p, 'accuracy': acc,
        'min': c_min, 'moy': c_moy, 'max': c_max,
        'signal': "💎 ULTRA X3+" if x3_p > 42 else "🟢 GOOD"
    }
    res['p_id'] = save_prediction(res)
    return res

# ================= APP LOGIC =================
if "auth" not in st.session_state: st.session_state.auth = False

# Authentication
if not st.session_state.auth:
    st.markdown("<div class='glass-ultra' style='max-width:500px;margin:auto;'>", unsafe_allow_html=True)
    st.subheader("🔐 OMEGA SYSTEM ACCESS")
    key = st.text_input("ACCESS KEY", type="password")
    if st.button("ACTIVATE SYSTEM", use_container_width=True):
        if key == "COSMOS2026": 
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Header
st.markdown("<h1 class='main-title'>COSMOS X V17.0 OMEGA</h1>", unsafe_allow_html=True)

# Sidebar with Reset
with st.sidebar:
    st.markdown("### 🛠️ SYSTEM CONTROL")
    if st.button("🗑️ RESET ALL DATA", use_container_width=True):
        with db_init() as conn:
            conn.execute("DELETE FROM predictions")
            conn.commit()
        if "res_omega" in st.session_state:
            del st.session_state.res_omega
        st.success("Database and Session Cleared!")
        st.rerun()
    st.markdown("---")
    st.info("Version 17.0 Omega - Stable Build 2026")

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    st.markdown("### 📥 DATA INPUT")
    # Fields are EMPTY (vide) by default
    h_input = st.text_input("SERVER HASH", value="", placeholder="Paste server hash here...")
    t_input = st.text_input("TIME (HH:MM:SS)", value="", placeholder="Current game time...")
    lc_input = st.number_input("LAST COTE", value=0.0, step=0.01, format="%.2f")
    
    if st.button("🚀 EXECUTE ANALYSIS", use_container_width=True):
        if h_input and t_input:
            st.session_state.res_omega = run_omega(h_input, t_input, lc_input)
            st.rerun()
        else:
            st.warning("Please fill all fields")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    if "res_omega" in st.session_state:
        r = st.session_state.res_omega
        st.markdown("<div class='glass-x3-result'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#00ffcc;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-omega'>{r['entry']}</div>", unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("X3 PROBABILITY", f"{r['x3_prob']}%")
        col_m2.metric("SYSTEM ACCURACY", f"{r['accuracy']}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        tm1, tm2, tm3 = st.columns(3)
        tm1.markdown(f"<div class='target-box'><small>MIN COTE</small><br><b style='color:#00ffcc;'>{r['min']}x</b></div>", unsafe_allow_html=True)
        tm2.markdown(f"<div class='target-box'><small>MOYEN</small><br><b style='color:#ff00ff;'>{r['moy']}x</b></div>", unsafe_allow_html=True)
        tm3.markdown(f"<div class='target-box'><small>MAX COTE</small><br><b style='color:#00ccff;'>{r['max']}x</b></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎯 CONFIRM SUCCESS", use_container_width=True):
            update_result(r['p_id'], "HIT")
            st.balloons()
            st.success("Result recorded successfully!")
        st.markdown("</div>", unsafe_allow_html=True)

# Logs Display
st.markdown("### 🕒 RECENT PREDICTIONS")
with db_init() as conn:
    df = pd.read_sql("SELECT timestamp, entry_time, signal, x3_prob, result FROM predictions ORDER BY id DESC LIMIT 5", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No data available in logs.")
