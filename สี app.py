import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# --- 1. SETTING & UI ---
st.set_page_config(page_title="SYNAPSE - Ultra Control", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; }
    .notif-badge { 
        padding: 10px; border-radius: 10px; background: #ff4747; 
        color: white; font-weight: bold; text-align: center; 
        margin-bottom: 15px; box-shadow: 0 0 15px #ff4747;
    }
    .bubble-me { background: rgba(0, 242, 254, 0.2); border: 2px solid #00f2fe; padding: 10px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; }
    .bubble-others { background: rgba(255, 71, 71, 0.2); border: 2px solid #ff4747; padding: 10px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGO DISPLAY (เช็คไฟล์ logo3.jpg) ---
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.image("logo3.jpg", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>SYNAPSE CONTROL</h1>", unsafe_allow_html=True)

# --- 3. HIDDEN AUDIO (27 MINS) ---
song_id = "1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
direct_link = f"https://docs.google.com/uc?export=download&id={song_id}"
st.components.v1.html(f"""
    <div style="display:none;"><audio id="bg-audio" loop autoplay><source src="{direct_link}" type="audio/mpeg"></audio></div>
    <script>
        var audio = document.getElementById("bg-audio");
        audio.volume = 0.4;
        document.body.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
    </script>
""", height=0)

# --- 4. FIREBASE ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e: st.error(f"Error: {e}")

# --- 5. SESSION & GPS ---
if 'my_name' not in st.session_state: st.session_state.my_name = "Guest"
my_name = st.session_state.my_name

# --- 6. TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 EXPERIENCE", "📊 GLOBAL MAP", "💬 CHAT"])

with tab1:
    st.markdown("### 👤 USER IDENTIFICATION")
    st.session_state.my_name = st.text_input("ระบุชื่อของคุณ:", value=st.session_state.my_name)
    
    if st.button("🚀 ACTIVATE STATUS (GLOBAL TIME)"):
        loc = get_geolocation()
        if loc:
            # ดึงเวลาจากเครื่องผู้ใช้โดยตรง (เป็น Unix Timestamp สากล)
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            # แปลงเป็นเวลาที่อ่านง่าย
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 
                'lon': loc['coords']['longitude'],
                'gps_time': local_time,  # เวลาจริงจากพิกัดนั้นๆ
                'status': 'online'
            })
            st.success(f"พิกัด {st.session_state.my_name} ซิงค์กับดาวเทียมโลกเรียบร้อย!")


with tab2:
    st.subheader("📍 GLOBAL GEOLOCATION MONITOR")
    users = db.reference('users').get()
    if users:
        # ปักหมุดทั่วโลกตามที่ GPS จับได้จริง
        m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                folium.Marker(
                    [info['lat'], info['lon']], 
                    popup=f"User: {name}\nTime: {info.get('time')}",
                    icon=folium.Icon(color='blue', icon='screenshot')
                ).add_to(m)
        st_folium(m, width="100%", height=550)

with tab3:
    # (โค้ดส่วนแชทสีฟ้า/แดงเหมือนเดิม...)
    all_u = db.reference('users').get()
    col_u, col_c = st.columns([1, 2])
    with col_u:
        if all_u:
            for f_name in all_u.keys():
                if f_name != my_name:
                    if st.button(f"คุยกับ {f_name}", key=f"chat-{f_name}"):
                        pair = sorted([my_name, f_name])
                        st.session_state.private_room = f"secret_{pair[0]}_{pair[1]}"
                        st.session_state.target_name = f_name
                        st.rerun()
    with col_c:
        room = st.session_state.get('private_room')
        target = st.session_state.get('target_name')
        if room and target:
            st.markdown(f"#### 🔒 ENCRYPTED WITH: {target}")
            chat_ref = db.reference(f'chats/{room}')
            msg_in = st.chat_input(f"ส่งข้อความหา {target}...")
            if msg_in:
                chat_ref.push({'name': my_name, 'msg': msg_in, 'ts': datetime.datetime.now().timestamp()})
                st.rerun()
            msgs = chat_ref.order_by_child('ts').limit_to_last(15).get()
            if msgs:
                for m_id in msgs:
                    d = msgs[m_id]
                    is_me = d.get('name') == my_name
                    st.markdown(f"<div style='text-align: {'right' if is_me else 'left'};'><div class='{'bubble-me' if is_me else 'bubble-others'}' style='display: inline-block;'><small>{d.get('name')}</small><br>{d.get('msg')}</div></div>", unsafe_allow_html=True)
