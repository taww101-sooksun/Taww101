import streamlit as st
import os 
import time
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. กลไกคำนวณ & ระบบพื้นฐาน
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # รัศมีโลก (กิโลเมตร)
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

# ==========================================
# 2. ROOM: แกนหลัก (Core Control)
# ==========================================
def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.now()
    st.markdown(f"""
        <div style="border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center;">
            <h2 style="margin: 0; color: {st.session_state.theme_color}; font-family: monospace;">{now.strftime('%H:%M:%S')}</h2>
            <p style="margin:0; color:gray;">STATUS: ONLINE | USER: {st.session_state.user}</p>
        </div>
    """, unsafe_allow_html=True)
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

# ==========================================
# 3. ROOM: เรดาร์ดาวเทียม & ระยะห่าง (Radar)
# ==========================================
def room_radar():
    st.subheader("🛰️ เรดาร์ระบุพิกัดจริง")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    my_lat, my_lon = 13.7367, 100.5231
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    folium.Marker([my_lat, my_lon], tooltip="คุณอยู่ที่นี่", icon=folium.Icon(color='red', icon='star')).add_to(m)

    if all_users:
        for uid, data in all_users.items():
            if uid == st.session_state.user: continue
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                is_active = (time.time() - data.get('ts', 0)) < 600
                color = 'green' if is_active else 'gray'
                folium.Marker([u_lat, u_lon], tooltip=f"{uid} ({dist:.2f} km)", 
                              icon=folium.Icon(color=color, icon='user', prefix='fa')).add_to(m)
                st.write(f"📍 **{uid}**: ห่างจากคุณ `{dist:.2f}` กม. ({'Active' if is_active else 'Offline'})")

    st_folium(m, width="100%", height=450)
    if loc and st.button("📡 กระจายพิกัดจริงลงดาวเทียม", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("พิกัดอัปเดตแล้ว!")

# ==========================================
# 4. ROOM: การสื่อสาร (Lobby & Video Call)
# ==========================================
def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t_lobby, t_video = st.tabs(["🌐 Lobby", "📹 Video Call"])
    
    with t_lobby:
        chat_ref = db.reference('public_chat')
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความ...")
            if st.form_submit_button("SEND") and msg:
                chat_ref.push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")

    with t_video:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("เลือกเป้าหมาย:", [""] + friends)
        if target:
            v_html = f"""
            <div style="background:#000; padding:10px; border:1px solid {st.session_state.theme_color}; border-radius:10px; text-align:center;">
                <video id="remoteV" autoplay playsinline style="width:100%; height:250px; background:#111;"></video>
                <video id="localV" autoplay playsinline muted style="width:80px; position:absolute; bottom:130px; right:30px; border:1px solid white;"></video>
                <button id="cBtn" style="width:100%; padding:10px; background:{st.session_state.theme_color}; font-weight:bold; cursor:pointer;">📹 CALL {target}</button>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('{st.session_state.user}');
                peer.on('call', c => {{
                    if(confirm('รับสาย?')) {{
                        navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{
                            document.getElementById('localV').srcObject=s; c.answer(s);
                            c.on('stream', rs => document.getElementById('remoteV').srcObject=rs);
                        }});
                    }}
                }});
                document.getElementById('cBtn').onclick = () => {{
                    navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{
                        document.getElementById('localV').srcObject=s;
                        const c = peer.call('{target}', s);
                        c.on('stream', rs => document.getElementById('remoteV').srcObject=rs);
                    }});
                }};
            </script>
            """
            components.html(v_html, height=400)

# ==========================================
# 5. ROOM: มัลติมีเดีย & เซนเซอร์ (Music & Sensor)
# ==========================================
def room_extras():
    st.subheader("🎧 เครื่องเล่น & 📟 เซนเซอร์")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("🎵 SYNAPSE Player")
        music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
        if music_files:
            st.audio(music_files[st.session_state.song_index])
            if st.button("Next Track ⏭️"):
                st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
                st.rerun()
        else: st.warning("ไม่พบไฟล์เพลง")

    with c2:
        st.write("🎙️ Audio Sensor")
        sensor_html = f"""
        <div style="background:#111; color:{st.session_state.theme_color}; padding:10px; border:1px solid {st.session_state.theme_color}; text-align:center;">
            <h1 id="db">0</h1><p>dB Level</p>
        </div>
        <script>
            navigator.mediaDevices.getUserMedia({{audio:true}}).then(s => {{
                const ctx = new AudioContext();
                const ana = ctx.createAnalyser();
                ctx.createMediaStreamSource(s).connect(ana);
                const data = new Uint8Array(ana.frequencyBinCount);
                function upd() {{
                    ana.getByteFrequencyData(data);
                    let sum = data.reduce((a,b) => a+b, 0);
                    document.getElementById('db').innerText = Math.round(sum/data.length);
                    requestAnimationFrame(upd);
                }}
                upd();
            }});
        </script>
        """
        components.html(sensor_html, height=150)

# ==========================================
# 6. แผงควบคุมหลัก (Main)
# ==========================================
def main():
    init_system()
    st.markdown(f"<style>.stApp {{ background-color: {st.session_state.bg_color} !important; color: white !important; }}</style>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 Theme Color", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 Background", st.session_state.bg_color)
        st.write(f"USER: **{st.session_state.user}**")

    menu = {"🚀 หลัก": room_core, "🛰️ เรดาร์": room_radar, "💬 สื่อสาร": room_comms, "🎧 พิเศษ": room_extras}
    tabs = st.tabs(list(menu.keys()))
    for i, func in enumerate(menu.values()):
        with tabs[i]: func()

if __name__ == "__main__":
    main()
