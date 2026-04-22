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
# Nahitsy: Natao ao anatin'ny project folder mba tsy hisy error permission
DATA_DIR = Path("cosmos_x_data")
DATA_DIR.mkdir(exist_ok=True)

DB_FILE = DATA_DIR / "cosmos_omega.db"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# ================= PREMIUM STYLING OMEGA =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #0d0033 0%, #000005 50%, #001a0d 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            radial-gradient(1.5px 1.5px at 20% 30%, #ffffff88, transparent),
            radial-gradient(1px 1px at 80% 10%, #00ffcc44, transparent),
            radial-gradient(1px 1px at 50% 60%, #ff00ff33, transparent),
            radial-gradient(2px 2px at 35% 85%, #00ffcc55, transparent),
            radial-gradient(1px 1px at 65% 45%, #ffffff22, transparent);
        background-size: 400px 400px, 350px 350px, 300px 300px, 450px 450px, 250px 250px;
        animation: stars-drift 80s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes stars-drift {
        from { background-position: 0 0, 0 0, 0 0, 0 0, 0 0; }
        to { background-position: 400px 400px, -350px 350px, 300px -300px, -450px -450px, 250px 250px; }
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
        font-size: 3.8rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #00ffcc);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 4s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .subtitle-omega {
        text-align: center;
        color: #00ffcc99;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        letter-spacing: 0.5em;
        margin-bottom: 2rem;
    }

    .entry-time-omega {
        font-family: 'Orbitron', sans-serif;
        font-size: 5.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00ffcc, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 40px #00ffccaa);
    }

    .x3-prob-omega {
        font-size: 5rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        background: linear-gradient(135deg, #ff00ff, #ff3399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .signal-ultra-x3 { color: #00ffcc; text-align: center; font-family: 'Orbitron'; font-size: 1.8rem; font-weight: 900; }
    .signal-strong-x3 { color: #ff00ff; text-align: center; font-family: 'Orbitron'; font-size: 1.6rem; font-weight: 700; }
    .signal-good-x3 { color: #00ff88; text-align: center; font-family: 'Orbitron'; font-size: 1.4rem; font-weight: 700; }
    .signal-skip { color: #ff4444; text-align: center; font-family: 'Orbitron'; font-size: 1.2rem; font-weight: 600; }

    .sec-label-omega {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.65rem;
        letter-spacing: 0.4em;
        color: #00ffcc66;
        text-transform: uppercase;
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
            entry_time TEXT, signal TEXT, x3_prob REAL, x3_5_prob REAL,
            x4_prob REAL, confidence REAL, strength REAL,
            min_target REAL, moy_target REAL, max_target REAL,
            result TEXT, real_cote REAL
        )
    """)
    conn.commit()
    return conn

def save_prediction(data):
    with db_init() as conn:
        conn.execute("""
            INSERT INTO predictions 
            (timestamp, hash_input, time_input, last_cote, entry_time, signal, 
             x3_prob, x3_5_prob, x4_prob, confidence, strength, 
             min_target, moy_target, max_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['timestamp'], data['hash'], data['time'], data['last_cote'],
            data['entry'], data['signal'], data['x3_prob'], data.get('x3_5_prob'),
            data.get('x4_prob'), data['conf'], data['strength'],
            data['min'], data['moy'], data['max']
        ))

def update_result(p_id, res, cote=None):
    with db_init() as conn:
        conn.execute("UPDATE predictions SET result = ?, real_cote = ? WHERE id = ?", (res, cote, p_id))

def get_stats():
    try:
        with db_init() as conn:
            s = conn.execute("""
                SELECT COUNT(*), 
                SUM(CASE WHEN result = 'x3_hit' THEN 1 ELSE 0 END),
                SUM(CASE WHEN result = 'x3_miss' THEN 1 ELSE 0 END)
                FROM predictions
            """).fetchone()
            total, hits, miss = s
            rate = (hits / (hits + miss) * 100) if (hits and (hits+miss)>0) else 0.0
            return {'total': total, 'hits': hits or 0, 'miss': miss or 0, 'rate': round(rate, 1)}
    except:
        return {'total': 0, 'hits': 0, 'miss': 0, 'rate': 0.0}

# ================= ENGINE =================
def run_omega(hash_in, time_in, last_c):
    h_hex = hashlib.sha256(hash_in.encode()).hexdigest()
    np.random.seed(int(h_hex[:8], 16))
    sims = np.random.lognormal(np.log(2.1), 0.22, 200000)
    
    x3_p = round(float(np.mean(sims >= 3.0)) * 100, 2)
    conf = round(float(x3_p * 1.2 + last_c * 5), 2)
    strength = round(float(x3_p * 0.8 + 20), 2)
    
    try:
        t_base = datetime.strptime(time_in.strip(), "%H:%M:%S")
     dream_time = (t_base + timedelta(seconds=45)).strftime("%H:%M:%S")
    except:
        dream_time = "00:00:00"

    res = {
        'timestamp': datetime.now().isoformat(), 'hash': hash_in, 'time': time_in, 'last_cote': last_c,
        'entry': dream_time, 'x3_prob': x3_p, 'x3_5_prob': round(x3_p*0.7, 2), 'x4_prob': round(x3_p*0.4, 2),
        'conf': min(99, conf), 'strength': min(99, strength), 'min': 1.5, 'moy': 2.5, 'max': 4.0,
        'signal': "💎 ULTRA X3+" if x3_p > 40 else "🟢 GOOD", 'signal_class': "signal-ultra-x3" if x3_p > 40 else "signal-good-x3"
    }
    save_prediction(res)
    return res

# ================= APP LOGIC =================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    key = st.text_input("OMEGA KEY", type="password")
    if st.button("LOGIN"):
        if key == "COSMOS2026": 
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.markdown("<h1 class='main-title'>COSMOS X OMEGA</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 STATS")
    s = get_stats()
    st.metric("TOTAL", s['total'])
    st.metric("WIN RATE", f"{s['rate']}%")

c1, c2 = st.columns([1, 2])

with c1:
    h = st.text_input("HASH")
    t = st.text_input("TIME (HH:MM:SS)")
    lc = st.number_input("LAST COTE", value=2.0)
    if st.button("ANALYSE"):
        st.session_state.res = run_omega(h, t, lc)
        with db_init() as conn:
            st.session_state.p_id = conn.execute("SELECT MAX(id) FROM predictions").fetchone()[0]

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown(f"<div class='{r['signal_class']}'>{r['signal']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-omega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='x3-prob-omega'>{r['x3_prob']}%</div>", unsafe_allow_html=True)
        
        if st.button("✅ HIT"):
            update_result(st.session_state.p_id, "x3_hit")
            st.success("Saved!")
        if st.button("❌ MISS"):
            update_result(st.session_state.p_id, "x3_miss")
            st.error("Saved!")

st.markdown("---")
with db_init() as conn:
    history = pd.read_sql("SELECT * FROM predictions ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(history, use_container_width=True)        
