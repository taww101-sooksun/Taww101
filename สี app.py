import streamlit as st
import os 
import time
import base64
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
    if 'my_name' not in st.session_state: st.session_state.my_name = ""
    if 'active_room' not in st.session_state: st.session_state.active_room = "🚀 แกนหลัก"
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ==========================================
# 2. พื้นที่เก็บห้อง (Modules)
# ==========================================

def room_core():
    # --- นาฬิกาจับพิกัด (คำนวณเวลาตามตำแหน่งจริง) ---
    loc = get_geolocation()
    current_time = datetime.now()
    
    st.subheader(f"🚀 ศูนย์ควบคุม: {st.session_state.my_name}")
    
    if loc and 'coords' in loc:
        lon = loc['coords']['longitude']
        lat = loc['coords']['latitude']
        # คำนวณเวลาท้องถิ่นจาก Longitude (15 องศา = 1 ชม.)
        offset = round(lon / 15) - 7 
        local_time = current_time + timedelta(hours=offset)
        st.success(f"🕰️ เวลาพิกัดปัจจุบัน: {local_time.strftime('%H:%M:%S')}")
        st.caption(f"📍 พิกัดดาวเทียม: {lat:.4f}, {lon:.4f}")

    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสเรียกขาน: **{st.session_state.my_name}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
    st.markdown("---")
    st.code(f"System Log: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\nStatus: Active")

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม (ระบุชื่อบนหมุด)")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

    # แผนที่ดาวเทียม Google Satellite
    m = folium.Map(location=[lat, lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for u_id, data in all_users.items():
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                # ระบุชื่อในแผนที่ (Tooltip โชว์ตลอด)
                folium.Marker(
                    [u_lat, u_lon], 
                    tooltip=f"<b>{u_id}</b>", 
                    popup=u_id,
                    icon=folium.Icon(color='red' if u_id == st.session_state.my_name else 'green', icon='user')
                ).add_to(m)

    st_folium(m, width="100%", height=450, key="radar_map")

    if loc and st.button("📡 กระจายพิกัดระบุตัวตน", use_container_width=True):
        db.reference(f'users/{st.session_state.my_name}').update({
            'lat': lat, 'lon': lon, 'ts': time.time()
        })
        st.toast("อัปเดตตำแหน่งแล้ว!")

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t1, t2 = st.tabs(["🌐 Lobby (สาธารณะ)", "🔐 Private (ส่วนตัว)"])
    with t1:
        chat_ref = db.reference('public_chat')
        with st.form("pub", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความเข้า Lobby...")
            if st.form_submit_button("SEND"):
                if msg:
                    chat_ref.push({'user': st.session_state.my_name, 'msg': msg, 'ts': time.time()})
                    st.rerun()
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")

def room_music():
    st.subheader("🎧 ห้องพักผ่อน (Auto-Next)")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง")
        return
    
    cur_idx = st.session_state.song_index
    st.audio(music_files[cur_idx], autoplay=True)

    # Playlist ให้เลือก
    st.write("🎵 รายการเพลง:")
    for i, song in enumerate(music_files):
        if st.button(f"{'▶️' if i==cur_idx else '🎵'} {song}", key=f"s_{i}"):
            st.session_state.song_index = i; st.rerun()

# ==========================================
# 3. แผงวงจรหลัก (UI & Styling)
# ==========================================
def main():
    init_system()

    # CSS ปรับแต่งปุ่ม 3D ยกสูง และโลโก้ไร้ขอบ
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
        
        /* ปุ่มเมนู 3D ยกสูงชัดเจน */
        div.stButton > button {{
            width: 100%; border-radius: 12px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.4); color: {st.session_state.theme_color} !important;
            padding: 12px; font-weight: bold; font-size: 16px;
            box-shadow: 0 6px 0 {st.session_state.theme_color}; /* ยกสูง */
            transition: all 0.1s ease; margin-bottom: 10px;
        }}
        div.stButton > button:active {{
            transform: translateY(4px); /* ยุบลง */
            box-shadow: 0 1px 0 {st.session_state.theme_color};
        }}
        
        h1, h2, h3, p, span {{ color: {st.session_state.text_color} !important; }}
        
        /* โลโก้ไร้กรอบ */
        .logo-box {{ text-align: center; padding: 10px; }}
        .logo-img {{ 
            width: 260px; 
            mix-blend-mode: screen; /* ตัดขอบดำ */
            filter: drop-shadow(0 0 12px {st.session_state.theme_color}); 
        }}
        </style>
        """, unsafe_allow_html=True)

    # หน้าจอ Login
    if st.session_state.my_name == "":
        logo_data = get_base64_img("logo1.jpg")
        if logo_data:
            st.markdown(f'<div class="logo-box"><img src="data:image/jpeg;base64,{logo_data}" class="logo-img"></div>', unsafe_allow_html=True)
        
        st.title("🛰️ SYNAPSE LOGIN")
        name = st.text_input("รหัสเรียกขาน:")
        if st.button("เข้าสู่ระบบ (ENTER)"):
            if name: st.session_state.my_name = name; st.rerun()
        return

    # แสดงโลโก้ในหน้าหลักด้วย
    logo_data = get_base64_img("logo1.jpg")
    if logo_data:
        st.markdown(f'<div class="logo-box"><img src="data:image/jpeg;base64,{logo_data}" class="logo-img" style="width:180px;"></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีนีออนหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 สีพื้นหลัง", st.session_state.bg_color)
        if st.button("Logout"): st.session_state.my_name = ""; st.rerun()

    # ปุ่มเมนูหลักแบบ 2 คอลัมน์ (ปุ่มนูนยกสูง)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 แกนหลัก"): st.session_state.active_room = "🚀 แกนหลัก"
        if st.button("💬 การสื่อสาร"): st.session_state.active_room = "💬 การสื่อสาร"
    with c2:
        if st.button("🛰️ เรดาร์"): st.session_state.active_room = "🛰️ เรดาร์"
        if st.button("🎧 ห้องพัก"): st.session_state.active_room = "🎧 ห้องพัก"

    st.markdown("---")
    
    # รันห้องที่เลือก
    rooms = {"🚀 แกนหลัก": room_core, "🛰️ เรดาร์": room_radar, "💬 การสื่อสาร": room_comms, "🎧 ห้องพัก": room_music}
    rooms[st.session_state.active_room]()

if __name__ == "__main__":
    main()
