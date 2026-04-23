import streamlit as st
import os
import pandas as pd
import math
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import hashlib

# --- [ 1. CONFIG & SETUP ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

# --- [ 2. หัวใจคำนวณ: ระบบถอดรหัส Lunar ] ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]

    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula, logic_type = f"√({day_val}² + {m_num}²)", "Vector Energy"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, logic_type = f"({day_val} × 1.618) / {m_num}", "Golden Ratio"

    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type}

# --- [ 3. UI STYLE ENGINE ] ---
def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        .stButton>button {
            border-radius: 15px; border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1); color: white;
            height: 80px; font-size: 16px; transition: 0.3s;
        }
        .stButton>button:hover { background: #00f2fe; color: #000; box-shadow: 0 0 20px #00f2fe; }
        .neon-text { text-align: center; color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; font-weight: bold; }
        .logic-box { background: rgba(10,10,10,0.9); border: 1px solid #333; padding: 15px; border-radius: 10px; margin: 10px 0; }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- [ 4. LOGIN SYSTEM ] ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 class='neon-text'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    new_user = st.text_input("ENTER AGENT NAME", placeholder="ระบุชื่อรหัสของคุณ").strip()
    if st.button("ACTIVATE SYSTEM", use_container_width=True):
        if new_user:
            # จำลองการลงทะเบียน (ปรับเชื่อม Firebase ตามจริง)
            st.session_state.user = new_user
            st.session_state.logged_in = True
            st.session_state.page = "HOME"
            st.success(f"WELCOME AGENT: {new_user}")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("กรุณาใส่ชื่อ AGENT!")
    st.stop()

# --- [ 5. NAVIGATION ] ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# ==========================================
# 🚀 MAIN HUB (10 APPS)
# ==========================================
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("🖼️ 2. IMAGE SEARCH", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("✨ 3. NEON GENERATOR", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("💖 4. DESTINY CHECK", use_container_width=True): st.session_state.page = "4"; st.rerun()
        if st.button("📝 5. SYSTEM LOG", use_container_width=True): st.session_state.page = "5"; st.rerun()
    with c2:
        if st.button("💬 6. CHAT SYSTEM", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("🎬 7. VIDEO HUB", use_container_width=True): st.session_state.page = "7"; st.rerun()
        if st.button("🌍 8. WORLD CLOCK", use_container_width=True): st.session_state.page = "8"; st.rerun()
        if st.button("🔢 9. DAILY CODE", use_container_width=True): st.session_state.page = "9"; st.rerun()
        if st.button("🎨 10. COLOR MASTER", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- PAGE 1: MUSIC ---
elif st.session_state.page == "1":
    st.header("🎵 SYNAPSE AUDIO DECK")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลงของคุณ", type=['mp3'])
    if uploaded_file: st.audio(uploaded_file)
    st.write("คลังเพลงในระบบ:")
    songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    for s in songs:
        if st.button(f"Play {s}"): st.audio(s)

# --- PAGE 2: IMAGE SEARCH ---
elif st.session_state.page == "2":
    st.header("🖼️ SATELLITE IMAGE SEARCH")
    query = st.text_input("ค้นหาภาพ (English):", "Cyberpunk")
    if st.button("SCAN"):
        st.image(f"https://source.unsplash.com/800x400/?{query}")

# --- PAGE 3: NEON GENERATOR ---
elif st.session_state.page == "3":
    st.header("✨ NEON TEXT GENERATOR")
    text = st.text_input("ใส่ข้อความ:", "SYNAPSE")
    color = st.color_picker("เลือกสีนีออน:", "#00f3ff")
    st.markdown(f"<h1 style='text-align:center; color:#fff; text-shadow: 0 0 20px {color}; font-size:4rem;'>{text}</h1>", unsafe_allow_html=True)

# --- PAGE 4: DESTINY CHECK ---
elif st.session_state.page == "4":
    st.header("💖 DESTINY ANALYSIS")
    n1 = st.text_input("AGENT 1")
    n2 = st.text_input("AGENT 2")
    if st.button("ANALYZE"):
        s1 = sum(ord(c) for c in n1)
        s2 = sum(ord(c) for c in n2)
        match = 100 - (abs(s1-s2)%100)
        st.metric("COMPATIBILITY", f"{match}%")

# --- PAGE 5: SYSTEM LOG ---
elif st.session_state.page == "5":
    st.header("📝 SYSTEM MEMORY LOG")
    log = st.text_area("บันทึกเหตุการณ์:")
    if st.button("SAVE"): st.success("บันทึกสำเร็จ (Offline Mode)")

# --- PAGE 6: CHAT SYSTEM ---
elif st.session_state.page == "6":
    st_autorefresh(interval=8000, key="chat_refresh")
    st.header("💬 SECURE CHAT")
    st.info("ระบบกำลังเชื่อมต่อสัญญาณ...")
    msg = st.chat_input("พิมพ์ข้อความ...")
    if msg: st.write(f"**You:** {msg}")

# --- PAGE 7: VIDEO HUB ---
elif st.session_state.page == "7":
    st.header("🎬 VIDEO CONTROL")
    v_url = st.text_input("URL วิดีโอ (YouTube/MP4):", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    if v_url: st.video(v_url)

# --- PAGE 8: WORLD CLOCK ---
elif st.session_state.page == "8":
    st.header("🌍 GLOBAL CHRONO")
    st.subheader(f"BANGKOK: {datetime.now().strftime('%H:%M:%S')}")

# --- PAGE 9: DAILY CODE ---
elif st.session_state.page == "9":
    st.header("🔢 DAILY SECURITY CODE")
    seed = f"{date.today()}_{st.session_state.get('user','GUEST')}"
    h = hashlib.sha256(seed.encode()).hexdigest()
    st.code(f"ACCESS CODE: {h[:6].upper()}", language='python')

# --- PAGE 10: COLOR MASTER ---
elif st.session_state.page == "10":
    st.header("🎨 THEME CONTROL")
    c = st.color_picker("ปรับสีหลักระบบ:", "#00f3ff")
    st.markdown(f"<style>.stApp {{ border-top: 10px solid {c}; }}</style>", unsafe_allow_html=True)
    st.success("สีระบบถูกเปลี่ยนเรียบร้อย")
