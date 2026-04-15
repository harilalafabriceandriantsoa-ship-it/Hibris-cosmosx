import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS X ANDR V9", layout="wide")

st.markdown("""
<style>
.stApp {background:#050505;color:#00ffcc;font-family:monospace;}
h1 {text-align:center;}
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
        hash REAL,
        time REAL,
        cote REAL,
        entry_delay REAL,
        result TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h, t, cote, delay, result):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (hash, time, cote, entry_delay, result)
    VALUES (?, ?, ?, ?, ?)
    """, (h, t, cote, delay, result))
    conn.commit()
    conn.close()

def load_db():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history", conn)
    conn.close()
    return df

# ---------------- SESSION ----------------
if "model" not in st.session_state:
    st.session_state.model = RandomForestRegressor(n_estimators=150)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "trained" not in st.session_state:
    st.session_state.trained = False

# ---------------- TIME ----------------
def get_now():
    tz = pytz.timezone("Indian/Antananarivo")
    return datetime.now(tz)

# ---------------- HASH ----------------
def hash_to_num(text):
    h = hashlib.sha512(text.encode()).hexdigest()
    return int(h[:16], 16) / 1e12

# ---------------- AI ----------------
def train_ai():
    df = load_db()
    if len(df) < 20:
        return

    X = df[["hash", "time", "cote"]]
    y = df["entry_delay"]

    Xs = st.session_state.scaler.fit_transform(X)
    st.session_state.model.fit(Xs, y)
    st.session_state.trained = True

def ai_predict(features):
    if not st.session_state.trained:
        return None
    X = st.session_state.scaler.transform([features])
    return st.session_state.model.predict(X)[0]

# ---------------- ENGINE ----------------
def compute(hash_input, heure_tour, cote_ref):

    now = get_now()

    # HEURE ACTUEL
    now_sec = now.hour*3600 + now.minute*60 + now.second

    # HEURE DU TOUR (INPUT)
    try:
        ht = datetime.strptime(heure_tour, "%H:%M:%S")
        tour_sec = ht.hour*3600 + ht.minute*60 + ht.second
    except:
        tour_sec = now_sec

    # HASH
    hash_val = hash_to_num(hash_input)

    # --------- DYNAMIC TIME FACTOR (NO FIX) ---------
    delta_time = abs(now_sec - tour_sec)

    time_factor = (
        np.sin(delta_time / 60) +
        np.cos((tour_sec % 300) / 50) +
        np.tanh((now_sec % 120) / 60)
    )

    time_norm = (time_factor + 3) / 6  # normalize 0-1

    # --------- CORE FORMULA ---------
    base = (
        (hash_val * 2.2) +
        (time_norm * 1.8) +
        (cote_ref * 0.6)
    )

    cote_min = round(base * 0.8, 2)
    cote_moy = round(base, 2)
    cote_max = round(base * 1.25, 2)

    confidence = round(
        (cote_moy * 30) +
        (time_norm * 40) +
        (hash_val * 30),
        2
    )

    # --------- ENTRY DELAY (100% DYNAMIC) ---------
    raw_delay = (
        (hash_val * 90) +
        (time_norm * 70) +
        (delta_time % 60) +
        (cote_ref * 25)
    )

    ai_delay = ai_predict([hash_val, time_norm, cote_ref])

    if ai_delay:
        raw_delay = (raw_delay * 0.6) + (ai_delay * 0.4)

    final_delay = int(raw_delay % 180)  # NEVER FIX

    entry_time = now + timedelta(seconds=final_delay)

    # --------- SIGNAL ---------
    if cote_moy > 2.2 and confidence > 75:
        signal = "🟢 STRONG X3+"
    elif cote_moy > 1.8:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    # SAVE
    save_db(hash_val, time_norm, cote_moy, final_delay, signal)
    train_ai()

    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "min": cote_min,
        "moy": cote_moy,
        "max": cote_max,
        "confidence": confidence,
        "signal": signal
    }

# ---------------- UI ----------------
st.title("🚀 COSMOS X ANDR V9")

hash_in = st.text_input("🔑 HASH")
heure_tour = st.text_input("⏰ HEURE DU TOUR (HH:MM:SS)")
cote_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5)

if st.button("🚀 SCAN ENTRY"):

    if hash_in:

        r = compute(hash_in, heure_tour, cote_ref)

        st.markdown(f"""
# 🎯 RESULT

⏰ NOW: {r['now']}  
🎯 ENTRY: {r['entry']}  

📉 MIN: {r['min']}  
📊 MOY: {r['moy']}  
📈 MAX: {r['max']}  

🧠 CONFIDENCE: {r['confidence']}  
🔥 SIGNAL: **{r['signal']}**
""")

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")
st.dataframe(load_db().tail(20))

# ---------------- GUIDE ----------------
st.subheader("📖 GUIDE UTILISATEUR")

st.markdown("""
### 🎯 INPUT
- HASH
- HEURE DU TOUR
- COTE RÉFÉRENCE

### ⚙️ SYSTEM
- HASH → randomness
- HEURE ACTUEL → real-time sync
- HEURE TOUR → cycle timing
- COTE → filter puissance

### ⏰ ENTRY
- Tsy fixe
- Miova arakaraka ireo 3 inputs

### 🧠 AI
- Mianatra amin'ny historique
- Manitsy delay

### 🔥 SIGNAL
- 🟢 STRONG X3+
- 🟡 WAIT
- 🔴 SKIP
""")
