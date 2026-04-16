import streamlit as st  
import hashlib  
import numpy as np  
import pandas as pd  
import sqlite3  
from datetime import datetime, timedelta  
import pytz  

# Ampidirina amin'ny fomba azo antoka ny Machine Learning
try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    st.error("Mila apetraka ny sklearn: pip install scikit-learn")

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
    .guide-box { background: #111; padding: 25px; border-left: 5px solid #ff00cc; border-radius: 10px; line-height: 1.6; }
    .strategy-box { background: #0a1a1a; padding: 20px; border: 1px dashed #00ffcc; border-radius: 10px; margin-top: 15px; }
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
    try:
        conn = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM history ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

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

# ---------------- ML MODEL (Robust Version) ----------------  

def train_model(df):
    if len(df) < 10 or "result" not in df.columns or "cote_moy" not in df.columns:
        return None
    try:
        X = df[["cote_moy"]].values
        y = df["result"].values
        # Ny AI dia mila "classes" farafaharatsiny 2 (1 sy 0) vao afaka mianatra
        if len(np.unique(y)) < 2:
            return None
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X, y)
        return model
    except:
        return None

def predict_win(model, cote):
    if model is None:
        return 0.5
    try:
        return model.predict_proba([[cote]])[0][1]
    except:
        return 0.5

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
    if delta > 43200: delta = 86400 - delta

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

    # ML Logic
    df_hist = load_db()
    model = train_model(df_hist)
    win_prob = predict_win(model, cote_moy)
    
    # Atambatra ny fahatokisana
    final_conf = round((confidence + win_prob * 100) / 2, 1)

    # Signal Logic
    if final_conf >= 85 and cote_moy >= 2.8:
        sig, res = "🔥 ULTRA X3+ SNIPER 🎯", 1
    elif final_conf >= 75:
        sig, res = "🟢 STRONG ENTRY ⚡", 1
    elif final_conf >= 55:
        sig, res = "🟡 TIMING WAIT ⏳", 0
    else:
        sig, res = "🔴 NO ENTRY ❌", 0

    save_db(now.strftime("%H:%M:%S"), heure_tour, entry_time.strftime("%H:%M:%S"), cote_moy, sig, res)

    return {
        "now": now.strftime("%H:%M:%S"),
        "entry": entry_time.strftime("%H:%M:%S"),
        "min": cote_min, "moy": cote_moy, "max": cote_max,
        "conf": final_conf, "sig": sig, "win_prob": round(win_prob*100, 1)
    }

# ---------------- UI ----------------  

st.markdown("<h1>🚀 COSMOS X ANDR V10.2 ⚡</h1>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.5])

with c1:
    st.markdown("### ⌨️ INPUT DATA")
    with st.form("main_form"):
        h_in = st.text_input("🔑 ACTUAL HASH")
        t_in = st.text_input("⏰ TIME (HH:MM:SS)")
        c_ref = st.number_input("📊 COTE REF", value=1.5, step=0.1)
        if st.form_submit_button("🚀 RUN ANALYSIS"):
            if h_in and t_in:
                st.session_state.res = compute(h_in, t_in, c_ref)
            else:
                st.error("Fenoy ny banga rehetra!")

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown(f"""
        <div class="prediction-card">
            <h2 style="color:#00ffcc; text-align:center;">{r['sig']}</h2>
            <div style="display:flex; justify-content:space-around;">
                <span>🧠 CONF: {r['conf']}%</span>
                <span>🤖 AI WIN: {r['win_prob']}%</span>
            </div>
            <hr style="border:1px solid #333">
            <p style="font-size:18px;">⏰ NOW: <b>{r['now']}</b></p>
            <p style="font-size:24px; color:#ff00cc; background:rgba(255,0,204,0.1); padding:10px; border-radius:10px; text-align:center;">
                🎯 ENTRY: <b>{r['entry']}</b>
            </p>
            <div style="display:flex; justify-content:space-around; font-weight:bold;">
                <div>📉 MIN: {r['min']}x</div>
                <div style="color:#00ffcc;">📊 MOY: {r['moy']}x</div>
                <div>🚀 MAX: {r['max']}x</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- HISTORY & GUIDE ----------------  

t_hist, t_guide = st.tabs(["📜 HISTORY", "📖 STRATEGY GUIDE"])

with t_hist:
    df_disp = load_db()
    if not df_disp.empty:
        st.dataframe(df_disp, use_container_width=True)

with t_guide:
    st.markdown("""
    <div class="guide-box">
        <h3 style="color:#00ffcc;">📋 TOROHEVITRA (GUIDE)</h3>
        <p>1. Ampidiro ny Hash farany ary jereo ny lera nivoahany.</p>
        <p>2. Ampiasao ny <b>Cote Ref 1.8 - 2.2</b> ho an'ny fitoniana (stability).</p>
        <p>3. Ny AI dia mila tantara (history) 10 vao manomboka maminany fahombiazana.</p>

        <div class="strategy-box">
            <h3 style="color:#ff00cc; margin-top:0;">🎯 PAIKADY MATANJAKA (PRO STRATEGY)</h3>
            <ul>
                <li><b>Timing Sniper:</b> Midira <b>5 segondra mialoha</b> ny <i>Entry Time</i>.</li>
                <li><b>Target X3:</b> Raha <b>🔥 ULTRA</b>, mivoaha amin'ny 3.00x.</li>
                <li><b>Security First:</b> Raha <b>🟢 STRONG</b>, mivoaha amin'ny <b>Min</b> na <b>Moyen</b>.</li>
                <li><b>Confirmation:</b> Raha <b>🟡 WAIT</b>, aza miloka fa miandrasa scan vaovao.</li>
                <li><b>Dila Lera:</b> Raha vao dila ny lera na dia 1s aza, <b>Ajanona</b> ny bet.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
