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

    # ---------------- HASH512 ----------------        
    def hash512(server, client):        
        return hashlib.sha512(f"{server}:{client}".encode()).hexdigest()        

    # ---------------- CORE CRASH ----------------        
    def crash(server, client):        
        h = hash512(server, client)        
        dec = int(h[-8:],16) or 1        
        return round((4294967295*0.97)/dec,2)    

    # ---------------- COTE FILTER ----------------        
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

    # ---------------- HEURE ULTRA DYNAMIQUE ----------------        
    def entry_time(server, client, cote, confidence):    

        h = hash512(server, client)    

        now = datetime.now()    
        seconds = now.hour*3600 + now.minute*60 + now.second    

        hash_seed = int(h[:16],16)    
        time_seed = int(h[16:32],16)    

        # 🔥 fusion HASH + TIME + COTE    
        raw = hash_seed + time_seed + seconds + int(cote*100) + confidence    

        # ⏰ dynamic window (NOT FIXED)    
        base_delay = 20 + (raw % 40)    
        micro_delay = (int(h[-6:],16) % 10)    

        final_delay = base_delay + micro_delay    

        return (now + timedelta(seconds=final_delay)).strftime("%H:%M:%S")    

    # ---------------- ENGINE ----------------        
    def analyse_cosmos(server, client):    

        series = [crash(server, client) for _ in range(20)]    

        mn = round(min(series),2)        
        avg = round(statistics.mean(series),2)        
        mx = round(max(series),2)        

        good = sum(1 for x in series if x >= 2)        
        accuracy = int((good / len(series)) * 100)        

        cote = compute_cote(avg, accuracy)        

        confidence = int((accuracy * 0.6) + (avg * 20 * 0.4))        

        # 🧠 SIGNAL ENGINE        
        if accuracy >= 85 and avg > 2:        
            signal = "🟢 X3+ READY"        
        elif accuracy >= 65:        
            signal = "🟡 WAIT"        
        else:        
            signal = "🔴 SKIP"        

        entry = entry_time(server, client, cote, confidence)    

        return {    
            "min": mn,    
            "avg": avg,    
            "max": mx,    
            "accuracy": accuracy,    
            "cote": cote,    
            "confidence": confidence,    
            "signal": signal,    
            "entry": entry    
        }    

    # ---------------- UI ----------------        
    server = st.text_input("Server Seed")        
    client = st.text_input("Client Seed")        

    auto_mode = st.checkbox("🤖 AUTO PLAY")    

    if st.button("SCAN COSMOS X"):    

        result = analyse_cosmos(server, client)    

        st.session_state.history.append(result)    

        # 🎯 RESULT DISPLAY (STYLE KEEP)    
        st.markdown(f"""
# 🌌 COSMOS RESULT ⏳🎯    

⏰ ENTRY TIME: **{result['entry']}**    
🎯 SIGNAL: **{result['signal']}**    
📊 ACCURACY: **{result['accuracy']}%**    
💎 COTE: x{result['cote']}    
🧠 CONFIDENCE: {result['confidence']}    
""")

        # AUTO MODE    
        if auto_mode:    
            if result["confidence"] > 75:    
                bet = st.session_state.balance * 0.02    
                st.session_state.balance += bet if random.random() > 0.5 else -bet    

            st.write("💰 BALANCE:", round(st.session_state.balance,2))    

    # ---------------- HISTORY ----------------    
    st.subheader("📜 HISTORY")    
    for h in reversed(st.session_state.history[-10:]):    
        st.write(f"⏰ {h['entry']} | 🎯 {h['signal']} | 📊 {h['accuracy']}% | x{h['cote']}")    

    # ---------------- AUTO REFRESH ----------------    
    st_autorefresh(interval=10000, limit=None)
