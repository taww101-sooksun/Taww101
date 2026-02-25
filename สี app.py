import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os  # <--- เพิ่มบรรทัดนี้เพื่อแก้ NameError
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="SYNAPSE - Live Control", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .status-box { padding: 15px; border-radius: 12px; border: 1px solid #4facfe; background: #1a1c24; margin-bottom: 20px; }
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
        st.error(f"Firebase Connection Error: {e}")

# --- 3. ตรวจสอบพิกัดจริง ---
location = get_geolocation()

# --- 4. ส่วนหัวและโลโก้ (Header & Logo) ---
# ตรวจสอบไฟล์โลโก้และแสดงผล
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.image("logo3.jpg", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE CONTROL</h1>", unsafe_allow_html=True)

# แถบ Status Dashboard
st.markdown("<div class='status-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"🛰️ **GPS:** {'🟢 CONNECTED' if location else '🔴 SEARCHING...'}")
with c2: st.markdown("🎵 **MUSIC:** 🟢 ONLINE")
with c3: st.markdown(f"🔥 **DB:** {'🟢 SYNCED' if firebase_admin._apps else '🔴 ERROR'}")
st.markdown("</div>", unsafe_allow_html=True)

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 Experience", "📊 Global Map", "💬 Community"])

with tab1:
    user_display_name = st.text_input("👤 ระบุชื่อผู้ใช้:", placeholder="ระบุชื่อของคุณ")
    if st.button("🚀 UPDATE JOURNEY"):
        if user_display_name and location:
            user_ref = db.reference(f'users/{user_display_name}')
            user_ref.set({
                'lat': location['coords']['latitude'],
                'lon': location['coords']['longitude'],
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.success("✅ บันทึกพิกัดใหม่และล้างข้อมูลเก่าแล้ว!")

    st.markdown("---")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&mute=1"
    st.components.v1.html(f'<iframe width="100%" height="200" src="{embed_url}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', height=220)

with tab2:
    st.subheader("📍 แผนที่ตรวจสอบพิกัดจริง")
    if firebase_admin._apps:
        if st.button("🗑️ Reset Map (ล้างทุกคน)"):
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
    st.subheader("👥 รายชื่อผู้ใช้งาน (Private Chat)")
    
    # ดึงรายชื่อคนทั้งหมดจาก Firebase
    all_users = db.reference('users').get()
    
    # สร้าง Layout 2 คอลัมน์ (ซ้าย: รายชื่อเพื่อน, ขวา: ห้องแชท)
    col_list, col_chat = st.columns([1, 2])
    
    with col_list:
        st.markdown("### 📱 เลือกเพื่อนที่ออนไลน์")
        if all_users:
            for friend_name in all_users.keys():
                # ไม่แสดงชื่อตัวเองในรายชื่อเพื่อน
                if friend_name != user_display_name:
                    # ปุ่มกดเพื่อเลือกคุยกับเพื่อนคนนี้
                    if st.button(f"💬 คุยกับ {friend_name}", key=f"user-{friend_name}"):
                        # สร้าง ID ห้องลับโดยเรียงลำดับชื่อ (เพื่อให้ทั้งสองคนได้ ID ห้องเดียวกันเสมอ)
                        pair = sorted([user_display_name, friend_name])
                        st.session_state.current_private_room = f"secret_{pair[0]}_{pair[1]}"
                        st.session_state.chat_target = friend_name
        else:
            st.write("ยังไม่มีใครออนไลน์เลยเพื่อน...")

    with col_chat:
        # ตรวจสอบว่าเลือกใครคุยอยู่หรือไม่
        target = st.session_state.get('chat_target', None)
        room_id = st.session_state.get('current_private_room', None)

        if target and room_id:
            st.markdown(f"### 🔒 แชทลับกับ: {target}")
            
            # --- ระบบ Video Call (แยกห้องตาม ID ห้องลับ) ---
            webrtc_streamer(
                key=f"call-{room_id}",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                media_stream_constraints={"video": True, "audio": True}
            )

            st.markdown("---")
            
            # --- ระบบ Chat ลับ ---
            chat_ref = db.reference(f'chats/{room_id}')
            
            # ดึงข้อความ (เรียงจากเก่าไปใหม่)
            messages = chat_ref.order_by_key().limit_to_last(15).get()
            
            # พื้นที่แสดงข้อความ
            chat_box = st.container()
            with chat_box:
                if messages:
                    for m_id in messages:
                        data = messages[m_id]
                        is_me = data.get('name') == user_display_name
                        align = "right" if is_me else "left"
                        bg = "rgba(79, 172, 254, 0.4)" if is_me else "rgba(255, 255, 255, 0.1)"
                        st.markdown(f"""
                            <div style='text-align: {align}; margin-bottom: 10px;'>
                                <span style='background: {bg}; padding: 8px 15px; border-radius: 15px; display: inline-block;'>
                                    <b>{data.get('name')}</b>: {data.get('msg')}
                                </span>
                            </div>
                        """, unsafe_allow_html=True)

            # ช่องพิมพ์ข้อความลับ
            user_input = st.chat_input(f"ส่งข้อความหา {target}...")
            if user_input:
                chat_ref.push({
                    'name': user_display_name,
                    'msg': user_input,
                    'time': datetime.datetime.now().strftime("%H:%M")
                })
                st.rerun()

            # ปุ่มลบประวัติเฉพาะห้องนี้
            if st.button("🗑️ ล้างแชทนี้"):
                chat_ref.delete()
                st.rerun()
        else:
            st.info("👈 เลือกรายชื่อเพื่อนด้านซ้ายเพื่อเริ่มคุยกันแบบส่วนตัว")
