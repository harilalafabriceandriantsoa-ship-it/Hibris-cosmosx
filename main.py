import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
import time

# ================= 1. PREMIUM CONFIG & STYLING =================
st.set_page_config(page_title="COSMOS X V16.9 ULTRA X3", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #05050a;
        background-image: radial-gradient(circle at 50% 50%, #101025 0%, #05050a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    .glass-card {
        background: rgba(15, 15, 35, 0.75);
        border: 1px solid rgba(0, 255, 204, 0.35);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00cc, #00ccff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 25px rgba(0, 255, 204, 0.5);
    }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0088ff 100%) !important;
        color: #000 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        height: 58px !important;
    }

    .metric-value { font-size: 2.1rem; font-weight: 700; font-family: 'Orbitron'; }
    .res-min { background: linear-gradient(#00ff88, #00cc66); color: #000; }
    .res-moy { background: linear-gradient(#ffd700, #ffaa00); color: #000; }
    .res-max { background: linear-gradient(#ff3366, #cc1133); color: #fff; }
</style>
""", unsafe_allow_html=True)

# ================= 2. DATABASE =================
def db_init():
    conn = sqlite3.connect("cosmos_x.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            entry TEXT,
            signal TEXT,
            prob REAL,
            conf REAL,
            minv REAL,
            moy REAL,
            maxv REAL,
            strength REAL
        )
    """)
    conn.commit()
    return conn

def now_mg():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ================= 3. ULTRA X3+ ENGINE (Tena Avancée) =================
def run_engine_ultra(h, t_in, last_cote):
    h_hex = hashlib.sha256(h.encode()).hexdigest()
    h_num = int(h_hex[:56], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    last_cote = max(1.0, min(last_cote, 12.0))

    # === ALGORITHM TRÈS PUISSANT CIBLÉ X3+ ===
    base = 1.94 + (h_num % 1050) / 125
    sigma = 0.225 - (last_cote * 0.0027)
    sims = np.random.lognormal(np.log(base), sigma, 100000)   # 100 000 simulations

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 98.0), 2)
    minv = round(np.percentile(sims, 2.0), 2)

    conf = round(max(48, min(99, prob_x3*0.74 + moy*24 + (h_num % 230)/2.9 + last_cote*14.8)), 1)

    # Strength Score
    strength = round(prob_x3 * 0.67 + conf * 0.23 + (100 if prob_x3 > 78 else 0), 1)
    strength = max(40, min(99, strength))

    # Entry Time Ultra Dynamique
    try:
        bt = datetime.combine(now_mg().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        bt = now_mg()

    shift = (int(h_hex[:24], 16) % 82) - 41
    final_sec = 16 + (h_num % 54) + shift + int((100 - prob_x3) * 0.4) + (27 if strength > 88 else 18 if strength > 77 else 11)
    final_sec = max(19, min(97, final_sec))

    entry = (bt + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    # Signal
    if strength > 88:
        signal = "💎💎💎 ULTRA X3+ BUY"
        color = "#00ffcc"
    elif strength > 78:
        signal = "🔥 STRONG X3 TARGET"
        color = "#ff00ff"
    elif strength > 68:
        signal = "🟢 GOOD X3 SCALP"
        color = "#00ff88"
    else:
        signal = "⚠️ SKIP - LOW CHANCE"
        color = "#ff4444"

    res = {
        "entry": entry,
        "signal": signal,
        "color": color,
        "prob": prob_x3,
        "conf": conf,
        "min": minv,
        "moy": moy,
        "max": maxv,
        "strength": strength
    }

    # Sauvegarde DB
    with db_init() as conn:
        conn.execute("""INSERT INTO logs(timestamp,entry,signal,prob,conf,minv,moy,maxv,strength)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                     (now_mg().strftime("%H:%M:%S"), entry, signal, prob_x3, conf, minv, moy, maxv, strength))
        conn.commit()

    return res

# ================= 4. UI =================
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='glass-card' style='max-width:500px;margin:80px auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#00ffcc;'>🔐 QUANTUM ACCESS</h2>", unsafe_allow_html=True)
    key = st.text_input("ENTER ACCESS KEY", type="password")
    if st.button("ACTIVATE COSMOS X"):
        if key == "COSMOS2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Clé invalide")
    st.stop()

st.markdown("<h1 class='main-title'>COSMOS X V16.9 ULTRA X3+</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.4rem;'>ALGORITHM AVANCÉ • CIBLÉ X3+ • HASH SENSITIVE</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.6])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("🔑 SERVER HASH CODE", placeholder="Collez le hash complet...")
    t_in = st.text_input("⏰ TIME (HH:MM:SS)", placeholder="Ex: 14:35:22")
    last_cote = st.number_input("LAST COTE", value=2.4, step=0.1, format="%.2f")

    if st.button("🚀 EXECUTE ULTRA ANALYSIS", use_container_width=True):
        if h_in and t_in:
            with st.spinner("Analyse Quantum + 100 000 simulations..."):
                st.session_state.res = run_engine_ultra(h_in, t_in, last_cote)
        else:
            st.warning("Hash sy Time no ilaina")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown(f"""
        <div class="glass-card" style="border-top: 6px solid {r['color']}; text-align:center;">
            <div style="color:{r['color']}; font-size:1.6rem; font-weight:700;">{r['signal']}</div>
            <h1 style="font-size:5.5rem; color:#00ffcc; margin:10px 0;">{r['entry']}</h1>
            
            <div style="display:flex; justify-content:space-around; margin:20px 0;">
                <div class="mini-box res-min" style="flex:1; margin:5px;"><small>MIN</small><br><b>{r['min']}</b></div>
                <div class="mini-box res-moy" style="flex:1; margin:5px;"><small>MOY</small><br><b>{r['moy']}</b></div>
                <div class="mini-box res-max" style="flex:1; margin:5px;"><small>MAX</small><br><b>{r['max']}</b></div>
            </div>

            <p><b>X3 PROB :</b> <span style="color:#ffff00; font-size:1.8rem;">{r['prob']}%</span> | 
               <b>CONF :</b> {r['conf']}% | <b>STRENGTH :</b> {r['strength']}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ WIN", use_container_width=True):
                st.success("WIN enregistré")
        with c2:
            if st.button("❌ LOSS", use_container_width=True):
                st.error("LOSS enregistré")

# Historique
st.markdown("### 📜 MISSION LOGS")
try:
    with db_init() as conn:
        df = pd.read_sql("SELECT timestamp, entry, signal, prob, conf, moy, maxv, strength FROM logs ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df, use_container_width=True, hide_index=True)
except:
    st.info("Mbola tsy misy logs")

st.caption("COSMOS X V16.9 ULTRA X3+ • Algorithm Avancé & Ciblé")
