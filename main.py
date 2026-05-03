import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from pathlib import Path

st.set_page_config(page_title="COSMOS SNIPER X4", layout="wide", initial_sidebar_state="collapsed")
try:
    D = Path(__file__).parent / "cx_sniper_data"
except:
    D = Path.cwd() / "cx_sniper_data"
D.mkdir(exist_ok=True, parents=True)
DB = D / "cx_sniper.db"
TZ = pytz.timezone("Indian/Antananarivo")

def db():
    c = sqlite3.connect(str(DB), check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS p(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, sha5 TEXT, hex8 TEXT, lc REAL, lt TEXT,
        ent TEXT, sh INTEGER, sig TEXT,
        bp4 REAL, p4 REAL, p45 REAL, p5 REAL, p6 REAL, p3 REAL,
        str REAL, state TEXT, hp REAL,
        t4min REAL, t4moy REAL, t4max REAL,
        res TEXT DEFAULT 'PENDING')""")
    c.commit(); return c

def sp(d):
    try:
        with db() as c:
            c.execute("""INSERT INTO p(ts,sha5,hex8,lc,lt,ent,sh,sig,
                bp4,p4,p45,p5,p6,p3,str,state,hp,t4min,t4moy,t4max)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (d["ts"],d["sha5"],d["hex8"],d["lc"],d["lt"],
                 d["ent"],d["sh"],d["sig"],
                 d["bp4"],d["p4"],d["p45"],d["p5"],d["p6"],d["p3"],
                 d["str"],d["state"],d["hp"],
                 d["t4min"],d["t4moy"],d["t4max"]))
            c.commit()
            return c.execute("SELECT MAX(id) FROM p").fetchone()[0]
    except: return None

def ur(pid, res):
    try:
        with db() as c: c.execute("UPDATE p SET res=? WHERE id=?",(res,pid)); c.commit()
    except: pass

def gh(n=12):
    try:
        with db() as c:
            return pd.read_sql(
                f"SELECT ts,ent,sig,bp4,p4,p5,str,state,t4min,t4moy,t4max,res FROM p ORDER BY id DESC LIMIT {n}",c)
    except: return pd.DataFrame()

def gs():
    try:
        with db() as c:
            r=c.execute("SELECT COUNT(*),SUM(CASE WHEN res='WIN' THEN 1 ELSE 0 END),SUM(CASE WHEN res='LOSS' THEN 1 ELSE 0 END) FROM p").fetchone()
        return {"t":r[0] or 0,"w":r[1] or 0,"l":r[2] or 0}
    except: return {"t":0,"w":0,"l":0}

def glc(n=50):
    try:
        with db() as c:
            rows=c.execute(f"SELECT lc FROM p ORDER BY id DESC LIMIT {n}").fetchall()
        return [r[0] for r in rows]
    except: return []

def rdb():
    try:
        with db() as c: c.execute("DROP TABLE IF EXISTS p"); c.commit(); db()
    except: pass

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 50% 0%,#0a1a00 0%,#020008 60%,#001a10 100%);color:#e8fffb;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(1.8rem,7vw,3rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#00ffcc,#ff00ff,#ffcc00,#00ffcc);background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:sh 4s ease infinite;margin-bottom:4px}
@keyframes sh{0%,100%{background-position:0%}50%{background-position:100%}}
.sub{text-align:center;color:#00ffcc44;font-size:.8rem;letter-spacing:.3em;margin-bottom:1.5rem}
.card{background:rgba(0,12,8,.93);border:2px solid rgba(0,255,204,.35);border-radius:18px;padding:clamp(14px,4vw,22px);backdrop-filter:blur(14px);margin-bottom:16px}
.etime{font-family:'Orbitron';font-size:clamp(3rem,12vw,5rem);font-weight:900;text-align:center;color:#00ffcc;text-shadow:0 0 40px #00ffcc;margin:18px 0;animation:ep 2s ease-in-out infinite}
@keyframes ep{0%,100%{text-shadow:0 0 28px #00ffcc}50%{text-shadow:0 0 58px #00ffcc,0 0 85px #00ffcc55}}
.pct{font-size:clamp(2.8rem,10vw,4.2rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#ffcc00;margin:8px 0}
.x4big{font-size:clamp(3.5rem,14vw,6rem);font-weight:900;font-family:'Orbitron';text-align:center;background:linear-gradient(135deg,#00ffcc,#ffcc00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:10px 0;filter:drop-shadow(0 0 30px #00ffcc88)}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(.95rem,3.5vw,1.5rem);font-weight:900;color:#00ffcc;text-shadow:0 0 18px #00ffcc88;padding:12px;letter-spacing:.06em}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.3rem);font-weight:700;color:#ffcc00;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1.1rem);color:#ffaa00;padding:10px}
.sig-x{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1rem);color:#555;padding:8px}
.tbox{background:rgba(255,255,255,.06);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.4rem,5vw,2.2rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.6rem;color:rgba(255,255,255,.38);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.ta{font-size:.7rem;color:#00ff88;margin-top:4px;font-weight:700}
.tag{background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#aaffee}
.tag-y{background:rgba(255,204,0,.12);border:1px solid rgba(255,204,0,.35);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#ffee88}
.sb{background:rgba(0,255,204,.07);border:1px solid rgba(0,255,204,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.sv{font-size:1.3rem;font-weight:900;font-family:'Orbitron';color:#00ffcc}
.sl{font-size:.56rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.ib{background:rgba(0,255,204,.05);border-left:3px solid #00ffcc;border-radius:0 10px 10px 0;padding:11px 15px;margin:8px 0;font-size:.88rem;line-height:1.8}
.stButton>button{background:linear-gradient(135deg,#00ffcc,#009977)!important;color:#000!important;font-weight:900!important;border-radius:12px!important;height:52px!important;border:none!important;width:100%!important;font-family:'Rajdhani'!important;font-size:.95rem!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 24px rgba(0,255,204,.6)!important}
.stTextInput label,.stNumberInput label{color:#aaffee!important;font-weight:700!important;font-size:.95rem!important;font-family:'Rajdhani'!important}

/* TETO NO NOVAINA MBA HO FOTSY SY MAINTY STYLÉ NY INPUTS REHETRA */
.stTextInput input{background:#ffffff!important;border:2px solid #00ffcc!important;color:#000000!important;font-weight:900!important;border-radius:11px!important;font-size:1.05rem!important;padding:11px 14px!important;font-family:'Orbitron',sans-serif!important;}
.stTextInput input::placeholder{color:#000000!important;font-weight:800!important;font-style:normal!important;opacity:0.6!important;}
.stTextInput input:focus{border-color:#ffcc00!important;box-shadow:0 0 16px rgba(0,255,204,.7)!important;background:#ffffff!important;}

.stNumberInput input{background:#ffffff!important;border:2px solid #00ffcc!important;color:#000000!important;font-weight:900!important;border-radius:11px!important;font-size:1.05rem!important;padding:11px 14px!important;font-family:'Orbitron',sans-serif!important;}
.stNumberInput input:focus{border-color:#ffcc00!important;box-shadow:0 0 16px rgba(0,255,204,.7)!important;background:#ffffff!important;}

@media(max-width:768px){.card{padding:12px!important}}
</style>
""", unsafe_allow_html=True)

for k,v in [("auth",False),("R",None),("pid",None),("ck",0)]:
    if k not in st.session_state: st.session_state[k]=v

ST=["COLD","NORMAL","WARM","HOT"]
def s2st(c):
    if c<1.5: return "COLD"
    if c<2.5: return "NORMAL"
    if c<3.5: return "WARM"
    return "HOT"

def markov(lc):
    cs=glc()
    tr={s:{s2:1 for s2 in ST} for s in ST}
    for i in range(len(cs)-1):
        tr[s2st(cs[i])][s2st(cs[i+1])]+=1
    mx={s:{s2:tr[s][s2]/sum(tr[s].values()) for s2 in ST} for s in ST}
    cur=s2st(lc); hp=mx[cur].get("HOT",0)+mx[cur].get("WARM",0)
    return round(hp*100,1),cur

def bayes(base):
    try:
        with db() as c:
            rows=c.execute("SELECT res FROM p WHERE res IN ('WIN','LOSS') ORDER BY id DESC LIMIT 20").fetchall()
        if len(rows)<3: return base
        w=sum(1 for r in rows if r[0]=="WIN"); n=len(rows)
        lik=(w+1)/(n+2); pr=base/100
        po=(lik*pr)/((lik*pr)+((1-lik)*(1-pr))+1e-9)
        return round(min(95,max(25,po*100)),1)
    except: return base

def calc_entry(hn, bp4, str_, lc, last_time_str):
    try:
        parts=last_time_str.strip().split(":")
        h2,m2,s2=(int(parts[0]),int(parts[1]),0) if len(parts)==2 else (int(parts[0]),int(parts[1]),int(parts[2]))
        now=datetime.now(TZ)
        bt=now.replace(hour=h2,minute=m2,second=s2,microsecond=0)
        if bt<now: bt+=timedelta(days=1)
    except:
        bt=datetime.now(TZ)
    hv=(hn%60)-30
    pb=int((bp4-30)*0.45)
    sb=int((str_-50)*0.25)
    cb=int(lc*3.0)
    sh=max(20,min(100,50+hv+pb+sb+cb))
    return (bt+timedelta(seconds=sh)).strftime("%H:%M:%S"),sh

def engine(sha5, hex8, lc, last_time):
    """
    COSMOS SNIPER X4 ENGINE
    SHA5 + HEX8 → seed ultra précis
    Sigma élargi pour capturer tail X4+
    500k simulations focalisées X4+
    """
    combined=f"{sha5}:{hex8}:{lc}:{last_time}"
    fh=hashlib.sha512(combined.encode()).hexdigest()
    hn=int(fh[:16],16)
    hex_b=0
    try:
        clean=hex8.strip()[:8]
        hex_b=int(clean,16) if all(c in '0123456789abcdefABCDEF' for c in clean) else sum(ord(c) for c in clean)
    except: pass
    sv=int((hn&0xFFFFFFFF)+(lc*1000)+(hex_b%10000))
    np.random.seed(sv%(2**32))

    if lc<1.5:   bs,sg=2.20,0.40
    elif lc<2.5: bs,sg=2.12,0.36
    elif lc<3.5: bs,sg=2.05,0.32
    else:        bs,sg=1.98,0.29
    bs+=(hn%200)/1100
    sg=max(0.22,sg-lc*0.014)

    sm=np.random.lognormal(np.log(bs),sg,500_000)
    p4   = round(float(np.mean(sm>=4.0))*100,2)
    p45  = round(float(np.mean(sm>=4.5))*100,2)
    p5   = round(float(np.mean(sm>=5.0))*100,2)
    p6   = round(float(np.mean(sm>=6.0))*100,2)
    p3   = round(float(np.mean(sm>=3.0))*100,2)
    sx4  = sm[sm>=4.0]

    if len(sx4)>0:
        t4min=round(float(np.percentile(sx4,15)),2)
        t4moy=round(float(np.percentile(sx4,50)),2)
        t4max=round(float(np.percentile(sx4,85)),2)
        acc4min=round(p4*0.85,1)
        acc4moy=round(p4*0.50,1)
        acc4max=round(p4*0.15,1)
    else:
        t4min,t4moy,t4max=4.0,5.0,7.0
        acc4min=acc4moy=acc4max=5.0

    hp,cur=markov(lc)
    bp4=bayes(p4+(hp/100-0.5)*15)
    str_=round(bp4*0.45+p45*0.25+p5*0.15+p3*0.05+(hn%200)/14+(hp/100)*12,1)
    str_=max(25.0,min(99.0,str_))

    ent,sh=calc_entry(hn,bp4,str_,lc,last_time)

    if   str_>=90 and bp4>=28: sig,sc="🎯🎯🎯 SNIPER OMEGA X4+ — FIRE!","sig-u"
    elif str_>=78 and bp4>=22: sig,sc="🎯🎯 STRONG X4+ — FIRE!","sig-u"
    elif str_>=65 and bp4>=16: sig,sc="🔥 X4+ POSSIBLE — GO","sig-s"
    elif str_>=52 and bp4>=11: sig,sc="🟡 X4 WEAK — MICRO BET","sig-w"
    else:                      sig,sc="⚠️ SKIP — NO X4 SIGNAL","sig-x"

    return {"ts":datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "sha5":sha5,"hex8":hex8[:8],"lc":lc,"lt":last_time,
            "ent":ent,"sh":sh,"sig":sig,"sc":sc,
            "bp4":bp4,"p4":p4,"p45":p45,"p5":p5,"p6":p6,"p3":p3,
            "str":str_,"state":cur,"hp":hp,
            "t4min":t4min,"t4moy":t4moy,"t4max":t4max,
            "acc4min":acc4min,"acc4moy":acc4moy,"acc4max":acc4max}

if not st.session_state.auth:
    st.markdown("<div class='ttl'>🌌 COSMOS SNIPER X4</div>",unsafe_allow_html=True)
    st.markdown("<div class='sub'>OMEGA • BAYESIAN • CIBLÉ X4+ ULTRA</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez: COSMOS2026")
        if st.button("🔓 ACTIVER OMEGA SNIPER",use_container_width=True):
            if pw=="COSMOS2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("""
    <div class='card' style='max-width:780px;margin:20px auto;'>
    <h3 style='color:#00ffcc;font-family:Orbitron;text-align:center;font-size:1.1rem;'>📖 FANAZAVANA MALAGASY</h3>
    <div class='ib'><b style='color:#00ffcc;'>🎯 INONA NY COSMOS SNIPER X4?</b><br>
    Ciblé <b>X4+ EXCLUSIVEMENT</b> (cote ≥ 4.00×)<br>
    SHA5 + HEX8 = seed ultra précis<br>
    500k sims sigma élargi = meilleure précision tail X4+</div>
    <div class='ib'><b style='color:#00ffcc;'>📥 INPUTS:</b><br>
    • <b>SHA512 5 decimals:</b> Ex: <code>ac50e</code><br>
    • <b>HEX 8 chars:</b> Ex: <code>7db8e014</code><br>
    • <b>LAST COTE:</b> Résultat taloha → Ex: <code>1.88</code><br>
    • <b>LAST TIME:</b> Ora round taloha → Ex: <code>20:22:24</code></div>
    <div class='ib'><b style='color:#00ffcc;'>🎯 SIGNAL:</b><br>
    🎯🎯🎯 OMEGA SNIPER → Str≥90+X4%≥28 | 🎯🎯 STRONG → Str≥78+X4%≥22<br>
    🔥 GO → Str≥65+X4%≥16 | 🟡 MICRO → Str≥52+X4%≥11 | ⚠️ SKIP</div>
    </div>
    """,unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("### 🌌 SNIPER X4")
    s=gs(); t,w,l=s["t"],s["w"],s["l"]
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='sb'><div class='sv'>{w}</div><div class='sl'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='sb'><div class='sv'>{l}</div><div class='sl'>LOSS</div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='sb'><div class='sv'>{t}</div><div class='sl'>TOTAL</div></div>",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET",use_container_width=True):
        rdb(); st.session_state.R=None; st.session_state.pid=None
        st.success("✅"); st.rerun()

st.markdown("<div class='ttl'>🌌 COSMOS SNIPER X4</div>",unsafe_allow_html=True)
st.markdown("<div class='sub'>500K SIMS • SHA5+HEX8 • BAYESIAN • X4+ ULTRA</div>",unsafe_allow_html=True)
ci,co=st.columns([1,2],gap="medium")

with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    sha5  = st.text_input("🔐 SHA512 (5 premiers decimals)",placeholder="Ex: ac50e  —  5 chars SHA512")
    hex8  = st.text_input("🔢 HEX (8 premiers chars)",placeholder="Ex: 7db8e014  —  hex Provably Fair")
    lc    = st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    lt_in = st.text_input("⏰ LAST TIME (HH:MM:SS)",placeholder="Ex: 20:22:24  —  ora round taloha")
    if   lc<1.5: sl,sc2="🔵 COLD","#4488ff"
    elif lc<2.5: sl,sc2="⚪ NORMAL","#aaa"
    elif lc<3.5: sl,sc2="🟡 WARM","#ffcc00"
    else:        sl,sc2="🔴 HOT","#ff3366"
    st.markdown(f"<div style='text-align:center;margin:6px 0;'><span style='background:rgba(255,255,255,.07);border-radius:8px;padding:4px 14px;color:{sc2};font-size:.82rem;'>{sl}</span></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🎯 SNIPER OMEGA",use_container_width=True):
        if sha5 and hex8 and lt_in:
            with st.spinner("🎯 500k sims X4+ targeting..."):
                r=engine(sha5.strip(),hex8.strip(),lc,lt_in.strip())
            pid=sp(r)
            st.session_state.R=r; st.session_state.pid=pid
            st.session_state.ck+=1; st.rerun()
        else: st.error("❌ SHA5, HEX et Last Time obligatoires!")

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,.4);font-size:.72rem;margin-top:14px;'>▸ ENTRY TIME (Last +{r['sh']}s)</p>",unsafe_allow_html=True)
        st.markdown(f"<div class='etime'>{r['ent']}</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:rgba(255,255,255,.35);font-size:.7rem;'>CIBLE PRINCIPALE</p>",unsafe_allow_html=True)
        st.markdown("<div class='x4big'>X4+</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp4']}%</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:rgba(255,255,255,.3);font-size:.68rem;'>PROB X4+ BAYESIAN</p>",unsafe_allow_html=True)
        st.markdown(f"""<div style='text-align:center;margin:10px 0;'>
        <span class='tag'>🔄 {r['state']}</span><span class='tag'>🔥 {r['hp']}%</span>
        <span class='tag'>💪 {r['str']}</span>
        <span class='tag-y'>X3+ {r['p3']}%</span>
        <span class='tag-y'>X4.5+ {r['p45']}%</span>
        <span class='tag-y'>X5+ {r['p5']}%</span>
        <span class='tag-y'>X6+ {r['p6']}%</span>
        </div>""",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>X4 MIN</div><div class='tv' style='color:#00ffcc;'>{r['t4min']}×</div><div class='ta'>{r['acc4min']}%</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>X4 MOYEN</div><div class='tv' style='color:#ffcc00;'>{r['t4moy']}×</div><div class='ta'>{r['acc4moy']}%</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>X4 MAX</div><div class='tv' style='color:#ff00ff;'>{r['t4max']}×</div><div class='ta'>{r['acc4max']}%</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN X4+",use_container_width=True,key="bw"):
                if st.session_state.pid: ur(st.session_state.pid,"WIN")
                st.success("🎯 SNIPER HIT!"); st.rerun()
        with cl2:
            if st.button("❌ MISS",use_container_width=True,key="bl"):
                if st.session_state.pid: ur(st.session_state.pid,"LOSS")
                st.rerun()
        st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,.18);font-size:.6rem;margin-top:8px;'>SHA:{r['sha5']} HEX:{r['hex8']} LC:{r['lc']}× • SQLite</p>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='min-height:380px;display:flex;align-items:center;justify-content:center;'><div style='text-align:center;'><div class='x4big' style='font-size:3rem;opacity:.2;'>X4</div><div style='color:rgba(255,255,255,.15);font-family:Orbitron;margin-top:10px;font-size:.85rem;'>OMEGA SNIPER EN ATTENTE...</div></div></div>",unsafe_allow_html=True)

st.markdown("---")
df=gh(10)
if not df.empty: st.dataframe(df,use_container_width=True,hide_index=True)
else: st.info("Aucun historique")
st.markdown("<div style='text-align:center;margin-top:18px;color:rgba(255,255,255,.07);font-size:.54rem;'>COSMOS SNIPER X4 • 500K SIMS • SHA5+HEX8 • BAYESIAN • SQLITE</div>",unsafe_allow_html=True)
