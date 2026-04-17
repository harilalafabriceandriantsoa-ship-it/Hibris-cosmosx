import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ================= CONFIG =================

st.set_page_config(page_title="COSMOS X ANDR V12.2 AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');

    .stApp {
        background-color: #05050A;
        color: #00ffcc;
        font-family: 'Share Tech Mono', monospace;
    }

    h1 {
        text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 15px #00ffcc;
    }

    .box {
        padding: 20px;
        border: 2px solid #00ffcc;
        border-radius: 15px;
        background: rgba(0,255,204,0.05);
    }

    .stButton>button {
        background: linear-gradient(90deg,#004d4d,#00ffcc);
        color: black;
        font-weight: bold;
        height: 50px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

DB = "cosmos_v12.db"

# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT,
        time TEXT,
        entry TEXT,
        cote REAL,
        conf REAL,
        signal TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_db(h, t, e, cote, conf, sig):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (hash,time,entry,cote,conf,signal)
    VALUES (?,?,?,?,?,?)
    """, (h,t,e,cote,conf,sig))
    conn.commit()
    conn.close()

def load_db():
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

# ================= AUTH =================

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 ACCESS")
    pwd = st.text_input("PASSWORD", type="password")

    if st.button("LOGIN"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("WRONG PASSWORD")
    st.stop()

# ================= CORE =================

def now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hash_val(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10],16)/0xFFFFFFFFFF

# ================= AI =================

def train(df):
    if len(df) < 5:
        return None, None

    df = df.copy()
    df["h"] = df["hash"].apply(hash_val)

    X = df[["h","conf"]]
    y = df["cote"]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(Xs,y)

    return model, scaler

# ================= ENGINE =================

def compute(h_input, last_time, cote_ref):

    nowt = now()
    sec = nowt.hour*3600 + nowt.minute*60 + nowt.second

    h = hash_val(h_input)

    df = load_db()

    vol = df["cote"].std() if len(df)>5 else 1.0

    # BASE
    base = 1.1 + np.log1p(h*10)*1.5

    # AI
    model, scaler = train(df)

    if model:
        X = scaler.transform([[h,75]])
        ai = model.predict(X)[0]
    else:
        ai = base

    # HASH BOOST
    boost = 1 + (h*0.5)

    # COTE REF (IMPORTANT FIX)
    alpha = 0.18
    ref_norm = float(cote_ref)/5

    final_cote = (
        base*0.25 +
        ai*0.65 +
        ref_norm*alpha
    ) * boost

    # TIME ENGINE
    delay = int(10 + (h*50) + vol*10)
    delay = max(8,min(120,delay))
    entry = nowt + timedelta(seconds=delay)

    # CONFIDENCE
    conf = min(99.5, (h*100) - vol*2 + len(df))

    # SIGNAL
    if conf >= 80 and final_cote >= cote_ref*1.4:
        sig = "🔥 ULTRA X3+"
    elif conf >= 60:
        sig = "🟢 STRONG"
    elif conf >= 40:
        sig = "🟡 WAIT"
    else:
        sig = "🔴 NO ENTRY"

    save_db(h_input,last_time,entry.strftime("%H:%M:%S"),round(final_cote,2),round(conf,1),sig)

    return {
        "entry": entry.strftime("%H:%M:%S"),
        "cote": round(final_cote,2),
        "conf": round(conf,1),
        "sig": sig,
        "vol": round(vol,2),
        "ref": cote_ref
    }

# ================= UI =================

st.title("🚀 COSMOS X ANDR V12.2 AI")

col1,col2 = st.columns(2)

with col1:
    h = st.text_input("HASH")
    t = st.text_input("TIME")
    c = st.number_input("COTE REF", value=2.0)

    if st.button("RUN"):
        st.session_state.res = compute(h,t,c)

with col2:
    if st.button("RESET"):
        reset_db()
        st.success("RESET DONE")

if "res" in st.session_state:
    r = st.session_state.res

    st.markdown(f"""
    <div class="box">
        <h2>{r['sig']}</h2>
        <p>ENTRY: {r['entry']}</p>
        <p>COTE: {r['cote']}</p>
        <p>CONF: {r['conf']}%</p>
        <p>REF: {r['ref']}</p>
        <p>VOL: {r['vol']}</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("HISTORY")
st.dataframe(load_db())
