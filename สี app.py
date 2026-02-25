import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. การตั้งค่าหน้าเว็บและการออกแบบ (SYNAPSE STYLE) ---
st.set_page_config(page_title="SYNAPSE - Final Control", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #0a2342 50%, #004e92 100%);
        color: #ffffff;
    }
    .status-box { 
        padding: 20px; border-radius: 15px; 
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(79, 172, 254, 0.3);
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%; border-radius: 30px;
        background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
        color: white; border: none; font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. เชื่อมต่อ Firebase ---
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
        st.error(f"Error: {e}")

# --- 3. ดึงพิกัดจริง ---
location = get_geolocation()

# --- 4. ส่วนหัวและโลโก้ ---
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m: st.image("logo3.jpg", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE CONTROL</h1>", unsafe_allow_html=True)

# Dashboard สถานะ
st.markdown("<div class='status-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"🛰️ **GPS:** {'🟢 CONNECTED' if location else '🔴 SEARCHING...'}")
with c2: st.markdown("🎵 **MUSIC:** 🟢 ONLINE")
with c3: st.markdown(f"🔥 **DB:** {'🟢 SYNCED' if firebase_admin._apps else '🔴 ERROR'}")
st.markdown("</div>", unsafe_allow_html=True)

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 Experience", "📊 Global Map", "💬 Community"])

with tab1:
    # ใช้ session_state จำชื่อเราไว้ไม่ให้เพี้ยน
    if 'my_name' not in st.session_state:
        st.session_state.my_name = ""
        
    name_input = st.text_input("👤 ระบุชื่อผู้ใช้:", value=st.session_state.my_name, placeholder="พิมพ์ชื่อของคุณ...")
    if st.button("🚀 UPDATE MY STATUS"):
        if name_input and location:
            st.session_state.my_name = name_input
            user_ref = db.reference(f'users/{name_input}')
            user_ref.set({
                'lat': location['coords']['latitude'],
                'lon': location['coords']['longitude'],
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.success(f"สวัสดีคุณ {name_input}! บันทึกพิกัดจริงเรียบร้อย")
            
    st.markdown("---")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&mute=1"
    st.components.v1.html(f'<iframe width="100%" height="200" src="{embed_url}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', height=220)

with tab2:
    st.subheader("📍 Real-time Location Map")
    if firebase_admin._apps:
        if st.button("🗑️ Reset Map (ล้างพิกัดทั้งหมด)"):
            db.reference('users').delete()
            st.rerun()
            
        users = db.reference('users').get()
        if users:
            center = [location['coords']['latitude'], location['coords']['longitude']] if location else [13.75, 100.5]
            m = folium.Map(location=center, zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
            for name, info in users.items():
                if isinstance(info, dict) and 'lat' in info:
                    folium.Marker([info['lat'], info['lon']], popup=name).add_to(m)
            st_folium(m, width="100%", height=500)

with tab3:
    st.subheader("👥 Private Chat & Call")
    my_name = st.session_state.get('my_name', "")
    
    if not my_name:
        st.warning("⚠️ เพื่อนต้องไปใส่ชื่อที่หน้า 🚀 Experience ก่อนนะ ถึงจะเริ่มแชทได้")
    else:
        all_users = db.reference('users').get()
        col_u, col_c = st.columns([1, 2])

        with col_u:
            st.write("📱 เลือกเพื่อนที่จะแชทด้วย:")
            if all_users:
                for f_name in all_users.keys():
                    if f_name != my_name:
                        if st.button(f"💬 {f_name}", key=f"chat-{f_name}"):
                            pair = sorted([my_name, f_name])
                            st.session_state.private_room = f"secret_{pair[0]}_{pair[1]}"
                            st.session_state.target_name = f_name
            else:
                st.write("ยังไม่มีใครออนไลน์...")

        with col_c:
            room = st.session_state.get('private_room', None)
            target = st.session_state.get('target_name', None)
            
            if room and target:
                st.info(f"🔒 ห้องแชทลับ: {my_name} ⚡ {target}")
                
                # --- Video Call v12 ---
                webrtc_streamer(
                    key=f"call-v12-{room}",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration={
                        "iceServers": [
                            {"urls": ["stun:stun.l.google.com:19302"]},
                            {"urls": ["stun:global.stun.twilio.com:3478"]},
                            {"urls": ["stun:stun.services.mozilla.com"]}
                        ]
                    },
                    media_stream_constraints={"video": True, "audio": True},
                    async_processing=True
                )
                
                st.markdown("---")
                chat_ref = db.reference(f'chats/{room}')
                
                # ช่องส่งข้อความ
                msg_in = st.chat_input(f"ส่งข้อความหา {target}...")
                if msg_in:
                    chat_ref.push({
                        'name': my_name,
                        'msg': msg_in,
                        'ts': datetime.datetime.now().timestamp()
                    })
                    st.rerun()
                
                # แสดงแชทแบบแยกฝั่ง
                msgs = chat_ref.order_by_child('ts').limit_to_last(20).get()
                if msgs:
                    for m_id in msgs:
                        d = msgs[m_id]
                        is_me = d.get('name') == my_name
                        align = "right" if is_me else "left"
                        bg = "rgba(0, 242, 254, 0.4)" if is_me else "rgba(255, 255, 255, 0.1)"
                        st.markdown(f"""
                            <div style='text-align: {align}; margin-bottom: 10px;'>
                                <div style='display: inline-block; background: {bg}; padding: 8px 15px; border-radius: 15px;'>
                                    <small style='opacity:0.6;'>{d.get('name')}</small><br>{d.get('msg')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                if st.button("🗑️ ล้างแชทห้องนี้"):
                    chat_ref.delete()
                    st.rerun()
            else:
                st.write("👈 เลือกเพื่อนด้านซ้ายเพื่อเปิดห้องลับ")
