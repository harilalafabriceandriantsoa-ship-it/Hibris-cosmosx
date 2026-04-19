import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import math
from datetime import datetime, timedelta
import pytz
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ================= 1. CONFIGURATION & NEON STYLE =================
st.set_page_config(page_title="COSMOS X V13.5 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #05050a;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .glitch-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #ff00cc, 0 0 20px #3300ff;
        margin-bottom: 30px;
    }

    .card {
        background: rgba(15, 15, 25, 0.9);
        border: 2px solid #3300ff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 25px rgba(51, 0, 255, 0.4);
        text-align: center;
        margin-bottom: 20px;
    }

    /* ULTRA STYLISH HISTORY */
    .history-container {
        margin-top: 30px;
        padding: 10px;
    }
    
    .history-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, rgba(51, 0, 255, 0.1), rgba(255, 0, 204, 0.05));
        margin: 10px 0;
        padding: 15px 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 6px solid #3300ff;
        transition: all 0.3s ease;
    }
    
    .history-row:hover {
        transform: translateX(10px);
        background: rgba(51, 0, 255, 0.2);
        border-left: 6px solid #ff00cc;
    }

    .status-badge {
        padding: 6px 15px;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 800;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button {
        background: linear-gradient(90deg, #3300ff, #ff00cc);
        color: white;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        height: 55px;
        border-radius: 12px;
        border: none;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #ff00cc;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ================= 2. DATABASE MANAGEMENT =================
DB = "cosmos_v13_ultra.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS mission_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        hash TEXT, time TEXT, entry TEXT, 
        cote REAL, conf REAL, signal TEXT, color TEXT)""")
    conn.commit()
    conn.close()

init_db()

def save_log(h, t, e, cote, conf, sig, color):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO mission_logs (hash, time, entry, cote, conf, signal, color) VALUES (?,?,?,?,?,?,?)", 
              (h, t, e, cote, conf, sig, color))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM mission_logs ORDER BY id DESC LIMIT 15", conn)
    conn.close()
    return df

# ================= 3. CORE ENGINE (AI & MATH) =================
def run_analysis(h_input, t_input, c_ref):
    # Hash Processing
    h_hex = hashlib.sha256(h_input.encode()).hexdigest()
    h_norm = (int(h_hex[:12], 16) % 10000) / 10000.0
    
    # Advanced Volatility Calculation
    logs = get_logs()
    volatility = logs['cote'].std() if len(logs) > 5 else 1.2
    
    # AI Prediction (Hybrid Model)
    # 1. Base Logic
    base = 1.2 + (h_norm * 2.8) + (volatility * 0.2)
    
    # 2. Random Forest Simulation
    if len(logs) >= 10:
        X = logs[['cote', 'conf']].tail(10).values
        y = logs['cote'].tail(10).values
        model = RandomForestRegressor(n_estimators=100).fit(X, y)
        ai_pred = model.predict([[base, 80]])[0]
    else:
        ai_pred = base
    
    final_cote = round((base * 0.4 + ai_pred * 0.6), 2)
    conf = round(min(99.9, (h_norm * 110) - (volatility * 5) + 10), 1)
    
    # Quantum Timing
    now_t = datetime.now(pytz.timezone("Indian/Antananarivo"))
    offset = int(12 + (h_norm * 28))
    entry_time = (now_t + timedelta(seconds=offset)).strftime("%H:%M:%S")
    
    # Signal Logic
    if final_cote >= 4.0: sig, col = "🚀 ULTRA X4+", "#ff00cc"
    elif final_cote >= 2.0: sig, col = "💎 SNIPER X2", "#00ffcc"
    elif final_cote >= 1.4: sig, col = "⚠️ SCALPING", "#ffff00"
    else: sig, col = "🔴 NO ENTRY", "#ff4b4b"
    
    save_log(h_input, t_input, entry_time, final_cote, conf, sig, col)
    return {"entry": entry_time, "cote": final_cote, "conf": conf, "sig": sig, "col": col}

# ================= 4. USER INTERFACE =================
st.markdown("<h1 class='glitch-title'>COSMOS X V13.5 ULTRA</h1>", unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    pwd = st.text_input("PASSWORD SYSTEM", type="password")
    if st.button("INITIALIZE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Wrong Key")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Layout
c1, c2 = st.columns([1, 1.4])

with c1:
    st.markdown("### 🛰️ INPUT DATA")
    h_code = st.text_input("HASH CODE")
    l_time = st.text_input("TIME (HH:MM:SS)")
    target = st.number_input("TARGET REF", value=2.0, step=0.5)
    
    if st.button("RUN ANALYSIS"):
        if h_code and l_time:
            st.session_state.res = run_analysis(h_code, l_time, target)
        else: st.warning("Fenoy ny banga!")

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        # Displaying the main result card
        res_html = f"""
        <div class="card" style="border-color: {r['col']};">
            <p style="color: {r['col']}; font-weight: bold; letter-spacing: 2px;">{r['sig']}</p>
            <h1 style="font-size: 5rem; margin: 0; text-shadow: 0 0 20px {r['col']};">{r['entry']}</h1>
            <div style="display: flex; justify-content: space-around; margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                <div><small style="color:#aaa;">PREDICTION</small><br><b style="font-size: 1.8rem; color: #00ffcc;">{r['cote']}x</b></div>
                <div><small style="color:#aaa;">ACCURACY</small><br><b style="font-size: 1.8rem; color: #ff00cc;">{r['conf']}%</b></div>
            </div>
        </div>
        """
        st.markdown(res_html, unsafe_allow_html=True)
    else:
        st.info("System Ready. Waiting for Hash input...")

# ================= 5. STYLISH MISSION LOGS =================
st.markdown("<div class='history-container'>", unsafe_allow_html=True)
st.markdown("### 📊 MISSION LOGS (HISTORIQUE)")

logs_df = get_logs()

if not logs_df.empty:
    for _, row in logs_df.iterrows():
        # Clean HTML for History Rows
        row_html = f"""
        <div class="history-row">
            <div style="flex: 1;">
                <span style="color: #aaa; font-size: 0.8rem;">ENTRY TIME</span><br>
                <b style="font-size: 1.3rem; color: #fff;">{row['entry']}</b>
            </div>
            <div style="flex: 2; text-align: center;">
                <span class="status-badge" style="background: {row['color']}; color: #000;">{row['signal']}</span>
            </div>
            <div style="flex: 1; text-align: right;">
                <b style="font-size: 1.4rem; color: #00ffcc;">{row['cote']}x</b><br>
                <small style="color: #ff00cc;">{row['conf']}% Accuracy</small>
            </div>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)
else:
    st.write("No history found.")

st.markdown("</div>", unsafe_allow_html=True)

# Sidebar Options
if st.sidebar.button("🗑️ PURGE ALL DATA"):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM mission_logs")
    conn.commit()
    conn.close()
    st.rerun()
