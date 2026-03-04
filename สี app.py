import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time, datetime, pytz
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME (ตั้งค่าเริ่มต้นและรีเฟรชหน้าจอ)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")
# รีเฟรชอัตโนมัติทุก 5 วินาที เพื่อให้แชตและพิกัดอัปเดตแบบ Real-time
st_autorefresh(interval=5000, key="global_refresh") 

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# --- SIDEBAR: การเข้าถึงและตั้งค่าส่วนตัว ---
with st.sidebar:
    st.markdown("### 🔐 ACCESS CONTROL")
    user_id = st.text_input("CODENAME:", value="Agent_001")
    # เลือกสีประจำตัว ซึ่งจะไปผูกกับสีข้อความแชตและสีหมุด GPS
    st.session_state.theme_color = st.color_picker("เลือกสีประจำตัว / สีหมุด", st.session_state.theme_color)
    
    st.write("---")
    st.write(f"USER: **{user_id}**")
    st.write(f"STATUS: **ONLINE**")
    st.write(f'**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"') # สโลแกนประจำตัวคุณ
    
    # นาฬิกาโลก
    st.markdown("---")
    st.markdown("### 🌍 WORLD CLOCK")
    zones = {'Bangkok': 'Asia/Bangkok', 'New York': 'America/New_York', 'London': 'Europe/London', 'Tokyo': 'Asia/Tokyo'}
    for city, zone in zones.items():
        t = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
        st.write(f"**{city}:** {t}")

# --- CSS CUSTOM STYLE (ปรับแต่งหน้าตาให้เป็นธีม Hacker/Neon) ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; }}
    .neon-text {{ 
        color: #fff; 
        text-shadow: 0 0 10px {st.session_state.theme_color}, 0 0 20px {st.session_state.theme_color};
        text-align: center; 
        font-weight: 900;
        border: 2px solid {st.session_state.theme_color}; 
        padding: 15px; 
        background: rgba(0,0,0,0.8);
        border-radius: 15px; 
        margin-bottom: 25px; 
        letter-spacing: 5px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        border: 1px solid {st.session_state.theme_color};
        padding: 10px 20px; border-radius: 10px 10px 0 0;
    }}
    .chat-msg {{ 
        border-left: 3px solid {st.session_state.theme_color}; 
        padding-left: 10px; 
        margin-bottom: 5px; 
        background-color: rgba(255,255,255,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGO & HEADER
# ==========================================
st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)

# ==========================================
# 3. FIREBASE CONNECTION
# ==========================================
# เช็กว่าเชื่อมต่อหรือยัง เพื่อป้องกัน Error การ Initialized ซ้ำซ้อน
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        # จัดการเรื่อง newline ใน private_key เพื่อป้องกัน Error ตอนอ่านค่าจาก TOML
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e:
        st.error(f"⚠️ DATABASE CONNECTION ERROR: {e}\n(กรุณาตรวจสอบไฟล์ .streamlit/secrets.toml)")

# ==========================================
# 4. MAIN MENU TABS
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS (แชต)", "📞 VOICE / VIDEO CALL"])

# --- [TAB 1: GPS & RADAR] ---
with tab_gps:
    col_map_ctrl, col_map_display = st.columns([1, 3])
    
    # ดึงพิกัดจากเบราว์เซอร์ (ต้องรันบน HTTPS หรือ Localhost เท่านั้นถึงจะขึ้น)
    loc = get_geolocation() 
    
    with col_map_ctrl:
        st.subheader("📡 ระบบระบุพิกัด")
        st.info(f"รหัสเรียกขาน: **{user_id}**") # ใช้ user_id จากระบบหลักของคุณ
        
        if st.button("🛰️ TRANSMIT MY LOCATION"):
            if loc and 'coords' in loc:
                try:
                    lat = loc['coords']['latitude']
                    lon = loc['coords']['longitude']
                    # บันทึกข้อมูลลง Firebase
                    db.reference(f'users/{user_id}').update({
                        'lat': lat, 
                        'lon': lon,
                        'color': st.session_state.theme_color,
                        'last_update': time.time()
                    })
                    st.success(f"ส่งพิกัดสำเร็จ! ({lat:.4f}, {lon:.4f})")
                    st.balloons()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ DB: {e}")
            else:
                st.warning("🚨 กรุณากด 'Allow' ให้เบราว์เซอร์เข้าถึงตำแหน่งของคุณ")

    with col_map_display:
        # ดึงข้อมูลทั้งหมดจาก Firebase มาเตรียมวาด Map
        all_users = db.reference('users').get()
        
        # 🎯 คำนวณจุดศูนย์กลางแผนที่: ถ้ามีตำแหน่งเรา ให้โฟกัสที่เรา ถ้าไม่มีให้ไปกรุงเทพฯ
        view_lat, view_lon = 13.75, 100.5 
        if all_users and user_id in all_users:
            view_lat = all_users[user_id].get('lat', 13.75)
            view_lon = all_users[user_id].get('lon', 100.5)

        # สร้างแผนที่แบบ Hybrid (เห็นพื้นผิวโลกจริงแบบอันแรกแต่คุมมู้ดให้เข้ากับ Dashboard)
        m = folium.Map(
            location=[view_lat, view_lon], 
            zoom_start=16, 
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
            attr="Google Satellite Hybrid"
        )

        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data and 'lon' in data:
                    # ถ้าเป็นตัวเราให้ใช้สีเขียว/น้ำเงินตาม Theme ถ้าคนอื่นให้ใช้สีที่เขาตั้งมา
                    u_color = data.get('color', '#FF0000') 
                    is_me = (name == user_id)
                    
                    folium.Marker(
                        location=[data['lat'], data['lon']],
                        tooltip=f"{'YOU' if is_me else 'AGENT'}: {name}",
                        icon=folium.Icon(
                            color='blue' if is_me else 'red', 
                            icon='user' if is_me else 'info-sign'
                        )
                    ).add_to(m)
                    # --- แก้ไขส่วน Circle ใน Loop ของคุณ ---
folium.Circle(
    location=[data['lat'], data['lon']],
    radius=50,
    color=u_color,
    fill=True,
    fill_opacity=0.2
).add_to(m) # <--- เช็กตรงนี้ว่ามี ) ครบ 2 อันไหม (อันหนึ่งปิด Circle อีกอันปิด add_to)


# --- [หัวใจสำคัญ: สั่ง Refresh อัตโนมัติทุก 10 วินาที] ---
# อยู่นิ่งๆ ไม่เจ็บตัว แต่แผนที่ต้องวิ่ง!
st_autorefresh(interval=10 * 1000, key="datarefresh") 

with tab_gps:
    col_map_ctrl, col_map_display = st.columns([1, 3])
    
    # ดึงพิกัดจาก Browser
    loc = get_geolocation() 
    
    with col_map_ctrl:
        st.subheader("📡 GPS CONTROL")
        if st.button("🛰️ TRANSMIT NOW"):
            if loc:
                # บันทึกพิกัดพร้อม Timestamp ปัจจุบัน
                now = time.time()
                db.reference(f'users/{user_id}').update({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'last_update': now
                })
                st.success(f"ส่งพิกัดแล้วตอน {time.strftime('%H:%M:%S', time.localtime(now))}")

    with col_map_display:
        # ดึงข้อมูลจาก Firebase (จะถูกดึงใหม่ทุก 10 วิจาก autorefresh)
        all_users = db.reference('users').get()
        
        # ตั้งค่า Center
        view_lat, view_lon = 13.75, 100.5
        if all_users and user_id in all_users:
            view_lat = all_users[user_id].get('lat')
            view_lon = all_users[user_id].get('lon')

        m = folium.Map(location=[view_lat, view_lon], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                       attr="Google Satellite")

        if all_users:
            for name, data in all_users.items():
                if 'lat' in data and 'lon' in data:
                    # คำนวณความสดใหม่ของข้อมูล (วินาที)
                    freshness = time.time() - data.get('last_update', 0)
                    
                    # ถ้าอัปเดตล่าสุดไม่เกิน 1 นาที ให้สีสด ถ้าเก่านานแล้วให้สีจาง (กันโดนหลอก)
                    u_color = 'blue' if name == user_id else 'red'
                    if freshness > 60: u_color = 'gray' 

                    folium.Marker(
                        [data['lat'], data['lon']], 
                        popup=f"{name} ({int(freshness)}s ago)",
                        icon=folium.Icon(color=u_color)
                    ).add_to(m)

        # 💡 ใช้ Key ผูกกับเวลาเพื่อให้ Map โหลดใหม่เมื่อมีการ Refresh
        st_folium(m, width="100%", height=500, key="radar_map_live")


# --- [TAB 2: COMMS / แชต] ---
with tab_chat:
    try:
        users_data = db.reference('users').get()
    except:
        users_data = {}
        
    target_list = ["🌐 Global Group"]
    if users_data:
        target_list += [u for u in users_data.keys() if u != user_id]
    
    col_chat1, col_chat2 = st.columns([1, 2])
    with col_chat1:
        target = st.selectbox("เลือกช่องทางสื่อสาร:", target_list)
        
    # กำหนด Path ใน Firebase ตามห้องที่เลือก
    if target == "🌐 Global Group":
        path = 'chats/global'
    else:
        room_id = "_".join(sorted([user_id, target]))
        path = f'chats/private/{room_id}'

    st.subheader(f"📟 Room: {target}")
    chat_container = st.container(height=350)
    
    try:
        # ดึงข้อความและเรียงตาม timestamp
        messages = db.reference(path).order_by_child('ts').get()
        if messages:
            # แปลงจาก OrderedDict เป็น List แล้วเรียงตาม ts (เพื่อความชัวร์ในการแสดงผลจริง)
            sorted_msgs = sorted(messages.values(), key=lambda x: x.get('ts', 0))
            for m in sorted_msgs:
                u_name = m.get('user', 'Unknown')
                u_msg = m.get('msg', '')
                # ถ้าเราเป็นคนพิมพ์ ใช้สีเรา ถ้าคนอื่น ใช้สีชมพูสะท้อนแสง
                txt_color = st.session_state.theme_color if u_name == user_id else "#ff00de"
                chat_container.markdown(f"<div class='chat-msg'><b style='color:{txt_color}'>{u_name}:</b> {u_msg}</div>", unsafe_allow_html=True)
    except Exception as e:
        chat_container.error("ยังไม่มีข้อความ หรือเชื่อมต่อฐานข้อมูลไม่ได้")

    # ฟอร์มส่งข้อความ
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            msg_input = st.text_input("TRANSMIT MESSAGE:", label_visibility="collapsed", placeholder="พิมพ์ข้อความที่นี่...")
        with col_btn:
            submit_btn = st.form_submit_button("SEND 🚀", use_container_width=True)
            
        if submit_btn and msg_input:
            try:
                db.reference(path).push({
                    'user': user_id, 
                    'msg': msg_input, 
                    'ts': time.time()
                })
                st.rerun() # รีโหลดหน้าเพื่อแสดงข้อความทันที
            except Exception as e:
                st.error("ส่งข้อความไม่สำเร็จ")

# --- [TAB 3: VOICE & VIDEO CALL] ---
with tab_call:
    st.markdown("### 📞 ระบบสื่อสารด้วยเสียงและภาพ (WebRTC Peer-to-Peer)")
    st.info("💡 ความจริง: กด 'Start' และเบราว์เซอร์จะขอสิทธิ์เข้าถึงกล้องและไมค์ของคุณ (ใช้งานได้ลื่นไหลสุดเมื่ออยู่บน Network เดียวกัน หรือมี TURN Server)")
    
    # ใช้งาน WebRTC ได้จริงตามคำสั่งนี้ (ใช้ Google STUN Server ฟรี)
    webrtc_streamer(
        key="synapse-vcall",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True}
    )

# ==========================================
# 5. FOOTER
# ==========================================
st.write("---")
st.caption(f"SYNAPSE SYSTEM v3.0 | Logged in as: {user_id} | อยู่นิ่งๆ ไม่เจ็บตัว 🤫")
