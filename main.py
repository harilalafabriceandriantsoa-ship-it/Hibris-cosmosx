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
st.set_page_config(page_title="COSMOS X ANDR V12.1 AI", layout="wide")

st.markdown("""
<style>
    .stApp {background:#020202; color:#00ffcc; font-family: 'Courier New', monospace;}
    h1 {
        text-align: center; color: #00ffcc;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        letter-spacing: 5px; border-bottom: 2px solid #00ffcc;
        padding-bottom: 10px;
    }
    .stButton>button {
        width: 100%; background: linear-gradient(45deg, #004e4e, #00ffcc);
        color: black; font-weight: bold; border: none;
        height: 50px; border-radius: 10px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 30px #00ffcc; transform: translateY(-2px); }
    .prediction-card {
        padding: 25px; border: 2px solid #00ffcc; border-radius: 15px;
        background: rgba(0, 255, 204, 0.05);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2); margin-bottom: 20px;
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
        h_actual TEXT,
        h_tour TEXT,
        h_entry TEXT,
        cote_moy REAL,
        signal TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h_act, h_tour, h_entry, cote, sig):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (h_actual, h_tour, h_entry, cote_moy, signal)
    VALUES (?, ?, ?, ?, ?)
    """, (h_act, h_tour, h_entry, cote, sig))
    conn.commit()
    conn.close()

def load_db_full():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df

def reset_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS history")
    conn.commit()
    conn.close()
    init_db()

# ---------------- LOGIN ----------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1>🔐 SECURITY ACCESS</h1>", unsafe_allow_html=True)
    pwd = st.text_input("ENTER PASSWORD", type="password")
    if st.button("ACTIVATE TERMINAL"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ACCESS DENIED")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("### ⚙️ MODE CONTROL")
mode = st.sidebar.radio("SELECT MODE", ["SAFE", "SNIPER"])

if st.sidebar.button("🗑️ RESET HISTORIQUE"):
    reset_db()
    st.sidebar.success("✅ Historique voafafa!")
    st.rerun()

if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.auth = False
    st.rerun()

# ---------------- CORE ----------------
def get_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_to_num(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF

# ---------------- AI MODEL ----------------
def train_ai():
    df = load_db_full()
    if len(df) < 10:
        return None, None

    df = df.copy()
    df['h_val'] = df['h_actual'].apply(hash_to_num)
    df['hour'] = df['h_entry'].apply(lambda x: int(x.split(":")[0]))
    df['minute'] = df['h_entry'].apply(lambda x: int(x.split(":")[1]))

    X = df[['h_val', 'hour', 'minute']]
    y = df['cote_moy']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=60)
    model.fit(X_scaled, y)

    return model, scaler

# ---------------- COMPUTE WITH ULTRA ENGINE ----------------
def compute(hash_input, heure_tour, cote_ref):
    now = get_now()
    now_sec = now.hour*3600 + now.minute*60 + now.second

    try:
        ht = datetime.strptime(heure_tour, "%H:%M:%S")
        tour_sec = ht.hour*3600 + ht.minute*60 + ht.second
    except:
        tour_sec = now_sec

    h_val = hash_to_num(hash_input)
    h_hex = hashlib.sha256(hash_input.encode()).hexdigest()

    # -------- AUTO REFERENCE --------
    df_hist = load_db_full()
    if len(df_hist) >= 10:
        recent_mean = df_hist.head(10)['cote_moy'].mean()
        cote_ref_dynamic = round(recent_mean, 2)
    else:
        cote_ref_dynamic = cote_ref

    # -------- MODE SWITCH --------
    if mode == "SAFE":
        cote_ref_dynamic *= 0.9
    else:
        cote_ref_dynamic *= 1.2

    # -------- T-FACTOR (Base Momentum) --------
    cycle = 120
    phase = (now_sec % cycle) / cycle
    t_factor = (np.sin(2 * np.pi * phase) + 1) / 2
    momentum = (h_val * 0.5) + (t_factor * 0.5)

    # -------- BASE COTE --------
    base_cote = 1.2 + (h_val * 3.5) + (t_factor * 1.5) + (cote_ref_dynamic * 0.2)

    # -------- AI --------
    model, scaler = train_ai()
    if model:
        X_pred = np.array([[h_val, now.hour, now.minute]])
        X_pred_scaled = scaler.transform(X_pred)
        ai_pred = model.predict(X_pred_scaled)[0]
    else:
        ai_pred = base_cote

    # -------- PATTERN BOOST --------
    boost = 1.0
    if len(df_hist) >= 5:
        last = df_hist.head(5)['cote_moy'].values
        if np.mean(last) < 2:
            boost += 0.3

    if momentum > 0.75:
        boost += 0.2

    final_cote = (base_cote * 0.5 + ai_pred * 0.5) * boost
    cote_moy = round(final_cote, 2)
    cote_min = round(cote_moy * 0.85, 2)
    cote_max = round(cote_moy * 1.5, 2)

    # -------- CONFIDENCE --------
    confidence = round((momentum ** 1.7) * 100, 1)
    confidence = min(confidence, 99.9)

    # -------- NEW ULTRA TIME ENGINE --------
    h_int = int(h_hex[:10], 16)
    h_a, h_b = int(h_hex[8:14], 16), int(h_hex[14:20], 16)
    h_c, h_d = int(h_hex[20:26], 16), int(h_hex[26:32], 16)
    
    base_delay = 18 + (h_int % 25)
    layers = (h_a % 19) + (h_b % 13) + (h_c % 11) + (h_d % 7)
    phase_entropy = (now_sec % 90) // 3
    
    # Amplifier le délai si le mode est SAFE (miandry ela kokoa)
    mode_bias = 8 if mode == "SAFE" else 0 
    
    raw_delay = base_delay + layers + phase_entropy + (int(cote_ref_dynamic * 3) % 17) + mode_bias
    micro = ((h_a % 5) - (h_c % 4))
    
    delay = max(12, min(110, raw_delay + micro))
    entry_time = now + timedelta(seconds=delay)

    # -------- SIGNAL --------
    if confidence >= 88 and cote_moy >= 3:
        sig = "🔥 ULTRA X3+ AI SNIPER 🎯"
    elif confidence >= 72 and cote_moy >= 2:
        sig = "🟢 STRONG AI ENTRY ⚡"
    elif confidence >= 50:
        sig = "🟡 WAIT AI ⏳"
    else:
        sig = "🔴 NO ENTRY ❌"

    save_db(now.strftime("%H:%M:%S"), heure_tour, entry_time.strftime("%H:%M:%S"), cote_moy, sig)

    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "min": cote_min,
        "moy": cote_moy,
        "max": cote_max,
        "conf": confidence,
        "sig": sig,
        "ref": cote_ref_dynamic,
        "mode": mode
    }

# ---------------- UI ----------------
st.markdown("<h1>🚀 COSMOS X ANDR V12.1 AI ⚡</h1>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.5])

with c1:
    with st.form("sc"):
        h_in = st.text_input("🔑 ACTUAL HASH")
        t_in = st.text_input("⏰ LAST TOUR TIME (HH:MM:SS)")
        c_ref = st.number_input("📊 REF COTE (fallback)", value=1.5)

        if st.form_submit_button("🚀 RUN AI"):
            if h_in and t_in:
                st.session_state.res = compute(h_in, t_in, c_ref)
            else:
                st.error("Fenoy tsara")

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown(f"""
        <div class="prediction-card">
            <h2 style="text-align:center;">{r['sig']}</h2>
            <p style="text-align:center;">CONF: {r['conf']}%</p>
            <p>MODE: {r['mode']} | REF: {r['ref']}</p>
            <p>NOW: {r['now']}</p>
            <p>ENTRY: <b>{r['entry']}</b></p>
            <p>MIN: {r['min']}x | MOY: {r['moy']}x | MAX: {r['max']}x</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.markdown("### 📜 HISTORY AI")
df = load_db_full()
if not df.empty:
    st.dataframe(df[['h_actual','h_tour','h_entry','cote_moy','signal']], use_container_width=True)
else:
    st.info("Tsy misy data")
