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
import hashlib

# ==========================================
# 1. CORE ENGINE & UTILS
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371 # รัศมีโลก (กม.)
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Error: {e}")

# ==========================================
# 2. ROOMS DEFINITION
# ==========================================

def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.now() + timedelta(hours=7)
    st.markdown(f"""
        <div style="border: 2px solid {st.session_state.theme_color}; padding: 20px; border-radius: 15px; text-align: center;">
            <h1 style="margin: 0; color: {st.session_state.theme_color}; font-family: monospace;">{now.strftime('%H:%M:%S')}</h1>
            <p style="color:gray;">SYSTEM ONLINE | AGENT: {st.session_state.user}</p>
            <hr style="border:0.5px solid {st.session_state.theme_color}; opacity:0.3;">
            <p style="font-style: italic;">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar():
    st.subheader("🛰️ เรดาร์ดาวเทียม (Real-time Tracker)")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    my_lat, my_lon = 13.7367, 100.5231 # Default BKK
    
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    # แผนที่ดาวเทียม Google Hybrid (จริงที่สุด)
    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")
    
    folium.Marker([my_lat, my_lon], tooltip="คุณ (Base)", icon=folium.Icon(color='red', icon='star')).add_to(m)

    if all_users:
        st.write("### 👥 ระยะห่างเพื่อนในเครือข่าย")
        for uid, data in all_users.items():
            if uid == st.session_state.user: continue
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                is_active = (time.time() - data.get('ts', 0)) < 600
                folium.Marker([u_lat, u_lon], tooltip=f"{uid}: {dist:.2f} km", 
                              icon=folium.Icon(color='green' if is_active else 'gray')).add_to(m)
                st.write(f"📍 **{uid}**: `{dist:.2f} กม.` ({'Active' if is_active else 'Offline'})")

    st_folium(m, width="100%", height=500)
    if loc and st.button("📡 กระจายพิกัดดาวเทียม", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.rerun()

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t_lobby, t_private, t_video = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว", "📹 วิดีโอคอล"])
    
    all_u = db.reference('users').get()
    friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []

    with t_lobby:
        with st.form("lobby_f", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความสาธารณะ...")
            if st.form_submit_button("📢 SEND") and msg:
                db.reference('public_chat').push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
        msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if msgs:
            for v in reversed(list(msgs.values())):
                st.write(f"🟢 **{v.get('user')}:** {v.get('msg')}")

    with t_private:
        target_p = st.selectbox("เลือกเพื่อนที่จะแชต:", [""] + friends, key="p_chat")
        if target_p:
            room_id = "_".join(sorted([st.session_state.user, target_p]))
            with st.form("priv_f", clear_on_submit=True):
                pm = st.text_input(f"ข้อความถึง {target_p}")
                if st.form_submit_button("🔒 SEND") and pm:
                    db.reference(f'private/{room_id}').push({'u': st.session_state.user, 'm': pm, 'ts': time.time()})
            p_msgs = db.reference(f'private/{room_id}').limit_to_last(10).get()
            if p_msgs:
                for v in reversed(list(p_msgs.values())):
                    st.write(f"👤 **{v.get('u')}:** {v.get('m')}")

    with t_video:
        target_v = st.selectbox("เลือกเพื่อนที่จะคอล:", [""] + friends, key="v_call")
        if target_v:
            v_html = f"""
            <div style="background:#000; padding:15px; border:2px solid {st.session_state.theme_color}; border-radius:15px; text-align:center;">
                <div style="position:relative; width:100%; height:300px; background:#111; border-radius:10px; overflow:hidden;">
                    <video id="rv" autoplay playsinline style="width:100%; height:100%; object-fit:cover;"></video>
                    <video id="lv" autoplay playsinline muted style="width:90px; position:absolute; bottom:10px; right:10px; border:1px solid white; border-radius:5px;"></video>
                </div>
                <button id="cb" style="width:100%; margin-top:10px; padding:15px; background:{st.session_state.theme_color}; color:black; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📹 CALL {target_v}</button>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('{st.session_state.user}');
                peer.on('call', c => {{
                    if(confirm('รับวิดีโอคอล?')) {{
                        navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{
                            document.getElementById('lv').srcObject=s; c.answer(s);
                            c.on('stream', rs => document.getElementById('rv').srcObject=rs);
                        }});
                    }}
                }});
                document.getElementById('cb').onclick = () => {{
                    navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{
                        document.getElementById('lv').srcObject=s;
                        const c = peer.call('{target_v}', s);
                        c.on('stream', rs => document.getElementById('rv').srcObject=rs);
                    }});
                }};
            </script>
            """
            components.html(v_html, height=480)

def room_music_sensor():
    st.subheader("🎧 เพลง & 📟 เซนเซอร์")
    c1, c2 = st.columns(2)
    with c1:
        st.write("💿 SYNAPSE Player")
        music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
        if music_files:
            st.audio(music_files[st.session_state.song_index])
            if st.button("Next Song ⏭️", use_container_width=True):
                st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
                st.rerun()
        else: st.warning("ไม่พบไฟล์ .mp3")

    with c2:
        st.write("🎙️ Audio Sensor")
        sensor_js = f"""
        <div style="background:#111; color:{st.session_state.theme_color}; padding:20px; border:1px solid {st.session_state.theme_color}; border-radius:15px; text-align:center;">
            <h1 id="db_v" style="font-size:3em; margin:0;">0</h1><p>dB Level</p>
        </div>
        <script>
            navigator.mediaDevices.getUserMedia({{audio:true}}).then(s => {{
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const ana = ctx.createAnalyser();
                ctx.createMediaStreamSource(s).connect(ana);
                const d = new Uint8Array(ana.frequencyBinCount);
                function upd() {{
                    ana.getByteFrequencyData(d);
                    let v = d.reduce((a,b)=>a+b,0)/d.length;
                    document.getElementById('db_v').innerText = Math.round(v * 2.5);
                    requestAnimationFrame(upd);
                }}
                upd();
            }}).catch(e => document.getElementById('db_v').innerText = "ERR");
        </script>
        """
        components.html(sensor_js, height=200)

# ==========================================
# 3. MAIN APP STRUCTURE
# ==========================================
def main():
    init_system()
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
        .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; }}
        h1, h2, h3, p, span, div, label {{ color: {st.session_state.text_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("✍️ ข้อความ", st.session_state.text_color)
        st.markdown("---")
        st.write(f"USER: **{st.session_state.user}**")
        st.write('**"อยู่นิ่งๆ ไม่เจ็บตัว"**')

    menu = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 สื่อสาร": room_comms,
        "🎧 พิเศษ": room_music_sensor
    }
    
    tabs = st.tabs(list(menu.keys()))
    for i, func in enumerate(menu.values()):
        with tabs[i]:
            func()

if __name__ == "__main__":
    main()
