import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime
import pytz
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="COSMOS V6 TRUE AI", layout="wide")

st.markdown("""
<style>
.stApp {background:#050505;color:#00ffcc;font-family:monospace;}
h1 {text-align:center;color:#00ffcc;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=120)

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
def hash_to_num(text):
    h = hashlib.sha512(text.encode()).hexdigest()
    return int(h[:16], 16) / 1e12


# ---------------- DATASET BUILDER ----------------
def build_dataset():
    if len(st.session_state.history) < 10:
        return None

    data = []
    for h in st.session_state.history:
        data.append([
            h["hash_val"],
            h["time_val"],
            h["cote"],
            h["label"]
        ])

    df = pd.DataFrame(data, columns=["hash", "time", "cote", "label"])
    return df


# ---------------- TRAIN AI ----------------
def train_ai():
    df = build_dataset()
    if df is None:
        return

    X = df[["hash", "time", "cote"]]
    y = df["label"]

    X_scaled = st.session_state.scaler.fit_transform(X)

    st.session_state.model.fit(X_scaled, y)
    st.session_state.trained = True


# ---------------- PREDICT ----------------
def predict(features):
    if not st.session_state.trained:
        return 0.5

    X = st.session_state.scaler.transform([features])
    return st.session_state.model.predict_proba(X)[0][1]


# ---------------- ENGINE ----------------
def compute(hash_input, cote_ref):

    now, sec = get_time()

    hash_val = hash_to_num(hash_input)
    time_val = (sec % 300) / 300

    # base logic
    base = (hash_val * 2.5) + (time_val * 1.5)

    cote_min = round(base * 0.75, 2)
    cote_moy = round(base, 2)
    cote_max = round(base * 1.3, 2)

    confidence = round((cote_moy * 30) + (hash_val * 40), 2)

    # AI prediction
    ai_score = predict([hash_val, time_val, cote_moy])

    # label simulation (for learning)
    label = 1 if cote_moy > 2.0 and confidence > 60 else 0

    st.session_state.history.append({
        "hash_val": hash_val,
        "time_val": time_val,
        "cote": cote_moy,
        "label": label
    })

    train_ai()

    if ai_score > 0.7:
        signal = "🟢 X3+ ENTRY POSSIBLE"
    elif ai_score > 0.5:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 SKIP"

    return {
        "time": now.strftime("%H:%M:%S"),
        "min": cote_min,
        "moy": cote_moy,
        "max": cote_max,
        "confidence": confidence,
        "ai": round(ai_score * 100, 2),
        "signal": signal
    }


# ---------------- UI ----------------
st.title("🚀 COSMOS V6 TRUE AI")

hash_in = st.text_input("HASH")
cote_ref = st.number_input("COTE REF", value=1.5)

if st.button("SCAN"):

    if hash_in:
        result = compute(hash_in, cote_ref)

        st.markdown(f"""
# 🎯 RESULT

⏰ TIME: {result['time']}  
📉 MIN: {result['min']}  
📊 MOY: {result['moy']}  
📈 MAX: {result['max']}  

🧠 CONFIDENCE: {result['confidence']}  
🤖 AI SCORE: {result['ai']}%  

🔥 SIGNAL: **{result['signal']}**
""")

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY (AI LEARNING)")
for h in reversed(st.session_state.history[-10:]):
    st.write(h)
