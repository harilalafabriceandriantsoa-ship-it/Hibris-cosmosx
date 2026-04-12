import streamlit as st
import hashlib
import statistics
import random
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="COSMOS V2000", layout="wide")

# ---------------- SESSION ----------------
if "login" not in st.session_state:
    st.session_state.login = False
if "memory_cosmos" not in st.session_state:
    st.session_state.memory_cosmos = []
if "balance" not in st.session_state:
    st.session_state.balance = 1000

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
    st.title("🌌 COSMOS V2000 AI SYSTEM")

    # ---------------- HASH ----------------
    def verify_hash(server, client, nonce):
        return hashlib.sha512(f"{server}:{client}:{nonce}".encode()).hexdigest()

    def crash(server, client, nonce):
        h = verify_hash(server, client, nonce)
        dec = int(h[-8:],16) or 1
        return round((4294967295*0.97)/dec,2)

    # ---------------- SCORE AI ----------------
    def compute_score(avg, accuracy, mn, series):
        trend = series[-1] - series[0]
        trend_factor = 1.1 if trend > 0 else 0.9

        score = (avg * 0.4) + ((accuracy/100) * 3 * 0.4) + (mn * 0.2)
        return score * trend_factor

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

    # ---------------- AUTO BET ----------------
    def auto_play(confidence):
        bet = st.session_state.balance * 0.02

        if confidence > 75:
            if random.random() > 0.45:
                st.session_state.balance += bet
                return "WIN"
            else:
                st.session_state.balance -= bet
                return "LOSE"
        return "SKIP"

    # ---------------- COSMOS TOUR V2000 ----------------
    def analyse_cosmos_tours(server, client, nonce):

        tours = []
        base_nonce = nonce

        for t in range(1,4):

            # PRE-SCAN
            test_series = [crash(server, client, base_nonce+i) for i in range(10)]
            avg_test = statistics.mean(test_series)
            variance = np.var(test_series)
            low_count = sum(1 for r in test_series if r < 2)

            # AUTO JUMP
            if low_count >= 6:
                jump = random.randint(7,10)
            elif variance < 1:
                jump = random.randint(5,8)
            elif avg_test < 1.5:
                jump = random.randint(4,6)
            else:
                jump = random.randint(2,4)

            new_nonce = base_nonce + jump

            # MAIN SCAN
            series = [crash(server, client, new_nonce + i) for i in range(20)]

            mn = round(min(series),2)
            avg = round(statistics.mean(series),2)
            mx = round(max(series),2)

            good = sum(1 for x in series if x >= 2)
            accuracy = int((good / len(series)) * 100)

            # SCORE AI
            score = compute_score(avg, accuracy, mn, series)

            # SIGNAL
            if accuracy >= 85 and avg > 2:
                signal = "🟢 GO"
            elif accuracy >= 65:
                signal = "🟡 WAIT"
            else:
                signal = "🔴 SKIP"

            # CONFIDENCE
            confidence = int((accuracy * 0.6) + (avg * 20 * 0.4))

            # COTE
            cote = compute_cote(avg, accuracy)

            tours.append({
                "tour": t,
                "nonce": new_nonce,
                "jump": jump,
                "min": mn,
                "avg": avg,
                "max": mx,
                "accuracy": accuracy,
                "signal": signal,
                "cote": cote,
                "score": score,
                "confidence": confidence
            })

            # SELF LEARNING
            st.session_state.memory_cosmos.append([avg, accuracy, mn])

            base_nonce = new_nonce

        return tours

    # ---------------- UI ----------------
    server = st.text_input("Server Seed")
    client = st.text_input("Client Seed")
    nonce = st.number_input("Nonce", value=1)

    auto_mode = st.checkbox("🤖 AUTO PLAY")

    if st.button("SCAN COSMOS"):

        tours = analyse_cosmos_tours(server, client, nonce)

        # ⭐ BEST TOUR
        best = max(tours, key=lambda x: x["score"])

        for t in tours:
            st.markdown(f"""
🎯 TOUR {t['tour']} → {t['signal']}  
Nonce: {t['nonce']} (+{t['jump']})  
MIN: {t['min']} | AVG: {t['avg']} | MAX: {t['max']}  
ACCURACY: {t['accuracy']}%  
🎲 COTE CONSEILLÉE: x{t['cote']}  
""")

        st.success(f"⭐ BEST TOUR: {best['tour']}")

        # AUTO PLAY
        if auto_mode:
            result = auto_play(best["confidence"])
            st.write("🤖 AUTO RESULT:", result)
            st.write("💰 BALANCE:", round(st.session_state.balance,2))

    st_autorefresh(interval=10000, limit=None)
