import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
import time
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CORE SYSTEM CONFIGURATION (NEON THEME)
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# ตกแต่ง UI แบบฉบับกองบัญชาการ ปุ่มเยอะ ลวดลายจัดเต็ม
st.markdown("""
    <style>
    /* พื้นหลังและฟอนต์สไตล์ Hacker Dark Mode */
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    
    /* หัวข้อหลักแบบเรืองแสงสะท้อนแสง */
    .neon-header { 
        font-size: 55px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #ff00de;
        border: 4px double #00f2fe; padding: 20px; background: rgba(0,0,0,0.8);
        border-radius: 20px; margin-bottom: 30px;
    }
    
    /* ปุ่มกดสไตล์ Futuristic พร้อมเอฟเฟกต์ */
    div.stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #000 50%, #ff00de 100%);
        color: white !important; border: 2px solid #fff; border-radius: 5px;
        height: 50px; font-weight: bold; width: 100%; transition: 0.5s;
        box-shadow: 0 0 10px #00f2fe;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 30px #ff00de; transform: scale(1.02);
    }
    
    /* กล่องข้อความแชทสีฟ้า/แดง */
    .bubble-me { background: rgba(0, 242, 254, 0.15); border: 1px solid #00f2fe; padding: 12px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; color: #fff; }
    .bubble-others { background: rgba(255, 71, 71, 0.15); border: 1px solid #ff4747; padding: 12px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; color: #fff; }
    
    /* กรอบข้อมูลลวดลาย Terminal */
    .terminal-container {
        border: 1px solid #00f2fe; padding: 20px; border-radius: 10px;
        background: rgba(0, 242, 254, 0.05); border-left: 8px solid #00f2fe;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUTOMATIC HIDDEN AUDIO (27 MINS)
# ==========================================
# ลิงก์ตรงจาก Google Drive (ความจริงคือไฟล์ ID 1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a)
direct_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"

st.components.v1.html(f"""
    <audio id="synapse-audio" loop autoplay style="display:none;">
        <source src="{direct_link}" type="audio/mpeg">
    </audio>
    <script>
        var audio = document.getElementById("synapse-audio");
        audio.volume = 0.5;
        // ปลดล็อกการเล่นอัตโนมัติเมื่อมีการสัมผัสหน้าจอ 1 ครั้ง
        window.parent.document.addEventListener('click', function() {{
            audio.play();
        }}, {{ once: true }});
    </script>
""", height=0)

# ==========================================
# 3. FIREBASE INFRASTRUCTURE
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
    except Exception as e:
        st.error(f"SYSTEM_ERROR: {e}")

# ==========================================
# 4. SIDEBAR : CONTROL CENTER
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>CONTROL CENTER</h2>", unsafe_allow_html=True)
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🎵 AUDIO FREQUENCY")
    # ตัวเล่นเพลงสำรองใน Sidebar เผื่อ Browser บล็อก
    st.audio(direct_link, format="audio/mpeg", loop=True)
    st.caption("STATUS: STREAMING (27 MINS)")
    
    st.markdown("---")
    st.markdown("### 🛡️ QUICK COMMANDS")
    st.button("🔍 SCAN NETWORK")
    st.button("🔐 ENCRYPT ALL")
    st.button("📡 PING SATELLITE")
    st.markdown("---")
    st.write(f"SYSTEM UPTIME: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ==========================================
# 5. MAIN INTERFACE (TABS 1-7)
# ==========================================
st.markdown('<div class="neon-header">S Y N A P S E _ O V E R L O R D</div>', unsafe_allow_html=True)

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 DATA LOG", "🔐 SECURITY", "📺 MEDIA", "🧹 SYSTEM"])

# --- TAB 1: CORE (IDENTIFICATION) ---
with tabs[0]:
    st.markdown('<div class="terminal-container"><h3>[ PROTOCOL_IDENTIFICATION ]</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Guest'))
    
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 
                'lon': loc['coords']['longitude'],
                'gps_time': local_time,
                'status': 'ACTIVE'
            })
            st.success("GLOBAL POSITIONING SYNCHRONIZED.")
        else:
            st.warning("PLEASE ENABLE GPS TO PROCEED.")

# --- TAB 2: RADAR (GLOBAL MAP) ---
with tabs[1]:
    st.markdown('<div class="terminal-container"><h3>[ GLOBAL_SURVEILLANCE_RADAR ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    if users:
        # แผนที่โลกแบบละเอียด (Global Fix)
        m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                # สีกำหนดตัวตน
                m_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker(
                    [info['lat'], info['lon']], 
                    popup=f"<b>User:</b> {name}<br><b>Time:</b> {info.get('gps_time')}",
                    icon=folium.Icon(color=m_color, icon='info-sign')
                ).add_to(m)
        st_folium(m, width="100%", height=600)

# --- TAB 3: COMMS (CHAT & CALL) ---
with tabs[2]:
    st.markdown('<div class="terminal-container"><h3>[ ENCRYPTED_COMM_PROTOCOL ]</h3></div>', unsafe_allow_html=True)
    
    # 3.1 VIDEO CALL (WebRTC)
    st.markdown("#### 📹 SATELLITE VIDEO FEED")
    webrtc_streamer(
        key="synapse-vcall",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True}
    )
    
    st.markdown("---")
    
    # 3.2 SECURE CHAT (สีฟ้า-แดง)
    col_u, col_c = st.columns([1, 2])
    with col_u:
        st.write("📡 ONLINE NODES")
        if users:
            for f_name in users.keys():
                if f_name != st.session_state.my_name:
                    if st.button(f"CONNECT TO {f_name}", key=f"btn-{f_name}"):
                        pair = sorted([st.session_state.my_name, f_name])
                        st.session_state.private_room = f"sec_{pair[0]}_{pair[1]}"
                        st.session_state.target_name = f_name
                        st.rerun()

    with col_c:
        room = st.session_state.get('private_room')
        target = st.session_state.get('target_name')
        if room:
            st.write(f"🔒 SECURE CHANNEL: {target}")
            chat_ref = db.reference(f'chats/{room}')
            msg_input = st.chat_input("TRANSMIT MESSAGE...")
            if msg_input:
                chat_ref.push({'name': st.session_state.my_name, 'msg': msg_input, 'ts': time.time()})
            
            msgs = chat_ref.order_by_child('ts').limit_to_last(15).get()
            if msgs:
                for m_id in msgs:
                    d = msgs[m_id]
                    is_me = d.get('name') == st.session_state.my_name
                    style = "bubble-me" if is_me else "bubble-others"
                    align = "right" if is_me else "left"
                    st.markdown(f"<div style='text-align:{align};'><div class='{style}' style='display:inline-block;'><small>{d.get('name')}</small><br>{d.get('msg')}</div></div>", unsafe_allow_html=True)

# --- TAB 4: DATA LOG ---
with tabs[3]:
    st.markdown('<div class="terminal-container"><h3>[ METADATA_ANALYSIS ]</h3></div>', unsafe_allow_html=True)
    if users:
        st.json(users)
    if st.button("🗑️ CLEAR ACCESS LOGS (ถังขยะ)"):
        db.reference('users').delete()
        st.rerun()

# --- TAB 5: SECURITY ---
with tabs[4]:
    st.markdown('<div class="terminal-container"><h3>[ SECURITY_OVERRIDE ]</h3></div>', unsafe_allow_html=True)
    st.write("สถานะการเข้ารหัส: **AES-256 BIT ACTIVE**")
    st.progress(100, "SIGNAL INTEGRITY")
    st.code("QUANTUM_KEY: SH-256-X99-SYNPSE-ALPHA", language="text")

# --- TAB 6: MEDIA ---
with tabs[5]:
    st.markdown('<div class="terminal-container"><h3>[ VISUAL_STREAMS ]</h3></div>', unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=f0h8PjdZzrw") # ตัวอย่างวิดีโอเท่ๆ

# --- TAB 7: SYSTEM (TRASH & RESET) ---
with tabs[6]:
    st.markdown('<div class="terminal-container"><h3>[ KERNEL_DESTRUCTION ]</h3></div>', unsafe_allow_html=True)
    st.error("🚨 DANGER: FACTORY DATA RESET")
    if st.button("💣 WIPE ALL CHATS (ล้างแชท)"):
        db.reference('chats').delete()
        st.success("ประวัติแชทถูกลบเรียบร้อย!")
    if st.button("🧼 FULL FACTORY RESET (ล้างเครื่อง)"):
        db.reference('/').delete()
        st.error("ข้อมูลทั้งหมดในฐานข้อมูลถูกล้างเรียบร้อย!")
