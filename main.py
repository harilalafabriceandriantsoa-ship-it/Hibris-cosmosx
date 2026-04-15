import streamlit as st
import hashlib
import statistics
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="COSMOS X ANDR AI", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0a0a0a,#111);
    color:#00ffcc;
    font-family: monospace;
}
h1,h2,h3{text-align:center;color:#00ffcc;}
.block{
    background:rgba(0,255,204,0.08);
    padding:20px;
    border-radius:15px;
    border:1px solid #00ffcc;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if "history" not in st.session_state:
    st.session_state.history = []

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=120)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "trained" not in st.session_state:
    st.session_state.trained = False

# ---------------- LOGIN ----------------
if not st.session_state.login:
    st.title("🔐 COSMOS AI LOGIN")
    pwd = st.text_input("Password", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.login = True
            st.rerun()
    st.stop()

# ---------------- HASH ENGINE ----------------
def crash(server, client, nonce):
    h = hashlib.sha512(f"{server}:{client}:{nonce}".encode()).hexdigest()
    dec = int(h[-8:],16) or 1
    return round((2**32 * 0.97) / dec, 2)

# ---------------- FEATURES ----------------
def make_features(server, client, nonce):
    h = hashlib.sha512(f"{server}:{client}:{nonce}".encode()).hexdigest()

    f1 = int(h[0:8],16) % 100
    f2 = int(h[8:16],16) % 100
    f3 = int(h[16:24],16) % 100

    return [f1, f2, f3]

# ---------------- DATASET ----------------
def build_dataset(history):
    data = []

    for h in history:
        data.append([
            h["avg"],
            h["accuracy"],
            h["cote"],
            h["confidence"],
            h["label"]
        ])

    if len(data) < 10:
        return None

    df = pd.DataFrame(data, columns=["avg","accuracy","cote","confidence","label"])
    return df

# ---------------- TRAIN AI ----------------
def train_ai():
    df = build_dataset(st.session_state.history)

    if df is None:
        return

    X = df.drop("label", axis=1)
    y = df["label"]

    X_scaled = st.session_state.scaler.fit_transform(X)
    st.session_state.model.fit(X_scaled, y)

    st.session_state.trained = True

# ---------------- COTE ----------------
def compute_cote(avg, acc):
    if acc > 85 and avg > 2.5:
        return 3.0
    elif acc > 75:
        return 2.5
    elif acc > 65:
        return 2.0
    return 1.5

# ---------------- ENTRY TIME (AI + HASH + TIME) ----------------
def entry_time(avg, acc, cote):
    now = datetime.now()

    h = hashlib.sha512(str(now.timestamp()).encode()).hexdigest()
    seed = int(h[:12],16)

    delay = 20 + (seed % 70) + int(avg*10) + int(acc*0.5)

    return (now + timedelta(seconds=delay)).strftime("%H:%M:%S")

# ---------------- PREDICTION ----------------
def predict(server, client, nonce):

    series = [crash(server, client, nonce+i) for i in range(20)]

    avg = round(np.mean(series),2)
    mn = round(min(series),2)
    mx = round(max(series),2)

    acc = int(sum(1 for x in series if x >= 2) / len(series) * 100)

    cote = compute_cote(avg, acc)

    confidence = int((acc * 0.7) + (avg * 10))

    entry = entry_time(avg, acc, cote)

    features = [[avg, acc, cote, confidence]]

    if st.session_state.trained:
        X = st.session_state.scaler.transform(features)
        prob = st.session_state.model.predict_proba(X)[0][1]
        ml_score = round(prob * 100,2)
    else:
        ml_score = None

    label = 1 if acc > 75 and avg > 2 else 0

    st.session_state.history.append({
        "avg": avg,
        "accuracy": acc,
        "cote": cote,
        "confidence": confidence,
        "label": label
    })

    return {
        "avg": avg,
        "min": mn,
        "max": mx,
        "accuracy": acc,
        "cote": cote,
        "confidence": confidence,
        "entry": entry,
        "ml": ml_score
    }

# ---------------- UI ----------------
st.title("🌌 COSMOS X ANDR AI SYSTEM")

server = st.text_input("Server Seed")
client = st.text_input("Client Seed")
nonce = st.number_input("Nonce", value=1)

if st.button("SCAN X3+ AI"):

    res = predict(server, client, nonce)

    train_ai()

    st.markdown(f"""
<div class="block">

# ⏰ ENTRY: {res['entry']}

📊 AVG: {res['avg']}  
📉 MIN: {res['min']} | 📈 MAX: {res['max']}  
🎯 ACCURACY: {res['accuracy']}%  
💎 COTE: x{res['cote']}  
🧠 CONFIDENCE: {res['confidence']}  
🤖 ML SCORE: {res['ml']}

</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.subheader("📜 HISTORY")
for h in reversed(st.session_state.history[-10:]):
    st.write(h)
