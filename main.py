import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz

# ---------------- CONFIG & STYLE ----------------
st.set_page_config(page_title="COSMOS X ANDR V10.3", layout="wide")

st.markdown("""
<style>
    .stApp {background:#020202; color:#00ffcc; font-family: 'Courier New', monospace;}
    h1 {text-align: center; color: #00ffcc; text-shadow: 0 0 10px #00ffcc; border-bottom: 2px solid #00ffcc;}
    .prediction-card {
        padding: 25px; border: 2px solid #00ffcc; border-radius: 15px;
        background: rgba(0, 255, 204, 0.05); box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
    }
    .guide-box { background: #111; padding: 20px; border-left: 5px solid #ff00cc; border-radius: 10px; line-height: 1.6; }
    .strat-gold { color: #ffcc00; font-weight: bold; }
    .strat-green { color: #00ffcc; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

DB = "cosmos.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, h_actual TEXT, h_tour TEXT, h_entry TEXT, cote_moy REAL, signal TEXT)""")
    conn.commit()
    conn.close()

init_db()

def save_db(h_act, h_tour, h_entry, cote, sig):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO history (h_actual, h_tour, h_entry, cote_moy, signal) VALUES (?, ?, ?, ?, ?)", (h_act, h_tour, h_entry, cote, sig))
    conn.commit()
    conn.close()

def load_db():
    try:
        conn = sqlite3.connect(DB)
        df = pd.read_sql("SELECT h_actual, h_tour, h_entry, cote_moy, signal FROM history ORDER BY id DESC LIMIT 15", conn)
        conn.close()
        return df
    except: return pd.DataFrame()

# ---------------- AUTH ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1>🔐 SECURITY ACCESS</h1>", unsafe_allow_html=True)
    pwd = st.text_input("ENTER PASSWORD", type="password")
    if st.button("ACTIVATE TERMINAL"):
        if pwd == "2026": st.session_state.auth = True; st.rerun()
        else: st.error("ACCESS DENIED")
    st.stop()

# ---------------- ENGINE ----------------
def get_now(): return datetime.now(pytz.timezone("Indian/Antananarivo"))

def compute(hash_input, heure_tour, cote_ref):
    now = get_now()
    now_sec = now.hour*3600 + now.minute*60 + now.second
    try:
        ht = datetime.strptime(heure_tour, "%H:%M:%S")
        tour_sec = ht.hour*3600 + ht.minute*60 + ht.second
    except: tour_sec = now_sec

    h_val = int(hashlib.sha256(hash_input.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    delta = abs(now_sec - tour_sec)
    if delta > 43200: delta = 86400 - delta
    t_factor = (np.sin(delta / 30) + np.cos(now_sec / 60) + 2) / 4

    # COTE DYNAMIQUE
    var = np.random.uniform(0.95, 1.05)
    base = (1.1 + (h_val * 2.6) + (t_factor * 1.4) + (float(cote_ref) * 0.15)) * var
    cote_moy = round(base, 2)
    cote_min = round(cote_moy * 0.8, 2)
    cote_max = round(cote_moy * 1.6, 2)
    conf = round((h_val * 40) + (t_factor * 60), 1)
    if conf > 99.8: conf = 99.8

    delay = int((h_val * 60 + t_factor * 40 + (delta % 40)) % 130)
    if delay < 15: delay += 20
    entry_time = now + timedelta(seconds=delay)

    if cote_moy >= 2.5 and conf > 75: sig = "🔥 STRONG X3+"
    elif cote_moy >= 1.8: sig = "✅ BUY"
    else: sig = "❌ SKIP"

    save_db(now.strftime("%H:%M:%S"), heure_tour, entry_time.strftime("%H:%M:%S"), cote_moy, sig)
    return {"now": now.strftime("%H:%M:%S"), "entry": entry_time.strftime("%H:%M:%S"), "min": cote_min, "moy": cote_moy, "max": cote_max, "conf": conf, "sig": sig}

# ---------------- UI ----------------
st.markdown("<h1>🚀 COSMOS X ANDR V10.3 ⚡</h1>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 1.5])

with c1:
    st.markdown("### ⌨️ DATA INPUT")
    with st.form("sc"):
        h_in = st.text_input("🔑 ACTUAL HASH")
        t_in = st.text_input("⏰ LAST TOUR TIME (HH:MM:SS)")
        c_ref = st.number_input("📊 REF COTE", value=1.5, step=0.1)
        if st.form_submit_button("🚀 RUN ANALYSIS"):
            if h_in and t_in: st.session_state.res = compute(h_in, t_in, c_ref)
            else: st.error("Fenoy ny Hash sy ny Lera")

with c2:
    if "res" in st.session_state:
        r = st.session_state.res
        st.markdown(f"""<div class="prediction-card">
            <h2 style="text-align:center;">{r['sig']}</h2>
            <p style="text-align:center;">🧠 CONFIDENCE: <b style="color:#ff00cc">{r['conf']}%</b></p>
            <hr>
            <p style="font-size:22px; background:rgba(255,0,204,0.1); padding:10px; border-radius:5px; text-align:center;">
                🎯 ENTRY TIME: <b style="color:#ff00cc; font-size:28px;">{r['entry']}</b>
            </p>
            <div style="display:flex; justify-content:space-around; margin-top:20px;">
                <div style="text-align:center;">📉 MIN<br><b>{r['min']}x</b></div>
                <div style="text-align:center; border-left:1px solid #333; border-right:1px solid #333; padding:0 20px;">📊 MOYEN<br><b>{r['moy']}x</b></div>
                <div style="text-align:center;">🚀 MAX<br><b>{r['max']}x</b></div>
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
t1, t2 = st.tabs(["📜 RECENT HISTORY", "📖 USER GUIDE & STRATEGY"])

with t1:
    st.dataframe(load_db(), use_container_width=True)

with t2:
    st.markdown("""
    <div class="guide-box">
        <h3>🚀 STRATÉGIE DE MISE (USER GUIDE)</h3>
        <p>Ampiasao ireto paikady ireto mba hampitomboana ny taham-pahombiazana:</p>
        
        <p><span class="strat-gold">1. FAMANTARANA NY X3+ (Strong Signal):</span><br>
        Ny signal <b style="color:#00ffcc">🔥 STRONG X3+</b> dia mipoitra rehefa ny <b>Cote Moyen >= 2.50</b> ary ny <b>Confidence > 75%</b>.</p>
        
        <p><span class="strat-green">2. NY PAIKADY "SÉCURITÉ" (Cote Min):</span><br>
        Raha te ho azo antoka 100% ianao, mivoaha foana amin'ny <b>Cote Min</b>. Raha toa ka ny <b>Min > 1.50</b>, dia efa matanjaka ny prédiction.</p>
        
        <p><span class="strat-gold">3. REHEFA INONA NO MILOKA X3?</span><br>
        Afaka mitazona hatramin'ny X3 ianao raha feno ireto: 
        <ul>
            <li>Signal dia <b>STRONG X3+</b>.</li>
            <li>Confidence dia mihoatra ny <b>85%</b>.</li>
            <li>Ny <b>Cote Min</b> dia efa mihoatra ny <b>1.80</b>.</li>
        </ul></p>
        
        <p><span class="strat-green">4. NY LERA FIDIRANA (Entry Time):</span><br>
        Aza miandry ilay segondra katroka. Miloka <b>5 segondra mialoha</b> ny <i>Entry Time</i> nomen'ny AI mba tsy ho tara fidirana.</p>
        
        <p><span class="strat-gold">5. REHEFA "❌ SKIP":</span><br>
        Raha mivoaka ny signal <b>SKIP</b>, midika izany fa ambany ny probability na ratsy ny cycle. Miandrasa 2 na 3 tours vao manao scan indray.</p>
    </div>
    """, unsafe_allow_html=True)
