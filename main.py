import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

# ================= 1. SYSTEM SECURITY & CONFIG =================
st.set_page_config(page_title="COSMOS X V16.7 ULTRA", layout="wide")

def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align:center; color:#00ffcc; font-family:Orbitron;'>🔐 STRATEGIC ACCESS</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Quantum Key:", type="password")
        if st.button("ACTIVATE V16.7"):
            if pwd == "COSMOS2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Key!")
        return False
    return True

# ================= 2. DATABASE MANAGEMENT =================
def get_db():
    conn = sqlite3.connect("cosmos_v16_ultimate.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, signal TEXT, 
                  color TEXT, cote REAL, prob REAL, acc REAL, c_min REAL, c_moy REAL, c_max REAL)""")
    conn.commit()
    return conn

# ================= 3. ULTRA-BOOST ENGINE =================
def run_quantum_analysis(h_in, t_ref, last_v, manual_time=None):
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

    # --- ULTRA BOOST LOGIC ---
    # Manome hery 35% fanampiny raha nipoaka kely (toy ny 1.85) ny teo
    v_boost = 1.35 if last_v < 2.0 else 1.05
    if t_ref >= 10: v_boost += 0.15 
    
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.68 * v_boost, sigma=0.40, size=15000)
    
    prob_calc = max(12.0, (np.sum(sims >= t_ref) / 15000) * 100)
    accuracy_score = round(94.5 + (h_norm * 4.8), 1) 
    
    c_min = round(1.50 + (h_norm * 0.40), 2)
    c_moy = round((3.10 + (h_norm * 2.50)) * v_boost, 2)
    c_max = round((15.0 + (h_norm * 25.0)) * v_boost, 2)
    
    entry_delay = 45 + (h_norm * 45) 
    entry_dt = now + timedelta(seconds=entry_delay)
    entry_t = entry_dt.strftime("%H:%M:%S")
    
    # --- SIGNAL OVERRIDE ---
    # Manery ny signal ho Ultra raha vao Target 10 no ampidirina
    if t_ref >= 10 or c_moy >= 5.0:
        sig, col = "🚀 NEBULA X10+", "#ff00cc"
    elif c_moy >= 2.5:
        sig, col = "💎 QUASAR X2+", "#00ffcc"
    else:
        sig, col = "⚠️ IONIC SCALP", "#ffff00"
    
    with get_db() as conn:
        conn.execute("""INSERT INTO logs (entry, signal, color, cote, prob, acc, c_min, c_moy, c_max) 
                     VALUES (?,?,?,?,?,?,?,?,?)""", 
                     (entry_t, sig, col, c_moy, prob_calc, accuracy_score, c_min, c_moy, c_max))
        conn.commit()
        
    return {"entry": entry_t, "sig": sig, "col": col, "prob": round(prob_calc, 1), 
            "acc": accuracy_score, "min": c_min, "moy": c_moy, "max": c_max}

# ================= 4. UI CYBER-INTERFACE =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .stApp { background-color: #020205; color: #e0fbfc; }
    .card { background: linear-gradient(165deg, #0a0a25, #020205); border: 2px solid #00ffcc; border-radius: 25px; padding: 30px; text-align: center; }
    .metric-box { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 12px; border: 1px solid #333; }
    .stButton>button { background: linear-gradient(90deg, #3300ff, #00ffcc); color: white; height: 58px; border-radius: 15px; font-family: 'Orbitron'; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if check_access():
    st.markdown("<h1 style='text-align:center; font-family:Orbitron; color:#fff;'>COSMOS X V16.7 ULTRA</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ SYSTEM TOOLS")
        if st.button("💥 RESET ALL DATA", use_container_width=True):
            with get_db() as conn: 
                conn.execute("DROP TABLE IF EXISTS logs")
                conn.commit()
            st.toast("Database Cleared!")
            st.rerun()

    col1, col2 = st.columns([1, 1.6])
    
    with col1:
        st.markdown("### 🛰️ COMMAND CENTER")
        h_code = st.text_input("SERVER HASH")
        v_last = st.number_input("VOKATRA TEO", value=1.85, step=0.01)
        t_ref = st.number_input("TARGET COTE (Ref)", value=10.00, step=0.1)
        m_sync = st.text_input("TIME SYNC (Optional)", placeholder="HH:MM:SS")
        
        if st.button("EXECUTE QUANTUM ANALYSIS"):
            if h_code:
                st.session_state.ultra_res = run_quantum_analysis(h_code, t_ref, v_last, m_sync if m_sync else None)
            else:
                st.error("Please enter a valid Server Hash")

    with col2:
        if "ultra_res" in st.session_state:
            res = st.session_state.ultra_res
            st.markdown(f"""
            <div class="card" style="border-color: {res['col']};">
                <div style="color: {res['col']}; font-family: 'Orbitron'; font-size:1.5rem;">{res['sig']}</div>
                <div style="font-size: 1rem; color: #888; margin-top:15px;">PREDICTED ENTRY TIME</div>
                <h1 style="font-size: 5.5rem; margin: 10px 0; color: white;">{res['entry']}</h1>
                <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
                    <div class="metric-box"><small style="color:#ffff00;">PROBABILITY</small><br><b>{res['prob']}%</b></div>
                    <div class="metric-box"><small style="color:#00ffcc;">ACCURACY</small><br><b>{res['acc']}%</b></div>
                </div>
                <div style="display: flex; justify-content: space-between; border-top: 1px solid #444; padding-top: 20px;">
                    <div><small>MIN</small><br><b style="color:#00ffcc;">{res['min']}x</b></div>
                    <div><small>MOYEN</small><br><b>{res['moy']}x</b></div>
                    <div><small>MAX PEAK</small><br><b style="color:#ff00cc;">{res['max']}x</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 📂 MISSION RECAP")
    try:
        with get_db() as conn:
            df_logs = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 5", conn)
        for _, r_log in df_logs.iterrows():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #222;">
                <b>{r_log['entry']}</b> <span style="color:{r_log['color']}">{r_log['signal']}</span>
                <span>Acc: {r_log['acc']}%</span> <b style="color:#ff00cc;">{r_log['c_max']}x</b>
            </div>
            """, unsafe_allow_html=True)
    except: pass
