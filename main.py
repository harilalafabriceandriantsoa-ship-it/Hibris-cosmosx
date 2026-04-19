import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

# ================= 1. QUANTUM CORE CONFIG =================
st.set_page_config(page_title="COSMOS X V16.5 DYNAMIC", layout="wide")

def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align:center; color:#00ffcc;'>🔐 QUANTUM TERMINAL</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Security Key:", type="password")
        if st.button("ACTIVATE"):
            if pwd == "COSMOS2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied!")
        return False
    return True

# ================= 2. DYNAMIC DATABASE =================
def get_db():
    conn = sqlite3.connect("cosmos_v16_dynamic.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, signal TEXT, 
                  color TEXT, cote REAL, prob REAL, c_min REAL, c_moy REAL, c_max REAL)""")
    conn.commit()
    return conn

# ================= 3. INTELLIGENCE WITH VOLATILITY CORRECTION =================
def run_dynamic_analysis(h_in, t_ref, last_voka=2.0, manual_time=None):
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

    # --- CORRECTION DE VOLATILITE ---
    # Raha 1.85 no nivoaka teo, ny AI dia mampiakatra ny hery hikarohana ny "Recovery"
    volatility_boost = 1.15 if last_voka < 2.0 else 1.0
    
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.65 * volatility_boost, sigma=0.42, size=15000)
    prob_calc = max(18.0, (np.sum(sims >= t_ref) / 15000) * 100)
    
    c_min = round(1.42 + (h_norm * 0.35), 2)
    c_moy = round(2.90 + (h_norm * 2.00) * volatility_boost, 2)
    c_max = round(12.0 + (h_norm * 18.0) * volatility_boost, 2)
    
    # STRATEGIC DELAY (45s - 90s)
    strategic_delay = 45 + (h_norm * 45) 
    entry_dt = now + timedelta(seconds=strategic_delay)
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

# ================= 4. UI DESIGN =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .stApp { background-color: #010103; color: #e0fbfc; }
    .card { background: #0a0a1a; border: 2px solid #00ffcc; border-radius: 20px; padding: 25px; text-align: center; }
    .stButton>button { background: linear-gradient(90deg, #3300ff, #00ffcc); color: white; height: 55px; border-radius: 12px; font-family: 'Orbitron'; }
</style>
""", unsafe_allow_html=True)

if check_access():
    st.markdown("<h1 style='text-align:center; font-family:Orbitron;'>COSMOS X V16.5 DYNAMIC</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🛠️ TOOLS")
        if st.button("💥 RESET DATA", use_container_width=True):
            with get_db() as conn: conn.execute("DROP TABLE IF EXISTS logs"); conn.commit()
            st.rerun()

    c1, c2 = st.columns([1, 1.4])
    
    with c1:
        st.markdown("### 🛰️ COMMAND")
        h_input = st.text_input("SERVER HASH (Lasa)")
        v_last = st.number_input("VOKATRA TEO (Ohatra: 1.85)", value=2.00, step=0.01)
        t_input = st.number_input("TARGET COTE (Reference)", value=2.20, step=0.1)
        m_time = st.text_input("TIME SYNC (HH:MM:SS)", placeholder="Avelao ho foana")
        
        if st.button("EXECUTE DYNAMIC ANALYSIS"):
            if h_input:
                st.session_state.dyn_res = run_dynamic_analysis(h_input, t_input, v_last, m_time if m_time else None)
            else:
                st.error("Hash missing!")

    with c2:
        if "dyn_res" in st.session_state:
            res = st.session_state.dyn_res
            st.markdown(f"""
            <div class="card" style="border-color: {res['col']};">
                <div style="color: {res['col']}; font-family: 'Orbitron';">{res['sig']}</div>
                <div style="font-size: 0.9rem; color: #888; margin-top:10px;">OPTIMAL ENTRY TIME</div>
                <h1 style="font-size: 5rem; margin: 5px 0; color: white;">{res['entry']}</h1>
                <div style="display: flex; justify-content: space-around; border-top: 1px solid #333; padding-top: 15px;">
                    <div><small>PROBABILITY</small><br><b style="color: #ffff00; font-size: 1.6rem;">{res['prob']}%</b></div>
                    <div><small>DYNAMIC MAX</small><br><b style="color: #ff00cc; font-size: 1.6rem;">{res['max']}x</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 📂 MISSION RECAP")
    try:
        with get_db() as conn:
            df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 5", conn)
        for _, row in df.iterrows():
            st.markdown(f"""<div style='display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #222;'>
                <b>{row['entry']}</b> <span style='color:{row['color']}'>{row['signal']}</span> <b>{row['c_moy']}x</b>
            </div>""", unsafe_allow_html=True)
    except: pass
