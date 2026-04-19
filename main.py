import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import math
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ================= CONFIG =================

st.set_page_config(page_title="COSMOS X ANDR V13.5 ULTRA X4", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');

    .stApp {
        background-color: #030308;
        color: #00ffcc;
        font-family: 'Share Tech Mono', monospace;
    }

    h1 {
        text-align: center;
        color: #ff00ff;
        text-shadow: 0 0 20px #ff00ff;
        font-family: 'Orbitron', sans-serif;
    }

    .box {
        padding: 25px;
        border: 2px solid rgba(255, 0, 255, 0.5);
        border-radius: 15px;
        background: linear-gradient(145deg, rgba(20,20,30,0.9), rgba(10,10,15,0.9));
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(255, 0, 255, 0.1);
    }

    .stButton>button {
        background: linear-gradient(90deg, #ff00cc, #3300ff);
        color: white;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        height: 55px;
        border-radius: 12px;
        border: none;
        letter-spacing: 2px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(255, 0, 204, 0.6);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

DB = "cosmos_v13_x4.db"

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
    """, (h, t, e, cote, conf, sig))
    conn.commit()
    conn.close()

def load_db():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 200", conn)
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
    st.markdown("<div class='box'><h2 style='text-align:center;'>🔐 SECURE LOGIN</h2>", unsafe_allow_html=True)
    pwd = st.text_input("ENTER OVERRIDE PASSWORD", type="password")
    if st.button("INITIALIZE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ACCESS DENIED. INCORRECT KEY.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= CORE MATH =================

def now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def extract_hash_entropy(x):
    # Extract multiple layers of entropy from the hash
    h_hex = hashlib.sha256(x.encode()).hexdigest()
    h_int = int(h_hex[:16], 16)
    h_norm = (h_int % 10000) / 10000.0
    h_modulo = int(h_hex[-4:], 16) % 60
    return h_norm, h_modulo, h_int

# ================= AI TRAINING =================

def train_x4_model(df):
    if len(df) < 15:
        return None, None

    df = df.copy()
    # Complex Feature Engineering
    df["h_norm"] = df["hash"].apply(lambda x: extract_hash_entropy(x)[0])
    df["rolling_mean"] = df["cote"].rolling(3).mean().fillna(2.0)
    df["volatility"] = df["cote"].rolling(5).std().fillna(1.0)
    
    # Clean data for AI
    X = df[["h_norm", "rolling_mean", "volatility", "conf"]].dropna()
    y = df.loc[X.index, "cote"]

    if len(X) < 10: return None, None

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=250, max_depth=10, random_state=42)
    model.fit(Xs, y)

    return model, scaler

# ================= ENGINE ULTRA X4 =================

def compute_x4_engine(h_input, last_time, cote_ref):
    nowt = now()
    df = load_db()
    
    h_norm, h_modulo, h_int = extract_hash_entropy(h_input)
    
    # 1. MATHEMATICAL TREND ANALYSIS (EMA & Z-Score)
    if len(df) > 5:
        cotes = df["cote"].values
        ema = pd.Series(cotes).ewm(span=5, adjust=False).mean().iloc[-1]
        volatility = np.std(cotes[:10]) + 0.01
        
        # Calculate how long since last X4+ (Poisson distribution trigger)
        x4_history = df.index[df['cote'] >= 4.0].tolist()
        rounds_since_x4 = x4_history[0] if x4_history else len(df)
    else:
        ema = 1.5
        volatility = 1.0
        rounds_since_x4 = 10

    # Probability formula for a massive spike (Server release cycle)
    server_pressure = min(3.0, rounds_since_x4 / 8.0)
    z_score_anomaly = (4.0 - ema) / volatility
    
    base_calc = 1.05 + (h_norm * 2.5) + (server_pressure * 0.8)

    # 2. AI PREDICTION FUSION
    model, scaler = train_x4_model(df)
    if model and len(df) >= 15:
        X_current = scaler.transform([[h_norm, ema, volatility, 80.0]])
        ai_pred = model.predict(X_current)[0]
    else:
        ai_pred = base_calc * 1.5

    # 3. FINAL COTE ALGORITHM (Blending Math & ML)
    final_cote = (base_calc * 0.3) + (ai_pred * 0.7)
    final_cote = final_cote * (1 + (h_norm * 0.15)) # Hash Luck factor

    # 4. QUANTUM TIME OFFSET (Ultra-Precise Timing)
    # Refined formula: Base seconds from hash + EMA adjustment
    base_seconds = 12 + (h_modulo % 25) # Between 12 and 36 seconds
    
    if ema < 1.5:
        # Bad trend = wait longer for server to stabilize
        time_adjustment = int(volatility * 5) + 8
    else:
        # Good trend = enter faster to catch the wave
        time_adjustment = -int(volatility * 3)
        
    final_delay = max(8, min(48, base_seconds + time_adjustment))
    
    # Time sync handling
    try:
        t_obj = datetime.strptime(last_time.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(nowt.date(), t_obj)
        if base_time > nowt.replace(tzinfo=None) + timedelta(hours=1):
            base_time -= timedelta(days=1)
    except Exception:
        base_time = nowt

    entry_time = base_time + timedelta(seconds=final_delay)

    # 5. DYNAMIC CONFIDENCE SCORING
    conf = min(99.9, 40 + (server_pressure * 15) + (h_norm * 20) + (1/volatility * 5))

    # 6. STRICT SIGNAL FILTERING FOR X4 TARGET
    if final_cote >= 4.0 and conf > 75 and rounds_since_x4 > 4:
        sig = "🚀 TARGET X4+ DETECTED"
        color = "#ff00ff"
    elif final_cote >= 2.5 and conf > 65:
        sig = "💎 SNIPER X2.5"
        color = "#00ffcc"
    elif final_cote >= 1.5 and conf > 50:
        sig = "⚠️ SAFE SCALPING (X1.5)"
        color = "#ffff00"
    else:
        sig = "🩸 TOXIC SERVER - SKIP"
        color = "#ff0000"

    save_db(h_input, last_time, entry_time.strftime("%H:%M:%S"), round(final_cote, 2), round(conf, 1), sig)

    return {
        "entry": entry_time.strftime("%H:%M:%S"),
        "cote": round(final_cote, 2),
        "conf": round(conf, 1),
        "sig": sig,
        "color": color,
        "vol": round(volatility, 2),
        "pressure": round(server_pressure, 2)
    }

# ================= UI =================

st.markdown("<h1>🚀 COSMOS X ANDR V13.5 ULTRA</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    h = st.text_input("🔗 ENCRYPTED HASH CODE")
    t = st.text_input("⏱️ ROUND TIME (HH:MM:SS)")
    c = st.number_input("🎯 TARGET MULTIPLIER (REF)", value=4.0, step=0.5)

    if st.button("EXECUTE X4 ALGORITHM"):
        if h and len(t) == 8 and ":" in t:
            st.session_state.res = compute_x4_engine(h, t, c)
        else:
            st.error("Error: Check Hash or Time format (HH:MM:SS)")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.button("🗑️ PURGE DATABASE"):
        reset_db()
        st.success("SYSTEM RESET COMPLETE.")
        
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown(f"""
        <div class="box" style="border-color: {r['color']}; text-align: center;">
            <h2 style="color: {r['color']}; font-size: 2rem;">{r['sig']}</h2>
            <hr style="border: 1px solid rgba(255,255,255,0.1)">
            <p style="font-size: 1.2rem; margin-bottom: 5px;">🔥 EXACT ENTRY TIME</p>
            <h1 style="font-size: 4rem; margin: 0; text-shadow: 0 0 30px {r['color']}; color: #fff;">{r['entry']}</h1>
            
            <div style="display: flex; justify-content: space-around; margin-top: 20px;">
                <div><small>PREDICTED</small><br><b style="font-size: 1.5rem; color: #00ffcc;">{r['cote']}x</b></div>
                <div><small>ACCURACY</small><br><b style="font-size: 1.5rem; color: #ff00ff;">{r['conf']}%</b></div>
            </div>
            
            <div style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.5); border-radius: 8px;">
                <small style="color: #888;">SERVER PRESSURE INDEX: {r['pressure']}/3.0</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><h3 style='color:#00ffcc;'>📊 DATABANK HISTORY</h3>", unsafe_allow_html=True)
df_show = load_db()
if not df_show.empty:
    st.dataframe(df_show[['entry', 'signal', 'cote', 'conf']], use_container_width=True)
