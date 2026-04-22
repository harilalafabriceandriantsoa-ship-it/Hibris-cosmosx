import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
import json
import os
from pathlib import Path

# ================= CONFIGURATION ULTRA =================
st.set_page_config(
    page_title="COSMOS X V17.0 OMEGA X3+", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ================= PERSISTENCE SYSTEM =================
# NAHITSY: Natao relative path mba tsy hisy error permission
DATA_DIR = Path("cosmos_x_data") 
DATA_DIR.mkdir(exist_ok=True)

DB_FILE = DATA_DIR / "cosmos_omega.db"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# ================= PREMIUM STYLING OMEGA =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #0d0033 0%, #000005 50%, #001a0d 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Animated background stars */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            radial-gradient(1.5px 1.5px at 20% 30%, #ffffff88, transparent),
            radial-gradient(1px 1px at 80% 10%, #00ffcc44, transparent),
            radial-gradient(1px 1px at 50% 60%, #ff00ff33, transparent),
            radial-gradient(2px 2px at 35% 85%, #00ffcc55, transparent),
            radial-gradient(1px 1px at 65% 45%, #ffffff22, transparent);
        background-size: 400px 400px, 350px 350px, 300px 300px, 450px 450px, 250px 250px;
        animation: stars-drift 80s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes stars-drift {
        from { background-position: 0 0, 0 0, 0 0, 0 0, 0 0; }
        to { background-position: 400px 400px, -350px 350px, 300px -300px, -450px -450px, 250px 250px; }
    }

    .glass-ultra {
        background: rgba(5, 5, 20, 0.85);
        border: 2px solid rgba(0, 255, 204, 0.4);
        border-radius: 22px;
        padding: 28px;
        backdrop-filter: blur(16px);
        box-shadow: 
            0 0 40px rgba(0, 255, 204, 0.15),
            0 0 80px rgba(0, 255, 204, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
        position: relative;
    }

    .glass-x3-result {
        background: rgba(2, 2, 15, 0.92);
        border: 3px solid;
        border-image: linear-gradient(135deg, #00ffcc, #ff00ff, #00ccff) 1;
        border-radius: 22px;
        padding: 32px;
        backdrop-filter: blur(20px);
        box-shadow: 
            0 0 60px rgba(0, 255, 204, 0.25),
            0 0 120px rgba(255, 0, 255, 0.15);
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.8rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #00ffcc);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 4s ease infinite;
        margin-bottom: 0;
        filter: drop-shadow(0 0 25px rgba(0, 255, 204, 0.6));
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .subtitle-omega {
        text-align: center;
        color: #00ffcc99;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        letter-spacing: 0.5em;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
    }

    .signal-ultra-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 20px #00ffcc, 0 0 40px #00ffcc, 0 0 60px #00ffccaa;
        letter-spacing: 0.1em;
        animation: pulse-ultra 2s ease-in-out infinite;
    }
    
    @keyframes pulse-ultra {
        0%, 100% { filter: drop-shadow(0 0 15px #00ffcc88); }
        50% { filter: drop-shadow(0 0 35px #00ffccee); }
    }

    .signal-strong-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        text-align: center;
        color: #ff00ff;
        text-shadow: 0 0 20px #ff00ff, 0 0 40px #ff00ff88;
        letter-spacing: 0.08em;
    }

    .signal-good-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        color: #00ff88;
        text-shadow: 0 0 15px #00ff88;
    }

    .signal-skip {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
        color: #ff4444;
        text-shadow: 0 0 10px #ff4444;
    }

    .entry-time-omega {
        font-family: 'Orbitron', sans-serif;
        font-size: 5.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00ffcc, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 40px #00ffccaa);
        letter-spacing: 0.12em;
        margin: 24px 0;
        animation: time-glow 3s ease-in-out infinite;
    }
    
    @keyframes time-glow {
        0%, 100% { filter: drop-shadow(0 0 30px #00ffcc88); }
        50% { filter: drop-shadow(0 0 60px #00ffccdd); }
    }

    .metric-box-min {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 200, 100, 0.1));
        border: 2px solid rgba(0, 255, 136, 0.5);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.2);
    }

    .metric-box-moy {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 170, 0, 0.1));
        border: 2px solid rgba(255, 215, 0, 0.5);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.2);
    }

    .metric-box-max {
        background: linear-gradient(135deg, rgba(255, 51, 102, 0.25), rgba(200, 0, 60, 0.1));
        border: 2px solid rgba(255, 51, 102, 0.6);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 30px rgba(255, 51, 102, 0.25);
    }

    .metric-value-omega {
        font-size: 2.8rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        margin: 8px 0;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #ffffff88;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    .x3-prob-omega {
        font-size: 5rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        background: linear-gradient(135deg, #ff00ff, #ff3399, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 40px #ff00ff88);
        margin: 20px 0;
        animation: prob-pulse 2.5s ease-in-out infinite;
    }
    
    @keyframes prob-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    .strength-track-omega {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 99px;
        height: 16px;
        overflow: hidden;
        margin: 10px 0;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }

    .strength-fill-omega {
        height: 100%;
        border-radius: 99px;
        background: linear-gradient(90deg, #ff00ff, #00ffcc);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.6), inset 0 0 15px rgba(255, 255, 255, 0.2);
        transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0088ff 100%) !important;
        color: #000 !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        border-radius: 14px !important;
        height: 60px !important;
        letter-spacing: 0.08em !important;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.4) !important;
        transition: all 0.3s !important;
        border: none !important;
    }

    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 40px rgba(0, 255, 204, 0.6) !important;
    }

    .stTextInput input, .stNumberInput input {
        background: rgba(0, 255, 204, 0.05) !important;
        border: 2px solid rgba(0, 255, 204, 0.3) !important;
        color: #00ffcc !important;
        border-radius: 12px !important;
        font-family: 'Rajdhani', monospace !important;
        font-size: 1rem !important;
    }

    .stat-omega {
        background: rgba(0, 255, 204, 0.08);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 8px 0;
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        color: #00ffcc;
    }

    .stat-label {
        font-size: 0.7rem;
        color: #ffffff66;
        letter-spacing: 0.15em;
    }

    .sec-label-omega {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.65rem;
        letter-spacing: 0.4em;
        color: #00ffcc66;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE FUNCTIONS =================
def db_init():
    """Initialize database with enhanced schema"""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            hash_input TEXT NOT NULL,
            time_input TEXT NOT NULL,
            last_cote REAL NOT NULL,
            entry_time TEXT NOT NULL,
            signal TEXT NOT NULL,
            x3_prob REAL NOT NULL,
            x3_5_prob REAL,
            x4_prob REAL,
            confidence REAL NOT NULL,
            strength REAL NOT NULL,
            min_target REAL NOT NULL,
            moy_target REAL NOT NULL,
            max_target REAL NOT NULL,
            result TEXT,
            real_cote REAL,
            notes TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_predictions INTEGER DEFAULT 0,
            x3_hits INTEGER DEFAULT 0,
            x3_misses INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0.0,
            avg_confidence REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    return conn

def save_prediction(data):
    """Save prediction to database"""
    with db_init() as conn:
        conn.execute("""
            INSERT INTO predictions 
            (timestamp, hash_input, time_input, last_cote, entry_time, signal, 
             x3_prob, x3_5_prob, x4_prob, confidence, strength, 
             min_target, moy_target, max_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['timestamp'], data['hash'], data['time'], data['last_cote'],
            data['entry'], data['signal'],
            data['x3_prob'], data.get('x3_5_prob'), data.get('x4_prob'),
            data['conf'], data['strength'],
            data['min'], data['moy'], data['max']
        ))
        conn.commit()

def update_result(prediction_id, result, real_cote=None):
    """Update prediction result"""
    with db_init() as conn:
        conn.execute("""
            UPDATE predictions 
            SET result = ?, real_cote = ?
            WHERE id = ?
        """, (result, real_cote, prediction_id))
        conn.commit()

def get_recent_predictions(limit=20):
    """Get recent predictions"""
    with db_init() as conn:
        df = pd.read_sql(f"""
            SELECT id, timestamp, entry_time, signal, x3_prob, confidence, 
                   strength, min_target, moy_target, max_target, result, real_cote
            FROM predictions 
            ORDER BY id DESC 
            LIMIT {limit}
        """, conn)
    return df

def get_statistics():
    """Calculate statistics"""
    try:
        with db_init() as conn:
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN result = 'x3_hit' THEN 1 ELSE 0 END) as x3_hits,
                    SUM(CASE WHEN result = 'x3_miss' THEN 1 ELSE 0 END) as x3_misses,
                    AVG(CASE WHEN result IS NOT NULL THEN confidence ELSE NULL END) as avg_conf,
                    AVG(CASE WHEN result IS NOT NULL THEN strength ELSE NULL END) as avg_strength
                FROM predictions
            """).fetchone()
        
        total, x3_hits, x3_misses, avg_conf, avg_strength = stats
        win_rate = (x3_hits / (x3_hits + x3_misses) * 100) if (x3_hits and (x3_hits + x3_misses) > 0) else 0.0
        
        return {
            'total': total or 0,
            'x3_hits': x3_hits or 0,
            'x3_misses': x3_misses or 0,
            'win_rate': round(win_rate, 1),
            'avg_conf': round(avg_conf, 1) if avg_conf else 0,
            'avg_strength': round(avg_strength, 1) if avg_strength else 0
        }
    except:
        return {'total': 0, 'x3_hits': 0, 'x3_misses': 0, 'win_rate': 0, 'avg_conf': 0, 'avg_strength': 0}

def create_backup():
    """Create database backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"cosmos_backup_{timestamp}.db"
    import shutil
    shutil.copy2(DB_FILE, backup_file)
    return backup_file

def reset_database():
    """Reset all data (with backup)"""
    backup_file = create_backup()
    with db_init() as conn:
        conn.execute("DROP TABLE IF EXISTS predictions")
        conn.execute("DROP TABLE IF EXISTS statistics")
        conn.commit()
    db_init()
    return backup_file

# ================= HELPER FUNCTIONS =================
def now_mg():
    """Get current Madagascar time"""
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ================= X3+ ULTRA ENGINE OMEGA =================
def run_engine_omega_x3(hash_input, time_input, last_cote):
    hash_hex = hashlib.sha256(hash_input.encode()).hexdigest()
    hash_num = int(hash_hex[:64], 16)
    np.random.seed(hash_num & 0xFFFFFFFF)
    last_cote = max(1.01, min(last_cote, 15.0))
    
    base = 2.00 + (hash_num % 1200) / 130
    sigma = 0.21 - (last_cote * 0.0024) - ((hash_num % 100) / 10000)
    sims = np.random.lognormal(np.log(base), sigma, 200_000)
    
    x3_prob = round(float(np.mean(sims >= 3.0)) * 100, 2)
    x3_5_prob = round(float(np.mean(sims >= 3.5)) * 100, 2)
    x4_prob = round(float(np.mean(sims >= 4.0)) * 100, 2)
    x5_prob = round(float(np.mean(sims >= 5.0)) * 100, 2)
    x3_count = int(np.sum(sims >= 3.0))
    
    moy = round(float(np.mean(sims)), 2)
    maxv = round(float(np.percentile(sims, 98.5)), 2)
    minv = round(float(np.percentile(sims, 1.5)), 2)
    
    conf = round(max(40, min(99,
        x3_prob * 1.10 + x3_5_prob * 0.45 + x4_prob * 0.30 + moy * 22.0 + (hash_num % 250) / 3.2 + last_cote * 15.5 - (100 - x3_prob) * 0.35
    )), 2)
    
    strength = round(x3_prob * 0.40 + conf * 0.25 + x3_5_prob * 0.15 + (x3_count / 2000) + (100 if x3_prob >= 45 else 80 if x3_prob >= 38 else 60 if x3_prob >= 30 else 40) * 0.20, 2)
    strength = max(35.0, min(99.0, strength))
    
    try:
        base_time = datetime.combine(now_mg().date(), datetime.strptime(time_input.strip(), "%H:%M:%S").time())
    except:
        base_time = now_mg()
    
    hash_shift = (int(hash_hex[:28], 16) % 90) - 45
    prob_adj = int((50 - x3_prob) * 0.6)
    str_bonus = 32 if strength > 90 else 24 if strength > 80 else 18 if strength > 70 else 12
    cote_factor = int(last_cote * 3.5)
    final_seconds = max(18, min(105, 20 + (hash_num % 58) + hash_shift + prob_adj + str_bonus + cote_factor))
    entry_time = (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")
    
    if strength >= 90 and x3_prob >= 42:
        signal, signal_class, confidence_label = "💎💎💎 ULTRA X3+ BUY — OMEGA LOCK", "signal-ultra-x3", "EXTREME"
    elif strength >= 78 and x3_prob >= 35:
        signal, signal_class, confidence_label = "🔥🔥 STRONG X3+ TARGET — HIGH CONF", "signal-strong-x3", "HIGH"
    elif strength >= 65 and x3_prob >= 28:
        signal, signal_class, confidence_label = "🟢 GOOD X3+ SCALP — MODERATE", "signal-good-x3", "MODERATE"
    else:
        signal, signal_class, confidence_label = "⚠️ LOW X3+ — SKIP OR MICRO BET", "signal-skip", "LOW"
    
    result = {
        'timestamp': now_mg().isoformat(), 'hash': hash_input, 'time': time_input, 'last_cote': last_cote,
        'entry': entry_time, 'signal': signal, 'signal_class': signal_class, 'confidence_label': confidence_label,
        'x3_prob': x3_prob, 'x3_5_prob': x3_5_prob, 'x4_prob': x4_prob, 'x5_prob': x5_prob, 'x3_count': x3_count,
        'conf': conf, 'strength': strength, 'min': minv, 'moy': moy, 'max': maxv,
    }
    save_prediction(result)
    return result

# ================= SESSION STATE =================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_prediction_id" not in st.session_state:
    st.session_state.last_prediction_id = None

# ================= LOGIN =================
if not st.session_state.auth:
    st.markdown("<div class='glass-ultra' style='max-width:550px;margin:100px auto;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;color:#00ffcc;font-family:Orbitron;'>🔐 OMEGA ACCESS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#ffffff88;margin-bottom:30px;'>COSMOS X V17.0 ULTRA X3+ SYSTEM</p>", unsafe_allow_html=True)
    key = st.text_input("ENTER OMEGA KEY", type="password", placeholder="Access code...")
    if st.button("🚀 ACTIVATE OMEGA SYSTEM", use_container_width=True):
        if key == "COSMOS2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Invalid Omega Key")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= MAIN APP =================
st.markdown("<h1 class='main-title'>COSMOS X V17.0 OMEGA</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-omega'>ULTRA X3+ • 200K SIMS • PERSISTENT DATA • ADVANCED ML</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 STATISTIQUES OMEGA")
    stats = get_statistics()
    st.markdown(f"<div class='stat-omega'><div class='stat-value'>{stats['total']}</div><div class='stat-label'>TOTAL PREDICTIONS</div></div>", unsafe_allow_html=True)
    if stats['total'] > 0:
        st.markdown(f"<div class='stat-omega'><div class='stat-value'>{stats['win_rate']}%</div><div class='stat-label'>X3+ WIN RATE</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("💾 Create Backup", use_container_width=True):
        bf = create_backup()
        st.success(f"✅ Backup: {bf.name}")
    if st.button("🗑️ Reset Database", use_container_width=True):
        if st.checkbox("Confirmer reset"):
            bf = reset_database()
            st.success("✅ Reset OK")
            st.rerun()

col_input, col_result = st.columns([1, 2.2], gap="large")

with col_input:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    st.markdown("<div class='sec-label-omega'>▸ PARAMÈTRES X3+ ROUND</div>", unsafe_allow_html=True)
    hash_in = st.text_input("🔑 SERVER HASH CODE")
    time_in = st.text_input("⌚ TIME (HH:MM:SS)")
    last_c = st.number_input("📊 LAST COTE", value=2.40)
    if st.button("🚀 E        
