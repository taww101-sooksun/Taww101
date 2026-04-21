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
import hashlib

# --- [ 1. INITIAL SETUP ] ---
if 'init' not in st.session_state:
    st.set_page_config(page_title="SYNAPSE HUB", layout="wide")
    st.session_state.init = True
    st.session_state.page = "HOME"
    st.session_state.custom_theme = "#00f3ff"

# --- [ 2. FIREBASE CONNECTION ] ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        if "private_key" in fb_creds:
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"❌ Firebase Error: {e}")

# --- [ 3. UI ENGINE & DESIGN ] ---
def setup_ui():
    theme_color = st.session_state.get('custom_theme', "#00f3ff")
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;600&display=swap');
    .stApp {{ background-color: #0A0A0A; font-family: 'Kanit', sans-serif; color: white; }}
    header, footer, #MainMenu {{visibility: hidden;}}
    
    .sss-header {{ color: #FF0000; font-size: 42px; font-weight: bold; text-align: center; text-shadow: 0 0 15px #FF0000; margin:0; }}
    .sss-motto {{ color: #FFD700; font-size: 16px; text-align: center; margin-bottom: 20px; letter-spacing: 2px; }}
    
    .stButton>button {{
        border-radius: 12px; border: 1px solid {theme_color} !important;
        background: rgba(0,0,0,0.5); color: white; transition: 0.3s;
        box-shadow: 0 0 5px {theme_color}; width: 100%; height: 50px;
    }}
    .stButton>button:hover {{ background: {theme_color}; color: black; box-shadow: 0 0 20px {theme_color}; }}
    </style>
    <div class="sss-header">S.S.S MUSIC × SYNAPSE</div>
    <div class="sss-motto">"อยู่นิ่งๆ ไม่เจ็บตัว"</div>
    """, unsafe_allow_html=True)

# --- [ 4. LOGIN SYSTEM ] ---
if not st.session_state.get('logged_in', False):
    setup_ui()
    st.markdown("<h2 style='text-align:center; color:#00f3ff;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    new_user = st.text_input("ENTER AGENT NAME", placeholder="ระบุชื่อรหัสของคุณ").strip()
    if st.button("ACTIVATE SYSTEM"):
        if new_user:
            st.session_state.user = new_user
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

setup_ui()

# --- [ 5. NAVIGATION ] ---
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก (MAIN MENU)"):
        st.session_state.page = "HOME"
        st.rerun()

# --- [ 6. PAGES LOGIC ] ---

# --- หน้าแรก: ศูนย์ควบคุม ---
if st.session_state.page == "HOME":
    st.markdown("<h3 style='text-align:center;'>เลือกฟังก์ชันควบคุมระบบ</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER"): st.session_state.page = "1"; st.rerun()
        if st.button("💬 2. CHAT SYSTEM"): st.session_state.page = "2"; st.rerun()
        if st.button("🔮 3. DESTINY TIMELINE"): st.session_state.page = "5"; st.rerun()
    with c2:
        if st.button("🛰️ 4. SENSOR & GPS"): st.session_state.page = "6"; st.rerun()
        if st.button("🔢 5. DAILY CODE"): st.session_state.page = "8"; st.rerun()
        if st.button("🎨 6. COLOR MASTER"): st.session_state.page = "10"; st.rerun()

# --- หน้า 1: MUSIC PLAYER ---
elif st.session_state.page == "1":
    st.markdown("<h2 style='text-align:center; color:#FF0000;'>🎵 MUSIC COMMAND</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"): st.image("logo1.png", use_container_width=True)
    
    note = st.text_input("", placeholder="ใจความสั้นๆ ที่จะให้ AI ขยี้...")
    if st.button("ขยี้ใจความ (GENERATE)"):
        st.info("กำลังประมวลผลทำนอง...")
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.button("💾 SAVE")
    with c2: st.button("📤 SHARE")
    with c3: st.button("🔥 TURBO")

# --- หน้า 2: CHAT SYSTEM ---
elif st.session_state.page == "2":
    st.markdown("<h2 style='text-align:center; color:#00f3ff;'>💬 PRIVATE CHAT</h2>", unsafe_allow_html=True)
    msg = st.text_input("ส่งข้อความถึงระบบ:")
    if st.button("SEND SIGNAL"):
        st.success("ข้อความถูกบันทึกแล้ว (Firebase)")

# --- หน้า 6: SENSOR & GPS (รวมร่างใหม่) ---
elif st.session_state.page == "6":
    st.markdown("<h2 style='text-align:center; color:#FFD700;'>🛰️ SENSOR CONTROL</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📍 GPS & WEATHER", "🎙️ SONIC SCAN", "📳 MOTION"])
    
    with tab1:
        env_js = """
        <div style="background:#111; color:#FFD700; padding:20px; border:2px solid #FFD700; border-radius:15px; text-align:center; font-family:monospace;">
            <p id="st">📍 พร้อมสแกนพิกัด</p>
            <div style="display:flex; justify-content:space-around;">
                <div><small>LAT</small><h2 id="lat">-</h2></div>
                <div><small>LON</small><h2 id="lon">-</h2></div>
            </div>
            <div style="margin-top:10px; background:#222; padding:10px; border
