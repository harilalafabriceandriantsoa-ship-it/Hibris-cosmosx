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
        font-size: 4rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        background: linear-gradient(135deg, #ff00ff, #ff3399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .target-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(0, 255, 204, 0.3);
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
        cursor = conn.cursor()
        cursor.execute("""
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
        conn.commit()
        return cursor.lastrowid

def update_result(p_id, res, cote=None):
    with db_init() as conn:
        conn.execute("UPDATE predictions SET result = ?, real_cote = ? WHERE id = ?", (res, cote, p_id))
        conn.commit()

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

# ================= ENGINE OMEGA =================
def run_omega(hash_in, time_in, last_c):
    h_hex = hashlib.sha256(hash_in.encode()).hexdigest()
    np.random.seed(int(h_hex[:8], 16))
    sims = np.random.lognormal(np.log(2.1), 0.22, 200000)
    
    x3_p = round(float(np.mean(sims >= 3.0)) * 100, 2)
    conf = round(float(x3_p * 1.2 + last_c * 5), 2)
    strength = round(float(x3_p * 0.8 + 20), 2)
    
    # Accuracy Logic
    acc = round(min(99.1, strength + (np.random.random() * 5)), 2)
    
    # Targets Logic
    c_min = round(1.5 + (np.random.random() * 0.5), 2)
    c_moy = round(2.5 + (np.random.random() * 1.0), 2)
    c_max = round(4.0 + (np.random.random() * 3.0), 2)
    
    try:
        t_base = datetime.strptime(time_in.strip(), "%H:%M:%S")
        dream_time = (t_base + timedelta(seconds=45)).strftime("%H:%M:%S")
    except:
        dream_time = "00:00:00"

    res = {
        'timestamp': datetime.now().isoformat(), 'hash': hash_in, 'time': time_in, 'last_cote': last_c,
        'entry': dream_time, 'x3_prob': x3_p, 'x3_5_prob': round(x3_p*0.7, 2), 'x4_prob': round(x3_p*0.4, 2),
        'conf': min(99, conf), 'strength': min(99, strength), 'accuracy': acc,
        'min': c_min, 'moy': c_moy, 'max': c_max,
        'signal': "💎 ULTRA X3+" if x3_p > 40 else "🟢 GOOD", 
        'signal_class': "signal-ultra-x3" if x3_p > 40 else "signal-good-x3"
    }
    # Tehirizina ny ID mba tsy hiala rehefa avadika
    res['p_id'] = save_prediction(res)
    return res

# ================= APP LOGIC =================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div class='glass-ultra' style='max-width:500px;margin:auto;'>", unsafe_allow_html=True)
    key = st.text_input("OMEGA ACCESS KEY", type="password")
    if st.button("ACTIVATE SYSTEM"):
        if key == "COSMOS2026": 
            st.session_state.auth = True
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown("<h1 class='main-title'>COSMOS X V17.0 OMEGA</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### PERFORMANCE")
    s = get_stats()
    st.metric("TOTAL", s['total'])
    st.metric("RATE", f"{s['rate']}%")
    if st.button("CLEAR HISTORY"):
        with db_init() as conn:
            conn.execute("DELETE FROM predictions")
            st.rerun()

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    h = st.text_input("SERVER HASH")
    t = st.text_input("TIME (HH:MM:SS)", value=datetime.now().strftime("%H:%M:%S"))
    lc = st.number_input("LAST COTE", value=2.0, step=0.1)
    if st.button("🚀 EXECUTE ANALYSIS", use_container_width=True):
        if h and t:
            # Rehefa ampidirina anaty session_state dia tsy miala intsony
            st.session_state.res = run_omega(h, t, lc)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown("<div class='glass-x3-result'>", unsafe_allow_html=True)
        st.markdown(f"<div class='{r['signal_class']}'>{r['signal']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-omega'>{r['entry']}</div>", unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.markdown(f"<div class='x3-prob-omega'>{r['x3_prob']}%</div><p style='text-align:center;'>PROBABILITY</p>", unsafe_allow_html=True)
        col_m2.markdown(f"<div class='x3-prob-omega' style='color:#00ffcc;'>{r['accuracy']}%</div><p style='text-align:center;'>ACCURACY</p>", unsafe_allow_html=True)
        
        # Target Section
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        t1.markdown(f"<div class='target-box'><small>MIN</small><br><b>{r['min']}x</b></div>", unsafe_allow_html=True)
        t2.markdown(f"<div class='target-box'><small>MOYEN</small><br><b>{r['moy']}x</b></div>", unsafe_allow_html=True)
        t3.markdown(f"<div class='target-box'><small>MAX</small><br><b>{r['max']}x</b></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_act1, col_act2 = st.columns(2)
        if col_act1.button("🎯 SUCCESS"):
            update_result(r['p_id'], "x3_hit")
            st.rerun()
        if col_act2.button("❌ FAILED"):
            update_result(r['p_id'], "x3_miss")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
with db_init() as conn:
    df = pd.read_sql("SELECT timestamp, entry_time, signal, x3_prob, result FROM predictions ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df, use_container_width=True)
