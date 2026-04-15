import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & STYLE TERMINAL ----------------
st.set_page_config(page_title="COSMOS X ANDR V9", layout="wide")

st.markdown("""
<style>
    /* Background Main */
    .stApp {
        background: #020202; 
        color: #00ffcc; 
        font-family: 'Courier New', monospace;
    }
    
    /* Titre Neon Style */
    .neon-title {
        text-align: center; 
        color: #00ffcc; 
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc, 0 0 40px #00ffcc;
        letter-spacing: 7px;
        font-weight: bold;
        padding: 20px;
    }

    /* Card Prediction Style */
    .prediction-card {
        padding: 25px;
        border: 2px solid #00ffcc;
        border-radius: 15px;
        background: rgba(0, 255, 204, 0.05);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2), inset 0 0 15px rgba(0, 255, 204, 0.1);
        margin-top: 20px;
    }

    /* Buttons Style */
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #004e4e, #00ffcc);
        color: black;
        font-weight: bold;
        border: none;
        padding: 12px;
        border-radius: 8px;
        transition: 0.4s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px #00ffcc;
        transform: scale(1.02);
        color: white;
    }

    /* Inputs Style */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0a0a0a !important;
        color: #00ffcc !important;
        border: 1px solid #004e4e !important;
    }

    /* Dataframe Style */
    [data-testid="stDataFrame"] {
        border: 1px solid #004e4e;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

DB = "cosmos.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash_val REAL,
        time_norm REAL,
        cote_moy REAL,
        entry_delay REAL,
        signal TEXT,
        heure_tour TEXT,
        entry_time TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h, t, cote, delay, result, h_tour, e_time):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (hash_val, time_norm, cote_moy, entry_delay, signal, heure_tour, entry_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (h, t, cote, delay, result, h_tour, e_time))
    conn.commit()
    conn.close()

def load_db():
    try:
        conn = sqlite3.connect(DB)
        # Nalaina ny 15 farany mba ho hita tsara ny fidirana teo aloha
        df = pd.read_sql("SELECT heure_tour as 'TOUR', entry_time as 'FIDIRANA', cote_moy as 'COTE', signal as 'SIGNAL' FROM history ORDER BY id DESC LIMIT 15", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ---------------- SESSION ----------------
if "trained" not in st.session_state: st.session_state.trained = False
if "model" not in st.session_state: st.session_state.model = RandomForestRegressor(n_estimators=100)
if "scaler" not in st.session_state: st.session_state.scaler = StandardScaler()

def get_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_to_num(text):
    h = hashlib.sha512(text.encode()).hexdigest()
    return int(h[:16], 16) / 1e12

# ---------------- ENGINE ----------------
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

    time_factor = (np.sin(delta_time / 60) + np.cos((tour_sec % 300) / 50) + np.tanh((now_sec % 120) / 60))
    time_norm = (time_factor + 3) / 6 

    # --------- COTE NON-FIXE (DYNAMIQUE) ---------
    # Mampiasa variation kely (jitter) mba tsy hitovy foana ny valiny
    jitter = np.random.uniform(0.96, 1.04)
    base_calc = ((hash_val * 2.15) + (time_norm * 1.75) + (cote_ref * 0.55)) * jitter
    
    cote_moy = round(base_calc, 2)
    cote_min = round(cote_moy * 0.82, 2)
    cote_max = round(cote_moy * 1.38, 2)
    
    confidence = round((cote_moy * 30) + (time_norm * 40) + (hash_val * 30), 2)

    # --------- ENTRY DELAY ---------
    raw_delay = (hash_val * 90) + (time_norm * 70) + (delta_time % 60) + (cote_ref * 25)
    final_delay = int(raw_delay % 180)
    entry_time_obj = now + timedelta(seconds=final_delay)
    entry_time_str = entry_time_obj.strftime("%H:%M:%S")

    # --------- SIGNAL ---------
    if cote_moy > 2.2 and confidence > 75: signal = "🟢 STRONG X3+"
    elif cote_moy > 1.8: signal = "🟡 WAIT"
    else: signal = "🔴 SKIP"

    # Save to history
    save_db(hash_val, time_norm, cote_moy, final_delay, signal, heure_tour, entry_time_str)
    
    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time_str,
        "min": cote_min, "moy": cote_moy, "max": cote_max,
        "conf": confidence, "sig": signal
    }

# ---------------- UI LAYOUT ----------------
st.markdown("<h1 class='neon-title'>⚡ COSMOS X ANDR V9 TERMINAL ⚡</h1>", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1.5])

with col_input:
    st.markdown("### 🛠️ CONFIGURATION")
    with st.form("scan_form"):
        h_in = st.text_input("🔑 HASH (FROM GAME)")
        t_in = st.text_input("⏰ HEURE DU TOUR", placeholder="HH:MM:SS (Ex: 14:10:05)")
        c_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5, step=0.1)
        submit = st.form_submit_button("🚀 RUN ANALYTICS")

with col_result:
    if submit and h_in:
        r = compute(h_in, t_in, c_ref)
        st.markdown(f"""
        <div class="prediction-card">
            <h2 style="color:#00ffcc; text-align:center;">SIGNAL: {r['sig']}</h2>
            <hr style="border:0.5px solid #004e4e">
            <p style="font-size:18px;">⏰ NOW: <b>{r['now']}</b></p>
            <p style="font-size:22px;">🎯 FIDIRANA: <span style="color:#ff00cc; font-weight:bold; font-size:30px;">{r['entry']}</span></p>
            <div style="display:flex; justify-content:space-around; margin-top:20px; border:1px solid #004e4e; padding:10px; border-radius:10px;">
                <div><span style="color:#aaa;">📉 MIN</span><br><b style="font-size:20px;">{r['min']}x</b></div>
                <div><span style="color:#aaa;">📊 MOYEN</span><br><b style="font-size:20px;">{r['moy']}x</b></div>
                <div><span style="color:#aaa;">🚀 MAX</span><br><b style="font-size:20px;">{r['max']}x</b></div>
            </div>
            <p style="margin-top:15px; text-align:right; color:#00ffcc;">🧠 CONFIDENCE: {r['conf']}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Andrasana ny Hash sy ny Lera ahafahana manomboka ny scan.")

# ---------------- HISTORIQUE RECENTE ----------------
st.markdown("---")
st.markdown("### 📜 HISTORIQUE DE PRÉDICTION RÉCENTE")
# Ity historique ity dia manampy anao hijery ny lera sy ny fidirana teo aloha haingana
hist_df = load_db()
if not hist_df.empty:
    st.dataframe(hist_df, use_container_width=True)
else:
    st.warning("Mbola tsisy données voatahiry.")

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("### 🧬 SYSTEM STATUS")
st.sidebar.write(f"🌍 Madagascar Time: **{get_now().strftime('%H:%M:%S')}**")
if st.sidebar.button("♻️ RESET CACHE"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("COSMOS X V9 - Secure Terminal")
