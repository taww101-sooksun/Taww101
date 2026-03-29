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

# ==========================================
# 1. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

def save_log(action):
    try:
        now = datetime.utcnow() + timedelta(hours=7)
        # แก้ไข: ใช้ f-string ปกติ ไม่ต้องเบิ้ลปีกกาตรงนี้
        path = f'synapse_logs/{now.strftime("%Y-%m-%d")}'
        db.reference(path).push({
            'time': now.strftime("%H:%M:%S"),
            'action': action,
            'user': 'Ta101'
        })
    except: pass

# ==========================================
# 2. พื้นที่เก็บห้อง (The Rooms / Modules)
# ==========================================
def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.utcnow() + timedelta(hours=7) 

    seconds_since_midnight = (now.hour * 3600) + (now.minute * 60) + now.second
    day_percent = seconds_since_midnight / 86400
    
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        st.markdown(f"""
            <div style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 5px; text-align: center;">
                <h3 style="margin: 0; color: {st.session_state.theme_color}; font-family: monospace;">{now.strftime('%H:%M:%S')}</h3>
                <small style="color: {st.session_state.theme_color}; opacity: 0.8;">THAILAND TIME</small>
            </div>
        """, unsafe_allow_html=True)
        
    with col_t2:
        st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
        st.progress(min(day_percent, 1.0))
    
    st.markdown("---")
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **Ta101**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
    st.code(f"Time: {now.strftime('%H:%M:%S')}\nUser: Ta101\nStatus: Active\nLoc: Roi-Et 101")

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    start_lat, start_lon = 13.7367, 100.5231
    if loc:
        start_lat = loc['coords']['latitude']
        start_lon = loc['coords']['longitude']

    # แก้ไขจุดนี้: ห้ามเบิ้ลปีกกาใน tiles เพราะไม่ได้ใช้ f-string ครอบบรรทัดนี้
    google_satellite = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    
    m = folium.Map(location=[start_lat, start_lon], zoom_start=15, 
                   tiles=google_satellite, 
                   attr="Google Satellite")

    if all_users:
        for user_id, data in all_users.items():
            u_lat, u_lon = data.get('lat'), data.get('lon')
            u_ts = data.get('ts', 0)
            if u_lat and u_lon:
                is_active = (time.time() - u_ts) < 3600
                icon_color = 'red' if user_id == "Ta101" else ('green' if is_active else 'gray')
                folium.Marker([u_lat, u_lon], tooltip=f"{user_id}",
                              icon=folium.Icon(color=icon_color, icon='user', prefix='fa')).add_to(m)

    st_folium(m, width="100%", height=500)
    if loc:
        if st.button("📡 กระจายพิกัดของฉัน", use_container_width=True):
            db.reference('users/Ta101').update({'lat': start_lat, 'lon': start_lon, 'ts': time.time()})
            st.rerun()

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    chat_tabs = st.tabs(["🌐 Lobby", "🔐 Private"])
    with chat_tabs[0]:
        chat_ref = db.reference('public_chat')
        with st.form("public_form", clear_on_submit=True):
            msg = st.text_input("ส่งสัญญาณ...")
            if st.form_submit_button("SEND"):
                if msg: 
                    chat_ref.push({'user': 'Ta101', 'msg': msg, 'ts': time.time()})
                    st.rerun()
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")

def room_music():
    st.subheader("🎧 SYNAPSE ROOMS")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง")
        return
    current_song = music_files[st.session_state.song_index]
    st.audio(current_song, autoplay=True)
    for i, song in enumerate(music_files):
        if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()

def room_sensor():
    st.subheader("🎙️ เครื่องวัดคลื่นเสียงความจริง")
    theme_hex = st.session_state.theme_color
    # ส่วนนี้ใช้ f-string ต้องเบิ้ลปีกกา {{ }} สำหรับ JavaScript เท่านั้น
    audio_js = f"""
    <div style="background-color: #000; color: {theme_hex}; padding: 20px; border: 2px solid {theme_hex}; border-radius: 15px; text-align: center; font-family: monospace;">
        <h2 id="status">🔴 STANDBY</h2>
        <div style="display: flex; justify-content: space-around;">
            <div><h3>dB</h3><h1 id="db_val">0</h1></div>
            <div><h3>Hz</h3><h1 id="hz_val">0</h1></div>
        </div>
    </div>
    <script>
    async function startAudio() {{
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            if (audioContext.state === 'suspended') {{ await audioContext.resume(); }}
            const analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 256;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            function update() {{
                analyser.getByteFrequencyData(dataArray);
                let sum = 0, maxVal = 0, maxIdx = 0;
                for (let i = 0; i < bufferLength; i++) {{
                    sum += dataArray[i];
                    if (dataArray[i] > maxVal) {{ maxVal = dataArray[i]; maxIdx = i; }}
                }
                let db = Math.round((sum / bufferLength) * 3);
                let hz = Math.round(maxIdx * audioContext.sampleRate / analyser.fftSize);
                document.getElementById('db_val').innerText = db;
                document.getElementById('hz_val').innerText = hz;
                document.getElementById('status').innerText = db > 5 ? "🟢 SENSING" : "🟡 IDLE";
                requestAnimationFrame(update);
            }}
            update();
        }} catch (err) {{ 
            document.getElementById('status').innerText = "❌ ERROR: " + err.message; 
        }}
    }}
    window.addEventListener('click', () => {{ startAudio(); }}, {{ once: true }});
    startAudio();
    </script>
    """
    components.html(audio_js, height=250)

# ==========================================
# 3. แผงวงจรหลัก
# ==========================================
def main():
    init_system()
    # CSS ส่วนนี้ใช้ f-string ต้องเบิ้ลปีกกา {{ }}
    st.markdown(f"""
        <style>
        .stApp {{ 
            background-color: {st.session_state.bg_color} !important; 
            color: {st.session_state.text_color} !important; 
        }}
        .stButton>button {{ 
            border: 2px solid {st.session_state.theme_color} !important; 
            color: {st.session_state.theme_color} !important; 
            background: transparent !important; 
        }}
        h1, h2, h3, p, span, div, label {{ 
            color: {st.session_state.text_color} !important; 
        }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("✍️ ข้อความ", st.session_state.text_color)
        st.markdown("---")
        st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

    room_map = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 สื่อสาร": room_comms,
        "🎧 เพลง": room_music,
        "📟 วัดเสียง": room_sensor
    }
    
    tabs = st.tabs(list(room_map.keys()))
    for i, room_func in enumerate(room_map.values()):
        with tabs[i]:
            room_func()

if __name__ == "__main__":
    main()
