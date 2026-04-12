import streamlit as st
import hashlib
import statistics
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="COSMOS AI", layout="wide")

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

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
    st.title("🌌 COSMOS AI SYSTEM")

    # ---------------- HASH ----------------
    def verify_hash(server, client, nonce):
        return hashlib.sha512(f"{server}:{client}:{nonce}".encode()).hexdigest()

    # ---------------- CRASH ----------------
    def crash(server, client, nonce):
        h = verify_hash(server, client, nonce)
        dec = int(h[-8:],16) or 1
        return round((4294967295*0.97)/dec,2)

    # ---------------- COSMOS AI ----------------
    def analyse_crash_series(server, client, nonce):
        results = [crash(server, client, nonce+i) for i in range(20)]
        avg = round(statistics.mean(results),2)

        streak_low = 0
        for r in reversed(results):
            if r < 2:
                streak_low += 1
            else:
                break

        signal = "🔴 SKIP"
        if streak_low >= 4 and avg > 1.8:
            signal = "🟢 PLAY"

        return results, avg, streak_low, signal

    # ---------------- COSMOS ENTRY ----------------
    def cosmos_signals(series):
        signals = []
        for i in range(3):
            part = series[i*5:(i+1)*5]
            if sum(x<2 for x in part) > 3:
                signals.append("🔴")
            else:
                signals.append("🟢")
        return signals

    # ---------------- UI ----------------
    server = st.text_input("Server Seed")
    client = st.text_input("Client Seed")
    nonce = st.number_input("Nonce", value=1)

    if st.button("SCAN COSMOS"):
        series, avg, streak, signal = analyse_crash_series(server, client, nonce)
        signals3 = cosmos_signals(series)

        st.success(f"GLOBAL: {signal}")
        st.write("3 SIGNAL:", signals3)
        st.write("AVG:", avg)

    st_autorefresh(interval=10000, limit=None)
