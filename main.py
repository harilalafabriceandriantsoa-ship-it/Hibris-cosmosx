import streamlit as st    
import hashlib    
import statistics    
import random    
import numpy as np    
from streamlit_autorefresh import st_autorefresh    
from datetime import datetime, timedelta

st.set_page_config(page_title="COSMOS X ANDR", layout="wide")

# ---------------- SESSION ----------------
if "login" not in st.session_state:    
    st.session_state.login = False    

if "memory_cosmos" not in st.session_state:    
    st.session_state.memory_cosmos = []    

if "balance" not in st.session_state:    
    st.session_state.balance = 1000    

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- LOGIN ----------------
if not st.session_state.login:    
    st.title("🔐 COSMOS ACCESS")    
    pwd = st.text_input("Password", type="password")    

    if st.button("ENTER"):    
        if pwd == "2026":    
            st.session_state.login = True    
            st.rerun()    
        else:    
            st.error("Wrong password")    

else:    
    st.title("🌌 COSMOS X ANDR SYSTEM")

    # ---------------- HASH ----------------    
    def verify_hash(server, client, nonce):    
        return hashlib.sha512(f"{server}:{client}:{nonce}".encode()).hexdigest()    

    def crash(server, client, nonce):    
        h = verify_hash(server, client, nonce)    
        dec = int(h[-8:],16) or 1    
        return round((4294967295*0.97)/dec,2)    

    # ---------------- AI SCORE ----------------    
    def ai_boost(avg, accuracy, mn, series):
        trend = series[-1] - series[0]
        trend_factor = 1.15 if trend > 0 else 0.9

        entropy = np.std(series)
        stability = 1 / (1 + entropy)

        score = (avg * 0.4) + ((accuracy/100) * 3 * 0.4) + (mn * 0.2)
        return score * trend_factor * (1 + stability)

    # ---------------- COTE ----------------    
    def compute_cote(avg, accuracy):    
        if accuracy > 90 and avg > 3:    
            return 3.0    
        elif accuracy > 80:    
            return 2.5    
        elif accuracy > 70:    
            return 2.0    
        elif accuracy > 60:    
            return 1.8    
        else:    
            return 1.5    

    # ---------------- HEURE D'ENTRÉE ULTRA ----------------
    def entry_time(server, client, nonce, confidence, cote):
        base = int(hashlib.sha512(f"{server}:{client}:{nonce}".encode()).hexdigest()[:16],16)

        time_now = datetime.now()
        seconds = time_now.hour*3600 + time_now.minute*60 + time_now.second

        risk_factor = int((cote * 10) + (confidence/10))

        seed = base + seconds + risk_factor

        delay = 25 + (seed % 50)   # ⏰ stable X3+ window

        return (time_now + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # ---------------- COSMOS ENGINE ----------------    
    def analyse_cosmos(server, client, nonce):

        series = [crash(server, client, nonce+i) for i in range(20)]

        mn = round(min(series),2)    
        avg = round(statistics.mean(series),2)    
        mx = round(max(series),2)    

        good = sum(1 for x in series if x >= 2)    
        accuracy = int((good / len(series)) * 100)    

        cote = compute_cote(avg, accuracy)    

        confidence = int((accuracy * 0.6) + (avg * 20 * 0.4))    

        score = ai_boost(avg, accuracy, mn, series)

        signal = "🔴 SKIP"
        if accuracy >= 85 and avg > 2:
            signal = "🟢 X3+ READY"
        elif accuracy >= 65:
            signal = "🟡 WAIT"
        else:
            signal = "🔴 SKIP"

        entry = entry_time(server, client, nonce, confidence, cote)

        return {
            "nonce": nonce,
            "min": mn,
            "avg": avg,
            "max": mx,
            "accuracy": accuracy,
            "cote": cote,
            "confidence": confidence,
            "score": score,
            "signal": signal,
            "entry": entry
        }

    # ---------------- UI ----------------    
    server = st.text_input("Server Seed")    
    client = st.text_input("Client Seed")    
    nonce = st.number_input("Nonce", value=1)    

    auto_mode = st.checkbox("🤖 AUTO PLAY")

    if st.button("SCAN COSMOS X"):

        result = analyse_cosmos(server, client, nonce)

        # SAVE HISTORY
        st.session_state.history.append(result)

        # 🎯 DISPLAY ONLY ONE RESULT
        st.markdown(f"""
# 🌌 COSMOS RESULT ⏳🎯

⏰ ENTRY TIME: **{result['entry']}**  
🎯 SIGNAL: **{result['signal']}**  
📊 ACCURACY: **{result['accuracy']}%**  
💎 COTE: x{result['cote']}  
🧠 CONFIDENCE: {result['confidence']}  
⚡ SCORE IA: {round(result['score'],2)}
""")

        if auto_mode:
            if result["confidence"] > 75:
                bet = st.session_state.balance * 0.02
                st.session_state.balance += bet if random.random() > 0.5 else -bet

            st.write("💰 BALANCE:", round(st.session_state.balance,2))

    # ---------------- HISTORY ----------------
    st.subheader("📜 HISTORY")
    for h in reversed(st.session_state.history[-10:]):
        st.write(f"⏰ {h['entry']} | 🎯 {h['signal']} | 📊 {h['accuracy']}% | x{h['cote']}")

    # ---------------- GUIDE ----------------
    st.subheader("📖 GUIDE")

    st.markdown("""
### 🎯 HOW TO USE COSMOS X ANDR
- 🔑 Enter Server Seed + Client Seed
- 🎲 Set nonce
- 🚀 Click SCAN COSMOS X

### ⏰ ENTRY RULE
- 🟢 X3+ READY = ENTRY POSSIBLE
- 🟡 WAIT = unstable zone
- 🔴 SKIP = avoid

### 💡 BEST ZONE
- COTE 1.8 → 2.5 = BEST X3+ WINDOW
""")

    st_autorefresh(interval=10000, limit=None)
