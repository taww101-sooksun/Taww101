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
from datetime import datetime, date
import math
import random
from streamlit_js_eval import get_geolocation 

# ==========================================
# 4. UPDATED CSS - เพิ่มความหนาขอบแบบจัดเต็ม
# ==========================================
def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(f"""
        <style>
        /* ขอบเมนูหลัก (Tabs) - ปรับให้ใหญ่และฟุ้ง */
        .stTabs [data-baseweb="tab-list"] {{
            border: 8px solid {theme} !important; 
            box-shadow: 0 0 50px {theme} !important;
            border-radius: 30px !important;
            background: rgba(0,0,0,0.9) !important;
        }}

        /* ขอบปุ่มกด - หนาและมีมิติ */
        div.stButton > button {{
            border: 5px solid {theme} !important;
            box-shadow: 0 0 20px {theme}88;
            font-size: 1.2rem !important;
            padding: 15px 30px !important;
        }}

        /* กล่องเนื้อเพลง / กล่องข้อมูล - ขอบหนาพิเศษ */
        .lyrics-box {{
            background: rgba(0, 0, 0, 0.7);
            border: 6px solid #00ff41; /* ขอบเขียว Matrix หนาๆ */
            border-radius: 25px;
            padding: 25px;
            color: #00ff41;
            font-family: 'Courier New', Courier, monospace;
            box-shadow: 0 0 35px rgba(0, 255, 65, 0.4);
            line-height: 1.8;
            text-align: center;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 5. MUSIC & LYRICS MODULE
# ==========================================
def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    
    # ส่วนแสดงเนื้อเพลงที่ท่านส่งมา
    lyrics = """
    (อยู่นิ่งๆ ไม่เจ็บตัว… Let’s go!)
    
    เริ่มที่หน้า LOGIN ใส่ AGENT ID เข้ามา
    ตั้งรหัสให้ดี อย่าให้ใครเห็นด้วยสายตา
    ถ้ายังไม่มี ก็ REGISTER สร้างตัวตน
    เข้าสู่ระบบความปลอดภัย ในโลกที่สับสน
    
    📍 มองไปที่ CORE เห็นเวลาและพิกัด
    ทุกอย่างมันชัดเจน ระบบเราน่ะคัดจัด!
    
    เลื่อนไปที่แถบเมนู ไฟนีออนมันสะท้อนตา
    ทุกฟีเจอร์ที่เราสร้างมา เพื่อให้คุณได้นำพา… Connection
    
    🔥 SYNAPSE ในมือคุณ จังหวะเบสกระแทกใจ
    RADAR ส่องพิกัด เพื่อนอยู่ไหนเรารู้ไป
    CHAT กันให้สุด ส่งรูปวิดีโอได้ทันที
    หรือจะ CALL แบบ P2P เสียงชัดแจ๋วเลย Baby
    
    (อยู่นิ่งๆ ไม่เจ็บตัว.!)
    """
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="lyrics-box">', unsafe_allow_html=True)
        st.write("### 📜 LYRICS")
        st.text(lyrics) # หรือใช้ st.markdown ถ้าต้องการใส่สี
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # ระบบเล่นเพลง
        files = sorted([f for f in os.listdir('.') if f.endswith(".mp3") or f.endswith(".mp4")])
        if files:
            song = st.selectbox("💿 SELECT TRACK", files)
            if song.endswith(".mp3"):
                st.audio(song, format="audio/mp3")
            else:
                st.video(song)
                
            st.markdown(f"""
                <div style="margin-top:20px; padding:20px; border:4px dashed {st.session_state.theme_color}; border-radius:15px; text-align:center;">
                    <h4 style="color:{st.session_state.theme_color};">NOW PLAYING:</h4>
                    <p style="font-size:1.5em; font-weight:bold;">{song}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("กรุณาตรวจสอบไฟล์ .mp3 หรือ .mp4 ในโฟลเดอร์")

# อย่าลืมเรียกใช้ในฟังก์ชัน main() นะครับ

def show_logo():
    theme = st.session_state.get('theme_color', "#1408BF")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo1.png"):
            with open("logo1.png", "rb") as f:
                data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div style="text-align:center; filter: drop-shadow(0 0 15px {theme}); margin-bottom: 25px;">
                    <img src="data:image/png;base64,{data}" style="width:100%; max-width:240px; border-radius:20px;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 15px {theme};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==========================================
# 1. UTILS & CALCULATION LOGIC
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def get_reality_logic(dt):
    """สูตรคำนวณรหัสคู่ขนานตามวันที่"""
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        res = math.sqrt((day_val**2) + (m_num**2))
        phase = f"ขึ้น {m_num} ค่ำ"
    else:
        m_num = int(pos - 14.765) + 1
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        phase = f"แรม {m_num} ค่ำ"
    return {"res": round(res, 4), "phase": phase}

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        return datetime.now(pytz.timezone(tz_str)) if tz_str else datetime.now()
    except: return datetime.now()

# ==========================================
# 2. CORE MODULES
# ==========================================
if os.path.exists("synapse.mp4"):
    st.video("synapse.mp4")
else:
    st.warning("⚠️ ไม่พบไฟล์วิดีโอ synapse.mp4")

def room_login():
    show_logo()
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="logic-box" style="text-align:center; border-color:#1408BF;">', unsafe_allow_html=True)
        tab_l, tab_r = st.tabs(["🔑 UNLOCK เข้าสู่ระบบ", "📝 NEW AGENT ลงทะเบียนก่อนเข้าระบบ"])
        with tab_l:
            with st.form("login_form"):
                uid = st.text_input("AGENT ID")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{uid}').get()
                    if user_data and user_data.get('pw') == pw:
                        st.session_state.user = uid
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.error("ACCESS DENIED: ข้อมูลไม่ถูกต้อง")
        with tab_r:
            with st.form("reg_form"):
                new_id = st.text_input("CREATE ID")
                new_pw = st.text_input("CREATE PASSWORD", type="password")
                if st.form_submit_button("REGISTER", use_container_width=True):
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("AGENT REGISTERED!")
        st.markdown('</div>', unsafe_allow_html=True)

def room_core(loc):
    st.subheader("🏠 CORE CONTROL - อยู่นิ่งๆไม่เจ็บตัว")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:40px; border:4px solid {st.session_state.theme_color}; border-radius:25px; background:rgba(0,0,0,0.6); box-shadow: 0 0 30px {st.session_state.theme_color}88;">
            <h1 style="font-size:6em; color:{st.session_state.theme_color}; margin:0; font-family: 'Courier New'; text-shadow: 0 0 20px {st.session_state.theme_color};">
                {current_time.strftime('%H:%M:%S')}
            </h1>
            <p style="color:#FFF; font-size:1.2em; letter-spacing: 4px;">DATE: {current_time.strftime('%Y-%m-%d')}</p>
            <hr style="border-color:{st.session_state.theme_color}; opacity:0.3;">
            <p style="color:#00ff41; font-family:monospace;">📍 POSITION: {lat:.5f}, {lon:.5f}</p>
            <p style="color:{st.session_state.theme_color}; font-weight:bold; font-size:1.5em;">AGENT {st.session_state.user} IS ONLINE</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR SCANNER")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Satellite')
    
    # Marker เรา
    folium.Marker([my_lat, my_lon], 
                  icon=folium.Icon(color='red', icon='screenshot', prefix='fa'),
                  tooltip="MY POSITION").add_to(m)
    
    # วงรัศมี
    folium.Circle([my_lat, my_lon], radius=400, color="#00ff41", fill=True, opacity=0.1).add_to(m)

    # ดึงพิกัด AGENTS อื่นๆ
    try:
        users = db.reference('users').get()
        if users:
            for uid, data in users.items():
                if uid != st.session_state.user and 'lat' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    folium.Marker([u_lat, u_lon], 
                                  icon=folium.Icon(color='blue', icon='user', prefix='fa'),
                                  tooltip=f"AGENT: {uid} | DIST: {dist:.2f} km").add_to(m)
                    folium.PolyLine([[my_lat, my_lon], [u_lat, u_lon]], color=st.session_state.theme_color, weight=1, dash_array='5').add_to(m)
    except: pass

    st_folium(m, width="100%", height=450)
    
    if st.button("📡 BROADCAST MY SIGNAL", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("SIGNAL BROADCASTED TO NETWORK")

def room_reality_scanner():
    st.subheader("🧬 Reality Extractor & Code Scanner")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.write("### 🔍 สแกนรหัสส่วนบุคคล")
        dob = st.date_input("เลือกวันเกิด / วันเหตุการณ์", value=date.today())
        if dob:
            logic = get_reality_logic(dob)
            st.metric("REALITY CODE", logic['res'])
            st.write(f"**สภาวะ:** {logic['phase']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="logic-box" style="border-color:#1408BF;">', unsafe_allow_html=True)
        st.write("### 🛰️ ตรวจสอบพิกัดรหัสคู่ขนาน")
        u1_date = st.date_input("AGENT 1 (วันเกิด)", value=date(1996, 8, 17))
        u2_date = st.date_input("AGENT 2 (วันเกิด)", value=date.today())
        if st.button("COMPUTE GAP"):
            r1 = get_reality_logic(u1_date)['res']
            r2 = get_reality_logic(u2_date)['res']
            gap = abs(r1 - r2)
            st.write(f"CODE 1: `{r1}` | CODE 2: `{r2}`")
            st.subheader(f"RESULT GAP: {gap:.4f}")
            if gap <= 1.0: st.success("ระดับความสัมพันธ์: แนบแน่นพิเศษ")
            elif gap <= 4.0: st.warning("ระดับความสัมพันธ์: รหัสสะท้อน (คู่ขนาน)")
            else: st.error("ระดับความสัมพันธ์: แรงผลักดัน")
        st.markdown('</div>', unsafe_allow_html=True)

def room_secure_chat():
    st.subheader("💬 SECURE REAL-TIME MESSENGER")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 SELECT TARGET AGENT:", friends)
    
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        chat_container = st.container(height=150, border=True)
        
        # Load Messages
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(25).get()
        
        with chat_container:
            if chats:
                for c in chats.values():
                    is_me = c['u'] == st.session_state.user
                    align = "right" if is_me else "left"
                    bg = st.session_state.theme_color if is_me else "#222"
                    st.markdown(f"""
                        <div style="text-align:{align}; margin-bottom:12px;">
                            <div style="display:inline-block; background:{bg}; padding:10px 18px; border-radius:18px; color:white; border:1px solid rgba(255,255,255,0.1);">
                                <small style="opacity:0.6;">{c['u']}</small><br>{c['m']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.caption("No communication history found.")

        with st.form("msg_form", clear_on_submit=True):
            c_input, c_btn = st.columns([4, 1])
            msg = c_input.text_input("Enter Message...", label_visibility="collapsed")
            if c_btn.form_submit_button("SEND", use_container_width=True):
                if msg:
                    db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                    st.rerun()

def room_voice_call():
    st.subheader("📞 P2P ENCRYPTED VOICE CALL")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("CALL TO:", friends, key="v_call_target")
    
    if target:
        st.markdown(f"""
            <div style="background:#000; padding:30px; border-radius:20px; border:2px solid {st.session_state.theme_color}; text-align:center; box-shadow: 0 0 20px {st.session_state.theme_color}55;">
                <h2 style="color:{st.session_state.theme_color};">VOICE CHANNEL ACTIVE</h2>
                <audio id="remoteAudio" autoplay></audio>
                <div style="margin: 20px 0;">
                    <div style="width:100px; height:100px; border-radius:50%; border:5px solid {st.session_state.theme_color}; display:inline-block; animation: pulse 1.5s infinite;"></div>
                </div>
                <button id="startCall" style="background:{st.session_state.theme_color}; color:white; padding:12px 30px; border:none; border-radius:10px; cursor:pointer;">START CALL</button>
                <button onclick="location.reload()" style="background:red; color:white; padding:12px 30px; border:none; border-radius:10px; cursor:pointer; margin-left:10px;">HANG UP</button>
            </div>
            <style> @keyframes pulse {{ 0%{{box-shadow:0 0 0 0 {st.session_state.theme_color}aa;}} 70%{{box-shadow:0 0 0 20px rgba(0,0,0,0);}} 100%{{box-shadow:0 0 0 0 rgba(0,0,0,0);}} }} </style>
            
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('{st.session_state.user}');
                peer.on('call', call => {{
                    navigator.mediaDevices.getUserMedia({{audio: true, video: false}}).then(s => {{
                        call.answer(s);
                        call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                    }});
                }});
                document.getElementById('startCall').onclick = () => {{
                    navigator.mediaDevices.getUserMedia({{audio: true, video: false}}).then(s => {{
                        const call = peer.call('{target}', s);
                        call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                    }});
                }};
            </script>
        """, unsafe_allow_html=True)

def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not files:
        st.warning("⚠️ No MP3 files detected in root directory.")
        return

    song = files[st.session_state.song_index]
    st.info(f"🎶 NOW STREAMING: {song}")
    
    with open(song, "rb") as f:
        st.audio(f.read(), format="audio/mp3", autoplay=True)

    # UI Controls
    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️ PREVIOUS", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(files)
        st.rerun()
    if c2.button("🔄 REFRESH", use_container_width=True): st.rerun()
    if c3.button("⏭️ NEXT", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(files)
        st.rerun()

# ==========================================
# 3. MAIN CONTROLLER
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation() 

    if not st.session_state.get('logged_in', False):
        room_login()
        return

    show_logo()

    # Sidebar Settings
    with st.sidebar:
        st.markdown(f"### 👤 AGENT: {st.session_state.user}")
        st.caption("Status: AUTHENTICATED")
        st.write("---")
        st.session_state.theme_color = st.color_picker("🎨 SYSTEM THEME (Neon)", st.session_state.theme_color)
        if st.button("🚪 LOGOUT SYSTEM", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.write("---")
        st.write("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    # Main Navigation
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC"])
    
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_reality_scanner()
    with tabs[3]: room_secure_chat()
    with tabs[4]: room_voice_call()
    with tabs[5]: room_music()

if __name__ == "__main__":
    main()
