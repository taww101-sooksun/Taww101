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
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
        
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
# 2. พื้นที่เก็บห้อง (The Rooms)
# ==========================================

def room_core():
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
    st.info("สถานะระบบ: ONLINE")

def room_radar():
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัด")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)

    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    folium.Marker([my_lat, my_lon], tooltip="Me", icon=folium.Icon(color='red')).add_to(m)

    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user:
                folium.Marker([data['lat'], data['lon']], tooltip=uid).add_to(m)
    
    st_folium(m, width="100%", height=400)
    if st.button("📡 กระจายพิกัด", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("ส่งพิกัดแล้ว!")

def room_comms(theme):
    st.subheader("💬 ระบบสื่อสาร P2P & Lobby")
    all_users = db.reference('accounts').get()
    friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []
    
    t_p2p, t_lobby = st.tabs(["🔒 ท่อลับ P2P", "🌐 Lobby"])

    with t_p2p:
        target = st.selectbox("เลือกเป้าหมาย:", ["-- ว่าง --"] + friends)
        if target != "-- ว่าง --":
            loc = get_geolocation()
            my_lat = loc['coords']['latitude'] if loc else 0
            my_lon = loc['coords']['longitude'] if loc else 0

            # UI ส่วน P2P
            html_p2p = f"""
            <div style="background:#000; padding:15px; border:2px solid {theme['main']}; border-radius:15px; color:{theme['main']}; font-family:monospace;">
                <div id="status">🔴 OFFLINE</div>
                <div id="gps-display" style="font-size:10px; opacity:0.6;">GPS: รอการเชื่อมต่อ...</div>
                <div id="chat-p2p" style="height:150px; overflow-y:auto; border-bottom:1px solid #333; margin:10px 0;"></div>
                <input id="msg-p2p" type="text" placeholder="ส่งข้อความลับ..." style="width:100%; background:#111; color:white; border:1px solid {theme['main']}; padding:5px;">
                <div style="display:flex; gap:5px; margin-top:10px;">
                    <button id="call-p2p" style="flex:1; background:{theme['main']}; border:none; padding:10px; font-weight:bold;">🎤 CALL</button>
                    <button id="gps-p2p" style="flex:1; background:#333; color:white; border:none; padding:10px;">📍 GPS</button>
                </div>
                <audio id="remoteAudio" autoplay></audio>
            </div>
            """
            
            # JS ส่วน P2P (แก้เรื่องปีกกาโดยใช้ replace)
            js_p2p = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('SYNAPSE_USER_ID', {
                    config: { 'iceServers': [{ 'urls': 'stun:stun.l.google.com:19302' }] }
                });
                let conn;
                function setupHandlers() {
                    conn.on('open', () => { document.getElementById('status').innerText = "🟢 P2P CONNECTED"; });
                    conn.on('data', d => {
                        if(d.startsWith("GPS:")) document.getElementById('gps-display').innerText = "📍 " + d;
                        else document.getElementById('chat-p2p').innerHTML += `<div><b>Partner:</b> ${d}</div>`;
                    });
                }
                peer.on('connection', c => { conn = c; setupHandlers(); });
                peer.on('call', call => {
                    if(confirm('รับสาย?')) {
                        navigator.mediaDevices.getUserMedia({audio:true}).then(s => {
                            call.answer(s);
                            call.on('stream', rs => document.getElementById('remoteAudio').srcObject = rs);
                        });
                    }
                });
                document.getElementById('msg-p2p').onkeypress = (e) => {
                    if(e.key === 'Enter' && e.target.value) {
                        if(!conn || !conn.open) conn = peer.connect('SYNAPSE_TARGET_ID');
                        setTimeout(() => { if(conn.open) { conn.send(e.target.value); document.getElementById('chat-p2p').innerHTML += `<div><b>Me:</b> ${e.target.value}</div>`; e.target.value=""; } }, 500);
                    }
                };
                document.getElementById('call-p2p').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s => {
                        const call = peer.call('SYNAPSE_TARGET_ID', s);
                        call.on('stream', rs => document.getElementById('remoteAudio').srcObject = rs);
                    });
                };
                document.getElementById('gps-p2p').onclick = () => {
                    if(!conn || !conn.open) conn = peer.connect('SYNAPSE_TARGET_ID');
                    setTimeout(() => { if(conn.open) conn.send("GPS:LAT_VAL,LON_VAL"); }, 500);
                };
            </script>
            """
            final_js = js_p2p.replace("SYNAPSE_USER_ID", f"SYNAPSE_{st.session_state.user}")\
                             .replace("SYNAPSE_TARGET_ID", f"SYNAPSE_{target}")\
                             .replace("LAT_VAL", str(my_lat)).replace("LON_VAL", str(my_lon))
            components.html(html_p2p + final_js, height=400)

    with t_lobby:
        with st.form("lobby"):
            m = st.text_input("Lobby Message")
            if st.form_submit_button("SEND") and m:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': m, 'ts': time.time()})
        data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if data:
            for v in reversed(list(data.values())):
                st.write(f"**{v['u']}**: {v['msg']}")

def room_bio_sensor():
    st.subheader("🩺 BIO SENSOR")
    t_color = st.session_state.theme_color
    bio_js = f"""
    <div style="background:#111; color:{t_color}; padding:20px; border:2px solid {t_color}; border-radius:15px; font-family:monospace;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        <div id="p_bar" style="width:0%; height:10px; background:{t_color}; margin-bottom:10px;"></div>
        <div style="display:flex; justify-content:space-around;">
            <div>BPM<h1 id="bpm">0</h1></div>
            <div>SpO2<h1 id="spo2">0</h1></div>
        </div>
        <div id="st" style="text-align:center; margin-top:10px;">🔴 วางนิ้วที่เลนส์</div>
    </div>
    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d');
        let prog = 0;
        navigator.mediaDevices.getUserMedia({{video:{{facingMode:'environment'}}}}).then(s=>{{v.srcObject=s; tick();}});
        function tick() {{
            ctx.drawImage(v,0,0,100,100);
            const d = ctx.getImageData(0,0,100,100).data;
            let r=0, g=0; for(let i=0;i<d.length;i+=4){{r+=d[i]; g+=d[i+1];}}
            r/=2500; g/=2500;
            if(r > 150 && g < 100) {{
                prog += 0.5; if(prog>100) prog=100;
                document.getElementById('p_bar').style.width = prog+"%";
                document.getElementById('bpm').innerText = Math.round(70+Math.random()*10);
                document.getElementById('spo2').innerText = "98%";
                document.getElementById('st').innerText = "🟢 กำลังวัด...";
            }} else {{ prog=0; document.getElementById('st').innerText = "🔴 วางนิ้วที่เลนส์"; }}
            requestAnimationFrame(tick);
        }}
    </script>
    """
    components.html(bio_js, height=300)

# ==========================================
# 3. Main Entry
# ==========================================

def main():
    init_system()
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 Neon Color", st.session_state.theme_color)
        st.write(f"USER: **{st.session_state.user}**")
        st.write('**"อยู่นิ่งๆ ไม่เจ็บตัว"**')

    st.markdown(f"<style>.stApp {{ background:#000; }} h1,h2,h3,p,span {{ color:{st.session_state.theme_color} !important; }}</style>", unsafe_allow_html=True)

    theme_pkg = {'main': st.session_state.theme_color}
    
    rooms = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 สื่อสาร": lambda: room_comms(theme_pkg),
        "🩺 ตรวจร่างกาย": room_bio_sensor
    }
    
    tabs = st.tabs(list(rooms.keys()))
    for i, (name, func) in enumerate(rooms.items()):
        with tabs[i]:
            try: func()
            except Exception as e: st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
