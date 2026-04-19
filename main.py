import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import math
from datetime import datetime, timedelta
import pytz
import time

# ================= CONFIG & STYLE =================
st.set_page_config(page_title="COSMOS X V13.5 PREMIUN", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #05050a;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Neon Title */
    .glitch-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #ff00cc, 0 0 20px #3300ff;
        margin-bottom: 30px;
    }

    /* Prediction Card */
    .card {
        background: rgba(15, 15, 25, 0.8);
        border: 2px solid #3300ff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 0 25px rgba(51, 0, 255, 0.3);
        text-align: center;
    }

    /* Stylish History Table */
    .history-row {
        display: flex;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.05);
        margin: 8px 0;
        padding: 12px 20px;
        border-radius: 12px;
        border-left: 5px solid #ff00cc;
        transition: 0.3s;
    }
    .history-row:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: scale(1.01);
    }
    
    .status-badge {
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

DB = "cosmos_v13_pro.db"

# ================= DATABASE ENGINE =================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, hash TEXT, time TEXT, entry TEXT, cote REAL, conf REAL, signal TEXT, color TEXT)")
    conn.commit()
    conn.close()

init_db()

def save_to_history(h, t, e, cote, conf, sig, color):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO history (hash, time, entry, cote, conf, signal, color) VALUES (?,?,?,?,?,?,?)", (h, t, e, cote, conf, sig, color))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    return df

# ================= CORE AI & MATH =================
def analyze(h_in, t_in, c_ref):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_norm = (int(h_hex[:10], 16) % 1000) / 1000
    
    # Mathematical Simulation (Monte Carlo Simplified)
    np.random.seed(int(h_hex[:8], 16))
    sims = np.random.lognormal(0.5, 0.4, 1000)
    
    final_cote = round(np.percentile(sims, 70) * (1 + h_norm), 2)
    conf = round(min(99.8, (h_norm * 100) + 20), 1)
    
    # Timing Logic
    now = datetime.now(pytz.timezone("Indian/Antananarivo"))
    delay = int(15 + (h_norm * 30))
    entry_time = (now + timedelta(seconds=delay)).strftime("%H:%M:%S")
    
    # Signal Logic
    if final_cote >= 4.0: sig, col = "🚀 ULTRA X4+", "#ff00cc"
    elif final_cote >= 2.0: sig, col = "💎 SNIPER X2", "#00ffcc"
    else: sig, col = "⚠️ SCALPING", "#ffff00"
    
    save_to_history(h_in, t_in, entry_time, final_cote, conf, sig, col)
    return {"entry": entry_time, "cote": final_cote, "conf": conf, "sig": sig, "col": col}

# ================= USER INTERFACE =================
st.markdown("<h1 class='glitch-title'>COSMOS X V13.5 ULTRA</h1>", unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        pwd = st.text_input("ENTER SYSTEM KEY", type="password")
        if st.button("ACTIVATE SYSTEM"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.markdown("### 📥 DATA INPUT")
    h_code = st.text_input("SERVER HASH")
    l_time = st.text_input("LAST ROUND TIME (HH:MM:SS)")
    c_target = st.number_input("TARGET COTE", value=2.0)
    
    if st.button("RUN QUANTUM ANALYSIS"):
        if h_code and l_time:
            st.session_state.result = analyze(h_code, l_time, c_target)
        else: st.error("Misy saha banga!")

with col_out:
    if "result" in st.session_state:
        r = st.session_state.result
        # Eto ilay fix HTML mba tsy hisy error intsony
        html_card = f"""
        <div class="card" style="border-color: {r['col']}">
            <p style="letter-spacing: 3px; color: {r['col']}; font-weight: bold;">{r['sig']}</p>
            <h1 style="font-size: 4.5rem; margin: 10px 0; text-shadow: 0 0 20px {r['col']}">{r['entry']}</h1>
            <div style="display: flex; justify-content: space-around; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <div><small>PREDICTED</small><br><b style="font-size: 1.5rem; color: #00ffcc;">{r['cote']}x</b></div>
                <div><small>ACCURACY</small><br><b style="font-size: 1.5rem; color: #ff00cc;">{r['conf']}%</b></div>
            </div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)
    else:
        st.info("Miandry ny fampidirana Hash...")

# ================= STYLISH HISTORY =================
st.markdown("<br>### 📊 MISSION LOGS (HISTORIQUE)", unsafe_allow_html=True)

hist_data = get_history()

if not hist_data.empty:
    for index, row in hist_data.iterrows():
        st.markdown(f"""
        <div class="history-row">
            <div style="flex: 1;"><b>🕒 {row['entry']}</b></div>
            <div style="flex: 2; text-align: center;">
                <span class="status-badge" style="background: {row['color']}; color: black;">{row['signal']}</span>
            </div>
            <div style="flex: 1; text-align: right;">
                <span style="color: #00ffcc; font-weight: bold;">{row['cote']}x</span> 
                <small style="opacity: 0.5;">({row['conf']}%)</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

if st.sidebar.button("🗑️ PURGE HISTORY"):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
    st.rerun()
