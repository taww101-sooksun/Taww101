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
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & STYLING (นูน มีไฟ อยู่นิ่งๆไม่เจ็บตัว)
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(
        f"""
        <style>
        /* 1. พื้นหลัง Rainbow Flow */
        .stApp {{
            background: linear-gradient(270deg, #AFEEEE, #FF7F50, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
            background-size: 1600% 1600%;
            animation: RainbowFlow 60s ease infinite;
        }}
        @keyframes RainbowFlow {{
            0%{{background-position:0% 50%}}
            50%{{background-position:100% 50%}}
            100%{{background-position:0% 50%}}
        }}

        /* 2. เมนู Tabs แบบมีไฟนีออน */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            border-radius: 20px !important;
            padding: 10px !important;
            border: 2px solid {theme} !important;
            box-shadow: 0 0 15px {theme}88;
            margin: 10px 0px !important;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important;
            background-color: {theme}44 !important;
            border: 1px solid {theme} !important;
            box-shadow: 0 0 15px {theme} !important;
            transform: scale(1.05);
        }}

        /* 3. ปุ่มกดสไตล์ Matrix นูนมีไฟ */
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 2px solid {theme} !important;
            border-radius: 15px !important;
            filter: drop-shadow(0 0 5px {theme});
            transition: all 0.3s;
        }}
        div.stButton > button:hover {{
            transform: scale(1.02);
            box-shadow: 0 0 20px {theme};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def show_logo():
    """แสดง logo1.png พร้อมเอฟเฟกต์ไฟฟุ้ง"""
    theme = st.session_state.get('theme_color', "#1408BF")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo1.png"):
            with open("logo1.png", "rb") as f:
                data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div style="text-align:center; filter: drop-shadow(0 0 15px {theme}); margin-bottom: 20px;">
                    <img src="data:image/png;base64,{data}" style="width:100%; max-width:220px; border-radius:15px;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 15px {theme};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==========================================
# 1. UTILS & SYSTEM INIT
# ==========================================
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
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        if tz_str:
            return datetime.now(pytz.timezone(tz_str))
    except: pass
    return datetime.now(pytz.timezone('Asia/Bangkok'))

# ==========================================
# 2. ROOM MODULES
# ==========================================
def room_login():
    show_logo()
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_l, tab_r = st.tabs(["🔑 UNLOCK SYSTEM", "📝 REGISTER AGENT"])
        with tab_l:
            with st.form("login"):
                uid = st.text_input("AGENT ID")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{uid}').get()
                    if user_data and user_data.get('pw') == pw:
                        st.session_state.user = uid
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.error("ข้อมูลไม่ถูกต้อง")
        with tab_r:
            with st.form("reg"):
                new_id = st.text_input("NEW AGENT ID")
                new_pw = st.text_input("SET PASSWORD", type="password")
                if st.form_submit_button("CREATE ACCOUNT", use_container_width=True):
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")

def room_core(loc):
    st.subheader("🏠 CORE CONTROL อยู่นิ่งๆไม่เจ็บตัว 🇹🇭")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:30px; border:4px solid {st.session_state.theme_color}; border-radius:15px; background:rgba(0,0,0,0.5); box-shadow: 0 0 20px {st.session_state.theme_color}66;">
            <h1 style="font-size:5em; color:{st.session_state.theme_color}; margin:0; font-family: monospace;">{current_time.strftime('%H:%M:%S')}</h1>
            <p style="color:#FFF; letter-spacing: 2px;">📍 LAT: {lat:.4f} | LON: {lon:.4f}</p>
            <p style="color:{st.session_state.theme_color}; font-weight:bold;">AGENT {st.session_state.user} ONLINE</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC GPS")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star'), tooltip="YOU").add_to(m)
    
    # ดึงพิกัดเพื่อน
    try:
        users = db.reference('users').get()
        if users:
            for uid, data in users.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], icon=folium.Icon(color='green'), tooltip=uid).add_to(m)
    except: pass

    st_folium(m, width="100%", height=350)
    if st.button("📡 BROADCAST LOCATION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("ส่งพิกัดแล้ว")
def room_secure_chat():
    st.subheader("💬 SECURE CHAT (Low-Latency) 📝")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 เลือกผู้รับข้อความ:", friends, key="chat_target_select")
    
    if target:
        # สร้าง ID ห้องแชตโดยเรียงชื่อตามตัวอักษรเพื่อให้ทั้งสองฝั่งเข้าห้องเดียวกัน
        rid = "_".join(sorted([st.session_state.user, target]))
        
        # ส่วนแสดงข้อความ (ใช้ Container เพื่อให้ดูแยกส่วนชัดเจน)
        chat_container = st.container(height=350, border=True)
        
        # ดึงข้อความจาก Firebase
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(20).get()
        
        with chat_container:
            if chats:
                for c in chats.values():
                    is_me = c['u'] == st.session_state.user
                    align = "right" if is_me else "left"
                    color = st.session_state.theme_color if is_me else "#333"
                    st.markdown(f"""
                        <div style="text-align:{align}; margin-bottom:8px;">
                            <div style="display:inline-block; background:{color}; padding:8px 15px; border-radius:15px; color:white; max-width:80%;">
                                <small style="color:#aaa;">{c['u']}</small><br>{c['m']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("ยังไม่มีข้อความ... เริ่มคุยได้เลย")

        # ส่วนส่งข้อความ
        with st.form("send_msg_form", clear_on_submit=True):
            col_msg, col_btn = st.columns([4, 1])
            new_msg = col_msg.text_input("พิมพ์ข้อความ...", label_visibility="collapsed")
            if col_btn.form_submit_button("🚀 ส่ง", use_container_width=True):
                if new_msg:
                    db.reference(f'private_rooms/{rid}').push({
                        'u': st.session_state.user,
                        'm': new_msg,
                        'ts': time.time()
                    })
                    st.rerun() # บังคับ Refresh เพื่อให้ข้อความเด้งทันที
def room_audio_call():
    st.subheader("📞 SYNAPSE VOICE CALL (P2P)")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("เลือก AGENT ที่จะโทรหา (เสียง):", friends, key="voice_target")
    
    if target:
        st.info(f"🎤 กำลังรอเชื่อมต่อสายกับ {target}...")
        
        # HTML/JS สำหรับ PeerJS (เน้นเฉพาะ Audio)
        call_html = f"""
        <div style="background:rgba(0,0,0,0.8); padding:30px; border-radius:20px; border:3px solid {st.session_state.theme_color}; text-align:center;">
            <div id="status" style="color:{st.session_state.theme_color}; font-weight:bold; margin-bottom:20px;">READY TO CALL</div>
            
            <div style="display:flex; justify-content:center; gap:5px; height:50px; align-items:center;">
                <div style="width:5px; height:20px; background:{st.session_state.theme_color}; animation: wave 1s infinite;"></div>
                <div style="width:5px; height:40px; background:{st.session_state.theme_color}; animation: wave 0.8s infinite;"></div>
                <div style="width:5px; height:25px; background:{st.session_state.theme_color}; animation: wave 1.2s infinite;"></div>
            </div>

            <audio id="remoteAudio" autoplay></audio>
            
            <div style="margin-top:30px;">
                <button id="startCall" style="background:{st.session_state.theme_color}; color:white; padding:15px 30px; border:none; border-radius:50px; cursor:pointer; font-size:18px;">📞 โทรออก</button>
                <button onclick="location.reload()" style="background:#ff4444; color:white; padding:15px 30px; border:none; border-radius:50px; cursor:pointer; font-size:18px; margin-left:10px;">❌ วางสาย</button>
            </div>
        </div>

        <style>
            @keyframes wave {{
                0%, 100% {{ height: 10px; }}
                50% {{ height: 40px; }}
            }}
        </style>

        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <script>
            const peer = new Peer('{st.session_state.user}');
            const status = document.getElementById('status');
            const remoteAudio = document.getElementById('remoteAudio');

            // รับสาย
            peer.on('call', call => {{
                status.innerText = "INCOMING CALL...";
                navigator.mediaDevices.getUserMedia({{audio: true, video: false}}).then(stream => {{
                    call.answer(stream);
                    status.innerText = "CONNECTED (ON CALL)";
                    call.on('stream', remoteStream => {{
                        remoteAudio.srcObject = remoteStream;
                    }});
                }});
            }});

            // กดโทรออก
            document.getElementById('startCall').onclick = () => {{
                status.innerText = "CALLING...";
                navigator.mediaDevices.getUserMedia({{audio: true, video: false}}).then(stream => {{
                    const call = peer.call('{target}', stream);
                    status.innerText = "RINGING...";
                    call.on('stream', remoteStream => {{
                        status.innerText = "CONNECTED (ON CALL)";
                        remoteAudio.srcObject = remoteStream;
                    }});
                }});
            }};
        </script>
        """
        components.html(call_html, height=300)

def room_music():
    st.subheader("🎧 MUSIC STATION")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("ไม่พบไฟล์เพลง")
        return

    current_song = music_files[st.session_state.song_index]
    st.info(f"🎵 Playing: {current_song}")
    
    with open(current_song, "rb") as f:
        st.audio(f.read(), format="audio/mp3", autoplay=True)

    # Auto Next Script
    components.html("""
        <script>
        setInterval(() => {
            const audios = window.parent.document.querySelectorAll('audio');
            audios.forEach(a => {
                if (!a.dataset.listen) {
                    a.dataset.listen = "true";
                    a.onended = () => { 
                        const btns = window.parent.document.querySelectorAll('button');
                        for(let b of btns) if(b.innerText.includes('⏭️')) b.click();
                    };
                }
            });
        }, 2000);
        </script>
    """, height=0)

    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️ Prev", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if c2.button("🔄 Reload", use_container_width=True): st.rerun()
    if c3.button("⏭️ Next", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

# ==========================================
# 3. MAIN (จุดรวมร่าง)
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation() 

    if not st.session_state.get('logged_in', False):
        room_login()
        return

    # แสดงโลโก้ด้านบนสุดของทุกห้อง
    show_logo()

    with st.sidebar:
        st.title("SYNAPSE MENU")
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", "🎧 MUSIC", "⚙️ SETTINGS"])
    
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_secure_chat() # เรียกใช้ฟังก์ชันเดิมของท่านได้เลย
    with tabs[3]: room_call()        # เรียกใช้ฟังก์ชันเดิมของท่านได้เลย
    with tabs[4]: room_music()
    with tabs[5]: 
        st.session_state.theme_color = st.color_picker("ปรับแต่งสีระบบ (ไฟนีออน)", st.session_state.theme_color)
        if st.button("SAVE THEME"): st.rerun()

if __name__ == "__main__":
    main()
