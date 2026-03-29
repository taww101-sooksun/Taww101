import streamlit as st
import os # แก้ NameError
import time
import base64
from datetime import datetime
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

def save_log(action):
    try:
        db.reference(f'synapse_logs/{datetime.now().strftime("%Y-%m-%d")}').push({
            'time': datetime.now().strftime("%H:%M:%S"),
            'action': action,
            'user': st.session_state.my_name
        })
    except: pass

# ==========================================
# 2. พื้นที่เก็บห้อง (Modules)
# ==========================================

def room_core():
    st.subheader(f"🚀 ศูนย์ควบคุม: {st.session_state.my_name}")
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสเรียกขาน: **{st.session_state.my_name}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม (Real-time)")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc: # แก้ KeyError
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        st.success(f"📍 พิกัดปัจจุบัน: {lat:.4f}, {lon:.4f}")

    m = folium.Map(location=[lat, lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for u_id, data in all_users.items():
            u_lat, u_lon = data.get('lat'), data.get('lon')
            u_ts = data.get('ts', 0)
            if u_lat and u_lon:
                is_active = (time.time() - u_ts) < 3600
                color = 'red' if u_id == st.session_state.my_name else ('green' if is_active else 'gray')
                folium.Marker([u_lat, u_lon], tooltip=u_id,
                              icon=folium.Icon(color=color, icon='user')).add_to(m)

    st_folium(m, width="100%", height=450, key="radar_map")

    if loc and 'coords' in loc:
        if st.button("📡 กระจายพิกัดสัญญาณ", use_container_width=True):
            db.reference(f'users/{st.session_state.my_name}').update({
                'lat': lat, 'lon': lon, 'ts': time.time()
            })
            st.toast("อัปเดตตำแหน่งแล้ว!")
            st.rerun()

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t1, t2 = st.tabs(["🌐 Lobby", "🔐 Private"])
    with t1:
        chat_ref = db.reference('public_chat')
        with st.form("pub", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความ...")
            if st.form_submit_button("SEND"):
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
    cur_song = music_files[cur_idx]
    st.audio(cur_song, autoplay=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏮️ ก่อนหน้า", use_container_width=True):
            st.session_state.song_index = (cur_idx - 1) % len(music_files); st.rerun()
    with c2:
        if st.button("⏭️ ถัดไป", use_container_width=True):
            st.session_state.song_index = (cur_idx + 1) % len(music_files); st.rerun()

    js_next = """<script>var check = setInterval(function() { var audio = window.parent.document.querySelector('audio'); if (audio) { audio.onended = function() { var btns = window.parent.document.querySelectorAll('button'); for (var i=0; i<btns.length; i++) { if (btns[i].innerText.includes('ถัดไป')) { btns[i].click(); break; } } }; clearInterval(check); } }, 1000);</script>"""
    components.html(js_next, height=0)

# ==========================================
# 3. แผงวงจรหลัก (Switchboard)
# ==========================================
def main():
    init_system()

    # CSS ปุ่มนูน 3D และธีมแอป
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
        div.stButton > button {{
            width: 100%; border-radius: 12px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.2); color: {st.session_state.theme_color} !important;
            padding: 12px; font-weight: bold; box-shadow: 0 5px 0 {st.session_state.theme_color};
            transition: all 0.1s ease; margin-bottom: 8px;
        }}
        div.stButton > button:active {{ transform: translateY(4px); box-shadow: 0 1px 0 {st.session_state.theme_color}; }}
        h1, h2, h3, p, span {{ color: {st.session_state.text_color} !important; }}
        .logo-img {{ width: 250px; display: block; margin: 0 auto 20px; filter: drop-shadow(0 0 10px {st.session_state.theme_color}); }}
        </style>
        """, unsafe_allow_html=True)

    # หน้า Login
    if st.session_state.my_name == "":
        st.markdown("<br>", unsafe_allow_html=True)
        # แสดงโลโก้ (ถ้ามีไฟล์)
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as f:
                data = base64.b64encode(f.read()).decode()
                st.markdown(f'<img src="data:image/png;base64,{data}" class="logo-img">', unsafe_allow_html=True)
        
        st.title("🛰️ SYNAPSE LOGIN")
        name = st.text_input("รหัสเรียกขาน (Username):")
        if st.button("เข้าสู่ระบบ"):
            if name: st.session_state.my_name = name; st.rerun()
        return

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีนีออน", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 สีพื้นหลัง", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("✍️ สีข้อความ", st.session_state.text_color)
        if st.button("Logout"): st.session_state.my_name = ""; st.rerun()

    # เมนูเลือกห้องแบบปุ่มนูน
    c_a, c_b = st.columns(2)
    rooms = {"🚀 แกนหลัก": room_core, "🛰️ เรดาร์": room_radar, "💬 การสื่อสาร": room_comms, "🎧 ห้องพัก": room_music}
    r_list = list(rooms.keys())
    with c_a:
        if st.button(r_list[0]): st.session_state.active_room = r_list[0]
        if st.button(r_list[2]): st.session_state.active_room = r_list[2]
    with c_b:
        if st.button(r_list[1]): st.session_state.active_room = r_list[1]
        if st.button(r_list[3]): st.session_state.active_room = r_list[3]

    st.markdown("---")
    rooms[st.session_state.active_room]()

if __name__ == "__main__": main()
