import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path

st.set_page_config(page_title="COSMOS V19 OMEGA", layout="wide", initial_sidebar_state="collapsed")

try:
    DATA_DIR = Path(__file__).parent / "cosmos_v19_data"
except:
    DATA_DIR = Path.cwd() / "cosmos_v19_data"
DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_FILE = DATA_DIR / "cosmos_v19.db"

TZ = pytz.timezone("Indian/Antananarivo")

def db_init():
    conn=sqlite3.connect(str(DB_FILE),check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS preds(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,hash_in TEXT,time_in TEXT,last_cote REAL,
        entry TEXT,signal TEXT,p3 REAL,p3_5 REAL,p4 REAL,p5 REAL,
        strength REAL,cur_state TEXT,hot_p REAL,
        tmin REAL,tmoy REAL,tmax REAL,result TEXT DEFAULT 'PENDING')""")
    conn.commit(); return conn

def save_pred(d):
    try:
        with db_init() as c:
            c.execute("INSERT INTO preds(ts,hash_in,time_in,last_cote,entry,signal,p3,p3_5,p4,p5,strength,cur_state,hot_p,tmin,tmoy,tmax) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (d["ts"],d["hash"],d["time"],d["last_cote"],d["entry"],d["signal"],d["p3"],d["p3_5"],d["p4"],d["p5"],d["strength"],d["cur_state"],d["hot_p"],d["tmin"],d["tmoy"],d["tmax"]))
            c.commit()
            return c.execute("SELECT MAX(id) FROM preds").fetchone()[0]
    except: return None

def update_result(pid,res):
    try:
        with db_init() as c: c.execute("UPDATE preds SET result=? WHERE id=?",(res,pid)); c.commit()
    except: pass

def get_history(n=20):
    try:
        with db_init() as c:
            return pd.read_sql(f"SELECT ts,entry,signal,p3,strength,cur_state,hot_p,tmin,tmoy,tmax,result FROM preds ORDER BY id DESC LIMIT {n}",c)
    except: return pd.DataFrame()

def get_stats():
    try:
        with db_init() as c:
            r=c.execute("SELECT COUNT(*),SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END),SUM(CASE WHEN result='LOSS' THEN 1 ELSE 0 END) FROM preds").fetchone()
            return {"total":r[0] or 0,"wins":r[1] or 0,"losses":r[2] or 0}
    except: return {"total":0,"wins":0,"losses":0}

def get_cotes_from_db():
    try:
        with db_init() as c:
            rows=c.execute("SELECT last_cote FROM preds ORDER BY id DESC LIMIT 50").fetchall()
            return [r[0] for r in rows]
    except: return []

def reset_db():
    try:
        with db_init() as c: c.execute("DROP TABLE IF EXISTS preds"); c.commit()
        db_init()
    except: pass

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 50% 0%,#0d0033 0%,#000008 55%,#001a0d 100%);color:#e0fbfc;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(1.8rem,7vw,3rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2px}
.glass{background:rgba(5,5,20,.9);border:2px solid rgba(0,255,204,.4);border-radius:18px;padding:clamp(12px,4vw,22px);backdrop-filter:blur(12px);margin-bottom:16px}
.entry{font-family:'Orbitron';font-size:clamp(3rem,12vw,5rem);font-weight:900;text-align:center;color:#00ffcc;text-shadow:0 0 30px #00ffcc;margin:16px 0}
.prob{font-size:clamp(2.5rem,10vw,4rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#ff00ff;margin:10px 0}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(1rem,3.5vw,1.6rem);font-weight:900;color:#00ffcc;text-shadow:0 0 20px #00ffcc;padding:10px}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.4rem);font-weight:700;color:#ff00ff;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.3rem);color:#ff6600;padding:10px}
.tbox{background:rgba(255,255,255,.05);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.4rem,5vw,2.2rem);font-weight:900;font-family:'Orbitron'}
.mbox{background:rgba(0,255,204,.06);border:1px solid rgba(0,255,204,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.mv{font-size:1.4rem;font-weight:900;font-family:'Orbitron';color:#00ffcc}
.stButton>button{background:linear-gradient(135deg,#00ffcc,#0088ff)!important;color:#000!important;font-weight:900!important;border-radius:11px!important;height:52px!important;border:none!important;width:100%!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 22px rgba(0,255,204,.5)!important}
.stTextInput input,.stNumberInput input{background:rgba(0,255,204,.04)!important;border:2px solid rgba(0,255,204,.22)!important;color:#e0fbfc!important;border-radius:11px!important;font-size:.9rem!important;padding:10px 13px!important}
.stTextInput input:focus,.stNumberInput input:focus{border-color:rgba(0,255,204,.65)!important}
.stSelectbox>div>div{background:rgba(0,255,204,.04)!important;border:2px solid rgba(0,255,204,.22)!important;border-radius:11px!important;color:#e0fbfc!important}
@media(max-width:768px){.glass{padding:11px!important}}
</style>
""", unsafe_allow_html=True)

for k,v in [("auth",False),("result",None),("last_id",None),("ck",0)]:
    if k not in st.session_state: st.session_state[k]=v

# ============================================================
# MARKOV + BAYESIAN
# ============================================================
STATES=["COLD","NORMAL","WARM","HOT"]

def cote_to_state(c):
    if c<1.5: return "COLD"
    if c<2.5: return "NORMAL"
    if c<3.5: return "WARM"
    return "HOT"

def build_markov_from_db():
    cotes=get_cotes_from_db()
    trans={s:{s2:1 for s2 in STATES} for s in STATES}
    for i in range(len(cotes)-1):
        s1=cote_to_state(cotes[i]); s2=cote_to_state(cotes[i+1])
        trans[s1][s2]+=1
    return {s:{s2:trans[s][s2]/sum(trans[s].values()) for s2 in STATES} for s in STATES}

def markov_predict(last_cote):
    matrix=build_markov_from_db()
    cur=cote_to_state(last_cote)
    p=matrix[cur]
    hot_p=p.get("HOT",0)+p.get("WARM",0)
    return hot_p,cur

def bayesian_update(base_prob):
    try:
        with db_init() as c:
            rows=c.execute("SELECT result FROM preds WHERE result IN ('WIN','LOSS') ORDER BY id DESC LIMIT 20").fetchall()
        if len(rows)<3: return base_prob
        hits=sum(1 for r in rows if r[0]=="WIN")
        total=len(rows)
        likelihood=(hits+1)/(total+2)
        prior=base_prob/100
        posterior=(likelihood*prior)/((likelihood*prior)+((1-likelihood)*(1-prior))+1e-9)
        return round(min(95,max(30,posterior*100)),1)
    except: return base_prob

# ============================================================
# ENGINE
# ============================================================
def run_engine(hash_in, time_in, last_cote):
    fh=hashlib.sha512(hash_in.encode()).hexdigest()
    hn=int(fh[:16],16)
    sv=int((hn&0xFFFFFFFFFFFFFFFF)+int(last_cote*10000))
    np.random.seed(sv%(2**32))

    if last_cote<1.5:   base,sigma=2.12,0.24
    elif last_cote<2.5: base,sigma=2.06,0.21
    elif last_cote<3.5: base,sigma=2.00,0.19
    else:               base,sigma=1.96,0.18
    base+=(hn%180)/1200; sigma-=last_cote*0.0022

    sims=np.random.lognormal(np.log(base),max(0.14,sigma),400_000)
    p3=round(float(np.mean(sims>=3.0))*100,2)
    p3_5=round(float(np.mean(sims>=3.5))*100,2)
    p4=round(float(np.mean(sims>=4.0))*100,2)
    p5=round(float(np.mean(sims>=5.0))*100,2)
    tmin=max(2.00,round(float(np.percentile(sims,30)),2))
    tmoy=max(2.60,round(float(np.percentile(sims,50)),2))
    sx3=sims[sims>=3.0]
    tmax=max(3.00,round(float(np.percentile(sx3,85)),2)) if len(sx3)>0 else 3.80

    hot_p,cur=markov_predict(last_cote)
    markov_boost=(hot_p-0.5)*20
    bayes_p=bayesian_update(p3+markov_boost)

    strength=round(bayes_p*0.50+p3_5*0.20+p4*0.10+(hn%200)/12+hot_p*15,1)
    strength=max(30.0,min(99.0,strength))

    now_mg=datetime.now(TZ)
    shift=max(20,min(110,48+(hn%90)-45+int(strength*0.35)+int(last_cote*4)-int((48-bayes_p)*0.45)))
    entry=(now_mg+timedelta(seconds=shift)).strftime("%H:%M:%S")

    if strength>=88 and bayes_p>=44:   sig,sc="💎💎💎 ULTRA OMEGA","sig-u"
    elif strength>=76 and bayes_p>=36: sig,sc="🔥🔥 STRONG X3+","sig-s"
    elif strength>=62 and bayes_p>=28: sig,sc="🟢 GOOD X3+","sig-s"
    else:                              sig,sc="⚠️ SKIP","sig-w"

    return {"ts":datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "hash":hash_in[:14]+"...","time":time_in,"last_cote":last_cote,
            "entry":entry,"signal":sig,"sig_class":sc,
            "p3":bayes_p,"p3_5":p3_5,"p4":p4,"p5":p5,
            "strength":strength,"cur_state":cur,"hot_p":round(hot_p*100,1),
            "tmin":tmin,"tmoy":tmoy,"tmax":tmax}

# ============================================================
# LOGIN
# ============================================================
if not st.session_state.auth:
    st.markdown("<div class='ttl'>🌌 COSMOS V19 OMEGA</div>", unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw=st.text_input("🔑 PASSWORD",type="password",placeholder="COSMOS2026")
        if st.button("ACTIVER",use_container_width=True):
            if pw=="COSMOS2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Diso")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# SIDEBAR
with st.sidebar:
    st.markdown("### 📊 STATS")
    s=get_stats()
    tot,w,l=s["total"],s["wins"],s["losses"]
    wr=round(w/tot*100,1) if tot>0 else 0
    st.markdown(f"<div class='mbox'><div class='mv'>{wr}%</div><div style='font-size:.6rem;color:#fff4'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='mbox'><div class='mv'>{w}</div><div style='font-size:.58rem;color:#fff3'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='mbox'><div class='mv'>{l}</div><div style='font-size:.58rem;color:#fff3'>LOSS</div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='mbox'><div class='mv'>{tot}</div><div style='font-size:.58rem;color:#fff3'>TOTAL</div></div>",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET",use_container_width=True):
        reset_db(); st.session_state.result=None; st.session_state.last_id=None
        st.success("✅ Reset!"); st.rerun()

# MAIN
st.markdown("<div class='ttl'>🌌 COSMOS V19 OMEGA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#00ffcc55;letter-spacing:.2em;margin-bottom:1rem;'>MARKOV + BAYESIAN • 400K SIMS • SQLITE</p>", unsafe_allow_html=True)

ci,co=st.columns([1,2],gap="medium")

with ci:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 INPUT")
    h_in=st.text_input("🔐 HASH",placeholder="d8d745d482adc...")
    t_in=st.text_input("⏰ TIME (HH:MM:SS)",placeholder="20:22:24")
    lc=st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("🚀 ANALYSER OMEGA",use_container_width=True):
        if h_in and t_in:
            r=run_engine(h_in.strip(),t_in.strip(),lc)
            pid=save_pred(r)
            st.session_state.result=r; st.session_state.last_id=pid
            st.session_state.ck+=1; st.rerun()
        else: st.error("HASH et TIME obligatoires")

with co:
    r=st.session_state.result
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sig_class']}'>{r['signal']}</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#ffffff55;margin-top:16px;font-size:.75rem;'>▸ ENTRY TIME</p>",unsafe_allow_html=True)
        st.markdown(f"<div class='entry'>{r['entry']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='prob'>{r['p3']}%</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#ffffff55;font-size:.72rem;'>X3+ BAYESIAN PROB</p>",unsafe_allow_html=True)
        st.markdown(f"""
        <div style='display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin:10px 0;'>
        <span style='background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:4px 12px;font-size:.82rem;'>🔄 {r['cur_state']}</span>
        <span style='background:rgba(255,0,255,.1);border:1px solid rgba(255,0,255,.3);border-radius:8px;padding:4px 12px;font-size:.82rem;'>🔥 {r['hot_p']}%</span>
        <span style='background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:4px 12px;font-size:.82rem;'>💪 {r['strength']}</span>
        </div>""",unsafe_allow_html=True)
        st.markdown(f"""
        <div style='display:flex;gap:10px;justify-content:center;margin:8px 0;flex-wrap:wrap;'>
        <div style='text-align:center;'><div style='font-size:1.2rem;font-weight:700;color:#ff00ff;'>{r['p3_5']}%</div><div style='font-size:.65rem;color:#ffffff55;'>X3.5+</div></div>
        <div style='text-align:center;'><div style='font-size:1.2rem;font-weight:700;color:#aa00ff;'>{r['p4']}%</div><div style='font-size:.65rem;color:#ffffff55;'>X4+</div></div>
        <div style='text-align:center;'><div style='font-size:1.2rem;font-weight:700;color:#6600ff;'>{r['p5']}%</div><div style='font-size:.65rem;color:#ffffff55;'>X5+</div></div>
        </div>""",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div style='font-size:.65rem;color:#ffffff55;'>MIN</div><div class='tv' style='color:#00ffcc;'>{r['tmin']}×</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div style='font-size:.65rem;color:#ffffff55;'>MOYEN</div><div class='tv' style='color:#ffd700;'>{r['tmoy']}×</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div style='font-size:.65rem;color:#ffffff55;'>MAX</div><div class='tv' style='color:#ff00ff;'>{r['tmax']}×</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True,key="bw"):
                if st.session_state.last_id: update_result(st.session_state.last_id,"WIN")
                st.success("🎯 Win!"); st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True,key="bl"):
                if st.session_state.last_id: update_result(st.session_state.last_id,"LOSS")
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("""<div class='glass' style='min-height:380px;display:flex;align-items:center;justify-content:center;'>
        <div style='text-align:center;'><div style='font-size:3rem;'>🌌</div>
        <div style='color:#ffffff22;font-family:Orbitron;margin-top:12px;'>EN ATTENTE...</div></div></div>""",unsafe_allow_html=True)

st.markdown("---"); st.markdown("### 📜 HISTORIQUE (SQLite)")
df=get_history(10)
if not df.empty: st.dataframe(df,use_container_width=True,hide_index=True)
else: st.info("Aucun historique")

st.markdown("<div style='text-align:center;margin-top:30px;color:#fff1;font-size:.58rem;'>COSMOS V19 OMEGA • MARKOV + BAYESIAN • 400K SIMS • SQLITE</div>",unsafe_allow_html=True)
