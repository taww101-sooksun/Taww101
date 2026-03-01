import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import os

# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบเลือกสี (Color/Theme Selector)
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    picked_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.session_state.theme_color = picked_color
    st.write(f"สีปัจจุบัน: {picked_color}")
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# ใช้ CSS ฉีดสีตามที่เลือก
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .chat-box {{ 
        border: 1px solid {st.session_state.theme_color}; 
        padding: 10px; border-radius: 10px; margin-bottom: 5px;
        background: rgba(255,255,255,0.05);
    }}
    /* ปรับแต่งสีปุ่มให้ตรงกับสีที่เลือก */
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background-color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")

# --- 3. LOGIN SYSTEM (แก้ไขจุดที่พัง) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>🔐 SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
    
    # แก้ไขจาก st.center() เป็นการใช้ Columns แทน เพื่อให้รันผ่าน
    col1, col2, col3 = st.columns([1, 2, 1
