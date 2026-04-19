import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

# ================= 1. SECURITY & SYSTEM CONFIG =================
st.set_page_config(page_title="COSMOS X V16.4 QUANTUM", layout="wide")

def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align:center; color:#00ffcc; font-family:Orbitron;'>🔐 QUANTUM TERMINAL</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Quantum Key:", type="password")
        if st.button("ACTIVATE SYSTEM"):
            if pwd == "2026": # Password-nao
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Security Key!")
        return False
    return True

# ================= 2. DATABASE ENGINE (WITH RESET FUNCTION) =================
def get_db():
    conn = sqlite3.connect("cosmos_v16_final_pro.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, signal TEXT, 
                  color TEXT, cote REAL, prob REAL, c_min REAL, c_moy REAL, c_max REAL)""")
    conn.commit()
    return conn

def reset_database():
    with get_db() as conn:
        conn.execute("DROP TABLE IF EXISTS logs")
        conn.commit()
    st.toast("🚀 Database Purged Successfully!", icon="🔥")

# ================= 3. ULTRA INTELLIGENCE ENGINE =================
def run_analysis(h_in, t_ref, manual_time=None):
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
    
    # 15k Simulations for High Accuracy
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.62, sigma=0.44, size=15000)
    prob_calc = max(18.0, (np.sum(sims >= t_ref) / 15000) * 100)
    
    c_min = round(1.40 + (h_norm * 0.40), 2)
    c_moy = round(2.85 + (h_norm * 1.80), 2)
    c_max = round(11.5 + (h_norm * 15.0), 2)
    
    # STRATEGIC DELAY (45s - 90s)
    strategic_buffer = 45 + (h_norm * 45) 
    entry_dt = now + timedelta(seconds=strategic_buffer)
    entry_time = entry_dt.strftime("%H:%M:%S")
    
    if c_moy >= 4.5: sig, col = "🚀 NEBULA X5+", "#ff00cc"
    elif c_moy >= 2.4: sig, col = "💎 QUASAR X2+", "#00ffcc"
    else: sig, col = "⚠️ IONIC SCALP", "#ffff00"
    
    with get_db() as conn:
        conn.execute("""INSERT INTO logs (entry, signal, color, cote, prob, c_min, c_moy, c_max) 
                     VALUES (?,?,?,?,?,?,?,?)""", 
                     (entry_time, sig, col, c_moy, prob_calc, c_min, c_moy, c_max))
        conn.commit()
        
    return {"entry": entry_time, "sig": sig, "col": col, "prob": round(prob_calc, 1), "min": c_min, "moy": c_moy, "max": c_max}

# ================= 4. UI CYBER-DESIGN =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .stApp { background-color: #010103; color: #e0fbfc; }
    .card { background: linear-gradient(165deg, #0a0a1a, #010103); border: 2px solid #00ffcc; border-radius: 20px; padding: 25px; text-align: center; }
    .stButton>button { background: linear-gradient(90deg, #3300ff, #00ffcc); color: white; height: 55px; border-radius: 12px; font-family: 'Orbitron'; font-weight: bold; }
    .reset-btn>div>button { background: linear-gradient(90deg, #ff0000, #aa0000) !important; height: 40px !important; font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

if check_access():
    st.markdown("<h1 style='text-align:center; font-family:Orbitron; text-shadow: 0 0 20px #00ffcc;'>COSMOS X V16.4 PRO</h1>", unsafe_allow_html=True)
    
    # Sidebar ho an'ny Reset
    with st.sidebar:
        st.markdown("### 🛠️ SYSTEM TOOLS")
        if st.button("💥 RESET ALL DATA", use_container_width=True):
            reset_database()
            st.rerun()
        st.info("Ny Reset dia mamafa ny tantara rehetra mba hadio ny database.")

    c1, c2 = st.columns([1, 1.4])
    
    with c1:
        st.markdown("### 🛰️ COMMAND")
        h_input = st.text_input("SERVER HASH (Lasa)")
        t_input = st.number_input("TARGET COTE (Ref)", value=2.20, step=0.1)
        m_time = st.text_input("TIME SYNC (Optional)", placeholder="HH:MM:SS")
        
        # Smart Alert raha cote 10 no ampidirina
        if t_input >= 10:
            st.warning("⚠️ ULTRA HIGH RISK MODE ACTIVATED")
        
        if st.button("RUN ANALYSIS"):
            if h_input:
                st.session_state.resultat = run_analysis(h_input, t_input, m_time if m_time else None)
            else:
                st.error("Hash missing!")

    with c2:
        if "resultat" in st.session_state:
            res = st.session_state.resultat
            st.markdown(f"""
            <div class="card" style="border-color: {res['col']};">
                <div style="color: {res['col']}; font-family: 'Orbitron';">{res['sig']}</div>
                <div style="font-size: 0.9rem; color: #888; margin-top:10px;">PROBABLE ENTRY TIME</div>
                <h1 style="font-size: 5rem; margin: 5px 0; color: white;">{res['entry']}</h1>
                <div style="display: flex; justify-content: space-around; border-top: 1px solid #333; padding-top: 15px;">
                    <div><small>PROBABILITY</small><br><b style="color: #ffff00; font-size: 1.6rem;">{res['prob']}%</b></div>
                    <div><small>MIN EXIT</small><br><b style="color: #00ffcc; font-size: 1.6rem;">{res['min']}x</b></div>
                </div>
                <div style="margin-top: 20px; display: flex; justify-content: space-between; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px;">
                    <small>MOY: <b>{res['moy']}x</b></small> | <small>MAX: <b>{res['max']}x</b></small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 📂 MISSION RECAP")
    try:
        with get_db() as conn:
            df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 8", conn)
        for _, row in df.iterrows():
            st.markdown(f"""<div style='display:flex; justify-content:space-between; padding:12px; border-bottom:1px solid #222; background:rgba(255,255,255,0.02); margin-bottom:5px; border-radius:8px;'>
                <b>{row['entry']}</b> <span style='color:{row['color']}'>{row['signal']}</span> <b style="color:#00ffcc;">{row['c_moy']}x</b>
            </div>""", unsafe_allow_html=True)
    except: pass
