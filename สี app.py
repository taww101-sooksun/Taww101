import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import os
import random
import time
from datetime import datetime

# --- 1. INITIALIZE & CONFIG (ตั้งค่าระบบ) ---
st.set_page_config(page_title="SYNAPSE OMNI", layout="wide")

def init_firebase():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"Firebase Connection Error: {e}")

def save_log(action_details):
    try:
        now = datetime.now()
        date_key = now.strftime("%Y-%m-%d")
        db.reference(f'synapse_logs/{date_key}').push({
            'time': now.strftime("%H:%M:%S"),
            'action': action_details,
            'user': 'Ta101'
        })
    except: pass

# --- 2. SYSTEM STATE (จำสถานะ) ---
if 'system_active' not in st.session_state:
    st.session_state.system_active = False
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14"
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#000000"

# --- 3. ACTIVATION SCREEN (หน้าแรกเพื่อเปิดระบบ) ---
if not st.session_state.system_active:
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; margin-top:20%; font-family:Orbitron;'>SYNAPSE OMNI SYSTEM</h1>", unsafe_allow_html=True)
    if st.button("🚀 CLICK TO ACTIVATE COMMAND CENTER", use_container_width=True):
        st.session_state.system_active = True
        init_firebase()
        save_log("SYSTEM ACTIVATED")
        st.rerun()
    st.stop()

# --- 4. DYNAMIC UI (CSS) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR (ปรับแต่ง) ---
with st.sidebar:
    st.title("⚙️ SETTINGS")
    st.session_state.theme_color = st.color_picker("Neon Color", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("Background Color", st.session_state.bg_color)
    st.write("---")
    st.markdown(f"**Slogan:**\n*'อยู่นิ่งๆ ไม่เจ็บตัว'*")

# --- 6. MAIN INTERFACE ---
st.markdown(f"<h1 style='text-align:center; text-shadow: 0 0 10px {st.session_state.theme_color};'>SYNAPSE OMNI V5</h1>", unsafe_allow_html=True)

main_tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOGS", "🎧 ROOMS"])

# --- TAB: CORE (Hierarchy System) ---
with main_tabs[0]:
    if st.session_state.nav_level != "HOME":
        if st.button("⬅️ BACK"):
            if "." in st.session_state.nav_level:
                st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
            else: st.session_state.nav_level = "HOME"
            st.rerun()
    
    st.subheader(f"PATH: {st.session_state.nav_level}")
    if st.session_state.nav_level == "HOME":
        c1, c2 = st.columns(2)
        if c1.button("กรอบที่ 1", use_container_width=True):
            st.session_state.nav_level = "1"; save_log("ENTERED LEVEL 1"); st.rerun()
        if c2.button("กรอบที่ 2", use_container_width=True):
            st.session_state.nav_level = "2"; save_log("ENTERED LEVEL 2"); st.rerun()

# --- TAB: COMMS (Firebase Chat) ---
with main_tabs[2]:
    st.subheader("🌐 LOBBY SIGNALS")
    chat_ref = db.reference('public_chat')
    msg = st.text_input("ระบุสัญญาณ...")
    if st.button("SEND"):
        if msg:
            chat_ref.push({'user': 'Ta101', 'msg': msg, 'ts': time.time()})
            st.rerun()
    
    msgs = chat_ref.order_by_key().limit_to_last(10).get()
    if msgs:
        for m in reversed(list(msgs.values())):
            st.write(f"💬 **{m['user']}:** {m['msg']}")

# --- TAB: LOGS (History) ---
with main_tabs[3]:
    st.subheader("📊 ACTIVITY LOG")
    today = datetime.now().strftime("%Y-%m-%d")
    logs = db.reference(f'synapse_logs/{today}').get()
    if logs:
        for lid in reversed(list(logs.keys())):
            l = logs[lid]
            st.code(f"[{l['time']}] {l['action']}")

# --- TAB: ROOMS (Music Player) ---
with main_tabs[4]:
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if music_files:
        if 'song_idx' not in st.session_state: st.session_state.song_idx = 0
        current_song = music_files[st.session_state.song_idx]
        st.markdown(f"🎶 **NOW PLAYING:** {current_song}")
        st.audio(current_song, autoplay=True)
        if st.button("⏭️ NEXT TRACK"):
            st.session_state.song_idx = (st.session_state.song_idx + 1) % len(music_files)
            st.rerun()
    else: st.warning("No MP3 files found in directory.")
