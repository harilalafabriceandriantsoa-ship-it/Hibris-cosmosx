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
    try:
        conn = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM history", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame(columns=["id", "hash", "time", "cote", "entry_delay", "result"])

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
        return False

    X = df[["hash", "time", "cote"]]
    y = df["entry_delay"]

    Xs = st.session_state.scaler.fit_transform(X)
    st.session_state.model.fit(Xs, y)
    st.session_state.trained = True
    return True

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

    # HEURE DU TOUR
    try:
        ht = datetime.strptime(heure_tour, "%H:%M:%S")
        tour_sec = ht.hour*3600 + ht.minute*60 + ht.second
    except:
        tour_sec = now_sec

    # HASH
    hash_val = hash_to_num(hash_input)

    # --------- TIME FACTOR & MINUIT FIX ---------
    delta_time = abs(now_sec - tour_sec)
    if delta_time > 43200:
        delta_time = 86400 - delta_time

    time_factor = (
        np.sin(delta_time / 60) +
        np.cos((tour_sec % 300) / 50) +
        np.tanh((now_sec % 120) / 60)
    )

    time_norm = (time_factor + 3) / 6 

    # --------- DYNAMIC COTE (NO FIX) ---------
    # Mampiasa randomness kely avy amin'ny Hash mba tsy hitovy foana ny elanelana
    volatility = 0.1 + (hash_val % 0.15) 
    
    # 1. MOYEN (Base)
    base_calc = (hash_val * 2.15) + (time_norm * 1.75) + (cote_ref * 0.55)
    cote_moy = round(base_calc, 2)
    
    # 2. MIN (Dynamic range: 80% hatramin'ny 90%)
    min_ratio = 0.85 - (volatility / 2)
    cote_min = round(cote_moy * min_ratio, 2)
    
    # 3. MAX (Dynamic range: 125% hatramin'ny 145%)
    max_ratio = 1.35 + volatility
    cote_max = round(cote_moy * max_ratio, 2)

    confidence = round(
        (cote_moy * 30) +
        (time_norm * 40) +
        (hash_val * 30),
        2
    )

    # --------- ENTRY DELAY ---------
    raw_delay = (
        (hash_val * 90) +
        (time_norm * 70) +
        (delta_time % 60) +
        (cote_ref * 25)
    )

    ai_delay = ai_predict([hash_val, time_norm, cote_moy])

    if ai_delay:
        raw_delay = (raw_delay * 0.6) + (ai_delay * 0.4)

    final_delay = int(raw_delay % 180)
    entry_time = now + timedelta(seconds=final_delay)

    # --------- SIGNAL ---------
    if cote_moy > 2.2 and confidence > 75:
        signal = "🟢 STRONG X3+"
    elif cote_moy > 1.8:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    save_db(hash_val, time_norm, cote_moy, final_delay, signal)

    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "min": cote_min,
        "moy": cote_moy,
        "max": cote_max,
        "confidence": confidence,
        "signal": signal
    }

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ SYSTEM CONTROL")
if st.sidebar.button("🧠 ENTRAÎNER L'IA"):
    if train_ai():
        st.sidebar.success("✅ L'IA mise à jour !")
    else:
        st.sidebar.warning("⚠️ Besoin de 20 entrées.")

# ---------------- UI ----------------
st.title("🚀 COSMOS X ANDR V9")

with st.form("entry_form"):
    hash_in = st.text_input("🔑 HASH")
    heure_tour = st.text_input("⏰ HEURE DU TOUR (HH:MM:SS)", placeholder="HH:MM:SS")
    cote_ref = st.number_input("📊 COTE RÉFÉRENCE", value=1.5)
    submitted = st.form_submit_button("🚀 SCAN ENTRY")

if submitted:
    if hash_in:
        r = compute(hash_in, heure_tour, cote_ref)
        st.markdown(f"""
# 🎯 RESULT
⏰ NOW: **{r['now']}** | 🎯 ENTRY: **{r['entry']}** 📉 MIN: **{r['min']}** | 📊 MOY: **{r['moy']}** | 📈 MAX: **{r['max']}** 🧠 CONFIDENCE: **{r['confidence']}** | 🔥 SIGNAL: **{r['signal']}**
""")

st.subheader("📜 HISTORY")
st.dataframe(load_db().tail(20)[::-1], use_container_width=True)
