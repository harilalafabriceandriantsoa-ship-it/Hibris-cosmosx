import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta
import pytz

# ================= 1. SYSTEM CONFIG =================
st.set_page_config(page_title="COSMOS X V16.1 ULTRA PRO", layout="wide")

def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align:center; color:#00ffcc;'>🔐 QUANTUM ACCESS</h2>", unsafe_allow_html=True)
        pwd = st.text_input("System Password:", type="password")
        if st.button("ACTIVATE SYSTEM"):
            if pwd == "COSMOS2026": # Ny password-nao
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Key!")
        return False
    return True

# ================= 2. DYNAMIC DATABASE (AUTO-FIX ERROR) =================
def get_db():
    conn = sqlite3.connect("cosmos_v16_final.db", check_same_thread=False)
    # Fafana ny table taloha raha misy error mba hamboatra vaovao mifanaraka amin'ny V16.1
    conn.execute("DROP TABLE IF EXISTS logs") 
    conn.execute("""CREATE TABLE logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, signal TEXT, 
                  color TEXT, cote REAL, prob REAL, conf REAL, c_min REAL, c_moy REAL, c_max REAL)""")
    conn.commit()
    return conn

# ================= 3. ULTRA INTELLIGENCE ENGINE =================
def run_analysis(h_in, t_ref, manual_time=None):
    h_hex = hashlib.sha512(h_in.encode()).hexdigest()
    seed_val = int(h_hex[:16], 16)
    h_norm = (seed_val % 1000000) / 1000000.0
    
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    
    # Famerenana ny Time Sync (Fametrahana ora)
    if manual_time:
        try:
            t_obj = datetime.strptime(manual_time, "%H:%M:%S")
            now = now.replace(hour=t_obj.hour, minute=t_obj.minute, second=t_obj.second)
        except: pass
    
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.58, sigma=0.46, size=10000)
    prob_calc = max(18.5, (np.sum(sims >= t_ref) / 10000) * 100)
    
    c_min = round(1.38 + (h_norm * 0.42), 2)
    c_moy = round(2.80 + (h_norm * 1.80), 2)
    c_max = round(10.2 + (h_norm * 14.5), 2)
    
    # Entry Time misy Quantum Delay
    delay = 12 + (h_norm * 20)
    entry_dt = now + timedelta(seconds=delay)
    entry_time = entry_dt.strftime("%H:%M:%S")
    
    if c_moy >= 4.2: sig, col = "🚀 NEBULA X4+", "#ff00cc"
    elif c_moy >= 2.3: sig, col = "💎 QUASAR X2", "#00ffcc"
    else: sig, col = "⚠️ IONIC SCALP", "#ffff00"
    
    with get_db() as conn:
        conn.execute("""INSERT INTO logs (entry, signal, color, cote, prob, conf, c_min, c_moy, c_max) 
                     VALUES (?,?,?,?,?,?,?,?,?)""", 
                     (entry_time, sig, col, c_moy, prob_calc, 94.8, c_min, c_moy, c_max))
        conn.commit()
        
    return {"entry": entry_time, "sig": sig, "col": col, "prob": round(prob_calc, 1), "min": c_min, "moy": c_moy, "max": c_max}

# ================= 4. UI CYBER-DESIGN =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #020205; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .card { 
        background: linear-gradient(165deg, #0a0a1a, #020205); 
        border: 2px solid #3300ff; border-radius: 20px; padding: 25px; 
        box-shadow: 0 0 30px rgba(51, 0, 255, 0.3); text-align: center;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #3300ff, #00ffcc); color: white; 
        height: 55px; border-radius: 12px; border: none; width: 100%; font-family: 'Orbitron';
    }
</style>
""", unsafe_allow_html=True)

if check_access():
    st.markdown("<h1 style='text-align:center; font-family:Orbitron; text-shadow: 0 0 20px #00ffcc;'>COSMOS X V16.1 ULTRA</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1.3])
    
    with c1:
        st.markdown("### 🛰️ COMMAND CENTER")
        h_code = st.text_input("SERVER HASH (Lasa)")
        t_ref = st.number_input("TARGET COTE (Hoavy)", value=2.20, step=0.1)
        # Famerenana ny fametrahana ora (Time Sync)
        m_time = st.text_input("TIME SYNC (Optional: HH:MM:SS)", placeholder="Ohatra: 21:45:00")
        
        if st.button("EXECUTE QUANTUM ANALYSIS"):
            if h_code:
                st.session_state.resultat = run_analysis(h_code, t_ref, m_time if m_time else None)
            else:
                st.error("Hash required!")

    with c2:
        if "resultat" in st.session_state:
            res = st.session_state.resultat
            st.markdown(f"""
            <div class="card" style="border-color: {res['col']};">
                <div style="color: {res['col']}; font-family: 'Orbitron';">{res['sig']}</div>
                <h1 style="font-size: 4.5rem; margin: 10px 0; color: white;">{res['entry']}</h1>
                <div style="display: flex; justify-content: space-around; border-top: 1px solid #333; padding-top: 15px;">
                    <div><small>PROBABILITY</small><br><b style="color: #ffff00; font-size: 1.5rem;">{res['prob']}%</b></div>
                    <div><small>MIN EXIT</small><br><b style="color: #00ffcc; font-size: 1.5rem;">{res['min']}x</b></div>
                </div>
                <div style="margin-top: 20px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px;">
                    <small>MOYEN: <b>{res['moy']}x</b></small> | <small>MAX: <b>{res['max']}x</b></small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ================= 5. HISTORY =================
    st.markdown("### 📂 MISSION RECAP")
    try:
        with sqlite3.connect("cosmos_v16_final.db") as conn:
            df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 8", conn)
        for _, row in df.iterrows():
            st.markdown(f"""<div style='display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #222;'>
                <b>{row['entry']}</b> <span style='color:{row['color']}'>{row['signal']}</span> <b>{row['c_moy']}x</b>
            </div>""", unsafe_allow_html=True)
    except: pass
