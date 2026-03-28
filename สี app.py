import streamlit as st
import os
import random
import time
import requests
import pytz
import folium
import firebase_admin
import streamlit.components.v1 as components
from datetime import datetime
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from firebase_admin import credentials, db

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212" 
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

# --- 2. INITIALIZE FIREBASE ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://sooksun1-default-rtdb.firebaseio.com/'})
    except: pass

# --- 3. SECURITY GATE ---
if not st.session_state.authenticated:
    st.markdown("""<style>.stApp { background: #000; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='padding:20px; border:2px solid #39FF14; border-radius:15px; background:rgba(0,0,0,0.8);'>", unsafe_allow_html=True)
        st.subheader("🔐 SYNAPSE ACCESS")
        u_id = st.text_input("ID")
        u_pw = st.text_input("Password", type="password")
        if st.button("UNLOCK"):
            if u_pw == "99999999" and u_id:
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
            else: st.error("Unauthorized!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. DYNAMIC CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .glossy-card {{ background: rgba(0, 0, 0, 0.85); border: 2px solid {st.session_state.theme_color}; border-radius: 15px; padding: 20px; box-shadow: 0 0 15px {st.session_state.theme_color}; margin-bottom: 15px; }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.6);
        padding: 15px 0; border-radius: 12px; margin-bottom: 15px; border: 2px solid {st.session_state.theme_color};
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite;
        font-family: 'Orbitron', sans-serif; font-size: 22px; color: {st.session_state.theme_color};
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    h1, h2, h3, p, span {{ font-family: 'Orbitron', sans-serif; color: {st.session_state.theme_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    logo_path = "logo2.jpg" if os.path.exists("logo2.jpg") else "logo3.jpg" if os.path.exists("logo3.jpg") else None
    if logo_path: st.image(logo_path, use_container_width=True)
    st.markdown("### 🎨 SYSTEM CONTROL")
    st.session_state.theme_color = st.color_picker("นีออน", st.session_state.theme_color)
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 6. DATA PREPARATION (ประกาศตัวแปรไว้ก่อนเพื่อกัน Error) ---
lat, lon = 13.7563, 100.5018 # ค่าเริ่มต้น (กรุงเทพ)
location_ready = False

location = get_geolocation()
if location and location.get('coords'):
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    location_ready = True

# --- 7. MAIN INTERFACE ---
col_main, col_sub = st.columns([2, 1])

with col_main:
    # --- MUSIC SYSTEM ---
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if music_files:
        if 'song_index' not in st.session_state: st.session_state.song_index = 0
        current_song = music_files[st.session_state.song_index]
        st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• SYNAPSE VIBE </p></div>', unsafe_allow_html=True)
        st.audio(current_song)
        
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("⏭️ NEXT"): 
                st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
                st.rerun()
        with c2:
            if st.button("🎲 RANDOM"):
                st.session_state.song_index = random.randint(0, len(music_files)-1)
                st.rerun()

    # --- DATABASE UPDATE ---
    st.markdown("### 📡 DATABASE STATUS")
    with st.form("db_form", clear_on_submit=True):
        msg = st.text_input("ส่งข้อความเข้าฐานข้อมูล:")
        if st.form_submit_button("🚀 UPDATE STATUS"):
            if msg:
                db.reference('public_chat').push({
                    'user': st.session_state.my_id,
                    'text': msg,
                    'time': time.time()
                })
                st.success("Sent!")

with col_sub:
    # --- RADAR MAP (แก้จุดพัง lat, lon) ---
    st.markdown("### 🛰️ RADAR MAP")
    if location_ready:
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles='https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', attr='Google')
        folium.Marker([lat, lon], popup="CURRENT LOCATION", icon=folium.Icon(color='red')).add_to(m)
        st_folium(m, height=300, use_container_width=True, key="synapse_map")
    else:
        st.warning("📡 WAITING FOR GPS...")

# --- 8. FOOTER ---
st.markdown("---")
st.markdown(f"<div class='glossy-card' style='text-align:center;'>'อยู่นิ่งๆ ไม่เจ็บตัว'</div>", unsafe_allow_html=True)
