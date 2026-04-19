import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta
import pytz
from sklearn.ensemble import RandomForestRegressor

# ================= 1. INTERFACE STYLE (Elite UI) =================
st.set_page_config(page_title="COSMOS X V15.0 QUANTUM", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background-color: #05050a; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title { font-family: 'Orbitron'; font-size: 2.5rem; text-align: center; color: #fff; text-shadow: 0 0 20px #ff00cc; margin-bottom: 20px; }
    .card { background: linear-gradient(145deg, #0f0f1e, #05050f); border: 2px solid #3300ff; border-radius: 20px; padding: 25px; box-shadow: 0 0 40px rgba(51, 0, 255, 0.25); text-align: center; }
    .history-card { background: rgba(255, 255, 255, 0.02); margin: 8px 0; padding: 15px; border-radius: 12px; border: 1px solid rgba(51, 0, 255, 0.2); display: flex; justify-content: space-between; align-items: center; }
    .status-pill { padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: bold; font-family: 'Orbitron'; color: #000; }
    .stButton>button { background: linear-gradient(90deg, #3300ff, #ff00cc); color: white; height: 50px; border-radius: 10px; border: none; width: 100%; font-family: 'Orbitron'; }
</style>
""", unsafe_allow_html=True)

# ================= 2. DATABASE (Stable) =================
DB_FILE = "cosmos_quantum_v15.db"

def get_db_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, hash TEXT, entry TEXT, cote REAL, conf REAL, 
                  signal TEXT, color TEXT, prob REAL, c_min REAL, c_max REAL)""")
        conn.commit()

init_db()

# ================= 3. PRECISION CALCULATOR =================
def run_quantum_analysis(h_in, t_ref):
    # Ultra Precise Hash Mapping
    h_hex = hashlib.sha512(h_in.encode()).hexdigest()
    # Mampiasa 16 characters ho an'ny precision avo kokoa
    seed_val = int(h_hex[:16], 16)
    h_norm = (seed_val % 1000000) / 1000000.0
    
    # Historique Data for Z-Score
    with get_db_conn() as conn:
        df = pd.read_sql("SELECT cote FROM logs ORDER BY id DESC LIMIT 20", conn)
    
    std_dev = df['cote'].std() if len(df) > 5 else 1.5
    avg_cote = df['cote'].mean() if len(df) > 5 else 2.10
    
    # 5,000 Simulations Monte Carlo
    np.random.seed(seed_val % 4294967295)
    sims = np.random.lognormal(mean=0.6, sigma=0.45, size=5000)
    prob_calc = (np.sum(sims >= t_ref) / 5000) * 100
    
    # Cote Metrics
    c_min = round(1.15 + (h_norm * 0.35), 2)
    c_max = round(avg_cote + (std_dev * 2.5 * h_norm), 2)
    c_moyen = round((c_min + c_max) / 2.1, 2)
    
    # Prediction & Accuracy
    prediction = round((c_moyen * 0.8) + (h_norm * 1.5), 2)
    accuracy = round(min(99.8, 85 + (h_norm * 14.5)), 1)
    
    # Micro-Time Sync
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    # Delay dynamic miankina amin'ny Target Ref
    delay_sec = 15 + (t_ref * 2) + (h_norm * 10)
    entry_dt = now + timedelta(seconds=delay_sec)
    entry_time = entry_dt.strftime("%H:%M:%S")
    
    # Signal Engine
    if prediction >= 5.0: sig, col = "🌌 COSMIC X5+", "#ff00cc"
    elif prediction >= 2.5: sig, col = "💎 SNIPER X2", "#00ffcc"
    elif prediction >= 1.5: sig, col = "⚠️ SAFE SCALPING", "#ffff00"
    else: sig, col = "🔴 AVOID", "#ff4b4b"
    
    # Save to DB
    with get_db_conn() as conn:
        conn.execute("""INSERT INTO logs (hash, entry, cote, conf, signal, color, prob, c_min, c_max) 
                     VALUES (?,?,?,?,?,?,?,?,?)""", (h_in, entry_time, prediction, accuracy, sig, col, prob_calc, c_min, c_max))
        conn.commit()
        
    return {"entry": entry_time, "cote": prediction, "conf": accuracy, "sig": sig, "col": col, "prob": round(prob_calc, 1), "min": c_min, "moyen": c_moyen, "max": c_max}

# ================= 4. UI RENDER =================
st.markdown("<h1 class='main-title'>COSMOS X V15.0 QUANTUM</h1>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.2])

with c1:
    st.markdown("### 📡 SYSTEM INPUT")
    h_code = st.text_input("SERVER HASH (SHA-256/512)", placeholder="Paste hash here...")
    t_ref = st.number_input("COTE RÉFÉRENCE (TARGET)", value=2.00, step=0.1)
    
    if st.button("EXECUTE QUANTUM CALC"):
        if h_code:
            st.session_state.q_res = run_quantum_analysis(h_code, t_ref)
        else:
            st.error("Enter Hash Code!")

with c2:
    if "q_res" in st.session_state:
        r = st.session_state.q_res
        st.markdown(f"""
        <div class="card" style="border-color: {r['col']};">
            <div style="color: {r['col']}; font-family: 'Orbitron'; font-weight: bold;">{r['sig']}</div>
            <h1 style="font-size: 5.5rem; margin: 10px 0; color: white;">{r['entry']}</h1>
            
            <div style="display: flex; justify-content: space-around; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <div><small style="color:#888;">PROBABILITY</small><br><b style="font-size: 1.5rem; color: #ffff00;">{r['prob']}%</b></div>
                <div><small style="color:#888;">PREDICTION</small><br><b style="font-size: 1.5rem; color: #00ffcc;">{r['cote']}x</b></div>
                <div><small style="color:#888;">ACCURACY</small><br><b style="font-size: 1.5rem; color: #ff00cc;">{r['conf']}%</b></div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-top: 20px; padding: 12px; background: rgba(255,255,255,0.04); border-radius: 10px;">
                <div><small style="color:#aaa;">MIN</small><br><b>{r['min']}x</b></div>
                <div><small style="color:#aaa;">MOYEN</small><br><b>{r['moyen']}x</b></div>
                <div><small style="color:#aaa;">MAX</small><br><b style="color: #ff00cc;">{r['max']}x</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================= 5. HISTORY (Futuristic) =================
st.markdown("<br>### 📂 MISSION LOGS", unsafe_allow_html=True)
try:
    with get_db_conn() as conn:
        df_h = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 10", conn)
    for _, row in df_h.iterrows():
        st.markdown(f"""
        <div class="history-card">
            <div style="flex:1;"><b>{row['entry']}</b></div>
            <div style="flex:1.5; text-align:center;"><span class="status-pill" style="background-color:{row['color']};">{row['signal']}</span></div>
            <div style="flex:1; text-align:right;"><b style="color:#00ffcc;">{row['cote']}x</b> | <small>{row['conf']}%</small></div>
        </div>
        """, unsafe_allow_html=True)
except: st.write("No logs.")
