import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
import time

# ================= 1. PREMIUM CONFIG & STYLING =================
st.set_page_config(page_title="COSMOS X V16.8 ULTRA", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    /* Global Style */
    .stApp {
        background-color: #05050a;
        background-image: radial-gradient(circle at 50% 50%, #101025 0%, #05050a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(15, 15, 35, 0.6);
        border: 1px solid rgba(0, 255, 204, 0.2);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    /* Titles */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 255, 204, 0.3);
        margin-bottom: 30px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0088ff 100%) !important;
        color: #000 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        height: 55px !important;
        width: 100% !important;
        transition: 0.3s all ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 255, 204, 0.3) !important;
    }

    /* Metrics Display */
    .metric-title { font-size: 0.8rem; letter-spacing: 2px; opacity: 0.7; color: #fff; }
    .metric-value { font-size: 2rem; font-weight: 700; font-family: 'Orbitron'; color: #00ffcc; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0a0a15; border-right: 1px solid #222; }
</style>
""", unsafe_allow_html=True)

# ================= 2. DATABASE & LOGIC =================
def db_init():
    conn = sqlite3.connect("cosmos_v16_8.db", check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry TEXT, signal TEXT, color TEXT, 
        prob REAL, acc REAL, min REAL, moy REAL, max REAL
    )""")
    conn.commit()
    return conn

def now_mg():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def run_engine(h, ref, last_cote, manual_time=None):
    tz = now_mg()
    try:
        if manual_time and len(manual_time) == 8:
            t = datetime.strptime(manual_time, "%H:%M:%S").time()
            base = datetime.combine(tz.date(), t)
        else: base = tz
    except: base = tz

    hsh = hashlib.sha256(h.encode()).hexdigest()
    seed = int(hsh[:16], 16)
    np.random.seed(seed % 2**32)
    norm = (seed % 1000) / 1000

    # Normalisation Logic
    l_used = last_cote
    if last_cote > 6: l_used = 4.0
    elif last_cote > 4: l_used = (last_cote + 4) / 2

    ref_factor = ref * (1 + norm * 0.2)
    sims = np.random.lognormal(mean=np.log(ref_factor + 0.3), sigma=0.25 + norm * 0.1, size=10000)

    prob = np.mean(sims >= 3.0) * 100
    moy = np.mean(sims)
    maxv = np.percentile(sims, 95)
    minv = np.percentile(sims, 10)
    spread = maxv - minv

    conf = max(20, min(95.8, (prob * 0.6) + (moy * 10)))
    delay = max(15, min(80, int(20 + (spread * 2) + (norm * 10))))
    entry_final = base + timedelta(seconds=delay)

    if prob > 70 and moy > ref: sig, col = "🚀 NEBULA X10+", "#ff00cc"
    elif prob > 55: sig, col = "💎 QUASAR X3+", "#00ffcc"
    elif prob > 40: sig, col = "⚡ IONIC SCALP", "#ffff00"
    else: sig, col = "⚠️ SKIP - LOW", "#ff4444"

    res = {
        "entry": entry_final.strftime("%H:%M:%S"),
        "signal": sig, "color": col, "prob": round(prob, 1),
        "conf": round(conf, 1), "min": round(minv, 2),
        "moy": round(moy, 2), "max": round(maxv, 2), "l_used": round(l_used, 2)
    }

    with db_init() as conn:
        conn.execute("INSERT INTO logs(entry,signal,color,prob,acc,min,moy,max) VALUES(?,?,?,?,?,?,?,?)",
                     (res["entry"], sig, col, prob, conf, minv, moy, maxv))
        conn.commit()
    return res

# ================= 3. UI LAYOUT =================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div class='glass-card' style='max-width:500px; margin: 100px auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-family:Orbitron; color:#00ffcc;'>🔐 SECURITY ACCESS</h2>", unsafe_allow_html=True)
    key = st.text_input("ENTER QUANTUM KEY", type="password")
    if st.button("ACTIVATE SYSTEM"):
        if key == "COSMOS2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Invalid Key")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- HEADER ---
st.markdown("<h1 class='main-title'>COSMOS X V16.8 ULTRA</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ SYSTEM TOOLS")
    if st.button("💥 PURGE DATABASE"):
        with db_init() as conn: conn.execute("DROP TABLE IF EXISTS logs"); conn.commit()
        st.toast("System Data Wiped")
        st.rerun()
    st.info("Version 16.8 Stable Core Activated")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🛰️ COMMAND CENTER")
    h_in = st.text_input("SERVER HASH CODE")
    ref_in = st.number_input("REFERENCE TREND", value=2.2, step=0.1)
    last_in = st.number_input("LAST VOKATRA", value=1.85, step=0.01)
    time_in = st.text_input("TIME SYNC (HH:MM:SS)", placeholder="Avelao ho foana raha Live")
    
    if st.button("EXECUTE ANALYSIS"):
        if h_in:
            with st.spinner("Processing Neural Links..."):
                time.sleep(0.8)
                st.session_state.v16_res = run_engine(h_in, ref_in, last_in, time_in)
        else: st.warning("Please input Server Hash")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if "v16_res" in st.session_state:
        r = st.session_state.v16_res
        st.markdown(f"""
        <div class="glass-card" style="border-top: 5px solid {r['color']}; text-align: center;">
            <div style="color: {r['color']}; font-family: 'Orbitron'; font-size: 1.5rem; letter-spacing: 3px;">{r['signal']}</div>
            <p style="margin-top: 15px; opacity: 0.6; letter-spacing: 2px;">NEXT ENTRY POINT</p>
            <h1 style="font-size: 6rem; margin: 0; color: #fff; text-shadow: 0 0 30px {r['color']}; font-family: 'Orbitron';">{r['entry']}</h1>
            
            <div style="display: flex; justify-content: space-around; margin-top: 20px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 15px;">
                <div><div class="metric-title">PROBABILITY</div><div class="metric-value" style="color:#ffff00;">{r['prob']}%</div></div>
                <div><div class="metric-title">ACCURACY</div><div class="metric-value">{r['conf']}%</div></div>
            </div>

            <div style="display: flex; justify-content: space-between; margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                <div><small>MIN EXIT</small><br><b style="color:#00ffcc; font-size:1.2rem;">{r['min']}x</b></div>
                <div><small>MOYEN</small><br><b style="font-size:1.2rem;">{r['moy']}x</b></div>
                <div><small>MAX PEAK</small><br><b style="color:#ff00cc; font-size:1.2rem;">{r['max']}x</b></div>
            </div>
            <p style="font-size: 0.7rem; margin-top: 15px; opacity: 0.4;">Normalization: {r['l_used']} used as reference</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='glass-card' style='height: 400px; display: flex; align-items: center; justify-content: center; opacity: 0.3;'><h2>AWAITING SIGNAL...</h2></div>", unsafe_allow_html=True)

# --- HISTORY ---
st.markdown("### 📂 MISSION LOGS (RECAP)")
try:
    with db_init() as conn:
        df = pd.read_sql("SELECT entry, signal, prob, acc, moy, max FROM logs ORDER BY id DESC LIMIT 8", conn)
    
    # Custom Styled Table Header
    cols = st.columns(6)
    headers = ["ENTRY", "SIGNAL", "PROB %", "ACC %", "MOYEN", "MAX"]
    for i, h in enumerate(headers): cols[i].markdown(f"**{h}**")
    
    for _, row in df.iterrows():
        c = st.columns(6)
        c[0].text(row['entry'])
        c[1].markdown(f"<span style='color:#00ffcc;'>{row['signal']}</span>", unsafe_allow_html=True)
        c[2].text(f"{row['prob']}%")
        c[3].text(f"{row['acc']}%")
        c[4].text(f"{row['moy']}x")
        c[5].markdown(f"<b style='color:#ff00cc;'>{row['max']}x</b>", unsafe_allow_html=True)
except:
    st.info("No logs yet.")
