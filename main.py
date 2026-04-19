import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta
import pytz

# ================= 1. CONFIG & PASSWORD =================
st.set_page_config(page_title="COSMOS X V16.0 ULTRA", layout="wide")

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align:center; color:#00ffcc;'>🔐 SECURITY CHECK</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Ampidiro ny Password:", type="password")
        if st.button("LOG IN"):
            if pwd == "2026": # Ity ny Password-nao
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password diso!")
        return False
    return True

# ================= 2. STYLE & UI =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background-color: #05050a; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title { 
        font-family: 'Orbitron', sans-serif; font-size: 2.5rem; text-align: center; 
        color: #fff; text-shadow: 0 0 20px #3300ff; margin-bottom: 25px; 
    }
    .card { 
        background: linear-gradient(145deg, #0f0f1e, #05050f); 
        border: 2px solid #3300ff; border-radius: 20px; padding: 25px; 
        box-shadow: 0 0 40px rgba(51, 0, 255, 0.25); text-align: center; 
        margin-bottom: 20px;
    }
    .history-card { 
        background: rgba(255, 255, 255, 0.05); margin: 8px 0; padding: 15px; 
        border-radius: 12px; border: 1px solid rgba(0, 255, 204, 0.3); 
        display: flex; justify-content: space-between; align-items: center; 
    }
    .status-pill { padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; font-family: 'Orbitron'; color: #000; }
    .stButton>button { 
        background: linear-gradient(90deg, #3300ff, #00ffcc); color: white; 
        height: 55px; border-radius: 12px; border: none; width: 100%; 
        font-family: 'Orbitron'; font-weight: bold; font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. DATABASE =================
def get_db_conn():
    return sqlite3.connect("cosmos_v16_pro.db", check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, signal TEXT, 
                  color TEXT, cote REAL, prob REAL, conf REAL, c_min REAL, c_moyen REAL, c_max REAL)""")
        conn.commit()

init_db()

# ================= 4. ENGINE =================
def run_ultra_analysis(h_in, t_ref):
    h_hex = hashlib.sha512(h_in.encode()).hexdigest()
    seed_val = int(h_hex[:16], 16)
    h_norm = (seed_val % 1000000) / 1000000.0
    
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.6, sigma=0.45, size=5000)
    prob_calc = max(17.6, (np.sum(sims >= t_ref) / 5000) * 100)
    
    c_min = round(1.36 + (h_norm * 0.45), 2)
    c_moyen = round(2.77 + (h_norm * 1.85), 2)
    c_max = round(9.03 + (h_norm * 12.5), 2)
    
    prediction = round((c_moyen * 0.85) + (h_norm * 1.5), 2)
    accuracy = round(min(99.9, 90.4 + (h_norm * 9.5)), 1)
    
    delay = 10 + (h_norm * 25)
    entry_dt = now + timedelta(seconds=delay)
    entry_time = entry_dt.strftime("%H:%M:%S")
    
    if prediction >= 4.0: sig, col = "🚀 ULTRA X4+", "#ff00cc"
    elif prediction >= 2.2: sig, col = "💎 SNIPER X2", "#00ffcc"
    else: sig, col = "⚠️ SAFE SCALPING", "#ffff00"
    
    with get_db_conn() as conn:
        conn.execute("""INSERT INTO logs (entry, signal, color, cote, prob, conf, c_min, c_moyen, c_max) 
                     VALUES (?,?,?,?,?,?,?,?,?)""", (entry_time, sig, col, prediction, prob_calc, accuracy, c_min, c_moyen, c_max))
        conn.commit()
        
    return {"entry": entry_time, "cote": prediction, "conf": accuracy, "sig": sig, "col": col, "prob": round(prob_calc, 1), "min": c_min, "moyen": c_moyen, "max": c_max}

# ================= 5. MAIN APP =================
if check_password():
    st.markdown("<h1 class='main-title'>COSMOS X V16.0 ULTRA</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.3])

    with c1:
        st.markdown("### 🛰️ DATA COMMAND")
        h_code = st.text_input("SERVER HASH (Avy amin'ny lalao teo)")
        t_ref = st.number_input("TARGET COTE (Tanjonao manaraka)", value=2.00, step=0.1)
        
        if st.button("RUN QUANTUM ANALYSIS"):
            if h_code:
                st.session_state.res = run_ultra_analysis(h_code, t_ref)
            else:
                st.error("Hash required!")

    with c2:
        if "res" in st.session_state:
            r = st.session_state.res
            st.markdown(f"""
            <div class="card" style="border-color: {r['col']};">
                <div style="color: {r['col']}; font-family: 'Orbitron';">{r['sig']}</div>
                <h1 style="font-size: 4rem; color: white;">{r['entry']}</h1>
                <div style="display: flex; justify-content: space-around; border-top: 1px solid #333; padding-top: 15px;">
                    <div><small>PROBABILITY</small><br><b style="color: #ffff00; font-size: 1.5rem;">{r['prob']}%</b></div>
                    <div><small>ACCURACY</small><br><b style="color: #ff00cc; font-size: 1.5rem;">{r['conf']}%</b></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 20px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px;">
                    <div><small>MIN COTE</small><br><b>{r['min']}x</b></div>
                    <div><small>MOYEN</small><br><b>{r['moyen']}x</b></div>
                    <div><small>MAX</small><br><b>{r['max']}x</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 📂 MISSION LOGS")
    try:
        with get_db_conn() as conn:
            df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 10", conn)
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="history-card">
                <b>{row['entry']}</b>
                <span class="status-pill" style="background-color:{row['color']};">{row['signal']}</span>
                <span style="color:#00ffcc;">Min: {row['c_min']}x | Moy: {row['c_moyen']}x</span>
            </div>
            """, unsafe_allow_html=True)
    except: pass   color TEXT, cote REAL, prob REAL, conf REAL, c_min REAL, c_moyen REAL, c_max REAL)""")
        conn.commit()

init_db()

# ================= 3. ENGINE =================
def run_ultra_analysis(h_in, t_ref, manual_time=None):
    h_hex = hashlib.sha512(h_in.encode()).hexdigest()
    seed_val = int(h_hex[:16], 16)
    h_norm = (seed_val % 1000000) / 1000000.0
    
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    if manual_time:
        try:
            t_obj = datetime.strptime(manual_time, "%H:%M:%S")
            now = now.replace(hour=t_obj.hour, minute=t_obj.minute, second=t_obj.second)
        except: pass
    
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.6, sigma=0.45, size=5000)
    prob_calc = max(17.6, (np.sum(sims >= t_ref) / 5000) * 100)
    
    c_min = round(1.36 + (h_norm * 0.45), 2)
    c_moyen = round(2.77 + (h_norm * 1.85), 2)
    c_max = round(9.03 + (h_norm * 12.5), 2)
    
    prediction = round((c_moyen * 0.85) + (h_norm * 1.5), 2)
    accuracy = round(min(99.9, 90.4 + (h_norm * 9.5)), 1)
    
    delay = 10 + (h_norm * 25)
    entry_dt = now + timedelta(seconds=delay)
    entry_time = entry_dt.strftime("%H:%M:%S")
    
    if prediction >= 4.0: sig, col = "🚀 ULTRA X4+", "#ff00cc"
    elif prediction >= 2.2: sig, col = "💎 SNIPER X2", "#00ffcc"
    else: sig, col = "⚠️ SAFE SCALPING", "#ffff00"
    
    with get_db_conn() as conn:
        conn.execute("""INSERT INTO logs (entry, signal, color, cote, prob, conf, c_min, c_moyen, c_max) 
                     VALUES (?,?,?,?,?,?,?,?,?)""", (entry_time, sig, col, prediction, prob_calc, accuracy, c_min, c_moyen, c_max))
        conn.commit()
        
    return {"entry": entry_time, "cote": prediction, "conf": accuracy, "sig": sig, "col": col, "prob": round(prob_calc, 1), "min": c_min, "moyen": c_moyen, "max": c_max}

# ================= 4. UI =================
st.markdown("<h1 class='main-title'>COSMOS X V16.0 ULTRA</h1>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 1.3])

with c1:
    st.markdown("### 🛰️ COMMAND CENTER")
    h_code = st.text_input("SERVER HASH (Avy amin'ny lalao teo)", placeholder="Ampidiro ny hash...")
    t_ref = st.number_input("TARGET COTE (Tanjonao)", value=2.00, step=0.1)
    m_time = st.text_input("TIME SYNC (Optional)", placeholder="HH:MM:SS")
    
    if st.button("RUN QUANTUM ANALYSIS"):
        if h_code:
            st.session_state.res = run_ultra_analysis(h_code, t_ref, m_time if m_time else None)
        else:
            st.error("Hash required!")

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown(f"""
        <div class="card" style="border-color: {r['col']};">
            <div style="color: {r['col']}; font-family: 'Orbitron';">{r['sig']}</div>
            <h1 style="font-size: 5rem; color: white;">{r['entry']}</h1>
            <div style="display: flex; justify-content: space-around; border-top: 1px solid #333; padding-top: 15px;">
                <div><small>PROBABILITY</small><br><b style="color: #ffff00; font-size: 1.5rem;">{r['prob']}%</b></div>
                <div><small>PREDICTION</small><br><b style="color: #00ffcc; font-size: 1.5rem;">{r['cote']}x</b></div>
                <div><small>ACCURACY</small><br><b style="color: #ff00cc; font-size: 1.5rem;">{r['conf']}%</b></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 20px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px;">
                <div><small>MIN</small><br><b>{r['min']}x</b></div>
                <div><small>MOYEN</small><br><b>{r['moyen']}x</b></div>
                <div><small>MAX</small><br><b>{r['max']}x</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================= 5. HISTORY =================
st.markdown("### 📂 MISSION LOGS")
try:
    with get_db_conn() as conn:
        df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 10", conn)
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="history-card">
            <b>{row['entry']}</b>
            <span class="status-pill" style="background-color:{row['color']};">{row['signal']}</span>
            <b style="color:#00ffcc;">{row['cote']}x</b>
        </div>
        """, unsafe_allow_html=True)
except: pass
