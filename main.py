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
st.set_page_config(page_title="COSMOS X ANDR V8", layout="wide")

st.markdown("""
<style>
.stApp {background:#050505;color:#00ffcc;font-family:monospace;}
.block {padding:15px;border:1px solid #00ffcc;border-radius:10px;margin:10px 0;}
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
        signal TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h, t, cote, delay, signal):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (hash, time, cote, entry_delay, signal)
        VALUES (?, ?, ?, ?, ?)
    """, (h, t, cote, delay, signal))
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
    sec = now.hour * 3600 + now.minute * 60 + now.second
    return now, sec

# ---------------- HASH ----------------
def hash_val(text):
    h = hashlib.sha512(text.encode()).hexdigest()
    return int(h[:16], 16) / 1e12

# ---------------- AI TRAIN ----------------
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

    # ⏰ HEURE DU TOUR (IMPORTANT FIX)
    now, sec = get_time()
    time_val = sec  # <<<<<< FIXED AND USED

    hash_number = hash_val(hash_input)

    # 📊 BASE LOGIC
    base = (hash_number * 2.3) + ((sec % 300) / 300)

    cote_min = round(base * 0.75, 2)
    cote_moy = round(base, 2)
    cote_max = round(base * 1.3, 2)

    confidence = round((cote_moy * 35) + (hash_number * 40), 2)

    # ⏳ ENTRY TIME (HASH + TIME + COTE REF)
    raw = int((hash_number * 50) + (time_val * 0.02) + (cote_ref * 20)) % 90

    ai_delay = ai_predict([hash_number, time_val, cote_ref])
    if ai_delay:
        raw = int((raw + ai_delay) / 2)

    entry_time = now + timedelta(seconds=20 + raw)

    # 🎯 SIGNAL
    if cote_moy > 2.2 and confidence > 70:
        signal = "🟢 X3+ STRONG"
    elif cote_moy > 1.8:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    # SAVE DB
    save_db(hash_number, time_val, cote_moy, raw, signal)

    train_ai()

    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "hash": hash_input[:10],
        "min": cote_min,
        "moy": cote_moy,
        "max": cote_max,
        "confidence": confidence,
        "signal": signal,
        "time_val": time_val   # <<<<<< visible for debug
    }

# ---------------- UI ----------------
st.title("🚀 COSMOS X ANDR V8 – FIXED ENTRY SYSTEM")

hash_in = st.text_input("🔑 HASH")
cote_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5)

if st.button("🚀 SCAN"):

    if hash_in:

        r = compute(hash_in, cote_ref)

        st.markdown(f"""
<div class="block">
<h2>🎯 RESULT</h2>

⏰ HEURE ACTUELLE: <b>{r['now']}</b><br>
⏳ HEURE DU TOUR (USED): <b>{r['time_val']}</b><br>
🎯 ENTRY TIME: <b>{r['entry']}</b><br><br>

📉 MIN: {r['min']}<br>
📊 MOY: {r['moy']}<br>
📈 MAX: {r['max']}<br><br>

🧠 CONFIDENCE: {r['confidence']}<br>
🔥 SIGNAL: <b>{r['signal']}</b>
</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")
df = load_db()
st.dataframe(df.tail(20))

# ---------------- GUIDE (SEPARATE BOX) ----------------
st.subheader("📖 GUIDE UTILISATEUR")

st.markdown("""
<div class="block">

### 🎯 FAMPIASANA
1. Ampidiro HASH
2. Ampidiro COTE RÉFÉRENCE
3. Tsindrio SCAN

---

### ⏰ LOGIQUE ENTRY
- HASH → mibaiko variation
- HEURE DU TOUR → fotoana marina (Madagascar time)
- COTE REF → manitsy risk
- COMBINAISON → entry window

---

### 🎯 INTERPRETATION
- 🟢 X3+ STRONG = entry possible
- 🟡 WAIT = zone unstable
- 🔴 SKIP = tsy safe

</div>
""", unsafe_allow_html=True)
