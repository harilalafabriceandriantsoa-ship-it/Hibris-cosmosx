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
st.set_page_config(page_title="COSMOS X ANDR V7", layout="wide")

st.markdown("""
<style>
.stApp {background:#050505;color:#00ffcc;font-family:monospace;}
h1 {text-align:center;color:#00ffcc;}
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
        entry_delay INTEGER,
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
    st.session_state.model = RandomForestRegressor(n_estimators=120)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "trained" not in st.session_state:
    st.session_state.trained = False

# ---------------- TIME ----------------
def get_time():
    tz = pytz.timezone("Indian/Antananarivo")
    now = datetime.now(tz)
    sec = now.hour*3600 + now.minute*60 + now.second
    return now, sec

# ---------------- HASH ----------------
def hash_to_num(text):
    h = hashlib.sha512(text.encode()).hexdigest()
    return int(h[:16], 16) / 1e12

# ---------------- TRAIN AI ----------------
def train_ai():
    df = load_db()
    if len(df) < 20:
        return

    X = df[["hash", "time", "cote"]]
    y = df["entry_delay"]

    Xs = st.session_state.scaler.fit_transform(X)
    st.session_state.model.fit(Xs, y)
    st.session_state.trained = True

# ---------------- AI PREDICT ----------------
def ai_predict(features):
    if not st.session_state.trained:
        return None
    X = st.session_state.scaler.transform([features])
    return st.session_state.model.predict(X)[0]

# ---------------- ENGINE ----------------
def compute(hash_input, cote_ref):

    now, sec = get_time()

    hash_val = hash_to_num(hash_input)
    time_val = (sec % 300) / 300

    # BASE LOGIC
    base = (hash_val * 2.5) + (time_val * 1.2)

    cote_min = round(base * 0.75, 2)
    cote_moy = round(base, 2)
    cote_max = round(base * 1.3, 2)

    confidence = round((cote_moy * 35) + (hash_val * 40), 2)

    # ENTRY TIME (dynamic)
    raw_delay = int(20 + (hash_val * 60) + (cote_ref * 10)) % 90

    ai_delay = ai_predict([hash_val, time_val, cote_ref])
    if ai_delay:
        raw_delay = int((raw_delay + ai_delay) / 2)

    entry_time = now + timedelta(seconds=raw_delay)

    # SIGNAL
    if cote_moy > 2.2 and confidence > 70:
        signal = "🟢 STRONG X3+"
    elif cote_moy > 1.8:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    # SAVE TO DB
    save_db(hash_val, time_val, cote_moy, raw_delay, signal)

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
st.title("🚀 COSMOS X ANDR V7 – AI DATABASE SYSTEM")

hash_in = st.text_input("🔑 HASH")
cote_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5)

if st.button("🚀 SCAN AI ENTRY"):

    if hash_in:
        r = compute(hash_in, cote_ref)

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
st.subheader("📜 HISTORY (DATABASE)")
df = load_db()
st.dataframe(df.tail(20))

# ---------------- GUIDE ----------------
st.subheader("📖 GUIDE UTILISATEUR")

st.markdown("""
### 🎯 COMMENT UTILISER
- 🔑 Entrer HASH
- 📊 Entrer COTE RÉFÉRENCE
- 🚀 Cliquer SCAN

### ⏰ HEURE D’ENTRÉE
- Calcul dynamique basé sur HASH + TIME + COTE
- Ajusté automatiquement par IA

### 🧠 IA SYSTEM
- Apprend des anciens résultats
- Améliore les prédictions avec le temps

### 📊 INTERPRÉTATION
- 🟢 STRONG X3+ → bonne opportunité
- 🟡 WAIT → zone instable
- 🔴 SKIP → éviter le trade
""")
