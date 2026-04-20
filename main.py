import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

# ================= CONFIG =================
st.set_page_config(page_title="COSMOS X V16.8 ULTRA STABLE", layout="wide")

# ================= LOGIN =================
def check_access():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("<h2 style='text-align:center;'>🔐 ACCESS</h2>", unsafe_allow_html=True)
        pwd = st.text_input("KEY", type="password")
        if st.button("ENTER"):
            if pwd == "COSMOS2026":
                st.session_state.auth = True
                st.rerun()
        st.stop()
    return True

# ================= DB =================
def db():
    conn = sqlite3.connect("cosmos.db", check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry TEXT,
        signal TEXT,
        color TEXT,
        prob REAL,
        acc REAL,
        min REAL,
        moy REAL,
        max REAL
    )
    """)
    return conn

# ================= TIME =================
def now_mg():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ================= STABLE ENGINE =================
def run_engine(h, ref, last_cote, manual_time=None):

    tz = now_mg()

    try:
        t = datetime.strptime(manual_time, "%H:%M:%S").time() if manual_time else tz.time()
        base = datetime.combine(tz.date(), t)
    except:
        base = tz

    hsh = hashlib.sha256(h.encode()).hexdigest()
    seed = int(hsh[:16], 16)

    np.random.seed(seed % 2**32)

    # ================= STABLE CORE =================
    norm = (seed % 1000) / 1000

    # LAST COTE NORMALISATION (IMPORTANT FIX)
    if last_cote > 6:
        last_cote = 4.0
    elif last_cote > 4:
        last_cote = (last_cote + 4) / 2

    # reference influence
    ref_factor = ref * (1 + norm * 0.2)

    # simulation stable (moins noise)
    sims = np.random.lognormal(
        mean=np.log(ref_factor + 0.3),
        sigma=0.25 + norm * 0.1,
        size=10000
    )

    prob = np.mean(sims >= 3.0) * 100

    moy = np.mean(sims)
    maxv = np.percentile(sims, 95)
    minv = np.percentile(sims, 10)

    spread = maxv - minv

    # ================= STABLE CONF =================
    conf = (prob * 0.6) + (moy * 10)

    conf = max(20, min(95, conf))

    # ================= ENTRY TIME (FIXED STABILITY) =================
    delay = 20 + (spread * 2) + (norm * 10)

    delay = max(15, min(80, int(delay)))

    entry = base + timedelta(seconds=delay)

    # ================= SIGNAL FIXED =================
    if prob > 70 and moy > ref:
        sig, col = "💎 ULTRA BUY", "#ff00cc"
    elif prob > 55:
        sig, col = "🟢 BUY", "#00ffcc"
    elif prob > 40:
        sig, col = "⚡ SCALP", "#ffff00"
    else:
        sig, col = "⚠️ SKIP", "#ff4444"

    result = {
        "entry": entry.strftime("%H:%M:%S"),
        "signal": sig,
        "color": col,
        "prob": round(prob, 1),
        "conf": round(conf, 1),
        "min": round(minv, 2),
        "moy": round(moy, 2),
        "max": round(maxv, 2),
        "last_cote_used": last_cote
    }

    with db() as conn:
        conn.execute("""
        INSERT INTO logs(entry,signal,color,prob,acc,min,moy,max)
        VALUES(?,?,?,?,?,?,?,?)
        """, (
            result["entry"], sig, col, prob, conf,
            minv, moy, maxv
        ))
        conn.commit()

    return result

# ================= UI =================
check_access()

st.title("🚀 COSMOS X V16.8 ULTRA STABLE")

col1, col2 = st.columns(2)

with col1:
    h = st.text_input("HASH")
    ref = st.number_input("REFERENCE COTE", value=2.0)
    last = st.number_input("LAST COTE", value=1.8)
    t = st.text_input("TIME HH:MM:SS")

    if st.button("RUN"):
        if h:
            st.session_state.res = run_engine(h, ref, last, t)

with col2:
    if "res" in st.session_state:
        r = st.session_state.res

        st.markdown(f"""
        <div style="border:2px solid {r['color']}; padding:20px;">
        <h2 style="color:{r['color']}">{r['signal']}</h2>

        <h1>{r['entry']}</h1>

        PROB: {r['prob']}% <br>
        CONF: {r['conf']}%

        <hr>

        MIN: {r['min']}x <br>
        MOY: {r['moy']}x <br>
        MAX: {r['max']}x

        <hr>

        LAST COTE USED: {r['last_cote_used']}
        </div>
        """, unsafe_allow_html=True)

# HISTORY
st.markdown("## HISTORY")
with db() as conn:
    df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 10", conn)
st.dataframe(df)
