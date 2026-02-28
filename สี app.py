import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import datetime
import time

# ==========================================
# 1. SETTING & UI (อยู่นิ่งๆ ไม่เจ็บตัว)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000; color: #00f2fe; }
    .box-button {
        border: 2px solid #ff1744; padding: 20px; border-radius: 15px;
        text-align: center; background: rgba(255, 23, 68, 0.1);
        box-shadow: 0 0 15px #ff1744; transition: 0.3s;
    }
    .neon-text { text-shadow: 0 0 10px #00f2fe; color: #fff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUDIO SYSTEM (ยักษ์ในตัวฉัน - Auto Play)
# ==========================================
def play_system_audio():
    audio_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.components.v1.html(f"""
        <audio id="bg-audio" loop autoplay><source src="{audio_link}" type="audio/mpeg"></audio>
        <script>document.addEventListener('click', function() {{ document.getElementById('bg-audio').play(); }}, {{once: true}});</script>
    """, height=0)

play_system_audio()

# ==========================================
# 3. FIREBASE & SESSION (ตัวเชื่อมข้อมูล)
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

if 'nav_level' not in st.session_state: st.session_state.nav_level = "HOME"
if 'my_name' not in st.session_state: st.session_state.my_name = "Agent_Unknown"

# ==========================================
# 4. LOGIC FUNCTIONS (กล่องความสามารถ)
# ==========================================

# 4.1 ระบบสีหมุดอัจฉริยะ (Dynamic Marker Color)
def get_marker_color(info, name):
    if name == st.session_state.my_name: return "cadetblue" # เราเอง
    battery = info.get('battery', 100)
    status = info.get('status', 'OFFLINE')
    if battery < 20: return "red"       # แบตต่ำ
    if status == "ACTIVE": return "green" # ออนไลน์
    return "gray"                       # ขาดการติดต่อ

# 4.2 แผนที่เรดาร์ (Radar Scanner)
def render_radar():
    st.subheader("🛰️ RADAR SCANNER (REAL-TIME)")
    m = folium.Map(location=[13.75, 100.5], zoom_start=6, tiles="cartodbpositron")
    users = db.reference('users').get()
    if users:
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                color = get_marker_color(info, name)
                folium.Marker(
                    [info['lat'], info['lon']],
                    tooltip=f"Agent: {name} | Bat: {info.get('battery', '??')}%",
                    icon=folium.Icon(color=color, icon='user', prefix='fa')
                ).add_to(m)
    st_folium(m, width="100%", height=500)

# ==========================================
# 5. NAVIGATION SYSTEM (ระบบแยกห้อง)
# ==========================================

# ปุ่มย้อนกลับ
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK TO MAIN MENU"):
        st.session_state.nav_level = "HOME"
        st.rerun()

# --- หน้าแรก (4 กรอบหลัก) ---
if st.session_state.nav_level == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE MAIN COMMAND</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛰️ 1. GPS SYSTEMS", use_container_width=True):
            st.session_state.nav_level = "GPS_MENU"
            st.rerun()
    with c2: st.button("💬 2. COMMUNICATIONS", use_container_width=True)
    with c1: st.button("📊 3. DATA ANALYSIS", use_container_width=True)
    with c2: st.button("🧹 4. SYSTEM TOOLS", use_container_width=True)

# --- หน้าเมนู GPS (10 กรอบย่อย) ---
elif st.session_state.nav_level == "GPS_MENU":
    st.markdown("<h2 class='neon-text'>GPS STRATEGIC UNITS</h2>", unsafe_allow_html=True)
    
    # วนลูปสร้าง 10 กรอบ (1.1 - 1.10)
    cols = st.columns(2)
    features = [
        "1.1 Signal Pulse", "1.2 Radar Tracking", "1.3 Tactical Ruler", 
        "1.4 Velocity Monitor", "1.5 Geofence Alarm", "1.6 ETA Calculator",
        "1.7 Satellite Switch", "1.8 Breadcrumb Trail", "1.9 Elevation Profile",
        "1.10 Area Density"
    ]
    
    for i, title in enumerate(features):
        with cols[i % 2]:
            if st.button(title, use_container_width=True):
                st.session_state.nav_level = f"FEATURE_{i+1}"
                st.rerun()

# --- หน้าแสดงผลความสามารถ 1.2 (Radar) ---
elif st.session_state.nav_level == "FEATURE_2":
    render_radar()
    st.info("สีหมุด: ฟ้า(เรา) | เขียว(ออนไลน์) | แดง(แบตต่ำ) | เทา(ออฟไลน์)")

else:
    st.warning(f"FEATURE {st.session_state.nav_level} IS UNDER CONSTRUCTION")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueGZ4ZzR6ZHg0eGZ4ZzR6ZHg0eGZ4ZzR6ZHg0eGZ4ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxxcaNlkP84/giphy.gif")

