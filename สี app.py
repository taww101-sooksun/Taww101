import streamlit as st
import os 
import time
import base64
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib

# นำเข้า MoviePy สำหรับระบบวิดีโอ
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# ==========================================
# 1. CORE SYSTEM & AUTHENTICATION
# ==========================================
def init_system():
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'vdo_index' not in st.session_state: st.session_state.vdo_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None
    if 'active_target' not in st.session_state: st.session_state.active_target = None 

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def apply_theme():
    themes = {
        "Matrix":  {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF", "chat_user": "#39FF14", "chat_friend": "#333"},
        "Ocean":   {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC", "chat_user": "#00A8E8", "chat_friend": "#005F73"},
        "Ember":   {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF", "chat_user": "#FF4D4D", "chat_friend": "#990000"},
        "Rainbow": {"bg": "#FFFFFF", "main": "#FF69B4", "text": "#000000", "chat_user": "#FFB6C1", "chat_friend": "#E0FFFF"}
    }
    t = themes.get(st.session_state.theme_set, themes["Matrix"])
    bg_style = f"background-color: {t['bg']} !important;"
    if st.session_state.theme_set == "Rainbow":
        bg_style = "background: linear-gradient(135deg, #FF99CC, #99CCFF, #99FFCC) !important;"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} color: {t['text']} !important; }}
        .stButton>button {{ border: 2px solid {t['main']} !important; color: {t['text']} !important; background: {t['main']} !important; border-radius: 12px; font-weight: bold; width: 100%; }}
        h1, h2, h3, p, span, label, .stMarkdown, .stMetric {{ color: {t['text']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 2. GPS RADAR
# ==========================================
def room_gps(theme):
    st.subheader("🛰️ SYNAPSE RADAR SYSTEM")
    st.components.v1.html(f"""
        <div style="background:rgba(0,0,0,0.5); padding:10px; border-radius:10px; border:1px solid {theme['main']};">
            <h3 style="color:{theme['main']}; margin:0; font-family:monospace;">🕒 SYSTEM TIME: <span id="clock">00:00:00</span></h3>
        </div>
        <script>setInterval(() => {{ document.getElementById('clock').innerText = new Date().toLocaleTimeString('th-TH'); }}, 1000);</script>
    """, height=70)
    
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        db.reference(f'locations/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        m = folium.Map(location=[lat, lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', attr='Google Satellite')
        folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
        st_folium(m, width=700, height=400)
    else: st.warning("📡 ค้นหาสัญญาณดาวเทียม...")

# ==========================================
# 3. COMMUNICATION
# ==========================================
def room_comms(theme):
    st.subheader("💬 ศูนย์กลางการสื่อสาร")
    t_lobby, t_private = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว"])
    
    with t_lobby:
        m = st.text_input("พิมพ์ข้อความ...")
        if st.button("📢 SEND") and m:
            db.reference('public_chat').push({'u': st.session_state.user, 'msg': m, 'ts': time.time()})
        data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if data:
            for v in reversed(list(data.values())): st.write(f"🟢 **{v.get('u')}**: {v.get('msg')}")

# ==========================================
# 4. MUSIC & VIDEO ENGINE
# ==========================================
def room_music():
    st.subheader("🎧 SYNAPSE PLAYER")
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if songs:
        curr = songs[st.session_state.song_index]
        st.info(f"💿 Track: {curr}")
        st.audio(curr)
        if st.button("⏭️ NEXT SONG"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(songs)
            st.rerun()

def room_video(theme):
    st.subheader("🎬 VIDEO LYRIC ENGINE")
    videos = sorted([f for f in os.listdir('.') if f.endswith(".mp4") and not f.startswith("sync_")])
    if not videos: return st.warning("⚠️ ไม่พบไฟล์วิดีโอ")
    
    current_vdo = videos[st.session_state.vdo_index]
    st.info(f"🎞️ Selected: {current_vdo}")

    # Timeline ความจริงที่เพื่อนให้มา
    lyrics = [
        (1.0, 10.0, "วันหนึ่งถ้าเธมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
        (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีต"),
        (26.0, 60.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง")
    ]

    if st.button("🚀 PROCESS VIDEO (วิ้งๆ)"):
        f_path = os.path.abspath("THSarabunNew.ttf")
        with st.spinner("กำลังประกอบร่างวิดีโอ..."):
            try:
                base = VideoFileClip(current_vdo)
                txt_clips = [base]
                for s, e, txt in lyrics:
                    t = TextClip(text=txt, font_size=50, color='yellow', font=f_path, 
                                 duration=(e-s), method='caption', size=(base.w*0.8, None)
                                ).with_start(s).with_position(('center', 0.8*base.h))
                    txt_clips.append(t)
                
                final = CompositeVideoClip(txt_clips)
                out = f"sync_{current_vdo}"
                final.write_videofile(out, fps=12, codec="libx264")
                st.video(out)
            except Exception as e: st.error(f"❌ Error: {e}")
    
    if st.button("⏭️ NEXT VIDEO"):
        st.session_state.vdo_index = (st.session_state.vdo_index + 1) % len(videos)
        st.rerun()

# ==========================================
# MAIN EXECUTION
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
    menu = {"🛰️ RADAR": lambda: room_gps(t), "💬 COMMS": lambda: room_comms(t), "🎧 MUSIC": room_music, "🎬 VIDEO": lambda: room_video(t)}
    tabs = st.tabs(list(menu.keys()))
    for i, (name, func) in enumerate(menu.items()):
        with tabs[i]: func()

if __name__ == "__main__": main()
