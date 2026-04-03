import streamlit as st
import os 
import random
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib
from math import radians, cos, sin, asin, sqrt

# ==========================================
# 0. ฟังก์ชันสนับสนุน (Helper Functions)
# ==========================================

def haversine(lat1, lon1, lat2, lon2):
    """
    คำนวณระยะห่างระหว่าง 2 พิกัดบนผิวโลก (หน่วย: กิโลเมตร)
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 
    return c * r

# ==========================================
# 1. กลไกกลาง (Core Engine)
# ==========================================

def init_system():
    # ตั้งค่า Session State เริ่มต้น
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
        
    # เชื่อมต่อ Firebase
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

# ==========================================
# 2. พื้นที่เก็บห้อง (The Rooms / Modules)
# ==========================================

def room_core():
    """
    ห้องแกนกลาง: แสดงเวลาและสถานะระบบ
    """
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.utcnow() + timedelta(hours=7) 
    seconds_since_midnight = (now.hour * 3600) + (now.minute * 60) + now.second
    day_percent = seconds_since_midnight / 84600
    
    st.markdown(f"""
        <div style="border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; background: rgba(0,0,0,0.5);">
            <h1 style="margin: 0; color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; font-size: 3em;">{now.strftime('%H:%M:%S')}</h1>
            <p style="color: {st.session_state.theme_color}; opacity: 0.8; letter-spacing: 2px;">SYNAPSE STANDBY</p>
        </div>
    """, unsafe_allow_html=True)
        
    st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
    st.progress(min(day_percent, 1.0))
    st.markdown("---")
    st.info("สถานะระบบ: ONLINE (CONNECTED TO SATELLITE)")
    st.write(f"รหัสผู้ใช้งาน: **{st.session_state.user}**")
    st.write(f"สโลแกน: **'อยู่นิ่งๆ ไม่เจ็บตัว'**")


def room_radar():
    """
    ห้องเรดาร์: ตรวจจับพิกัดและระยะห่างเพื่อนในทีม
    """
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัดและระยะห่าง")
    
    map_mode = st.radio("🗺️ โหมดแผนที่:", ["ดาวเทียม", "ถนนปกติ", "Dark Mode"], horizontal=True)
    tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" 
    if map_mode == "ถนนปกติ":
        tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    elif map_mode == "Dark Mode":
        tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    my_lat, my_lon = 13.7367, 100.5231 # พิกัด Default (กทม.)
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles=tile_url, attr="SYNAPSE Strategic Map")

    folium.Circle(
        location=[my_lat, my_lon],
        radius=500,
        color=st.session_state.theme_color,
        fill=True,
        fill_opacity=0.1,
        tooltip="เขตรัศมี 500 เมตร"
    ).add_to(m)

    folium.Marker(
        [my_lat, my_lon], 
        tooltip="ตำแหน่งของคุณ", 
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)

    if all_users:
        st.write("### 👥 รายงานสถานะพิกัดเป้าหมาย")
        col1, col2 = st.columns(2)
        
        for index, (uid, data) in enumerate(all_users.items()):
            if uid == st.session_state.user: continue
            
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                avg_speed = 40 
                eta_mins = (dist / avg_speed) * 60
                is_active = (time.time() - data.get('ts', 0)) < 600
                
                with (col1 if index % 2 == 0 else col2):
                    color_status = "🟢" if is_active else "⚪"
                    st.write(f"{color_status} **{uid}**: `{dist:.2f} กม.` | ⏳ `{int(eta_mins)} นาที`")
                
                folium.Marker(
                    [u_lat, u_lon], 
                    tooltip=f"{uid} (ห่าง {dist:.2f} km)", 
                    icon=folium.Icon(color='green' if is_active else 'gray', icon='user', prefix='fa')
                ).add_to(m)

                folium.PolyLine(
                    [[my_lat, my_lon], [u_lat, u_lon]], 
                    color=st.session_state.theme_color, 
                    weight=1, 
                    opacity=0.4, 
                    dash_array='5'
                ).add_to(m)

    st_folium(m, width="100%", height=500)
    
    if st.button("📡 กระจายพิกัดเข้าศูนย์บัญชาการ", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("ส่งพิกัดเข้าดาวเทียมเรียบร้อย!")
        st.rerun()


def room_comms():
    """
    ห้องสื่อสาร: แชทโลกและวิดีโอคอลแบบ Peer-to-Peer
    """
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    chat_tabs = st.tabs(["🌐 Lobby (แชท)", "📹 Video Call"])
    
    with chat_tabs[0]:
        chat_ref = db.reference('public_chat')
        with st.form("public_form", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("SEND"):
                if msg: 
                    chat_ref.push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
                    st.rerun()
        
        msgs = chat_ref.order_by_key().limit_to_last(15).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")

    with chat_tabs[1]:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("เลือกเป้าหมายที่จะคอล:", [""] + friends)
        
        if target:
            call_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#000; padding:15px; border-radius:15px; border:2px solid %s; text-align:center;">
                <div style="position:relative; width:100%%; height:300px; background:#111; border-radius:10px; overflow:hidden; margin-bottom:10px;">
                    <video id="remoteVideo" autoplay playsinline style="width:100%%; height:100%%; object-fit:cover;"></video>
                    <video id="localVideo" autoplay playsinline muted style="position:absolute; bottom:10px; right:10px; width:100px; border:2px solid %s; border-radius:5px;"></video>
                </div>
                <p style="color:white; font-size:0.8em;">ID: <b>%s</b> | กำลังเชื่อมต่อ: <b>%s</b></p>
                <div style="display:flex; gap:10px;">
                    <button id="callBtn" style="flex:1; padding:12px; background:%s; color:black; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📹 CALL</button>
                    <button id="hangupBtn" onclick="location.reload()" style="flex:0.5; padding:12px; background:#ff4444; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">❌ วางสาย</button>
                </div>
            </div>
            <script>
                const peer = new Peer('%s');
                const localVideo = document.getElementById('localVideo');
                const remoteVideo = document.getElementById('remoteVideo');

                peer.on('call', call => {
                    if(confirm("มีสายเรียกเข้า... รับหรือไม่?")) {
                        navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
                            localVideo.srcObject = stream;
                            call.answer(stream);
                            call.on('stream', remStream => { remoteVideo.srcObject = remStream; });
                        });
                    }
                });

                document.getElementById('callBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
                        localVideo.srcObject = stream;
                        const call = peer.call('%s', stream);
                        call.on('stream', remStream => { remoteVideo.srcObject = remStream; });
                    });
                };
            </script>
            """ % (st.session_state.theme_color, st.session_state.theme_color, st.session_state.user, target, st.session_state.theme_color, st.session_state.user, target)
            components.html(call_html, height=450)

