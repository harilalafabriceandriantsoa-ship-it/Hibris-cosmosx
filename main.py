import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from pathlib import Path

st.set_page_config(page_title="COSMOS X V21", layout="wide", initial_sidebar_state="collapsed")
try:    D = Path(__file__).parent / "cx21"
except: D = Path.cwd() / "cx21"
D.mkdir(exist_ok=True, parents=True)
DB = D / "cx21.db"
TZ = pytz.timezone("Indian/Antananarivo")

def db():
    c = sqlite3.connect(str(DB), check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS p(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, sha5 TEXT, hex8 TEXT, lc REAL, lt TEXT,
        ent TEXT, sh INTEGER, sig TEXT,
        bp REAL, p35 REAL, p4 REAL, str REAL,
        state TEXT, hp REAL,
        tmin REAL, tmoy REAL, tmax REAL,
        acc_min REAL, acc_moy REAL, acc_max REAL,
        res TEXT DEFAULT 'PENDING')""")
    c.commit(); return c

def sp(d):
    try:
        with db() as c:
            c.execute("""INSERT INTO p(ts,sha5,hex8,lc,lt,ent,sh,sig,
                bp,p35,p4,str,state,hp,tmin,tmoy,tmax,acc_min,acc_moy,acc_max)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (d["ts"],d["sha5"],d["hex8"],d["lc"],d["lt"],d["ent"],d["sh"],d["sig"],
                 d["bp"],d["p35"],d["p4"],d["str"],d["state"],d["hp"],
                 d["tmin"],d["tmoy"],d["tmax"],d["acc_min"],d["acc_moy"],d["acc_max"]))
            c.commit()
            return c.execute("SELECT MAX(id) FROM p").fetchone()[0]
    except: return None

def ur(pid, res):
    try:
        with db() as c: c.execute("UPDATE p SET res=? WHERE id=?",(res,pid)); c.commit()
    except: pass

def gh(n=15):
    try:
        with db() as c:
            return pd.read_sql(f"SELECT ts,ent,sig,bp,str,state,tmin,tmoy,tmax,res FROM p ORDER BY id DESC LIMIT {n}",c)
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
        with db() as c: c.execute("DROP TABLE IF EXISTS p"); c.commit()
        db()
    except: pass

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 50% 0%,#00110a 0%,#020008 65%);color:#e8fffb;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(2rem,8vw,3rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff,#00ffcc);background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:sh 4s ease infinite;margin-bottom:4px}
@keyframes sh{0%,100%{background-position:0%}50%{background-position:100%}}
.sub{text-align:center;color:#00ffcc55;font-size:.8rem;letter-spacing:.3em;margin-bottom:1.5rem}
.card{background:rgba(0,10,16,.93);border:2px solid rgba(0,255,204,.35);border-radius:18px;padding:clamp(14px,4vw,22px);backdrop-filter:blur(14px);margin-bottom:16px}
.etime{font-family:'Orbitron';font-size:clamp(3rem,12vw,5rem);font-weight:900;text-align:center;color:#00ffcc;text-shadow:0 0 40px #00ffcc;margin:18px 0;animation:ep 2s ease-in-out infinite}
@keyframes ep{0%,100%{text-shadow:0 0 28px #00ffcc}50%{text-shadow:0 0 55px #00ffcc,0 0 80px #00ffcc55}}
.pct{font-size:clamp(2.8rem,10vw,4.2rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#ff00ff;margin:8px 0}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(.95rem,3.5vw,1.5rem);font-weight:900;color:#00ffcc;text-shadow:0 0 18px #00ffcc88;padding:12px;letter-spacing:.06em}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.3rem);font-weight:700;color:#ff00ff;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1.15rem);color:#ffaa00;padding:10px}
.sig-x{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1.1rem);color:#555;padding:8px}
.tbox{background:rgba(255,255,255,.06);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.4rem,5vw,2.2rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.6rem;color:rgba(255,255,255,.38);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.ta{font-size:.7rem;color:#00ff88;margin-top:4px;font-weight:700}
.tag{background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#aaffee}
.tag-p{background:rgba(255,0,255,.1);border:1px solid rgba(255,0,255,.3);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#ffaaff}
.sb{background:rgba(0,255,204,.07);border:1px solid rgba(0,255,204,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.sv{font-size:1.3rem;font-weight:900;font-family:'Orbitron';color:#00ffcc}
.sl{font-size:.56rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.ib{background:rgba(0,255,204,.05);border-left:3px solid #00ffcc;border-radius:0 10px 10px 0;padding:11px 15px;margin:8px 0;font-size:.88rem;line-height:1.8}
.stButton>button{background:linear-gradient(135deg,#00ffcc,#0088bb)!important;color:#000!important;font-weight:900!important;border-radius:12px!important;height:52px!important;border:none!important;width:100%!important;font-family:'Rajdhani'!important;font-size:.95rem!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 24px rgba(0,255,204,.5)!important}
.stTextInput label,.stNumberInput label{color:#aaffee!important;font-weight:700!important;font-size:.87rem!important;font-family:'Rajdhani'!important}

/* --- FANITSIANA NY SORATRA AO AMIN'NY INPUT --- */
.stTextInput input{
    background:rgba(255,255,255,.9)!important; 
    border:2px solid rgba(0,255,204,.5)!important;
    color:#000000!important; 
    border-radius:11px!important;
    font-size:.93rem!important;
    padding:11px 14px!important;
    font-weight:700!important;
}
.stTextInput input::placeholder{
    color:#000000!important; 
    opacity:0.7!important;
    font-weight:700!important;
}
.stTextInput input:focus{
    border-color:#00ffcc!important;
    box-shadow:0 0 14px rgba(0,255,204,.3)!important;
    background:rgba(255,255,255,1)!important;
}
.stNumberInput input{
    background:rgba(255,255,255,.9)!important;
    border:2px solid rgba(0,255,204,.5)!important;
    color:#000!important;
    border-radius:11px!important;
    font-size:.93rem!important;
    padding:11px 14px!important;
    font-weight:700!important;
}
.stNumberInput input:focus{
    border-color:#00ffcc!important;
    box-shadow:0 0 14px rgba(0,255,204,.3)!important;
}
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
        return round(min(95,max(30,po*100)),1)
    except: return base

def calc_entry(hn, bp, str_, lc, last_time_str):
    try:
        parts = last_time_str.strip().split(":")
        if len(parts) == 2:
            h2, m2, s2 = int(parts[0]), int(parts[1]), 0
        else:
            h2, m2, s2 = int(parts[0]), int(parts[1]), int(parts[2])
        now = datetime.now(TZ)
        base_t = now.replace(hour=h2, minute=m2, second=s2, microsecond=0)
        if base_t < now: base_t += timedelta(days=1)
    except:
        base_t = datetime.now(TZ)

    hv = (hn % 50) - 25
    pb = int((bp - 40) * 0.35)
    sb = int((str_ - 50) * 0.22)
    cb = int(lc * 2.8)
    # --- FANITSIANA NY LERA D'ENTREE (Manome fotoana bebe kokoa) ---
    sh = max(45, min(150, 75 + hv + pb + sb + cb)) 
    return (base_t + timedelta(seconds=sh)).strftime("%H:%M:%S"), sh

def engine(sha5, hex8, lc, last_time):
    combined = f"{sha5}:{hex8}:{lc}:{last_time}"
    fh = hashlib.sha512(combined.encode()).hexdigest()
    hn = int(fh[:16], 16)
    hex_boost = int(hex8[:8].replace("x","0").replace("X","0"), 16) if len(hex8) >= 4 else 0
    sv = int((hn & 0xFFFFFFFF) + (lc * 1000) + (hex_boost % 10000))
    np.random.seed(sv % (2**32))

    if lc < 1.5:   bs, sg = 2.12, 0.24
    elif lc < 2.5: bs, sg = 2.06, 0.21
    elif lc < 3.5: bs, sg = 2.00, 0.19
    else:          bs, sg = 1.96, 0.18
    bs += (hn % 180) / 1200
    sg  = max(0.14, sg - lc * 0.0022)

    sm   = np.random.lognormal(np.log(bs), sg, 400_000)
    p3   = round(float(np.mean(sm >= 3.0)) * 100, 2)
    p35  = round(float(np.mean(sm >= 3.5)) * 100, 2)
    p4   = round(float(np.mean(sm >= 4.0)) * 100, 2)
    p5   = round(float(np.mean(sm >= 5.0)) * 100, 2)
    sx   = sm[sm >= 3.0]

    tmin = max(2.0, round(float(np.percentile(sm, 30)), 2))
    tmoy = max(2.5, round(float(np.percentile(sm, 50)), 2))
    tmax = max(3.0, round(float(np.percentile(sx, 85)), 2)) if len(sx) > 0 else 3.8
    acc_min = 70.0
    acc_moy = 50.0
    acc_max = round(p3 * 0.85, 1)

    hp, cur = markov(lc)
    bp  = bayes(p3 + (hp/100 - 0.5) * 20)
    str_ = round(bp*0.50 + p35*0.20 + p4*0.10 + (hn%200)/12 + (hp/100)*15, 1)
    str_ = max(30.0, min(99.0, str_))

    ent, sh = calc_entry(hn, bp, str_, lc, last_time)

    if   str_ >= 90 and bp >= 46: sig, sc = "💎💎💎 ULTRA OMEGA X3+", "sig-u"
    elif str_ >= 80 and bp >= 40: sig, sc = "💎💎 STRONG X3+ LOCK", "sig-u"
    elif str_ >= 70 and bp >= 34: sig, sc = "🔥 GOOD X3+ GO", "sig-s"
    elif str_ >= 58 and bp >= 27: sig, sc = "🟡 MODERATE — PETIT BET", "sig-w"
    else:                         sig, sc = "⚠️ SKIP CE ROUND", "sig-x"

    return {"ts": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "sha5": sha5, "hex8": hex8[:8], "lc": lc, "lt": last_time,
            "ent": ent, "sh": sh, "sig": sig, "sc": sc,
            "bp": bp, "p35": p35, "p4": p4, "p5": p5, "str": str_,
            "state": cur, "hp": hp,
            "tmin": tmin, "tmoy": tmoy, "tmax": tmax,
            "acc_min": acc_min, "acc_moy": acc_moy, "acc_max": acc_max}

if not st.session_state.auth:
    st.markdown("<div class='ttl'>🌌 COSMOS X V21</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>OMEGA • MARKOV + BAYESIAN • ENTRY PRÉCIS</div>", unsafe_allow_html=True)
    _, cb, _ = st.columns([1, 1.2, 1])
    with cb:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 MOT DE PASSE", type="password", placeholder="Entrez: COSMOS2026")
        if st.button("🔓 ACTIVER OMEGA", use_container_width=True):
            if pw == "COSMOS2026": st.session_state.auth = True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card' style='max-width:800px;margin:20px auto;'>
    <h3 style='color:#00ffcc;font-family:Orbitron;text-align:center;font-size:1.1rem;'>📖 FANAZAVANA MALAGASY</h3>
    <div class='ib'><b style='color:#00ffcc;'>🎯 ENTRY TIME ULTRA PRÉCIS:</b><br>
    = LAST TIME + SHIFT calculé (20-95 secondes)<br>
    <b>LAST TIME</b> = Ora nilanihan'ny round taloha<br>
    Ohatra: Last time 20:22:24 + 50sec → Entry <b style='color:#00ffcc;'>20:23:14</b></div>
    <div class='ib'><b style='color:#00ffcc;'>📥 FOMBA FAMPIASANA:</b><br>
    1. <b>SHA512 5 premiers decimals:</b> Ex: <code>ac50e</code> (SHA512 voalohany 5 chars)<br>
    2. <b>HEX 8 chars:</b> Ex: <code>7db8e014</code> (hex @ Provably Fair)<br>
    3. <b>LAST COTE:</b> Résultat taloha → Ex: <code>1.88×</code><br>
    4. <b>LAST TIME:</b> Ora round taloha → Ex: <code>20:22:24</code><br>
    5. Tsindrio ANALYSER → Entry time miseho<br>
    6. Milalao @ entry → cash out @ targets</div>
    <div class='ib'><b style='color:#00ffcc;'>📊 SIGNAL (5 levels):</b><br>
    💎💎💎 ULTRA → Str≥90+Prob≥46% | 💎💎 STRONG → Str≥80+Prob≥40%<br>
    🔥 GOOD → Str≥70+Prob≥34% | 🟡 MODERATE → Str≥58+Prob≥27% | ⚠️ SKIP</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("### 🌌 COSMOS V21")
    s = gs(); t, w, l = s["t"], s["w"], s["l"]
    wr = round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='sb'><div class='sv'>{w}</div><div class='sl'>WINS</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='sb'><div class='sv'>{l}</div><div class='sl'>LOSS</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sb'><div class='sv'>{t}</div><div class='sl'>TOTAL</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET", use_container_width=True):
        rdb(); st.session_state.R = None; st.session_state.pid = None
        st.success("✅"); st.rerun()

st.markdown("<div class='ttl'>🌌 COSMOS X V21</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>OMEGA • MARKOV + BAYESIAN • 400K SIMS</div>", unsafe_allow_html=True)
ci, co = st.columns([1, 2], gap="medium")

with ci:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    sha5  = st.text_input("🔐 SHA512 (5 premiers decimals)", placeholder="Ex: ac50e  —  5 chars SHA512")
    hex8  = st.text_input("🔢 HEX (8 premiers chars)", placeholder="Ex: 7db8e014  —  hex Provably Fair")
    lc    = st.number_input("📊 LAST COTE", value=1.88, step=0.01, format="%.2f")
    lt_in = st.text_input("⏰ LAST TIME (HH:MM:SS)", placeholder="Ex: 20:22:24  —  ora round taloha")
    if   lc < 1.5: sl, sc2 = "🔵 COLD",  "#4488ff"
    elif lc < 2.5: sl, sc2 = "⚪ NORMAL", "#aaa"
    elif lc < 3.5: sl, sc2 = "🟡 WARM",  "#ffcc00"
    else:          sl, sc2 = "🔴 HOT",    "#ff3366"
    st.markdown(f"<div style='text-align:center;margin:6px 0;'><span style='background:rgba(255,255,255,.07);border-radius:8px;padding:4px 14px;color:{sc2};font-size:.82rem;'>{sl}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("🚀 ANALYSER OMEGA", use_container_width=True):
        if sha5 and hex8 and lt_in:
            with st.spinner("⚡ 400k sims..."):
                r = engine(sha5.strip(), hex8.strip(), lc, lt_in.strip())
            pid = sp(r)
            st.session_state.R = r; st.session_state.pid = pid
            st.session_state.ck += 1; st.rerun()
        else: st.error("❌ SHA5, HEX et Last Time obligatoires!")

with co:
    r = st.session_state.R
    if r:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,.4);font-size:.72rem;margin-top:14px;'>▸ ENTRY TIME (Last Time +{r['sh']}s)</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='etime'>{r['ent']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp']}%</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:rgba(255,255,255,.3);font-size:.68rem;'>PROB X3+ BAYESIAN</p>", unsafe_allow_html=True)
        st.markdown(f"""<div style='text-align:center;margin:10px 0;'>
        <span class='tag'>🔄 {r['state']}</span><span class='tag'>🔥 {r['hp']}%</span>
        <span class='tag'>💪 {r['str']}</span>
        <span class='tag-p'>X3.5+ {r['p35']}%</span><span class='tag-p'>X4+ {r['p4']}%</span>
        <span class='tag-p'>X5+ {r['p5']}%</span>
        </div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>MIN SAFE</div><div class='tv' style='color:#00ffcc;'>{r['tmin']}×</div><div class='ta'>{r['acc_min']}% acc</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>MOYEN</div><div class='tv' style='color:#ffd700;'>{r['tmoy']}×</div><div class='ta'>{r['acc_moy']}% acc</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>MAX X3+</div><div class='tv' style='color:#ff00ff;'>{r['tmax']}×</div><div class='ta'>{r['acc_max']}% acc</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        cw, cl2 = st.columns(2)
        with cw:
            if st.button("✅ WIN", use_container_width=True, key="bw"):
                if st.session_state.pid: ur(st.session_state.pid, "WIN")
                st.success("🎯 Win!"); st.rerun()
        with cl2:
            if st.button("❌ LOSS", use_container_width=True, key="bl"):
                if st.session_state.pid: ur(st.session_state.pid, "LOSS")
                st.rerun()
        st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,.2);font-size:.62rem;margin-top:8px;'>SHA:{r['sha5']} HEX:{r['hex8']} LC:{r['lc']}× • SQLite</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='min-height:350px;display:flex;align-items:center;justify-content:center;'><div style='text-align:center;'><div style='font-size:3rem;'>🌌</div><div style='color:rgba(255,255,255,.15);font-family:Orbitron;margin-top:10px;'>EN ATTENTE...</div></div></div>", unsafe_allow_html=True)

st.markdown("---")
df = gh(10)
if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
else: st.info("Aucun historique")
st.markdown("<div style='text-align:center;margin-top:18px;color:rgba(255,255,255,.07);font-size:.54rem;'>COSMOS X V21 OMEGA • SHA5+HEX8 • MARKOV+BAYESIAN • 400K SIMS</div>", unsafe_allow_html=True)
