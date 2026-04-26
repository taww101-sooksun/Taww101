# =========================================================
# 🛡️ SYNAPSE COMMAND CENTER - NEON POWER
# =========================================================

import streamlit as st
import os
import time
import json
import uuid
import base64
import hashlib
import io
from datetime import datetime, timedelta
import pytz

# --- แก้ไขจุดที่ Error (Import เฉพาะตัวที่จำเป็นของ WebRTC) ---
try:
    from streamlit_webrtc import webrtc_streamer
except ImportError:
    pass

# --- Import อื่นๆ ยังอยู่ครบตามเดิม ---
import firebase_admin
from firebase_admin import credentials, firestore, storage

# =========================================================
# 🎨 ZONE 1: CSS 7 สีสะท้อนแสง (NEON RAINBOW FLOW)
# =========================================================

st.set_page_config(page_title="SYNAPSE", layout="wide")

st.markdown("""
    <style>
    /* ลบส่วนเกิน Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* พื้นหลังดำสนิทเพื่อให้สีสะท้อนแสงเด่นที่สุด */
    .stApp { background-color: #000000; }

    /* สโลแกน 7 สีสะท้อนแสง วิ่งสลับสี (Rainbow Neon) */
    .neon-slogan {
        font-family: 'Courier New', Courier, monospace;
        font-size: 30px;
        font-weight: bold;
        text-align: center;
        letter-spacing: 5px;
        background: linear-gradient(to right, #FF3131, #FF5E33, #FFF01F, #0FFF50, #00F3FF, #1F51FF, #FF44CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow-glow 5s linear infinite;
        text-shadow: 0 0 10px rgba(255,255,255,0.2);
    }

    @keyframes rainbow-glow {
        0% { filter: hue-rotate(0deg) drop-shadow(0 0 5px #00F3FF); }
        100% { filter: hue-rotate(360deg) drop-shadow(0 0 5px #00F3FF); }
    }

    /* ปุ่มกดแบบขอบสะท้อนแสง */
    .stButton>button {
        background-color: transparent;
        color: #0FFF50; /* เริ่มต้นด้วยสีเขียว Matrix */
        border: 2px solid #0FFF50;
        border-radius: 15px;
        height: 60px;
        font-weight: bold;
        text-transform: uppercase;
        box-shadow: 0 0 10px #0FFF50;
        transition: 0.4s;
    }

    .stButton>button:hover {
        background-color: #0FFF50;
        color: #000;
        box-shadow: 0 0 30px #0FFF50, 0 0 60px #0FFF50;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🏠 ZONE 2: HEADER (LOGO1 + NEON SLOGAN)
# =========================================================

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo1.png", width=200)
    except:
        st.write("")

# แสดงสโลแกน 7 สีสะท้อนแสง
st.markdown('<p class="neon-slogan">SYNAPSE : อยู่นิ่งๆ ไม่เจ็บตัว</p>', unsafe_allow_html=True)

# =========================================================
# 📟 ZONE 3: 20-UNIT HUB
# =========================================================

if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    cols = st.columns(4)
    for i in range(1, 21):
        with cols[(i-1)%4]:
            # สลับสีขอบปุ่มตาม Unit (เพื่อให้ครบ 7 สี)
            colors = ["#FF3131", "#FF5E33", "#FFF01F", "#0FFF50", "#00F3FF", "#1F51FF", "#FF44CC"]
            current_color = colors[(i-1)%7]
            
            # ใช้ CSS เฉพาะปุ่มเพื่อเปลี่ยนสีขอบ
            st.markdown(f"""
                <style>
                div.stButton > button[key="u{i}"] {{
                    color: {current_color};
                    border-color: {current_color};
                    box-shadow: 0 0 5px {current_color};
                }}
                div.stButton > button[key="u{i}"]:hover {{
                    background-color: {current_color};
                    box-shadow: 0 0 20px {current_color};
                }}
                </style>
            """, unsafe_allow_html=True)
            
            if st.button(f"UNIT {i:02d}", key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()

else:
    if st.sidebar.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"
        st.rerun()
    
    st.markdown(f"### ⚡ SYSTEM ONLINE : UNIT {st.session_state.page}")
    st.markdown("---")
    
    # พื้นที่วางโค้ดในแต่ละห้อง
    if st.session_state.page == "1":
        st.write("พร้อมรับข้อมูลความจริง...")

# =========================================================
