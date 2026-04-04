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
        /* 1. พื้นหลังหลัก (เหมือนเดิม) */
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

        /* 2. แก้ไขเมนูห้อง (Tabs) ให้มีไฟและนูน */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.7) !important; /* พื้นหลังแถบเมนูเข้มขึ้นเพื่อให้ไฟชัด */
            border-radius: 20px !important;
            padding: 10px !important;
            gap: 10px !important;
            border: 2px solid {st.session_state.theme_color} !important;
            box-shadow: 0 0 15px {st.session_state.theme_color}88, inset 0 0 10px rgba(0,0,0,0.5) !important;
            margin: 10px 0px !important;
        }}

        /* ตัวอักษรในเมนู */
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            padding: 8px 16px !important;
            height: 50px !important;
            color: #BBBBBB !important; /* สีเทาอ่อนตอนยังไม่เลือก */
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            border: 1px solid transparent !important;
        }}

        /* เมนูห้องตอนที่ถูกเลือก (Selected Tab) */
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important; /* ตัวหนังสือขาวชัดเจน */
            background-color: {st.session_state.theme_color}44 !important;
            border: 1px solid {st.session_state.theme_color} !important;
            box-shadow: 0 0 15px {st.session_state.theme_color} !important; /* ไฟนีออนรอบเมนูที่เลือก */
            transform: scale(1.05); /* นูนออกมานิดนึง */
        }}

        /* เส้นใต้เมนูที่เลือก (ไฟวิ่งด้านล่าง) */
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: #FFFFFF !important;
            height: 4px !important;
            box-shadow: 0 0 10px #FFFFFF !important;
        }}

        /* 3. ปรับแต่งปุ่มทั่วไป (นูนมีไฟเหมือนเดิม) */
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 2px solid {st.session_state.theme_color} !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
            filter: drop-shadow(0 0 5px {st.session_state.theme_color});
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
    st.subheader("🛰️ STRATEGIC GPS - ระบบติดตามพิกัดเครือข่าย AGENT อยู่นิ้งๆไม่เจ็บตัว📡")
    
    # 1. พิกัดตัวเรา
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat = loc['coords'].get('latitude', my_lat)
        my_lon = loc['coords'].get('longitude', my_lon)
    
    # สร้าง Container แผนที่ให้นูนมีไฟ (เปิด div)
    st.markdown(f'<div style="border: 2px solid {st.session_state.theme_color}; border-radius: 15px; overflow: hidden; box-shadow: 0 0 20px {st.session_state.theme_color}88;">', unsafe_allow_html=True)
    
    # 2. สร้างแผนที่ดาวเทียม
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=15, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
        attr='Google Satellite'
    )
    
    # Marker ของตัวเรา (สีแดง)
    folium.Marker(
        [my_lat, my_lon], 
        icon=folium.Icon(color='red', icon='star'), 
        tooltip="YOU (ฉันเอง)"
    ).add_to(m)

    # ลูกเล่น: วงรัศมีเรดาร์รอบตัวเรา
    folium.Circle(
        location=[my_lat, my_lon],
        radius=1000,
        color=st.session_state.theme_color,
        fill=True,
        fill_color=st.session_state.theme_color,
        fill_opacity=0.1,
        weight=2
    ).add_to(m)
    
    # 3. ดึงข้อมูล AGENT คนอื่นๆ และลากเส้น
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data and 'lon' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    
                    # วาง Marker เพื่อน
                    folium.Marker(
                        [u_lat, u_lon], 
                        icon=folium.Icon(color='green', icon='info-sign'), 
                        tooltip=f"AGENT: {uid} | ห่าง: {dist:.2f} กม."
                    ).add_to(m)
                    
                    # ลากเส้นเชื่อมโยง
                    folium.PolyLine(
                        [[my_lat, my_lon], [u_lat, u_lon]], 
                        color=st.session_state.theme_color, 
                        weight=2, 
                        dash_array='10', 
                        opacity=0.6
                    ).add_to(m)
    except: pass
    
    # แสดงแผนที่
    st_folium(m, width="100%", height=250, returned_objects=[])
    
    # ปิด Container (สำคัญมาก!)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 4. ปุ่มส่งพิกัด (เพื่อให้เพื่อนเห็นเรา)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📡 BROADCAST MY LOCATION", key="btn_broadcast", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 
            'lon': my_lon, 
            'ts': time.time()
        })
        st.toast("ส่งพิกัดสำเร็จ! เพื่อนๆ จะเห็นคุณบนเรดาร์")
def room_camera():
    st.subheader("📷 AGENT SCANNER - ระบบบันทึกภาพสนาม")
    
    # ใช้ camera_input ซึ่งเป็น Widget มาตรฐานของ Streamlit ที่ใช้งานได้จริงทั้งคอมและมือถือ
    img_file = st.camera_input("TAKE A SNAPSHOT")

    if img_file:
        # แสดงรูปที่ถ่ายได้
        st.image(img_file, caption="PREVIEW", use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 UPLOAD TO CLOUD", use_container_width=True):
                try:
                    # แปลงไฟล์ภาพเป็น Base64 เพื่อเก็บใน Realtime Database (ตามโครงสร้างเดิมของคุณ)
                    bytes_data = img_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode()
                    
                    # ส่งข้อมูลเข้า Firebase
                    db.reference(f'gallery/{st.session_state.user}').push({
                        'u': st.session_state.user,
                        'img': base64_image,
                        'ts': time.time(),
                        'type': 'image/jpeg'
                    })
                    st.success("บันทึกภาพลงฐานข้อมูล SYNAPSE สำเร็จ!")
                except Exception as e:
                    st.error(f"การอัปโหลดขัดข้อง: {e}")
        
        with col2:
            st.download_button("💾 SAVE TO DEVICE", data=img_file, file_name=f"SYNAPSE_{int(time.time())}.jpg", mime="image/jpeg", use_container_width=True)

    # แสดงคลังภาพล่าสุดจาก AGENT คนอื่นๆ
    st.write("---")
    st.caption("🖼️ RECENT FIELD PHOTOS (GALLERY)")
    gallery = db.reference('gallery').get()
    if gallery:
        # รวมภาพจากทุก Agent มาแสดง
        for agent_id, photos in gallery.items():
            for p_id, p_data in list(photos.items())[-1:]: # ดึงรูปปัจจุบันรูปเดียวของแต่ละคนมาโชว์
                st.write(f"👤 จาก AGENT: {agent_id}")
                st.image(base64.b64decode(p_data['img']), width=300)


def room_call():
    st.subheader("📞 SYNAPSE P2P CALL อยู่นิ้งๆไม่เจ็บตัว")
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


# ==========================================
# 2. CORE MODULES (ปรับปรุงส่วน Music)
# ==========================================

def room_music():
    st.subheader("🎧 ระบบสถานีเพลงต่อเนื่อง (Non-Stop Station) อยู่นิ้งๆไม่เจ็บตัว🎙")
    
    # 1. ค้นหาไฟล์เพลง
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในระบบ")
        return

    # ตรวจสอบ index เพลง
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    if st.session_state.song_index >= len(music_files):
        st.session_state.song_index = 0

    current_song = music_files[st.session_state.song_index]
    st.info(f"🎵 กำลังเล่น: {current_song}")

    # 2. เล่นเพลง (Native Player)
    with open(current_song, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # 3. JS สำหรับ Auto-Next (แอบกดปุ่ม Next ให้เมื่อเพลงจบ)
    components.html(
        """
        <script>
        const autoNext = () => {
            const audios = window.parent.document.querySelectorAll('audio');
            audios.forEach(audio => {
                if (!audio.dataset.listener) {
                    audio.dataset.listener = "true";
                    audio.onended = () => {
                        const buttons = window.parent.document.querySelectorAll('button');
                        for (let btn of buttons) {
                            if (btn.innerText.includes('⏭️ Next')) {
                                btn.click();
                                break;
                            }
                        }
                    };
                }
            });
        };
        setInterval(autoNext, 2000);
        </script>
        """,
        height=0,
    )

    # 4. ปุ่มควบคุมหลัก (ใช้ Key ที่ชัดเจน)
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ Back", key="main_prev", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    
    if col2.button("🔄 Reload", key="main_reload", use_container_width=True):
        st.rerun()

    if col3.button("⏭️ Next", key="main_next", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # 5. รายชื่อเพลง (จุดที่เกิด Error - แก้ไขโดยใช้ key เฉพาะทาง)
    st.write("---")
    st.subheader("📂 รายชื่อเพลงทั้งหมด")
    for i, f_name in enumerate(music_files):
        is_playing = (i == st.session_state.song_index)
        label = f"▶️ {f_name}" if is_playing else f"🎵 {f_name}"
        
        # แก้ไขจุดนี้: ใช้ key="list_btn_{i}" เพื่อไม่ให้ซ้ำกับปุ่มอื่นแน่นอน
        if st.button(label, key=f"list_btn_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()
        

def room_secure_chat():
    st.subheader("💬 SECURE CHAT📝อยู่นิ้งๆไม่เจ็บตัว")
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
# 3. MAIN (ปรับปรุงตำแหน่งโลโก้และลำดับการรัน)
# ==========================================
def main():
    init_system()
    apply_custom_background()
    
    # ดึงพิกัด (ต้องดึงก่อนเริ่มเงื่อนไขอื่นเพื่อให้ loc พร้อมใช้งาน)
    loc = get_geolocation() 

    # 1. ตรวจสอบการ Login
    if not st.session_state.get('logged_in', False):
        room_login()
        return

    # 2. ส่วนที่แสดงเมื่อ Login แล้ว (โชว์โลโก้ทุกห้อง)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo1.jpg"):
            st.image("logo1.jpg", use_container_width=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

    # 3. Sidebar และเนื้อหาหลัก
    with st.sidebar:
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- ส่วนของ Tabs ในฟังก์ชัน main ---
    # บรรทัด 472 (ย่อหน้าปกติ)
        # บรรทัด 464 เดิม (เป็นตัวอย่างระดับย่อหน้าที่ถูก)
    with st.sidebar:
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        # ... โค้ดอื่นๆ ...

    # --- ส่วนของ Tabs ในฟังก์ชัน main (เลื่อนขวาให้ตรงกับ with st.sidebar) ---
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", "🎧 MUSIC", "⚙️ SETTINGS", "📷 SCANNER"])
    
    with tabs[0]:
        room_core(loc)
    with tabs[1]:
        room_radar(loc)
    with tabs[2]:
        room_secure_chat()
    with tabs[3]:
        room_call()
    with tabs[4]:
        room_music()
    with tabs[5]:
        st.session_state.theme_color = st.color_picker("ปรับแต่งสีระบบ", st.session_state.theme_color)
    with tabs[6]:
        room_camera()

if __name__ == "__main__":
    main()

