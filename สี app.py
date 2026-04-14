import streamlit as st
import os 
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib

# นำเข้า MoviePy
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# ==========================================
# 1. CORE SYSTEM & THEME
# ==========================================
def init_system():
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'vdo_index' not in st.session_state: st.session_state.vdo_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def apply_theme():
    themes = {
        "Matrix":  {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF"},
        "Ocean":   {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC"},
        "Ember":   {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF"},
        "Rainbow": {"bg": "#FFFFFF", "main": "#FF69B4", "text": "#000000"}
    }
    t = themes.get(st.session_state.theme_set, themes["Matrix"])
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {t['bg']} !important; color: {t['text']} !important; }}
        .stButton>button {{ border: 2px solid {t['main']} !important; background: {t['main']} !important; color: {t['text']} !important; border-radius: 12px; }}
        h1, h2, h3, p, span {{ color: {t['text']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 2. RADAR & COMMS (GPS ดัก Error)
# ==========================================
def room_gps(theme):
    st.subheader("🛰️ SYNAPSE RADAR")
    loc = get_geolocation()
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        db.reference(f'locations/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')
        folium.Marker([lat, lon], icon=folium.Icon(color='red')).add_to(m)
        st_folium(m, width=700, height=400)
    else:
        st.info("📡 กำลังรอพิกัด... กรุณากด 'Allow' บนเบราว์เซอร์")

def room_comms():
    st.subheader("💬 LOBBY CHAT")
    msg = st.text_input("Message")
    if st.button("SEND") and msg:
        db.reference('public_chat').push({'u': st.session_state.user, 'msg': msg, 'ts': time.time()})
    data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
    if data:
        for v in reversed(list(data.values())):
            st.write(f"🟢 **{v.get('u')}**: {v.get('msg')}")

# ==========================================
# 3. MUSIC & VIDEO (แก้ปัญหาระบบฟอนต์)
# ==========================================
def room_music():
    st.subheader("🎧 MUSIC PLAYER")
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if songs:
        curr = songs[st.session_state.song_index]
        st.audio(curr)
        if st.button("⏭️ NEXT"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(songs)
            st.rerun()

def room_video():
    st.subheader("🎬 VIDEO ENGINE")
    videos = sorted([f for f in os.listdir('.') if f.endswith(".mp4") and not f.startswith("sync_")])
    if not videos: return st.warning("⚠️ ไม่พบไฟล์วิดีโอ")
    
    current_vdo = videos[st.session_state.vdo_index]
    st.info(f"🎞️ Selected: {current_vdo}")

    lyrics = [(1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา"), (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล")]

    if st.button("🚀 PROCESS (วิ้งๆ)"):
        with st.spinner("กำลังเสกวิดีโอ..."):
            try:
                clip = VideoFileClip(current_vdo)
                txt_clips = [clip]
                for s, e, txt in lyrics:
                    # แก้ปัญหา Unknown Format โดยใช้ฟอนต์ระบบ Linux แทนการดึงไฟล์ .ttf
                    t = TextClip(text=txt, font_size=50, color='yellow', 
                                 font='DejaVu-Sans-Bold', # ฟอนต์นี้ชัวร์ที่สุดบน Streamlit
                                 duration=(e-s), method='caption', size=(clip.w*0.8, None)
                                ).with_start(s).with_position(('center', 0.8*clip.h))
                    txt_clips.append(t)
                
                final = CompositeVideoClip(txt_clips)
                out = f"sync_{current_vdo}"
                final.write_videofile(out, fps=12, codec="libx264")
                st.video(out)
                st.success("✅ วิ้งแล้วครับ!")
            except Exception as e: st.error(f"❌ ระบบดื้อ: {e}")

# ==========================================
# 4. MAIN
# ==========================================
def main():
    init_system()
    if not st.session_state.auth_status:
        st.title("🛡️ SYNAPSE LOGIN")
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("ENTER"):
            acc = db.reference(f'accounts/{u}').get()
            if acc and acc.get('pw') == hash_pw(p):
                st.session_state.auth_status, st.session_state.user = True, u
                st.rerun()
        return

    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 Theme:", ["Matrix", "Ocean", "Ember", "Rainbow"])
        if st.button("🚪 LOGOUT"): st.session_state.auth_status = False; st.rerun()
    
    t = apply_theme()
    menu = {"🛰️ RADAR": lambda: room_gps(t), "💬 COMMS": room_comms, "🎧 MUSIC": room_music, "🎬 VIDEO": room_video}
    tabs = st.tabs(list(menu.keys()))
    for i, (name, func) in enumerate(menu.items()):
        with tabs[i]: func()

if __name__ == "__main__": main()
