import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from pathlib import Path

st.set_page_config(page_title="COSMOS X V20", layout="wide", initial_sidebar_state="collapsed")

try:    D = Path(__file__).parent / "cx20_data"
except: D = Path.cwd() / "cx20_data"
D.mkdir(exist_ok=True, parents=True)
DB = D / "cx20.db"

TZ = pytz.timezone("Indian/Antananarivo")

# ─── DATABASE ───
def db():
    c = sqlite3.connect(str(DB), check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS p(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, hash_in TEXT, time_in TEXT, lc REAL,
        ent TEXT, sig TEXT, bp REAL, p35 REAL, p4 REAL, p5 REAL,
        str REAL, state TEXT, hp REAL,
        tmin REAL, tmoy REAL, tmax REAL,
        res TEXT DEFAULT 'PENDING')""")
    c.commit(); return c

def save_p(d):
    try:
        with db() as c:
            c.execute("INSERT INTO p(ts,hash_in,time_in,lc,ent,sig,bp,p35,p4,p5,str,state,hp,tmin,tmoy,tmax) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (d["ts"],d["hash"],d["time"],d["lc"],d["ent"],d["sig"],
                 d["bp"],d["p35"],d["p4"],d["p5"],d["str"],d["state"],d["hp"],
                 d["tmin"],d["tmoy"],d["tmax"]))
            c.commit()
            return c.execute("SELECT MAX(id) FROM p").fetchone()[0]
    except: return None

def upd(pid, res):
    try:
        with db() as c: c.execute("UPDATE p SET res=? WHERE id=?",(res,pid)); c.commit()
    except: pass

def get_hist(n=15):
    try:
        with db() as c:
            return pd.read_sql(f"SELECT ts,ent,sig,bp,str,state,tmin,tmoy,tmax,res FROM p ORDER BY id DESC LIMIT {n}",c)
    except: return pd.DataFrame()

def get_stats():
    try:
        with db() as c:
            r=c.execute("SELECT COUNT(*),SUM(CASE WHEN res='WIN' THEN 1 ELSE 0 END),SUM(CASE WHEN res='LOSS' THEN 1 ELSE 0 END) FROM p").fetchone()
        return {"t":r[0] or 0,"w":r[1] or 0,"l":r[2] or 0}
    except: return {"t":0,"w":0,"l":0}

def get_lcs(n=50):
    try:
        with db() as c:
            rows=c.execute(f"SELECT lc FROM p ORDER BY id DESC LIMIT {n}").fetchall()
        return [r[0] for r in rows]
    except: return []

def reset_db():
    try:
        with db() as c: c.execute("DROP TABLE IF EXISTS p"); c.commit()
        db()
    except: pass

# ─── CSS AMBOARINA NY SORATRA ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 50% 0%,#00110a88 0%,#020008 65%);color:#e8fffb;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(2rem,8vw,3.2rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff,#00ffcc);background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:sh 4s ease infinite;margin-bottom:4px}
@keyframes sh{0%,100%{background-position:0%}50%{background-position:100%}}
.sub{text-align:center;color:#00ffcc55;font-size:.8rem;letter-spacing:.3em;margin-bottom:1.5rem}
.card{background:rgba(0,10,16,.93);border:2px solid rgba(0,255,204,.35);border-radius:18px;padding:clamp(14px,4vw,24px);backdrop-filter:blur(14px);margin-bottom:16px;box-shadow:0 0 25px rgba(0,255,204,.07)}
.etime{font-family:'Orbitron';font-size:clamp(3.5rem,13vw,5.5rem);font-weight:900;text-align:center;color:#00ffcc;text-shadow:0 0 40px #00ffcc;margin:20px 0;animation:ep 2s ease-in-out infinite}
@keyframes ep{0%,100%{text-shadow:0 0 30px #00ffcc}50%{text-shadow:0 0 65px #00ffcc,0 0 100px #00ffcc55}}
.pct{font-size:clamp(3rem,11vw,4.5rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#ff00ff;margin:8px 0}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(1rem,3.5vw,1.6rem);font-weight:900;color:#00ffcc;text-shadow:0 0 20px #00ffcc88;padding:12px}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.95rem,3vw,1.4rem);font-weight:700;color:#ff00ff;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.2rem);color:#ffaa00;padding:10px}
.sig-x{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.1rem);color:#666;padding:8px}
.tbox{background:rgba(255,255,255,.05);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.5rem,5.5vw,2.4rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.62rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.ta{font-size:.72rem;color:#00ff88;margin-top:4px;font-weight:700}
.tag{background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:4px 12px;font-size:.82rem;display:inline-block;margin:3px;color:#aaffee}
.tag-p{background:rgba(255,0,255,.1);border:1px solid rgba(255,0,255,.3);border-radius:8px;padding:4px 12px;font-size:.82rem;display:inline-block;margin:3px;color:#ffaaff}
.sb{background:rgba(0,255,204,.07);border:1px solid rgba(0,255,204,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.sv{font-size:1.4rem;font-weight:900;font-family:'Orbitron';color:#00ffcc}
.sl{font-size:.58rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.ib{background:rgba(0,255,204,.05);border-left:3px solid #00ffcc;border-radius:0 10px 10px 0;padding:12px 16px;margin:8px 0;font-size:.9rem;line-height:1.8}
.stButton>button{background:linear-gradient(135deg,#00ffcc,#0088bb)!important;color:#000!important;font-weight:900!important;border-radius:12px!important;height:52px!important;border:none!important;width:100%!important;font-family:'Rajdhani'!important;font-size:.95rem!important;letter-spacing:.04em!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 24px rgba(0,255,204,.5)!important}

/* --- KAJY HO AN'NY INPUT (MAINTY SY STYLÉ) --- */
.stTextInput label, .stNumberInput label {
    color:#aaffee!important; 
    font-weight:700!important; 
    font-size:.88rem!important;
}
.stTextInput input, .stNumberInput input {
    background: #ffffff !important; /* Fotsy tanteraka ny background */
    color: #000000 !important; /* Mainty ny soratra */
    border: 2px solid #00ffcc !important;
    border-radius: 11px !important;
    font-size: 1rem !important;
    font-weight: 800 !important; /* Matevina kely */
    font-family: 'Rajdhani', sans-serif !important;
    opacity: 1 !important;
}
.stTextInput input::placeholder {
    color: #333333 !important; /* Placeholder somary maty kely */
    opacity: 0.7 !important;
}
.stTextInput input:focus {
    box-shadow: 0 0 15px rgba(0,255,204,0.5) !important;
    border-color: #ff00ff !important;
}

@media(max-width:768px){.card{padding:12px!important}}
</style>
""", unsafe_allow_html=True)

# ─── STATE ───
for k,v in [("auth",False),("R",None),("pid",None),("ck",0)]:
    if k not in st.session_state: st.session_state[k]=v

# ─── MARKOV ───
ST=["COLD","NORMAL","WARM","HOT"]
def s2st(c):
    if c<1.5: return "COLD"
    if c<2.5: return "NORMAL"
    if c<3.5: return "WARM"
    return "HOT"

def markov(lc):
    cs=get_lcs()
    tr={s:{s2:1 for s2 in ST} for s in ST}
    for i in range(len(cs)-1):
        tr[s2st(cs[i])][s2st(cs[i+1])]+=1
    mx={s:{s2:tr[s][s2]/sum(tr[s].values()) for s2 in ST} for s in ST}
    cur=s2st(lc)
    hp=mx[cur].get("HOT",0)+mx[cur].get("WARM",0)
    return round(hp*100,1),cur

# ─── BAYESIAN ───
def bayes(base):
    try:
        with db() as c:
            rows=c.execute("SELECT res FROM p WHERE res IN ('WIN','LOSS') ORDER BY id DESC LIMIT 20").fetchall()
        if len(rows)<3: return base
        w=sum(1 for r in rows if r[0]=="WIN"); n=len(rows)
        lik=(w+1)/(n+2); pr=base/100
        po=(lik*pr)/((lik*pr)+((1-lik)*(1-pr))+1e-9)
        return round(min(95,max(30,po*100)),1)
    except: return base

# ─── ENGINE ───
def engine(hash_in, tin, lc):
    fh=hashlib.sha512(hash_in.encode()).hexdigest()
    hn=int(fh[:16],16)
    sv=int((hn&0xFFFFFFFF)+(lc*1000))
    np.random.seed(sv%(2**32))

    if lc<1.5:   bs,sg=2.12,0.24
    elif lc<2.5: bs,sg=2.06,0.21
    elif lc<3.5: bs,sg=2.00,0.19
    else:        bs,sg=1.96,0.18
    bs+=(hn%180)/1200; sg=max(0.14,sg-lc*0.0022)

    sm=np.random.lognormal(np.log(bs),sg,400_000)
    p3=round(float(np.mean(sm>=3.0))*100,2)
    p35=round(float(np.mean(sm>=3.5))*100,2)
    p4=round(float(np.mean(sm>=4.0))*100,2)
    p5=round(float(np.mean(sm>=5.0))*100,2)
    sx=sm[sm>=3.0]
    tmin=max(2.0,round(float(np.percentile(sm,30)),2))
    tmoy=max(2.5,round(float(np.percentile(sm,50)),2))
    tmax=max(3.0,round(float(np.percentile(sx,85)),2)) if len(sx)>0 else 3.8

    hp,cur=markov(lc)
    bp=bayes(p3+(hp/100-0.5)*20)
    str_=round(bp*0.50+p35*0.20+p4*0.10+(hn%200)/12+(hp/100)*15,1)
    str_=max(30.0,min(99.0,str_))

    now=datetime.now(TZ)
    hs=(hn%60)-30         
    sb=int(str_*0.28)     
    cf=int(lc*3)          
    pp=int((48-bp)*0.38)  
    shift=max(15,min(90,38+hs+sb+cf-pp))
    ent=(now+timedelta(seconds=shift)).strftime("%H:%M:%S")

    if str_>=88 and bp>=44:   sig,sc="💎💎💎 ULTRA OMEGA X3+","sig-u"
    elif str_>=76 and bp>=36: sig,sc="🔥🔥 STRONG X3+ LOCK","sig-s"
    elif str_>=62 and bp>=28: sig,sc="🟢 GOOD X3+ SCALP","sig-w"
    else:                     sig,sc="⚠️ SKIP CE ROUND","sig-x"

    return {"ts":datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "hash":hash_in[:14]+"...","time":tin,"lc":lc,
            "ent":ent,"sig":sig,"sc":sc,
            "bp":bp,"p35":p35,"p4":p4,"p5":p5,
            "str":str_,"state":cur,"hp":hp,
            "tmin":tmin,"tmoy":tmoy,"tmax":tmax}

# ─── LOGIN ───
if not st.session_state.auth:
    st.markdown("<div class='ttl'>🌌 COSMOS X V20</div>",unsafe_allow_html=True)
    st.markdown("<div class='sub'>OMEGA • MARKOV + BAYESIAN • ULTRA X3+</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez: COSMOS2026")
        if st.button("🔓 ACTIVER OMEGA",use_container_width=True):
            if pw=="COSMOS2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

# ─── SIDEBAR ───
with st.sidebar:
    st.markdown("### 🌌 COSMOS X V20")
    s=get_stats()
    t,w,l=s["t"],s["w"],s["l"]
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='sb'><div class='sv'>{w}</div><div class='sl'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='sb'><div class='sv'>{l}</div><div class='sl'>LOSS</div></div>",unsafe_allow_html=True)
    if st.button("🗑️ RESET",use_container_width=True):
        reset_db(); st.session_state.R=None; st.session_state.pid=None
        st.success("✅ Reset!"); st.rerun()

# ─── MAIN ───
st.markdown("<div class='ttl'>🌌 COSMOS X V20</div>",unsafe_allow_html=True)
st.markdown("<div class='sub'>OMEGA • MARKOV + BAYESIAN • 400K SIMS</div>",unsafe_allow_html=True)

ci,co=st.columns([1,2],gap="medium")

with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.markdown("<p style='font-family:Orbitron;font-size:.85rem;color:#00ffcc;margin-bottom:12px;'>📥 PARAMÈTRES</p>",unsafe_allow_html=True)
    h_in=st.text_input("🔐 SERVER HASH",placeholder="Paste hash here...")
    t_in=st.text_input("⏰ TIME ROUND",placeholder="Ex: 20:22:24")
    lc=st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🚀 ANALYSER OMEGA",use_container_width=True):
        if h_in and t_in:
            with st.spinner("⚡ 400k sims..."):
                r=engine(h_in.strip(),t_in.strip(),lc)
            pid=save_p(r)
            st.session_state.R=r; st.session_state.pid=pid
            st.rerun()

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='etime'>{r['ent']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp']}%</div>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>MIN SAFE</div><div class='tv' style='color:#00ffcc;'>{r['tmin']}×</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>MOYEN</div><div class='tv' style='color:#ffd700;'>{r['tmoy']}×</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>MAX X3+</div><div class='tv' style='color:#ff00ff;'>{r['tmax']}×</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True,key="bw"):
                if st.session_state.pid: upd(st.session_state.pid,"WIN")
                st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True,key="bl"):
                if st.session_state.pid: upd(st.session_state.pid,"LOSS")
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='min-height:380px;display:flex;align-items:center;justify-content:center;'><div style='text-align:center;'><div style='font-size:3rem;'>🌌</div><div style='color:rgba(255,255,255,.18);font-family:Orbitron;margin-top:12px;font-size:.9rem;'>AMPIDITRA HASH + TIME<br>TSINDRIO ANALYSER</div></div></div>",unsafe_allow_html=True)

st.markdown("---"); st.markdown("### 📜 HISTORIQUE (SQLite)")
df=get_hist(10)
if not df.empty: st.dataframe(df,use_container_width=True,hide_index=True)

st.markdown("<div style='text-align:center;margin-top:24px;color:rgba(255,255,255,.1);font-size:.56rem;'>COSMOS X V20 OMEGA • SQLITE</div>",unsafe_allow_html=True)
