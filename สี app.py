import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime

# --- จุดสำคัญ: ต้อง Import แบบนี้เท่านั้น ---
from streamlit_js_eval import get_geolocation 
def apply_custom_background():
    st.markdown(
        f"""
        <style>
        /* จัดการพื้นหลังหลักของแอป */
        .stApp {{
            background: linear-gradient(270deg, #AFEEEE, #FF7F50, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
            background-size: 1600% 1600%;
            animation: RainbowFlow 60s ease infinite;
        }}

        /* ตัวคุมการวิ่งของสี */
        @keyframes RainbowFlow {{
            0%{{background-position:0% 50%}}
            50%{{background-position:100% 50%}}
            100%{{background-position:0% 50%}}
        }}

        /* ปรับสีพื้นหลังของ Sidebar ให้โปร่งแสงเพื่อให้เห็นพื้นหลังวิ่งๆ */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }}

        /* ปรับพื้นหลังของ Tabs ให้ดูอ่านง่ายขึ้น */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        if timezone_str:
            local_tz = pytz.timezone(timezone_str)
            return datetime.now(local_tz)
    except: pass
    return datetime.now(pytz.timezone('Asia/Bangkok'))

# ==========================================
# 1. AUTHENTICATION
# ==========================================
def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; letter-spacing: 5px;'>SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
        tab_l, tab_r = st.tabs(["🔑 UNLOCK SYSTEM", "📝 REGISTER AGENT"])
        with tab_l:
            with st.form("login"):
                uid = st.text_input("AGENT ID ใสชื่อผู้ใช่")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{uid}').get()
                    if user_data and user_data.get('pw') == pw:
                        st.session_state.user = uid
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.error("รหัสผ่านไม่ถูกต้อง")
        with tab_r:
            with st.form("reg"):
                new_id = st.text_input("NEW AGENT ID")
                new_pw = st.text_input("SET PASSWORD", type="password")
                if st.form_submit_button("CREATE ACCOUNT", use_container_width=True):
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")

# ==========================================
# 2. CORE MODULES
# ==========================================
def room_core(loc):
    st.subheader("🏠 CORE CONTROL อยู่นิ้งๆไม่เจ็บตัว 🇹🇭")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat = loc['coords'].get('latitude', lat)
        lon = loc['coords'].get('longitude', lon)
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:30px; border:4px solid {st.session_state.theme_color}; border-radius:15px; background:rgba(0,0,0,0.3); box-shadow: 0 0 20px {st.session_state.theme_color}44;">
            <h1 style="font-size:5em; color:{st.session_state.theme_color}; margin:0; font-family: monospace;">{current_time.strftime('%H:%M:%S')}</h1>
            <p style="color:#888; letter-spacing: 2px;">📍 LAT: {lat:.4f} | LON: {lon:.4f}</p>
            <p style="color:{st.session_state.theme_color}; font-weight:bold;">AGENT {st.session_state.user} ONLINE</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat = loc['coords'].get('latitude', my_lat)
        my_lon = loc['coords'].get('longitude', my_lon)
    
    # --- เติมส่วนแผนที่ที่หายไป ---
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Satellite')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star'), tooltip="YOU").add_to(m)
    
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color='green', icon='info-sign'), tooltip=f"AGENT: {uid}").add_to(m)
                    folium.PolyLine([[my_lat, my_lon], [u_lat, u_lon]], color=st.session_state.theme_color, weight=1, dash_array='5', opacity=0.5).add_to(m)
    except: pass
    
    st_folium(m, width="100%", height=300)
    if st.button("📡 BROADCAST LOCATION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("พิกัดถูกส่งเข้าศูนย์บัญชาการแล้ว")

def room_call():
    st.subheader("📞 SYNAPSE P2P CALL")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("เลือก AGENT ที่จะโทรหา:", friends)
    if target:
        st.info(f"พร้อมเชื่อมต่อกับ {target} ผ่านเครือข่าย P2P")
        call_html = f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:4px solid {st.session_state.theme_color}; text-align:center;">
            <video id="remoteVideo" autoplay playsinline style="width:100%; height:300px; background:#000; border-radius:10px;"></video>
            <video id="localVideo" autoplay playsinline muted style="width:100px; position:absolute; bottom:30px; right:30px; border:2px solid {st.session_state.theme_color};"></video>
            <div style="margin-top:10px;">
                <button id="startCall" style="background:{st.session_state.theme_color}; color:black; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📞 START CALL</button>
                <button onclick="location.reload()" style="background:#ff4444; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">❌ DISCONNECT</button>
            </div>
        </div>
        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <script>
            const peer = new Peer('{st.session_state.user}');
            const localVideo = document.getElementById('localVideo');
            const remoteVideo = document.getElementById('remoteVideo');
            peer.on('call', call => {{
                navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                    localVideo.srcObject = stream;
                    call.answer(stream);
                    call.on('stream', remoteStream => {{ remoteVideo.srcObject = remoteStream; }});
                }});
            }});
            document.getElementById('startCall').onclick = () => {{
                navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                    localVideo.srcObject = stream;
                    const call = peer.call('{target}', stream);
                    call.on('stream', remoteStream => {{ remoteVideo.srcObject = remoteStream; }});
                }});
            }};
        </script>
        """
        components.html(call_html, height=450)


def room_music():
    st.subheader("🎧 ระบบสถานีเพลงต่อเนื่อง (Non-Stop Station)")
    
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในระบบ")
        return

    # ตรวจสอบ index เพลง
    if st.session_state.song_index >= len(music_files):
        st.session_state.song_index = 0

    current_song = music_files[st.session_state.song_index]
    
    # แสดงข้อมูลเพลงปัจจุบัน
    st.info(f"🎵 กำลังเล่น: {current_song}")

    # เล่นเพลงด้วย Streamlit Native Player (เสถียรกว่า Base64 ในตัวแปร)
    with open(current_song, "rb") as audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # --- หัวใจสำคัญ: JS ตัวนี้จะแอบดักฟัง Audio Player ของ Streamlit ---
    # ถ้าเพลงจบ มันจะไปคลิกปุ่ม Next ให้เราเอง
    components.html(
        """
        <script>
        window.parent.document.querySelectorAll('audio').forEach(audio => {
            audio.onended = function() {
                // หาปุ่ม "⏭️ Next" ในหน้าจอแล้วสั่งคลิก
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.innerText.includes('⏭️ Next')) {
                        btn.click();
                        break;
                    }
                }
            };
        });
        </script>
        """,
        height=0,
    )

    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ Back", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    
    if col2.button("🔄 Reload", use_container_width=True):
        st.rerun()

    if col3.button("⏭️ Next", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()


def room_secure_chat():
    st.subheader("💬 SECURE CHAT")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 เลือกผู้รับข้อความ:", friends)
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความที่นี่...")
            up = st.file_uploader("ส่งรูปภาพ/วิดีโอ", type=['jpg', 'png', 'mp4'])
            if st.form_submit_button("SEND MESSAGE"):
                f_data, f_type = (base64.b64encode(up.read()).decode(), up.type) if up else (None, None)
                db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'f': f_data, 'ft': f_type, 'ts': time.time()})
                st.rerun()
        
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        if chats:
            for c in reversed(list(chats.values())):
                align = "right" if c['u'] == st.session_state.user else "left"
                color = st.session_state.theme_color if c['u'] == st.session_state.user else "#333"
                st.markdown(f'<div style="text-align:{align}; margin-bottom:10px;"><div style="display:inline-block; background:{color}; padding:10px; border-radius:10px; color:white;"><b>{c["u"]}</b>: {c["m"]}</div></div>', unsafe_allow_html=True)
                if c.get('f'):
                    try:
                        dec = base64.b64decode(c['f'])
                        if "image" in c['ft']: st.image(dec, width=250)
                        elif "video" in c['ft']: st.video(dec)
                    except: pass

# ==========================================
# 3. MAIN
# ==========================================
def main():
    # ... (ส่วนเช็ค Login เหมือนเดิม) ...

    # วางไว้ตรงนี้ จะโชว์อยู่เหนือ Tabs ทุกห้อง
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            st.image("logo1.jpg", width=250) # ปรับขนาดตามเหมาะสม
        except: pass


    if not st.session_state.logged_in:
        room_login()
        return

    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", "🎧 MUSIC", "⚙️ SETTINGS"])
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_secure_chat()
    with tabs[3]: room_call()
    with tabs[4]: room_music()
    with tabs[5]: 
        st.session_state.theme_color = st.color_picker("ปรับแต่งสีระบบ", st.session_state.theme_color)

if __name__ == "__main__":
    main()
