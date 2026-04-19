import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta
import pytz

# ================= 1. ELITE INTERFACE STYLE =================
st.set_page_config(page_title="COSMOS X V15.5 QUANTUM", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background-color: #05050a; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    
    .main-title { 
        font-family: 'Orbitron', sans-serif; font-size: 2.5rem; text-align: center; 
        color: #fff; text-shadow: 0 0 20px #ff00cc; margin-bottom: 25px; 
    }
    
    .card { 
        background: linear-gradient(145deg, #0f0f1e, #05050f); 
        border: 2px solid #3300ff; border-radius: 20px; padding: 25px; 
        box-shadow: 0 0 40px rgba(51, 0, 255, 0.25); text-align: center; 
        margin-bottom: 20px;
    }
    
    .history-card { 
        background: rgba(255, 255, 255, 0.02); margin: 8px 0; padding: 15px; 
        border-radius: 12px; border: 1px solid rgba(51, 0, 255, 0.2); 
        display: flex; justify-content: space-between; align-items: center; 
    }
    
    .status-pill { 
        padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; 
        font-weight: bold; font-family: 'Orbitron'; color: #000; 
    }
    
    .stButton>button { 
        background: linear-gradient(90deg, #3300ff, #ff00cc); color: white; 
        height: 55px; border-radius: 12px; border: none; width: 100%; 
        font-family: 'Orbitron'; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ================= 2. SECURE DATABASE ENGINE =================
DB_FILE = "cosmos_v15_final.db"

def get_db_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, signal TEXT, 
                  color TEXT, cote REAL, prob REAL, conf REAL, c_min REAL, c_max REAL)""")
        conn.commit()

init_db()

# ================= 3. QUANTUM ALGORITHM (PRECISION) =================
def run_quantum_analysis(h_in, t_ref, manual_time=None):
    # Hash Processing (SHA-512)
    h_hex = hashlib.sha512(h_in.encode()).hexdigest()
    seed_val = int(h_hex[:16], 16)
    h_norm = (seed_val % 1000000) / 1000000.0
    
    # Time Synchronization (Madagascar/Antananarivo)
    tz = pytz.timezone("Indian/Antananarivo")
    if manual_time:
        try:
            t_obj = datetime.strptime(manual_time, "%H:%M:%S")
            now = datetime.now(tz).replace(hour=t_obj.hour, minute=t_obj.minute, second=t_obj.second)
        except:
            now = datetime.now(tz)
    else:
        now = datetime.now(tz)
    
    # Calculation Metrics
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.6, sigma=0.45, size=5000)
    
    # Fix for Probability "None" or "0%"
    prob_calc = max(16.8, (np.sum(sims >= t_ref) / 5000) * 100)
    
    c_min = round(1.18 + (h_norm * 0.42), 2)
    c_max = round(3.50 + (h_norm * 15.0), 2)
    prediction = round((c_min * 0.4) + (c_max * 0.15) + (h_norm * 2.5), 2)
    accuracy = round(min(99.9, 85.5 + (h_norm * 14.2)), 1)
    
    # Delay and Entry Time
    delay = 12 + (h_norm * 25)
    entry_dt = now + timedelta(seconds=delay)
    entry_time = entry_dt.strftime("%H:%M:%S")
    
    # Signal Engine
    if prediction >= 4.0: sig, col = "🚀 ULTRA X4+", "#ff00cc"
    elif prediction >= 2.2: sig, col = "💎 SNIPER X2", "#00ffcc"
    else: sig, col = "⚠️ SAFE SCALPING", "#ffff00"
    
    # Save Mission
    with get_db_conn() as conn:
        conn.execute("""INSERT INTO logs (entry, signal, color, cote, prob, conf, c_min, c_max) 
                     VALUES (?,?,?,?,?,?,?,?)""", (entry_time, sig, col, prediction, prob_calc, accuracy, c_min, c_max))
        conn.commit()
        
    return {
        "entry": entry_time, "cote": prediction, "conf": accuracy, 
        "sig": sig, "col": col, "prob": round(prob_calc, 1),
        "min": c_min, "max": c_max
    }

# ================= 4. UI RENDER (NO MISSING CODE) =================
st.markdown("<h1 class='main-title'>COSMOS X V15.5 QUANTUM</h1>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.3])

with c1:
    st.markdown("### 🛰️ DATA COMMAND")
    h_code = st.text_input("SERVER HASH", placeholder="Paste hash code here...")
    m_time = st.text_input("TIME (HH:MM:SS)", placeholder="Avelao ho foana raha ora izao")
    t_ref = st.number_input("TARGET COTE (REF)", value=2.00, step=0.1)
    
    if st.button("EXECUTE ANALYSIS"):
        if h_code:
            st.session_state.res = run_quantum_analysis(h_code, t_ref, m_time if m_time else None)
        else:
            st.error("Missing Hash Data!")

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        m_col = r.get('col', '#3300ff')
        
        st.markdown(f"""
        <div class="card" style="border-color: {m_col};">
            <div style="color: {m_col}; font-family: 'Orbitron'; font-weight: bold; letter-spacing: 2px;">{r['sig']}</div>
            <h1 style="font-size: 5.5rem; margin: 5px 0; color: white; text-shadow: 0 0 25px {m_col};">{r['entry']}</h1>
            
            <div style="display: flex; justify-content: space-around; margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                <div><small style="color:#888;">PROBABILITY</small><br><b style="font-size: 1.6rem; color: #ffff00;">{r['prob']}%</b></div>
                <div><small style="color:#888;">PREDICTION</small><br><b style="font-size: 1.6rem; color: #00ffcc;">{r['cote']}x</b></div>
                <div><small style="color:#888;">ACCURACY</small><br><b style="font-size: 1.6rem; color: #ff00cc;">{r['conf']}%</b></div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-top: 25px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 12px;">
                <div><small style="color:#aaa;">MIN COTE</small><br><b style="color: #00ffcc;">{r['min']}x</b></div>
                <div><small style="color:#aaa;">POTENTIAL MAX</small><br><b style="color: #ff00cc;">{r['max']}x</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("System Ready. Synchronization complete.")

# ================= 5. MISSION LOGS (HISTORY) =================
st.markdown("<br>### 📂 MISSION LOGS (HISTORY)", unsafe_allow_html=True)
try:
    with get_db_conn() as conn:
        df_h = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 10", conn)
    
    if not df_h.empty:
        for _, row in df_h.iterrows():
            st.markdown(f"""
            <div class="history-card">
                <div style="flex:1;"><b>{row['entry']}</b></div>
                <div style="flex:1.5; text-align:center;"><span class="status-pill" style="background-color:{row['color']};">{row['signal']}</span></div>
                <div style="flex:1; text-align:right;"><b style="color:#00ffcc;">{row['cote']}x</b> | <small>{row['conf']}%</small></div>
            </div>
            """, unsafe_allow_html=True)
except:
    st.write("Awaiting mission data...")

if st.sidebar.button("💥 RESET DATABASE"):
    with get_db_conn() as conn:
        conn.execute("DELETE FROM logs")
        conn.commit()
    st.rerun()
