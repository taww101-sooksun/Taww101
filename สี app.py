import streamlit as st
# --- 1. ชื่อมสถานะ (หัวใจหลัก) ---# --- เริ่มรันระบบ ---
setup_ui()          # เรียกใช้หน้าตา
init_firebase()     # เชื่อมฐานข้อมูล
music_url = play_audio() # สั่งเปิดเพลง

# แสดงส่วนหัว (Logo + Clocks)
# ... โค้ดส่วนหัว ...

# สร้าง Tabs แล้วส่งไปให้ฟังก์ชัน render_tabs จัดการ
main_tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOG", "🔐 SEC", "📺 MEDIA", "🧹 SYS"])
render_tabs(main_tabs, music_url)

if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME" # หน้าแรก

# --- 2. ฟังก์ชันวาดกรอบ (UI Style) ---def setup_ui():
    st.markdown("""
        <style>
        .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
        .neon-header { 
            font-size: 40px; font-weight: 900; text-align: center;
            color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
            border: 10px double #ff1744; padding: 20px; border-radius: 20px;
        }
        /* ... (โค้ด CSS อื่นๆ ที่เหลือ) ... */
        </style>
    """, unsafe_allow_html=True)
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import os
import time
import pandas as pd
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh
from geopy.distance import geodesic # ต้องใช้เพื่อคำนวณระยะทางจริง

# ==========================================
# 1. CORE SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

direct_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 40px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
        border: 10px double #ff1744; padding: 20px; background: rgba(0,0,0,0.85);
        border-radius: 20px; margin-bottom: 30px;
    }
    .terminal-container {
        border: 1px solid rgba(0, 242, 254, 0.5); padding: 20px; border-radius: 10px;
        background: rgba(0, 5, 15, 0.9); border-left: 8px solid #00f2fe;
    }
    .clock-box { background: rgba(0, 242, 254, 0.1); border: 1px solid #00f2fe; padding: 10px; border-radius: 10px; text-align: center; }
    .bubble-me { background: rgba(0, 242, 254, 0.15); border: 2px solid #00f2fe; padding: 12px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; }
    .bubble-others { background: rgba(255, 23, 68, 0.15); border: 2px solid #ff1744; padding: 12px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE (เชื่อมต่อจริงจาก KEY ของคุณ)
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# ดึงข้อมูลทั้งหมดมาเตรียมไว้ (ของจริง 100%)
users_data = db.reference('users').get()

# ==========================================
# 3. UI HEADER & CLOCKS
# ==========================================
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2: st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><small>{city}</small><br><b style='color:#ff1744;'>{now}</b></div>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN INTERFACE (TABS)
# ==========================================
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 10-UNITS", "🔐 SECURITY", "📺 MEDIA", "🧹 SYSTEM"])

# --- TAB 1: CORE (ระบบยืนยันตัวตนจริง) ---
with tabs[0]:
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Agent_Unknown'))
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            db.reference(f'users/{st.session_state.my_name}').update({
                'lat': loc['coords']['latitude'], 
                'lon': loc['coords']['longitude'],
                'status': 'ACTIVE',
                'last_seen': time.time()
            })
            st.success("GLOBAL POSITIONING SYNCHRONIZED.")

# --- TAB 2: RADAR (แผนที่จริง) ---
with tabs[1]:
    m = folium.Map(location=[13.75, 100.5], zoom_start=4, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    if users_data:
        for name, info in users_data.items():
            if 'lat' in info:
                f_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker([info['lat'], info['lon']], tooltip=name, icon=folium.Icon(color=f_color)).add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS (แชทจริง) ---
with tabs[2]:
    msg_input = st.chat_input("ส่งข้อความถึงกองบัญชาการ...")
    if msg_input: db.reference('global_chat').push({'name': st.session_state.my_name, 'msg': msg_input, 'ts': time.time()})
    raw_msgs = db.reference('global_chat').get()
    if raw_msgs:
        for d in sorted(raw_msgs.values(), key=lambda x: x.get('ts', 0))[-10:]:
            align = "right" if d['name'] == st.session_state.my_name else "left"
            style = "bubble-me" if d['name'] == st.session_state.my_name else "bubble-others"
            st.markdown(f"<div style='text-align:{align};'><div class='{style}' style='display:inline-block;'><small>{d['name']}</small><br>{d['msg']}</div></div>", unsafe_allow_html=True)

# --- TAB 4: 10-UNITS (ยกระดับจาก DATA LOG เดิม เป็นระบบวิเคราะห์จริง) ---
with tabs[3]:
    st.markdown('<div class="terminal-container"><h3>[ STRATEGIC_10_UNITS_ANALYSIS ]</h3></div>', unsafe_allow_html=True)
    if users_data:
        df = pd.DataFrame.from_dict(users_data, orient='index')
        st.write("### 📑 รายงานสถานะโหนดเครือข่าย")
        st.dataframe(df[['lat', 'lon', 'status']] if 'lat' in df.columns else df, use_container_width=True)
        
        # แสดง 1.3 Tactical Ruler (ระยะห่างจริง)
        me = users_data.get(st.session_state.my_name)
        if me and 'lat' in me:
            st.write("---")
            st.write("📏 **ระยะห่างจาก Agent อื่น (KM):**")
            for name, info in users_data.items():
                if name != st.session_state.my_name and 'lat' in info:
                    dist = geodesic((me['lat'], me['lon']), (info['lat'], info['lon'])).km
                    st.metric(f"ห่างจาก {name}", f"{dist:.2f} KM")

# --- TAB 5: SECURITY (ระบบเฝ้าระวังจริง) ---
with tabs[4]:
    st.markdown('<div class="terminal-container"><h3>[ SECURITY_ENFORCEMENT ]</h3></div>', unsafe_allow_html=True)
    if users_data and st.session_state.my_name in users_data:
        me = users_data[st.session_state.my_name]
        # 1.5 Geofence (รัศมี 10 กม. จากกรุงเทพ)
        hq = (13.75, 100.5)
        if 'lat' in me:
            d_from_hq = geodesic(hq, (me['lat'], me['lon'])).km
            if d_from_hq > 10: st.error(f"🚨 ALERT: OUTSIDE SECURE ZONE ({d_from_hq:.2f} KM)")
            else: st.success(f"✅ STATUS: WITHIN SECURE ZONE ({d_from_hq:.2f} KM)")
        
        # 1.9 Elevation & Status
        st.write(f"ความเร็วปัจจุบัน: {me.get('speed', '0')} KM/H")
        st.progress(100, "SIGNAL INTEGRITY")
    else: st.warning("กรุณา INITIATE LINK ในหน้า CORE ก่อน")

# --- TAB 6 & 7 (MEDIA & SYSTEM) ---
with tabs[5]: 
    st.video("https://www.youtube.com/watch?v=f0h8PjdZzrw")
with tabs[6]:
    if st.button("🧼 RESET ALL DATA"):
        db.reference('/').delete()
        st.rerun()

# --- SIDEBAR (KEEP ORIGINAL) ---
with st.sidebar:
    st.markdown("### 🛰️ NETWORK CENTER")
    st.audio(direct_link, format="audio/mpeg", loop=True)
    st.write(f"UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

def draw_box(title, target_level):
    # วาดกรอบสวยๆ แบบที่เพื่อนชอบ
    if st.button(title, use_container_width=True):
        st.session_state.nav_level = target_level
        st.rerun()
def setup_ui():
    st.markdown("""
        <style>
        .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
        .neon-header { 
            font-size: 40px; font-weight: 900; text-align: center;
            color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
            border: 10px double #ff1744; padding: 20px; border-radius: 20px;
        }
        /* ... (โค้ด CSS อื่นๆ ที่เหลือ) ... */
        </style>
    """, unsafe_allow_html=True)

# --- 3. การประกอบร่าง ---
st.title("SYNAPSE HIERARCHY SYSTEM")

# ปุ่มย้อนกลับ (อยู่นิ่งๆ ไม่เจ็บตัว ต้องมีทางถอย!)
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        # วิธีถอยกลับแบบฉลาด
        if "." in st.session_state.nav_level:
            # ตัดเลขท้ายออก เช่น 1.1.1 -> 1.1
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

st.write(f"CURRENT PATH: **{st.session_state.nav_level}**")
st.markdown("---")

# --- 4. ระบบคุมชั้น (Navigation Logic) ---

# ชั้นที่ 0: หน้าแรก
if st.session_state.nav_level == "HOME":
    c1, c2 = st.columns(2)
    with c1: draw_box("กรอบที่ 1", "1")
    with c2: draw_box("กรอบที่ 2", "2")
    with c1: draw_box("กรอบที่ 3", "3")
    with c2: draw_box("กรอบที่ 4", "4")

# ชั้นที่ 1: เมื่อเจาะจงเลข 1
elif st.session_state.nav_level == "1":
    c1, c2 = st.columns(2)
    with c1: draw_box("กรอบที่ 1.1", "1.1")
    with c2: draw_box("กรอบที่ 1.2", "1.2")
    with c1: draw_box("กรอบที่ 1.3", "1.3")
    with c2: draw_box("กรอบที่ 1.4", "1.4")

# ชั้นที่ 2: เมื่อเจาะจงเลข 1.1
elif st.session_state.nav_level == "1.1":
    c1, c2 = st.columns(2)
    with c1: draw_box("กรอบที่ 1.1.1", "1.1.1")
    with c2: draw_box("กรอบที่ 1.1.2", "1.1.2")
    with c1: draw_box("กรอบที่ 1.1.3", "1.1.3")
    with c2: draw_box("กรอบที่ 1.1.4", "1.1.4")

# ชั้นอื่นๆ (สมมุติว่ายังไม่ได้ทำเนื้อหา)
else:
    st.warning(f"ระบบส่วน {st.session_state.nav_level} กำลังพัฒนา...")
