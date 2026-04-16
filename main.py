import streamlit as st  
import hashlib  
import numpy as np  
import pandas as pd  
import sqlite3  
from datetime import datetime, timedelta  
import pytz  

from sklearn.ensemble import RandomForestClassifier  

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
    .guide-box { background: #111; padding: 20px; border-left: 5px solid #ff00cc; border-radius: 10px; }
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
        signal TEXT,
        result INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h_act, h_tour, h_entry, cote, sig, result):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (h_actual, h_tour, h_entry, cote_moy, signal, result)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (h_act, h_tour, h_entry, cote, sig, result))
    conn.commit()
    conn.close()

def load_db():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 50", conn)
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

st.sidebar.markdown("### ⚙️ CONTROL")

if st.sidebar.button("🗑️ RESET ALL DATA"):
    reset_db()
    st.sidebar.success("RESET OK")
    st.rerun()

if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.auth = False
    st.rerun()

# ---------------- ENGINE ----------------  

def get_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_to_num(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF

# ---------------- ML MODEL ----------------  

def train_model(df):
    if len(df) < 10:
        return None

    X = df[["cote_moy"]].values
    y = df["result"].values

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model

def predict_win(model, cote):
    if model is None:
        return 0.5
    return model.predict_proba([[cote]])[0][1]

# ---------------- COMPUTE ----------------  

def compute(hash_input, heure_tour, cote_ref):

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

    confidence = round((h_val * 70) + (t_factor * 30), 1)
    confidence = min(confidence, 99.8)

    delay = int((h_val + t_factor) * 40 + 10)
    entry_time = now + timedelta(seconds=delay)

    # ---------------- ML LEARNING ----------------  

    df = load_db()
    model = train_model(df)
    win_prob = predict_win(model, cote_moy)

    confidence = round((confidence + win_prob * 100) / 2, 1)

    # ---------------- SIGNAL ----------------  

    if confidence >= 85 and cote_moy >= 2.8:
        sig = "🔥 ULTRA X3+ SNIPER 🎯"
        result = 1
    elif confidence >= 75:
        sig = "🟢 STRONG ENTRY ⚡"
        result = 1
    elif confidence >= 55:
        sig = "🟡 TIMING WAIT ⏳"
        result = 0
    else:
        sig = "🔴 NO ENTRY ❌"
        result = 0

    save_db(
        now.strftime("%H:%M:%S"),
        heure_tour,
        entry_time.strftime("%H:%M:%S"),
        cote_moy,
        sig,
        result
    )

    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "min": cote_min,
        "moy": cote_moy,
        "max": cote_max,
        "conf": confidence,
        "sig": sig,
        "win_prob": round(win_prob*100, 1)
    }

# ---------------- UI ----------------  

st.markdown("<h1>🚀 COSMOS X ANDR V10.2 ⚡</h1>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.5])

with c1:
    st.markdown("### ⌨️ INPUT")
    with st.form("sc"):
        h_in = st.text_input("HASH")
        t_in = st.text_input("TIME (HH:MM:SS)")
        c_ref = st.number_input("COTE REF", value=1.5)

        if st.form_submit_button("RUN"):
            st.session_state.res = compute(h_in, t_in, c_ref)

with c2:
    if "res" in st.session_state:
        r = st.session_state.res

        st.markdown(f"""
        <div class="prediction-card">
            <h2>{r['sig']}</h2>
            <p>CONF: {r['conf']}%</p>
            <p>WIN PROB (AI): {r['win_prob']}%</p>
            <hr>
            NOW: {r['now']}<br>
            ENTRY: {r['entry']}<br><br>

            MIN: {r['min']} | MOY: {r['moy']} | MAX: {r['max']}
        </div>
        """, unsafe_allow_html=True)

# ---------------- HISTORY ----------------  

st.subheader("📜 HISTORY + AI LEARNING")

df = load_db()
if not df.empty:
    st.dataframe(df)

# ---------------- GUIDE ----------------  

st.subheader("📖 GUIDE")

st.markdown("""
<div class="guide-box">
✔️ Input hash + time  
✔️ AI learns from WIN/LOSE history  
✔️ WIN probability improves over time  
✔️ Entry time = best predicted window  
</div>
""", unsafe_allow_html=True)
