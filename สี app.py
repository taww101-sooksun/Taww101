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
from folium.features import DivIcon # เพิ่มการ Import ตัวนี้ไว้บนสุดของไฟล์ด้วยนะครับ

def room_radar():
    # ... (ส่วนดึงพิกัด my_lat, my_lon เดิม) ...

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles="OpenStreetMap")

    # 1. ปักหมุดตัวเรา + เขียนตัวหนังสือแปะไว้บนหัว
    folium.Marker(
        [my_lat, my_lon],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # --- ส่วนที่เพิ่ม: ตัวหนังสือบอกตำแหน่งแบบลอย (Static Text) ---
    folium.Marker(
        [my_lat - 0.0002, my_lon], # ขยับตำแหน่งตัวหนังสือลงมานิดนึงจะได้ไม่ทับหมุด
        icon=DivIcon(
            icon_size=(150,36),
            icon_anchor=(75,0),
            html=f'<div style="font-size: 12pt; color: red; font-weight: bold; text-align: center; background: rgba(255,255,255,0.7); border-radius: 5px; padding: 2px;">📍 ตำแหน่งของต๊ะ</div>',
        )
    ).add_to(m)

    # 2. ปักหมุดเพื่อน + เขียนชื่อเพื่อนและระยะห่างแปะไว้เลย
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user:
                    u_lat, u_lon = data.get('lat'), data.get('lon')
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        
                        # หมุดเพื่อน
                        folium.Marker([u_lat, u_lon], icon=folium.Icon(color='green')).add_to(m)
                        
                        # ตัวหนังสือบอกชื่อเพื่อนและระยะห่าง (ลอยค้างไว้เลย)
                        folium.Marker(
                            [u_lat - 0.0002, u_lon],
                            icon=DivIcon(
                                icon_size=(150,36),
                                icon_anchor=(75,0),
                                html=f'<div style="font-size: 10pt; color: green; font-weight: bold; text-align: center; background: rgba(255,255,255,0.7); border-radius: 5px; padding: 2px;">👤 {uid}<br>📏 {dist:.2f} km</div>',
                            )
                        ).add_to(m)
    except: pass

    st_folium(m, width="100%", height=500)
    
    # แสดงพิกัดเป็นข้อความใต้แผนที่อีกชั้นเพื่อความชัวร์
    st.info(f"🛰️ ระบบระบุตำแหน่ง: ขณะนี้คุณอยู่ที่ละติจูด {my_lat:.5f} ลองจิจูด {my_lon:.5f}")

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

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม (Satellite View)")
    
    # ดึงพิกัดปัจจุบัน
    loc = get_geolocation()
    if loc:
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
    else:
        my_lat, my_lon = 13.7367, 100.5231 # พิกัดสำรอง
        st.info("📡 กำลังซิงค์สัญญาณดาวเทียม...")

    # --- ส่วนสำคัญ: เปลี่ยนเป็นภาพถ่ายดาวเทียมแบบมีชื่อถนน (Hybrid) ---
    # ใช้ Google Maps Satellite Hybrid (เห็นทั้งภาพจริงและชื่อซอย)
    google_satellite_hybrid = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=18, # ซูมให้เห็นหลังคาบ้านแบบในรูป
        tiles=google_satellite_hybrid,
        attr='Google Maps Satellite'
    )
    
    # 🔴 ปักหมุดตัวเรา (สีแดง)
    folium.Marker(
        [my_lat, my_lon],
        popup="ตำแหน่งของคุณ",
        icon=folium.Icon(color='red', icon='user', prefix='fa')
    ).add_to(m)

    # 🟢 ดึงพิกัดเพื่อนและคำนวณระยะห่าง
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user:
                    u_lat, u_lon = data.get('lat'), data.get('lon')
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        
                        # ปักหมุดเพื่อน (สีเขียว หรือ ตามรูปอาจจะเป็นหมุดสีเทา/ขาว)
                        folium.Marker(
                            [u_lat, u_lon],
                            tooltip=f"{uid}: {dist:.2f} km",
                            icon=folium.Icon(color='lightgray', icon='info-sign')
                        ).add_to(m)
                        
                        # ลากเส้นเรดาร์เชื่อมโยง
                        folium.PolyLine(
                            [[my_lat, my_lon], [u_lat, u_lon]],
                            color=st.session_state.theme_color,
                            weight=2,
                            opacity=0.7,
                            dash_array='5, 10'
                        ).add_to(m)
    except: pass

    # แสดงผลแผนที่
    st_folium(m, width="100%", height=500)
    
    # ปุ่มส่งพิกัด
    if st.button("📡 แชร์ตำแหน่งปัจจุบันลงกลุ่ม", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.success("ส่งพิกัดเข้าสู่ระบบรวมกลุ่มแล้ว!")


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
    
    # 1. ตรวจสอบไฟล์เพลงในโฟลเดอร์
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในระบบ")
        return

    # 2. เลือกเพลงปัจจุบัน
    current_song = music_files[st.session_state.song_index]
    st.info(f"🎵 กำลังเล่น: {current_song} (ลำดับที่ {st.session_state.song_index + 1}/{len(music_files)})")

    # 3. ใช้ HTML5 Audio + JS เพื่อให้เล่นต่อเนื่อง (Auto-next)
    # เราจะแปลงไฟล์เป็น Base64 เพื่อให้ส่งเข้า Player ได้ชัวร์ๆ
    with open(current_song, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        mime = "audio/mp3"
        audio_url = f"data:{mime};base64,{b64}"

    # เทคนิค: ใส่ Event Listener 'ended' เมื่อเพลงจบให้กดปุ่ม 'ถัดไป' อัตโนมัติ
    audio_html = f"""
        <audio id="audio-player" controls autoplay style="width: 100%;">
            <source src="{audio_url}" type="{mime}">
        </audio>
        <script>
            var audio = document.getElementById('audio-player');
            audio.onended = function() {{
                // เมื่อเพลงจบ ให้ส่งสัญญาณไปที่ Streamlit เพื่อเปลี่ยนเพลง
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }};
        </script>
    """
    
    # ใช้ components เพื่อรัน HTML/JS
    result = components.html(audio_html, height=100)

    # 4. ส่วนควบคุมการเปลี่ยนเพลง
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ ก่อนหน้า"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    
    if col2.button("🔄 เริ่มใหม่"):
        st.rerun()

    if col3.button("⏭️ ถัดไป") or result == 'next':
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # 5. รายชื่อเพลงทั้งหมด (คลิกเลือกได้)
    st.write("---")
    with st.expander("📂 รายชื่อเพลงในคลัง"):
        for i, f in enumerate(music_files):
            if st.button(f"🎼 {f}", key=f"song_{i}", use_container_width=True):
                st.session_state.song_index = i
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
    init_system()
    loc = get_geolocation() 
    
    with st.sidebar:
        if os.path.exists("logo1.jpg"): st.image("logo1.jpg", use_container_width=True)
        else: st.markdown(f"<h2 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.session_state.logged_in:
            st.write(f"👤 AGENT: **{st.session_state.user}**")
            st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")
            if st.button("🚪 LOGOUT ออกจากระบบ", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

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
