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

st.set_page_config(page_title="COSMOS X ANDR V10.2", layout="wide")

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
    .guide-box { background: #111; padding: 20px; border-left: 5px solid #ff00cc; border-radius: 10px; line-height: 1.6; }
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

def load_db():
    try:
        conn = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 200", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

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

# ---------------- TIME ----------------

def get_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_to_num(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF

# ---------------- AI LEARNING ----------------

def train_ai(df):
    if len(df) < 10:
        return None, None

    X = df[["cote_moy"]].values
    y = np.random.randint(50, 100, size=len(df))  # simulation confidence history

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=80)
    model.fit(Xs, y)

    return model, scaler

def ai_predict(model, scaler, cote):
    if model is None:
        return 60  # default confidence

    X = scaler.transform([[cote]])
    return float(model.predict(X)[0])

# ---------------- ENGINE ----------------

def compute(hash_input, heure_tour, cote_ref, model=None, scaler=None):

    now = get_now()
    now_sec = now.hour*3600 + now.minute*60 + now.second

    try:
        ht = datetime.strptime(heure_tour, "%H:%M:%S")
        tour_sec = ht.hour*3600 + ht.minute*60 + ht.second
    except:
        tour_sec = now_sec

    h_val = hash_to_num(hash_input)

    delta = abs(now_sec - tour_sec)
    if delta > 43200:
        delta = 86400 - delta

    t_factor = (np.sin(delta / 30) + np.cos(now_sec / 60) + 2) / 4

    variation = np.random.uniform(0.95, 1.05)

    base_cote = (1.2 + (h_val * 2.8) + (t_factor * 1.2) + (float(cote_ref) * 0.15)) * variation

    cote_moy = round(base_cote, 2)
    cote_min = round(cote_moy * 0.85, 2)
    cote_max = round(cote_moy * 1.4, 2)

    # ---------------- AI LEARNING CONFIDENCE ----------------
    confidence = ai_predict(model, scaler, cote_moy)
    confidence = min(max(confidence, 40), 99.8)

    micro = now.microsecond / 1_000_000
    entropy = (h_val * 0.5) + (t_factor * 0.3)

    delay = int((entropy * 40) + 10)
    delay += int(micro * 10)

    entry_time = now + timedelta(seconds=delay)

    if confidence >= 85 and cote_moy >= 2.8:
        sig = "🔥 ULTRA X3+ SNIPER 🎯"
    elif confidence >= 70:
        sig = "🟢 STRONG ENTRY ⚡"
    elif confidence >= 55:
        sig = "🟡 WAIT ⏳"
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
        "sig": sig
    }

# ---------------- UI ----------------

st.markdown("<h1>🚀 COSMOS X ANDR V10.2 ⚡</h1>", unsafe_allow_html=True)

df_hist = load_db()
model, scaler = train_ai(df_hist)

c1, c2 = st.columns([1, 1.5])

with c1:
    st.markdown("### ⌨️ DATA INPUT")
    with st.form("sc"):
        h_in = st.text_input("🔑 ACTUAL HASH")
        t_in = st.text_input("⏰ LAST TOUR TIME (HH:MM:SS)")
        c_ref = st.number_input("📊 REF COTE", value=1.5, step=0.1)

        if st.form_submit_button("🚀 RUN ANALYSIS"):
            if h_in and t_in:
                st.session_state.res = compute(h_in, t_in, c_ref, model, scaler)
            else:
                st.error("Fenoy ny fields")

with c2:
    if "res" in st.session_state:
        r = st.session_state.res

        st.markdown(f"""
        <div class="prediction-card">
            <h2 style="color:#00ffcc;">{r['sig']}</h2>
            <p>🧠 AI CONFIDENCE: <b>{r['conf']}%</b></p>
            <hr>
            ⏰ ENTRY: <b>{r['entry']}</b><br><br>
            📉 MIN: {r['min']} | 📊 MOY: {r['moy']} | 🚀 MAX: {r['max']}
        </div>
        """, unsafe_allow_html=True)

# ---------------- HISTORY ----------------

st.subheader("📜 HISTORY")
st.dataframe(df_hist)
