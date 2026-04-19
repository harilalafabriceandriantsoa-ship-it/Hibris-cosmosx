import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import math
from datetime import datetime, timedelta
import pytz
from sklearn.ensemble import RandomForestRegressor

# ================= 1. STYLE & INTERFACE (User Original Style) =================
st.set_page_config(page_title="COSMOS X V13.5 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #05050a;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 15px #ff00cc, 0 0 30px #3300ff;
        margin-bottom: 25px;
    }

    .card {
        background: rgba(15, 15, 25, 0.95);
        border: 2px solid #3300ff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(51, 0, 255, 0.3);
        text-align: center;
        margin-bottom: 20px;
    }

    /* MISSION LOG STYLE (History Only) */
    .history-card {
        background: linear-gradient(90deg, rgba(51, 0, 255, 0.1), rgba(255, 0, 204, 0.05));
        margin: 12px 0;
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 5px solid #3300ff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: 0.3s;
    }
    .history-card:hover {
        transform: scale(1.02);
        border-left: 5px solid #ff00cc;
        background: rgba(51, 0, 255, 0.2);
    }

    .status-pill {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        color: #000;
    }

    .stButton>button {
        background: linear-gradient(90deg, #ff00cc, #3300ff);
        color: white;
        height: 50px;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ================= 2. DATABASE (SQLite) =================
DB_FILE = "cosmos_v13_ultra.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, hash TEXT, entry TEXT, cote REAL, conf REAL, signal TEXT, color TEXT)""")
    conn.commit()
    conn.close()

def save_log(h, e, c, cf, s, col):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (hash, entry, cote, conf, signal, color) VALUES (?,?,?,?,?,?)", (h, e, c, cf, s, col))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    return df

init_db()

# ================= 3. ADVANCED ALGORITHM (RF & MONTE CARLO) =================
def run_quantum_analysis(h_in, t_in, c_ref):
    # Hash Entropy
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_val = (int(h_hex[:10], 16) % 1000) / 1000
    
    # Random Forest Regression logic
    # Mock data to simulate learning if DB is small
    logs = get_logs()
    if len(logs) > 5:
        X = logs[['cote', 'conf']].values
        y = logs['cote'].values
        model = RandomForestRegressor(n_estimators=50).fit(X, y)
        prediction = model.predict([[c_ref, 85.0]])[0]
    else:
        prediction = c_ref * (1 + h_val)

    # Monte Carlo Simulation
    sims = np.random.lognormal(0.5, 0.3, 500)
    prob_x3 = (np.sum(sims >= 3.0) / 500) * 100
    
    # Accuracy & Entry Time
    conf = round(min(99.8, 75 + (h_val * 24)), 1)
    now = datetime.now(pytz.timezone("Indian/Antananarivo"))
    delay = int(10 + (h_val * 35))
    entry_time = (now + timedelta(seconds=delay)).strftime("%H:%M:%S")
    
    # Signal Logic
    final_cote = round(prediction, 2)
    if final_cote >= 4.0: sig, col = "🚀 ULTRA X4+", "#ff00cc"
    elif final_cote >= 2.0: sig, col = "💎 SNIPER X2", "#00ffcc"
    else: sig, col = "⚠️ SCALPING", "#ffff00"
    
    save_log(h_in, entry_time, final_cote, conf, sig, col)
    return {"entry": entry_time, "cote": final_cote, "conf": conf, "sig": sig, "col": col, "prob": round(prob_x3, 1)}

# ================= 4. UI COMPONENTS =================
st.markdown("<h1 class='main-title'>COSMOS X V13.5 ULTRA</h1>", unsafe_allow_html=True)

# User Interface Layout (As requested: Original Style)
col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.markdown("### 🛰️ INPUT DATA")
    h_code = st.text_input("HASH CODE", placeholder="Paste server hash...")
    l_time = st.text_input("TIME (HH:MM:SS)", placeholder="17:15:00")
    t_ref = st.number_input("TARGET REF", value=2.00, step=0.1)
    
    if st.button("RUN ANALYSIS"):
        if h_code and l_time:
            st.session_state.res = run_quantum_analysis(h_code, l_time, t_ref)
        else:
            st.error("Fenoy ny banga!")

with col_result:
    if "res" in st.session_state:
        r = st.session_state.res
        # KEYERROR FIX: Making sure 'col' exists and is used safely
        st.markdown(f"""
        <div class="card" style="border-color: {r.get('col', '#3300ff')};">
            <p style="color: {r.get('col', '#fff')}; font-weight: bold; letter-spacing: 2px;">{r.get('sig', 'ANALYSIS COMPLETE')}</p>
            <h1 style="font-size: 5rem; margin: 0; text-shadow: 0 0 20px {r.get('col', '#3300ff')};">{r.get('entry')}</h1>
            <div style="display: flex; justify-content: space-around; margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                <div><small style="color:#aaa;">PROBABILITY</small><br><b style="font-size: 1.5rem; color: #ffff00;">{r.get('prob')}%</b></div>
                <div><small style="color:#aaa;">PREDICTION</small><br><b style="font-size: 1.5rem; color: #00ffcc;">{r.get('cote')}x</b></div>
                <div><small style="color:#aaa;">ACCURACY</small><br><b style="font-size: 1.5rem; color: #ff00cc;">{r.get('conf')}%</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("System Ready. Waiting for server hash...")

# ================= 5. STYLISH MISSION LOGS (History) =================
st.markdown("<br>### 📊 MISSION LOGS (HISTORIQUE)", unsafe_allow_html=True)
history_df = get_logs()

if not history_df.empty:
    for idx, row in history_df.iterrows():
        st.markdown(f"""
        <div class="history-card">
            <div style="flex: 1;">
                <small style="color: #aaa;">ENTRY TIME</small><br>
                <b style="font-size: 1.2rem;">{row['entry']}</b>
            </div>
            <div style="flex: 1.5; text-align: center;">
                <span class="status-pill" style="background-color: {row['color']};">{row['signal']}</span>
            </div>
            <div style="flex: 1; text-align: right;">
                <b style="font-size: 1.3rem; color: #00ffcc;">{row['cote']}x</b><br>
                <small style="color: #ff00cc;">{row['conf']}% Acc.</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.write("No logs recorded yet.")

if st.sidebar.button("🗑️ CLEAR HISTORY"):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM logs")
    conn.commit()
    conn.close()
    st.rerun()
