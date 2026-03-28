import streamlit as st
import os 
import random
import time
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
    # --- ระบบควบคุม 3 ชุดสี ---
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
        now = datetime.now()
        db.reference(f'synapse_logs/{now.strftime("%Y-%m-%d")}').push({
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
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **Ta101**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์และพิกัดจริง")
    loc = get_geolocation()
    
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 พิกัดปัจจุบัน: {lat}, {lon}")
        
        m = folium.Map(location=[lat, lon], zoom_start=17, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                       attr="Google Satellite")
        folium.Marker([lat, lon], tooltip="Ta101", icon=folium.Icon(color='blue')).add_to(m)
        st_folium(m, width="100%", height=400)
        
        if st.button("📡 กระจายสัญญาณพิกัด"):
            db.reference('users/Ta101').update({'lat': lat, 'lon': lon, 'ts': time.time()})
            save_log("LOCATION UPDATED")
            st.toast("ส่งพิกัดสำเร็จ!")
    else:
        st.warning("🚨 กำลังรอสัญญาณ GPS...")

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    
    chat_tabs = st.tabs(["🌐 Lobby (สาธารณะ)", "🔐 Private (ส่วนตัว)"])
    
    # --- แท็บที่ 1: Lobby ---
    with chat_tabs[0]:
        chat_ref = db.reference('public_chat')
        with st.form("public_form", clear_on_submit=True):
            msg = st.text_input("ส่งสัญญาณเข้า Lobby...")
            if st.form_submit_button("SEND TO LOBBY"):
                if msg:
                    chat_ref.push({'user': 'Ta101', 'msg': msg, 'ts': time.time()})
                    save_log(f"SENT LOBBY MSG")
                    st.rerun()
        
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                u = m.get('user', 'ระบบ')
                txt = m.get('msg', '...')
                st.write(f"🟢 **{u}:** {txt}")

    # --- แท็บที่ 2: Private (สัญญาณลับ) ---
    with chat_tabs[1]:
        target_id = st.text_input("ระบุรหัสผู้รับ (เช่น Bas, Dad):", value="Admin")
        private_ref = db.reference(f'private_messages/Ta101_{target_id}')
        
        with st.form("private_form", clear_on_submit=True):
            p_msg = st.text_area("ระบุข้อความลับ...")
            if st.form_submit_button("SEND PRIVATE"):
                if p_msg:
                    private_ref.push({'sender': 'Ta101', 'msg': p_msg, 'ts': time.time()})
                    save_log(f"SENT PRIVATE TO {target_id}")
                    st.toast(f"ส่งสัญญาณลับแล้ว")
                    st.rerun()
        
        p_msgs = private_ref.order_by_key().limit_to_last(5).get()
        if p_msgs:
            st.markdown("---")
            for pm in reversed(list(p_msgs.values())):
                st.caption(f"🔒 {pm.get('sender')}: {pm.get('msg')}")

def room_music():
    st.subheader("🎧 SYNAPSE ROOMS (BETA V5)")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3")
        return

    current_song = music_files[st.session_state.song_index]
    base_name = os.path.splitext(current_song)[0]

    st.markdown(f"<div style='border:2px solid {st.session_state.theme_color}; padding:10px; border-radius:10px; text-align:center;'>NOW PLAYING: {current_song}</div>", unsafe_allow_html=True)
    
    col_vis, col_list = st.columns([3, 2])
    with col_vis:
        if os.path.exists(f"{base_name}.mp4"):
            st.video(f"{base_name}.mp4", loop=True, autoplay=True, muted=True)
        elif os.path.exists(f"{base_name}.jpg"):
            st.image(f"{base_name}.jpg", use_container_width=True)
        st.audio(current_song, autoplay=True)

    with col_list:
        st.write("🎧 PLAYLIST")
        for i, song in enumerate(music_files):
            if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

    js_next = """
    <script>
    var audio = window.parent.document.querySelector('audio');
    if (audio) {
        audio.onended = function() {
            var btns = window.parent.document.querySelectorAll('button');
            for (var i=0; i<btns.length; i++) {
                if (btns[i].textContent.includes('🎵')) {
                    btns[(i+1)%btns.length].click(); break;
                }
            }
        };
    }
    </script>
    """
    components.html(js_next, height=0)

# ==========================================
# 3. แผงวงจรหลัก (Main Switchboard)
# ==========================================
def main():
    init_system()
    
    # ฉีด CSS ควบคุมบรรยากาศตามสีที่เลือก
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
        .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; }}
        h1, h2, h3, p, span, div {{ color: {st.session_state.text_color} !important; }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก (นีออน)", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 สีพื้นหลัง", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("✍️ สีข้อความ", st.session_state.text_color)
        st.write(f'**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

    room_map = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 การสื่อสาร": room_comms,
        "🎧 ห้องพัก": room_music
    }
    
    tabs = st.tabs(list(room_map.keys()))
    for i, room_func in enumerate(room_map.values()):
        with tabs[i]:
            room_func()

if __name__ == "__main__":
    main()
