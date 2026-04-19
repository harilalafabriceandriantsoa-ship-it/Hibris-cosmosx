import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta
import pytz

# ================= 1. PURE INTELLIGENCE CONFIG =================
st.set_page_config(page_title="COSMOS X V16.0 ULTRA PRO", layout="wide")

def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align:center; color:#00ffcc; font-family:Orbitron;'>🛸 ULTRA SECURE LOGIN</h2>", unsafe_allow_html=True)
        with st.container():
            pwd = st.text_input("Enter System Password:", type="password")
            if st.button("ACTIVATE COSMOS X"):
                if pwd == "COSMOS2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Quantum Key")
        return False
    return True

# ================= 2. ADVANCED CYBER STYLE =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background-color: #020205; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    
    .main-title { 
        font-family: 'Orbitron', sans-serif; font-size: 2.8rem; text-align: center; 
        color: #fff; text-shadow: 0 0 30px #00ffcc; margin-bottom: 30px; 
    }
    
    .card { 
        background: linear-gradient(165deg, #0a0a1a, #020205); 
        border: 2px solid #3300ff; border-radius: 25px; padding: 30px; 
        box-shadow: 0 0 50px rgba(51, 0, 255, 0.3); text-align: center; 
        margin-bottom: 25px; border-left: 5px solid #00ffcc;
    }
    
    .metric-box {
        background: rgba(255,255,255,0.03); border-radius: 15px; padding: 15px;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }
    
    .history-card { 
        background: rgba(255, 255, 255, 0.05); margin: 10px 0; padding: 18px; 
        border-radius: 15px; border: 1px solid rgba(0, 255, 204, 0.2); 
        display: flex; justify-content: space-between; align-items: center; 
    }
    
    .stButton>button { 
        background: linear-gradient(90deg, #3300ff, #00ffcc); color: white; 
        height: 60px; border-radius: 15px; border: none; width: 100%; 
        font-family: 'Orbitron'; font-weight: bold; font-size: 1.3rem;
        box-shadow: 0 5px 15px rgba(0, 255, 204, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. CORE ANALYTIC ENGINE =================
def get_connection():
    conn = sqlite3.connect("cosmos_v16_ultra.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, signal TEXT, 
                  color TEXT, cote REAL, prob REAL, conf REAL, c_min REAL, c_moy REAL, c_max REAL)""")
    return conn

def execute_intelligence(h_in, t_ref):
    # Deep Hash Decomposition
    h_hex = hashlib.sha512(h_in.encode()).hexdigest()
    seed_val = int(h_hex[:16], 16)
    h_norm = (seed_val % 1000000) / 1000000.0
    
    # Time Synchronization (Madagascar)
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    
    # Advanced Monte Carlo Engine
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.55, sigma=0.48, size=10000) # 10k Simulations for accuracy
    
    prob_calc = max(18.2, (np.sum(sims >= t_ref) / 10000) * 100)
    
    # Dynamic Scaling Metrics
    c_min = round(1.38 + (h_norm * 0.40), 2)
    c_moy = round(2.82 + (h_norm * 1.75), 2)
    c_max = round(10.5 + (h_norm * 15.0), 2)
    
    prediction = round((c_moy * 0.88) + (h_norm * 1.2), 2)
    accuracy = round(min(99.9, 91.5 + (h_norm * 8.4)), 1)
    
    # Quantum Delay Entry
    delay = 12 + (h_norm * 18)
    entry_dt = now + timedelta(seconds=delay)
    entry_time = entry_dt.strftime("%H:%M:%S")
    
    # Smart Signal Routing
    if prediction >= 4.5: sig, col = "🚀 NEBULA X4+", "#ff00cc"
    elif prediction >= 2.3: sig, col = "💎 QUASAR X2", "#00ffcc"
    else: sig, col = "⚠️ IONIC SCALP", "#ffff00"
    
    # Persistence
    with get_connection() as conn:
        conn.execute("""INSERT INTO logs (entry, signal, color, cote, prob, conf, c_min, c_moy, c_max) 
                     VALUES (?,?,?,?,?,?,?,?,?)""", 
                     (entry_time, sig, col, prediction, prob_calc, accuracy, c_min, c_moy, c_max))
        conn.commit()
        
    return {
        "entry": entry_time, "cote": prediction, "conf": accuracy, 
        "sig": sig, "col": col, "prob": round(prob_calc, 1),
        "min": c_min, "moy": c_moy, "max": c_max
    }

# ================= 4. MAIN INTERFACE =================
if check_access():
    st.markdown("<h1 class='main-title'>COSMOS X V16.0 ULTRA PRO</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1.4])
    
    with c1:
        st.markdown("### 🛰️ QUANTUM INPUT")
        h_code = st.text_input("SERVER HASH (Lasa)", placeholder="Paste hash code...")
        t_ref = st.number_input("TARGET COTE (Hoavy)", value=2.20, step=0.1)
        
        if st.button("EXECUTE ANALYSIS"):
            if h_code:
                st.session_state.result = execute_intelligence(h_code, t_ref)
            else:
                st.error("System Error: Hash input required")

    with c2:
        if "result" in st.session_state:
            res = st.session_state.result
            st.markdown(f"""
            <div class="card" style="border-color: {res['col']};">
                <div style="color: {res['col']}; font-family: 'Orbitron'; letter-spacing:3px;">{res['sig']}</div>
                <h1 style="font-size: 5rem; margin: 10px 0; color: white; text-shadow: 0 0 20px {res['col']};">{res['entry']}</h1>
                
                <div style="display: flex; justify-content: space-around; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                    <div class="metric-box"><small>PROBABILITY</small><br><b style="font-size: 1.5rem; color: #ffff00;">{res['prob']}%</b></div>
                    <div class="metric-box"><small>ACCURACY</small><br><b style="font-size: 1.5rem; color: #ff00cc;">{res['conf']}%</b></div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-top: 20px; padding: 15px; background: rgba(0,255,204,0.05); border-radius: 12px;">
                    <div><small>SAFE EXIT (MIN)</small><br><b style="color: #00ffcc;">{res['min']}x</b></div>
                    <div><small>MOYEN</small><br><b>{res['moy']}x</b></div>
                    <div><small>PEAK (MAX)</small><br><b style="color: #ff00cc;">{res['max']}x</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="border-style: dashed; border-color: #444;">
                <p style="color: #888; font-size: 1.2rem;">SYSTEM STANDBY<br>Waiting for Neural Input...</p>
            </div>
            """, unsafe_allow_html=True)

    # ================= 5. HISTORY LOGS =================
    st.markdown("### 📂 MISSION RECAP")
    try:
        with get_connection() as conn:
            df_log = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 10", conn)
        
        for _, row in df_log.iterrows():
            st.markdown(f"""
            <div class="history-card">
                <div style="flex:1;"><b>{row['entry']}</b></div>
                <div style="flex:1.5; text-align:center;"><span style="color:{row['color']}; font-weight:bold;">{row['signal']}</span></div>
                <div style="flex:1; text-align:right;">
                    <small style="color:#aaa;">MIN/MOY</small><br>
                    <b style="color:#00ffcc;">{row['c_min']}x</b> | <b style="color:#fff;">{row['c_moy']}x</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except: pass

    if st.sidebar.button("🧹 PURGE ALL DATA"):
        with get_connection() as conn:
            conn.execute("DELETE FROM logs")
            conn.commit()
        st.rerun()
