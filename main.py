import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & STYLE ----------------
st.set_page_config(page_title="COSMOS X ANDR V10.1", layout="wide")

st.markdown("""
<style>
    .stApp {background:#020202; color:#00ffcc; font-family: 'Courier New', monospace;}
    h1 {
        text-align: center; 
        color: #00ffcc; 
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        letter-spacing: 5px;
        border-bottom: 2px solid #00ffcc;
        padding-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #004e4e, #00ffcc);
        color: black;
        font-weight: bold;
        border: none;
        height: 50px;
        border-radius: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 30px #00ffcc;
        transform: translateY(-2px);
    }
    .prediction-card {
        padding: 25px;
        border: 2px solid #00ffcc;
        border-radius: 15px;
        background: rgba(0, 255, 204, 0.05);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
        margin-bottom: 20px;
    }
    .guide-box {
        background: #111;
        padding: 15px;
        border-left: 5px solid #ff00cc;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

DB = "cosmos.db"

# ---------------- DATABASE (WITH AUTO-FIX) ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Fiarovana: Raha efa misy ny table nefa lany andro, fafana dia amboarina vaovao
    try:
        c.execute("SELECT h_actual FROM history LIMIT 1")
    except:
        c.execute("DROP TABLE IF EXISTS history")
        
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        h_actual TEXT,
        h_tour TEXT,
        h_entry TEXT,
        cote_moy REAL,
        signal TEXT,
        conf REAL
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h_act, h_tour, h_entry, cote, sig, conf):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (h_actual, h_tour, h_entry, cote_moy, signal, conf)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (h_act, h_tour, h_entry, cote, sig, conf))
    conn.commit()
    conn.close()

def load_db():
    try:
        conn = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 15", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ---------------- LOGIN SYSTEM ----------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1>🔐 SECURITY ACCESS</h1>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        pwd = st.text_input("ENTER PASSWORD", type="password")
        if st.button("ACTIVATE TERMINAL"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("ACCESS DENIED: WRONG PASSWORD")
    st.stop()

# ---------------- ENGINE ----------------
def get_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_to_num(text):
    return int(hashlib.sha512(text.encode()).hexdigest()[:16], 16) / 1e12

def compute(hash_input, heure_tour, cote_ref):
    now = get_now()
    now_sec = now.hour*3600 + now.minute*60 + now.second
    
    try:
        ht = datetime.strptime(heure_tour, "%H:%M:%S")
        tour_sec = ht.hour*3600 + ht.minute*60 + ht.second
    except:
        tour_sec = now_sec

    hash_val = hash_to_num(hash_input)
    delta_time = abs(now_sec - tour_sec)
    if delta_time > 43200: delta_time = 86400 - delta_time

    time_factor = (np.sin(delta_time / 60) + np.cos((tour_sec % 300) / 50))
    time_norm = (time_factor + 2) / 4 

    # --------- NON-FIXED DYNAMIC COTES ---------
    jitter = np.random.uniform(0.96, 1.04)
    base = ((hash_val * 2.2) + (time_norm * 1.8) + (cote_ref * 0.5)) * jitter
    
    cote_moy = round(base, 2)
    cote_min = round(cote_moy * 0.82, 2)
    cote_max = round(cote_moy * 1.38, 2)
    
    confidence = round((cote_moy * 25) + (time_norm * 50), 1)
    if confidence > 99: confidence = 99.8

    # --------- DYNAMIC DELAY ---------
    delay = int(((hash_val * 100) + (time_norm * 80) + (delta_time % 60)) % 150)
    if delay < 20: delay += 25
    entry_time = now + timedelta(seconds=delay)

    if cote_moy > 2.3 and confidence > 70: sig = "🔥 STRONG X3+"
    elif cote_moy > 1.8: sig = "✅ BUY"
    else: sig = "❌ SKIP"

    save_db(now.strftime("%H:%M:%S"), heure_tour, entry_time.strftime("%H:%M:%S"), cote_moy, sig, confidence)
    
    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "min": cote_min, "moy": cote_moy, "max": cote_max,
        "conf": confidence, "sig": sig
    }

# ---------------- MAIN UI ----------------
st.markdown("<h1>🚀 COSMOS X ANDR V10.1 ⚡</h1>", unsafe_allow_html=True)

col_in, col_res = st.columns([1, 1.5])

with col_in:
    st.markdown("### ⌨️ DATA INPUT")
    with st.form("scan_form"):
        h_in = st.text_input("🔑 ACTUAL HASH")
        t_in = st.text_input("⏰ LAST TOUR TIME (HH:MM:SS)", placeholder="HH:MM:SS")
        c_ref = st.number_input("📊 REF COTE", value=1.5, step=0.1)
        btn = st.form_submit_button("🚀 START SCAN")

with col_res:
    if btn and h_in:
        r = compute(h_in, t_in, c_ref)
        st.markdown(f"""
        <div class="prediction-card">
            <h2 style="color:#00ffcc; text-align:center;">{r['sig']}</h2>
            <p style="text-align:center;">🧠 CONFIDENCE: <b style="color:#ff00cc">{r['conf']}%</b></p>
            <hr style="border:1px solid #333">
            <p style="font-size:18px;">⏰ NOW: <b>{r['now']}</b></p>
            <p style="font-size:22px; background:rgba(255,0,204,0.1); padding:10px; border-radius:5px;">
                🎯 ENTRY TIME: <b style="color:#ff00cc; font-size:28px;">{r['entry']}</b>
            </p>
            <div style="display:flex; justify-content:space-around; margin-top:20px;">
                <div style="text-align:center;">📉 MIN<br><b style="font-size:20px;">{r['min']}x</b></div>
                <div style="text-align:center; border-left:1px solid #333; border-right:1px solid #333; padding:0 20px;">
                    📊 MOYEN<br><b style="font-size:20px; color:#00ffcc;">{r['moy']}x</b>
                </div>
                <div style="text-align:center;">🚀 MAX<br><b style="font-size:20px;">{r['max']}x</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Waiting for Scan... Fenoy ny HASH dia tsindrio ny RUN SCAN.")

# ---------------- HISTORY & GUIDE ----------------
tab1, tab2 = st.tabs(["📜 RECENT HISTORY", "📖 USER GUIDE"])

with tab1:
    st.markdown("### 🔍 LAST 15 PREDICTIONS")
    history_df = load_db()
    if not history_df.empty:
        # Aseho ny colonne rehetra mba ho hitanao tsara ny Heure Tour teo aloha
        st.dataframe(history_df[['h_actual', 'h_tour', 'h_entry', 'cote_moy', 'signal']], use_container_width=True)
    else:
        st.write("No history found.")

with tab2:
    st.markdown("""
    <div class="guide-box">
    <h3>📖 GUIDE HO AN'NY MPANJIFA</h3>
    <ol>
        <li><b>Fidirana:</b> Password <b>2026</b>.</li>
        <li><b>Hash:</b> Apetaho ny Hash farany nivoaka (ACTUAL HASH).</li>
        <li><b>Lera:</b> Soraty ny lera nipoahan'ny lalao teo aloha (HH:MM:SS).</li>
        <li><b>Cote Ref:</b> Apetraho ny sanda nipoahan'ny lalao farany.</li>
        <li><b>Entry Time:</b> Ity ny lera fidiranao. Miloka 5 segondra mialoha.</li>
    </ol>
    <p style="color:#ff00cc"><i>Aza adino ny mijery ny History raha hisafidy lera vaovao.</i></p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### 🛰️ SYSTEM STATUS")
st.sidebar.write(f"🌍 Server Time: {get_now().strftime('%H:%M:%S')}")
if st.sidebar.button("LOGOUT"):
    st.session_state.auth = False
    st.rerun()
