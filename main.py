import streamlit as st
import numpy as np
import hashlib
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import pickle

# ===================== CONFIG =====================
st.set_page_config(
    page_title="COSMOS X V18.0 OMEGA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== PERSISTENCE =====================
try:
    DATA_DIR = Path(__file__).parent / "cosmos_v18_data"
except:
    DATA_DIR = Path.cwd() / "cosmos_v18_data"

DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_FILE = DATA_DIR / "cosmos_v18.db"
ML_FILE = DATA_DIR / "ml_model.pkl"

TZ_MG = pytz.timezone("Indian/Antananarivo")

# ===================== DATABASE =====================
def db_init():
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            hash_input TEXT,
            time_input TEXT,
            last_cote REAL,
            entry_time TEXT,
            signal TEXT,
            x3_prob REAL,
            prob_x3_5 REAL,
            prob_x4 REAL,
            conf REAL,
            strength REAL,
            target_min REAL,
            target_moy REAL,
            target_max REAL,
            result TEXT DEFAULT 'PENDING'
        )
    """)
    conn.commit()
    return conn

def save_prediction(data):
    try:
        with db_init() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions
                (timestamp, hash_input, time_input, last_cote, entry_time, signal,
                 x3_prob, prob_x3_5, prob_x4, conf, strength,
                 target_min, target_moy, target_max)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data['timestamp'], data['hash'], data['time'], data['last_cote'],
                data['entry'], data['signal'],
                data['prob'], data['prob_x3_5'], data['prob_x4'],
                data['conf'], data['strength'],
                data['min'], data['moy'], data['max']
            ))
            conn.commit()
            return cursor.lastrowid
    except:
        return None

def update_result(pred_id, result):
    try:
        with db_init() as conn:
            conn.execute("UPDATE predictions SET result=? WHERE id=?", (result, pred_id))
            conn.commit()
    except:
        pass

def get_history(limit=15):
    try:
        with db_init() as conn:
            df = pd.read_sql(f"""
                SELECT timestamp as DATE, entry_time as ENTRY,
                       signal as SIGNAL, x3_prob as X3_PROB,
                       conf as CONF, result as RESULT
                FROM predictions
                ORDER BY id DESC LIMIT {limit}
            """, conn)
        return df
    except:
        return pd.DataFrame()

def get_stats():
    try:
        with db_init() as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result='LOSS' THEN 1 ELSE 0 END) as losses
                FROM predictions
            """).fetchone()
        return {'total': row[0] or 0, 'wins': row[1] or 0, 'losses': row[2] or 0}
    except:
        return {'total': 0, 'wins': 0, 'losses': 0}

def reset_db():
    try:
        with db_init() as conn:
            conn.execute("DROP TABLE IF EXISTS predictions")
            conn.commit()
        db_init()
    except:
        pass

# ===================== ML LOGIC =====================
def save_ml(model, scaler):
    try:
        with open(ML_FILE, 'wb') as f:
            pickle.dump({'model': model, 'scaler': scaler}, f)
    except:
        pass

def load_ml():
    try:
        if ML_FILE.exists():
            with open(ML_FILE, 'rb') as f:
                d = pickle.load(f)
                return d['model'], d['scaler']
    except:
        pass
    return None, None

def train_ml():
    try:
        with db_init() as conn:
            df = pd.read_sql("""
                SELECT hash_input, last_cote, x3_prob, conf, strength, result
                FROM predictions
                WHERE result IN ('WIN','LOSS')
            """, conn)
        if len(df) < 10: return None, None
        X, y = [], []
        for _, row in df.iterrows():
            h_val = int(row['hash_input'][:12], 16) if len(row['hash_input']) >= 12 else 0
            X.append([h_val % 1000, (h_val >> 10) % 1000, row['last_cote'], row['x3_prob'], row['conf'], row['strength']])
            y.append(1 if row['result'] == 'WIN' else 0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(np.array(X))
        model = GradientBoostingRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42)
        model.fit(X_scaled, np.array(y))
        save_ml(model, scaler)
        return model, scaler
    except:
        return None, None

# ===================== CSS =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 0%, #0d0033 0%, #000008 60%, #001a0d 100%); color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: clamp(2rem, 8vw, 3.5rem); text-align: center; background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 20px 0; }
    .glass { background: rgba(5, 5, 20, 0.9); border: 2px solid rgba(0, 255, 204, 0.4); border-radius: 20px; padding: 20px; backdrop-filter: blur(12px); margin-bottom: 20px; }
    .entry-mega { font-family: 'Orbitron', sans-serif; font-size: clamp(3rem, 12vw, 5rem); text-align: center; color: #00ffcc; text-shadow: 0 0 30px #00ffcc; margin: 10px 0; }
    .prob-mega { font-size: 3.5rem; font-weight: 900; font-family: 'Orbitron'; text-align: center; color: #ff00ff; }
    .target-box { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 15px; text-align: center; margin: 5px; }
    .target-val { font-size: 1.8rem; font-weight: 900; font-family: 'Orbitron'; }
    /* Mobile optimization for labels */
    .stTextInput label, .stNumberInput label { color: #00ffcc !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION =====================
if "auth" not in st.session_state: st.session_state.auth = False
if "last_res" not in st.session_state: st.session_state.last_res = None
if "last_id" not in st.session_state: st.session_state.last_id = None
if "ml_model" not in st.session_state: st.session_state.ml_model, st.session_state.ml_scaler = load_ml()

# ===================== LOGIN =====================
if not st.session_state.auth:
    st.markdown("<div class='main-title'>COSMOS V18.0</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1,1.5,1])
    with col_b:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        # Nafenina ny label (collapsed) mba tsy hisy soratra ivelany
        pw = st.text_input("PASSWORD", type="password", placeholder="🔑 Entrez le mot de passe...", label_visibility="collapsed")
        if st.button("ACTIVATE OMEGA", use_container_width=True):
            if pw == "COSMOS2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Password Incorrect")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===================== ENGINE =====================
def run_omega_v18(hash_in, time_in, last_cote):
    full_hash = hashlib.sha512(hash_in.encode()).hexdigest()
    hash_num = int(full_hash[:16], 16)
    seed_val = int((hash_num & 0xFFFFFFFFFFFFFFFF) + int(last_cote * 10000))
    np.random.seed(seed_val % (2**32))

    if last_cote < 1.5: base, sigma = 2.12, 0.24
    elif last_cote < 2.5: base, sigma = 2.06, 0.21
    elif last_cote < 3.5: base, sigma = 2.00, 0.19
    else: base, sigma = 1.96, 0.18

    sims = np.random.lognormal(np.log(base + (hash_num % 180) / 1200), max(0.14, sigma), 400_000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    conf = round(max(40, min(99, prob_x3 * 1.2 + last_cote * 10)), 2)
    strength = round(prob_x3 * 0.6 + conf * 0.4, 2)

    # ML Boost
    ml_boost = 0
    if st.session_state.ml_model:
        try:
            h_val = int(hash_in[:12], 16)
            feat = st.session_state.ml_scaler.transform([[h_val % 1000, (h_val >> 10) % 1000, last_cote, prob_x3, conf, strength]])
            ml_boost = float(st.session_state.ml_model.predict(feat)[0]) * 8
            conf = min(99, conf + ml_boost)
            strength = min(99, strength + ml_boost)
        except: pass

    now_mg = datetime.now(TZ_MG)
    entry_time = (now_mg + timedelta(seconds=45 + (hash_num % 30))).strftime("%H:%M:%S")

    res = {
        'timestamp': datetime.now(TZ_MG).strftime("%Y-%m-%d %H:%M:%S"),
        'hash': hash_in[:20], 'time': time_in, 'last_cote': last_cote, 'entry': entry_time,
        'signal': "💎 ULTRA" if strength >= 85 else "🔥 STRONG" if strength >= 70 else "🟢 GOOD",
        'prob': prob_x3, 'prob_x3_5': round(float(np.mean(sims >= 3.5))*100,2), 'prob_x4': round(float(np.mean(sims >= 4.0))*100,2),
        'conf': conf, 'strength': strength, 'ml_boost': round(ml_boost, 1),
        'min': round(float(np.percentile(sims, 30)), 2), 'moy': round(float(np.percentile(sims, 50)), 2), 'max': round(float(np.percentile(sims, 80)), 2)
    }
    return res, save_prediction(res)

# ===================== UI =====================
with st.sidebar:
    st.markdown("### 📊 STATS & ML")
    s = get_stats()
    st.metric("WIN RATE", f"{round(s['wins']/(s['wins']+s['losses'])*100, 1) if (s['wins']+s['losses'])>0 else 0}%")
    if st.button("🧠 TRAIN ML", use_container_width=True):
        m, sc = train_ml()
        if m: st.success("ML Active!")
        else: st.warning("Besoin 10+ data")
    if st.button("🗑️ RESET", use_container_width=True): reset_db(); st.rerun()

st.markdown("<div class='main-title'>COSMOS V18.0</div>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 1.2])

with c1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    # Nesorina ny '###' fa nampiasana HTML style tsotra
    st.markdown("<h3 style='color:#00ffcc; margin-top:0;'>📥 FAMENOANA DATA</h3>", unsafe_allow_html=True)
    h_in = st.text_input("🔐 HASH", placeholder="Server seed...")
    t_in = st.text_input("⏰ TIME", placeholder="Round time...")
    l_in = st.number_input("📊 LAST COTE", value=1.88, step=0.01)
    if st.button("🚀 ANALYSER", use_container_width=True):
        if h_in and t_in:
            with st.spinner("⚡ Analyse..."):
                r, pid = run_omega_v18(h_in, t_in, l_in)
                st.session_state.last_res, st.session_state.last_id = r, pid
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#00ffcc;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prob-mega'>{r['prob']}%</div>", unsafe_allow_html=True)
        
        ca, cb, cc = st.columns(3)
        with ca: st.markdown(f"<div class='target-box'>MIN<br><span class='target-val' style='color:#00ffcc;'>{r['min']}x</span></div>", unsafe_allow_html=True)
        with cb: st.markdown(f"<div class='target-box'>MOY<br><span class='target-val' style='color:#ffd700;'>{r['moy']}x</span></div>", unsafe_allow_html=True)
        with cc: st.markdown(f"<div class='target-box'>MAX<br><span class='target-val' style='color:#ff00ff;'>{r['max']}x</span></div>", unsafe_allow_html=True)
        
        bw, bl = st.columns(2)
        with bw: 
            if st.button("✅ WIN", use_container_width=True): 
                update_result(st.session_state.last_id, 'WIN'); st.rerun()
        with bl: 
            if st.button("❌ LOSS", use_container_width=True): 
                update_result(st.session_state.last_id, 'LOSS'); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📜 HISTORIQUE DES SIGNAUX")
st.dataframe(get_history(), use_container_width=True)
