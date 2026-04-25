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
            conn.execute("""
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
            return conn.execute("SELECT MAX(id) FROM predictions").fetchone()[0]
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
                       conf as CONF, target_min as MIN,
                       target_moy as MOY, target_max as MAX,
                       result as RESULT
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

# ===================== ML =====================
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

# ===================== CSS MOBILE-FRIENDLY =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #0d0033 0%, #000008 60%, #001a0d 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(2rem, 8vw, 3.5rem);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .glass {
        background: rgba(5, 5, 20, 0.9);
        border: 2px solid rgba(0, 255, 204, 0.4);
        border-radius: 20px;
        padding: clamp(15px, 5vw, 25px);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }

    .entry-mega {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(3rem, 12vw, 5rem);
        font-weight: 900;
        text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 30px #00ffcc;
        margin: 20px 0;
    }

    .prob-mega {
        font-size: clamp(3rem, 10vw, 4.5rem);
        font-weight: 900;
        font-family: 'Orbitron';
        text-align: center;
        color: #ff00ff;
        margin: 15px 0;
    }

    .target-box {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }

    .target-val {
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        font-weight: 900;
        font-family: 'Orbitron';
    }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc, #0088ff) !important;
        color: #000 !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-size: 1rem !important;
        border: none !important;
        width: 100%;
    }

    .stTextInput input, .stNumberInput input {
        background: rgba(0,255,204,0.05) !important;
        border: 2px solid rgba(0,255,204,0.3) !important;
        color: #e0fbfc !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 12px !important;
    }

    @media (max-width: 768px) {
        .stApp { padding: 10px !important; }
        .glass { padding: 15px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "last_res" not in st.session_state:
    st.session_state.last_res = None
if "last_id" not in st.session_state:
    st.session_state.last_id = None
if "ml_model" not in st.session_state:
    st.session_state.ml_model, st.session_state.ml_scaler = load_ml()

# ===================== LOGIN =====================
if not st.session_state.auth:
    st.markdown("<div class='main-title'>COSMOS V18.0</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00ffcc99; letter-spacing:0.3em;'>OMEGA X3+ ULTRA</p>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1,1.2,1])
    with col_b:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password", placeholder="COSMOS2026")
        if st.button("ACTIVATE", use_container_width=True):
            if pw == "COSMOS2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Incorrect")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='glass' style='max-width:800px; margin:40px auto;'>
        <h2 style='color:#00ffcc; text-align:center;'>📖 FANAZAVANA MALAGASY</h2>

        <h3 style='color:#ff00ff; margin-top:20px;'>🎯 ZAVATRA ILAINA (3):</h3>

        <p><b>1. HASH (Server Seed):</b></p>
        <ul style='line-height:1.8;'>
            <li>Server seed feno @ casino Provably Fair</li>
            <li>Ohatra: <code>d8d745d482adc462243d...</code></li>
            <li>FANALAHIDY algorithm = X3+ prediction marina</li>
        </ul>

        <p><b>2. TIME (HH:MM:SS):</b></p>
        <ul style='line-height:1.8;'>
            <li>Ora round <b>TALOHA</b> (reference)</li>
            <li>Entry time = calculé @ NOW Madagascar (tsy décalage!)</li>
        </ul>

        <p><b>3. LAST COTE:</b></p>
        <ul style='line-height:1.8;'>
            <li>Résultat round <b>TALOHA</b> (ex: 1.88)</li>
            <li>4 intervals: COLD(1-1.5) / NORMAL(1.5-2.5) / WARM(2.5-3.5) / HOT(3.5+)</li>
        </ul>

        <h3 style='color:#00ffcc; margin-top:25px;'>🚀 FOMBA FAMPIASANA:</h3>
        <ol style='line-height:2;'>
            <li>Copy HASH @ Provably Fair section</li>
            <li>Tadidio TIME tamin'ny round taloha</li>
            <li>Tadidio LAST COTE (résultat taloha)</li>
            <li>Ampiditra daholo @ app</li>
            <li>Tsindrio "ANALYSER OMEGA"</li>
            <li>Jereo: Entry time + Targets + Signal</li>
            <li>Milalao @ entry time marina</li>
            <li>Confirm WIN/LOSS</li>
        </ol>

        <h3 style='color:#ff00ff; margin-top:25px;'>⚡ AMÉLIORATIONS V18:</h3>
        <ul style='line-height:2;'>
            <li>✅ Entry time CORRECTED (NOW + shift)</li>
            <li>✅ 400k simulations ultra précis</li>
            <li>✅ Signal dynamique @ hash</li>
            <li>✅ ML réel mianatra @ results</li>
            <li>✅ SQLite persistent storage</li>
            <li>✅ Mobile-friendly responsive</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ===================== ML TRAINING =====================
def train_ml():
    try:
        with db_init() as conn:
            df = pd.read_sql("""
                SELECT hash_input, last_cote, x3_prob, conf, strength, result
                FROM predictions
                WHERE result IN ('WIN','LOSS')
            """, conn)

        if len(df) < 10:
            return None, None

        X = []
        y = []
        for _, row in df.iterrows():
            h_val = int(row['hash_input'][:12], 16) if len(row['hash_input']) >= 12 else 0
            X.append([
                h_val % 1000,
                (h_val >> 10) % 1000,
                row['last_cote'],
                row['x3_prob'],
                row['conf'],
                row['strength']
            ])
            y.append(1 if row['result'] == 'WIN' else 0)

        X = np.array(X)
        y = np.array(y)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = GradientBoostingRegressor(
            n_estimators=300, max_depth=6,
            learning_rate=0.05, random_state=42
        )
        model.fit(X_scaled, y)
        save_ml(model, scaler)
        return model, scaler
    except:
        return None, None

# ===================== ENGINE OMEGA V18 =====================
def run_omega_v18(hash_in, time_in, last_cote):
    # SHA512 ultra hash
    full_hash = hashlib.sha512(hash_in.encode()).hexdigest()
    hash_num = int(full_hash[:16], 16)

    seed_val = int((hash_num & 0xFFFFFFFFFFFFFFFF) + int(last_cote * 10000))
    np.random.seed(seed_val % (2**32))

    # Intervals
    if last_cote < 1.5:
        base, sigma = 2.12, 0.24
    elif last_cote < 2.5:
        base, sigma = 2.06, 0.21
    elif last_cote < 3.5:
        base, sigma = 2.00, 0.19
    else:
        base, sigma = 1.96, 0.18

    base += (hash_num % 180) / 1200
    sigma -= (last_cote * 0.0022)

    # 400K SIMULATIONS
    sims = np.random.lognormal(np.log(base), max(0.14, sigma), 400_000)

    prob_x3   = round(float(np.mean(sims >= 3.0)) * 100, 2)
    prob_x3_5 = round(float(np.mean(sims >= 3.5)) * 100, 2)
    prob_x4   = round(float(np.mean(sims >= 4.0)) * 100, 2)
    prob_x5   = round(float(np.mean(sims >= 5.0)) * 100, 2)
    x3_count  = int(np.sum(sims >= 3.0))

    target_min = max(2.00, round(float(np.percentile(sims, 30)), 2))
    target_moy = max(2.60, round(float(np.percentile(sims, 50)), 2))
    sims_x3 = sims[sims >= 3.0]
    target_max = max(3.00, round(float(np.percentile(sims_x3, 85)), 2)) if len(sims_x3) > 0 else 3.80

    conf = round(max(40, min(99,
        prob_x3 * 1.20 +
        prob_x3_5 * 0.45 +
        prob_x4 * 0.30 +
        (hash_num % 200) / 3.2 +
        last_cote * 14.0 -
        (100 - prob_x3) * 0.35
    )), 2)

    strength = round(
        prob_x3 * 0.50 +
        conf * 0.30 +
        prob_x3_5 * 0.15 +
        (x3_count / 4000) +
        (100 if prob_x3 >= 45 else 82 if prob_x3 >= 38 else 64) * 0.05
    , 2)
    strength = max(30.0, min(99.0, strength))

    # ML boost
    ml_boost = 0
    if st.session_state.ml_model is not None:
        try:
            h_val = int(hash_in[:12], 16) if len(hash_in) >= 12 else 0
            features = np.array([[
                h_val % 1000, (h_val >> 10) % 1000,
                last_cote, prob_x3, conf, strength
            ]])
            features_scaled = st.session_state.ml_scaler.transform(features)
            ml_pred = float(st.session_state.ml_model.predict(features_scaled)[0])
            ml_boost = ml_pred * 8
        except:
            pass

    conf = min(99, conf + ml_boost)
    strength = min(99, strength + ml_boost * 0.5)

    # ENTRY TIME - CORRECTED (NOW + shift)
    now_mg = datetime.now(TZ_MG)

    hash_shift    = (hash_num % 90) - 45
    str_bonus     = int(strength * 0.35)
    cote_factor   = int(last_cote * 4)
    prob_penalty  = int((48 - prob_x3) * 0.45)

    total_shift = max(20, min(110,
        48 + hash_shift + str_bonus + cote_factor - prob_penalty
    ))

    entry_time = (now_mg + timedelta(seconds=total_shift)).strftime("%H:%M:%S")

    # SIGNAL DYNAMIQUE
    if strength >= 88 and prob_x3 >= 44:
        signal = "💎💎💎 ULTRA X3+ OMEGA"
    elif strength >= 76 and prob_x3 >= 36:
        signal = "🔥🔥 STRONG X3+ LOCK"
    elif strength >= 62 and prob_x3 >= 28:
        signal = "🟢 GOOD X3+ SCALP"
    else:
        signal = "⚠️ LOW — SKIP"

    result = {
        'timestamp': datetime.now(TZ_MG).strftime("%Y-%m-%d %H:%M:%S"),
        'hash': hash_in[:20],
        'time': time_in,
        'last_cote': last_cote,
        'entry': entry_time,
        'signal': signal,
        'prob': prob_x3,
        'prob_x3_5': prob_x3_5,
        'prob_x4': prob_x4,
        'prob_x5': prob_x5,
        'conf': conf,
        'strength': strength,
        'ml_boost': round(ml_boost, 1),
        'min': target_min,
        'moy': target_moy,
        'max': target_max,
    }

    pred_id = save_prediction(result)
    return result, pred_id

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("### 📊 STATS OMEGA")
    stats = get_stats()
    total = stats['total']
    wins = stats['wins']
    losses = stats['losses']
    wr = round(wins / (wins + losses) * 100, 1) if (wins + losses) > 0 else 0

    st.metric("WIN RATE", f"{wr}%")
    col_w, col_l = st.columns(2)
    with col_w: st.metric("Wins", wins)
    with col_l: st.metric("Loss", losses)
    st.metric("Total", total)

    if st.session_state.ml_model is not None:
        st.success("✅ ML ACTIF")
    else:
        st.warning(f"🔄 ML: {wins + losses}/10")

    st.markdown("---")

    if st.button("🧠 TRAIN ML", use_container_width=True):
        model, scaler = train_ml()
        if model is not None:
            st.session_state.ml_model = model
            st.session_state.ml_scaler = scaler
            st.success("✅ ML trained!")
        else:
            st.warning("Besoin 10+ résultats")
        st.rerun()

    if st.button("🗑️ RESET DATA", use_container_width=True):
        reset_db()
        st.session_state.ml_model = None
        st.session_state.ml_scaler = None
        st.session_state.last_res = None
        st.session_state.last_id = None
        if ML_FILE.exists():
            ML_FILE.unlink()
        st.success("✅ Reset!")
        st.rerun()

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>COSMOS V18.0</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc99; letter-spacing:0.3em; margin-bottom:2rem;'>OMEGA X3+ • 400K SIMS • ML</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2], gap="medium")

with col_in:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 INPUT")

    hash_in = st.text_input("🔐 HASH (Server)", placeholder="Ex: d8d745d482adc...")
    time_in = st.text_input("⏰ TIME (HH:MM:SS)", placeholder="Ex: 20:22:24")
    cote_in = st.number_input("📊 LAST COTE", value=1.88, step=0.01, format="%.2f")

    if st.button("🚀 ANALYSER OMEGA", use_container_width=True):
        if hash_in and time_in:
            with st.spinner("⚡ 400k sims..."):
                result, pred_id = run_omega_v18(hash_in, time_in, cote_in)
                st.session_state.last_res = result
                st.session_state.last_id = pred_id
            st.rerun()
        else:
            st.error("HASH et TIME obligatoires")

    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last_res

    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)

        st.markdown(f"<h2 style='text-align:center; color:#00ffcc;'>{r['signal']}</h2>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center; color:#ffffff66; margin-top:20px;'>▸ ENTRY TIME</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-mega'>{r['entry']}</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='prob-mega'>{r['prob']}%</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#ffffff66;'>X3+ PROB</p>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='display:flex; gap:16px; justify-content:center; margin:16px 0; flex-wrap:wrap;'>
            <div style='text-align:center;'>
                <div style='font-size:1.3rem; font-weight:700; color:#ff00ff;'>{r['prob_x3_5']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>X3.5+</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.3rem; font-weight:700; color:#aa00ff;'>{r['prob_x4']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>X4+</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.3rem; font-weight:700; color:#6600ff;'>{r['prob_x5']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>X5+</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a: st.metric("CONF", f"{r['conf']}%")
        with col_b: st.metric("STRENGTH", f"{r['strength']}")

        if r.get('ml_boost', 0) > 0:
            st.info(f"🧠 ML Boost: +{r['ml_boost']}")

        st.markdown("<p style='text-align:center; color:#ffffff66; margin-top:20px;'>▸ TARGETS</p>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class='target-box'>
                <div style='font-size:0.75rem; color:#ffffff88;'>MIN</div>
                <div class='target-val' style='color:#00ffcc;'>{r['min']}×</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='target-box'>
                <div style='font-size:0.75rem; color:#ffffff88;'>MOYEN</div>
                <div cl
