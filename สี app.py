import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. ตั้งค่าและสไตล์ ---
st.set_page_config(page_title="SYNAPSE - Live", layout="wide")
st.markdown("<style>.status-box { padding: 15px; border-radius: 12px; border: 1px solid #4facfe; background: #1a1c24; }</style>", unsafe_allow_html=True)

# --- 2. เชื่อมต่อ Firebase ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e: st.error(f"Firebase Error: {e}")

# --- 3. ดึงพิกัดจริง ---
location = get_geolocation()

# --- 4. Dashboard สถานะ ---
st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE CONTROL</h1>", unsafe_allow_html=True)
st.markdown("<div class='status-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"🛰️ **GPS:** {'🟢 CONNECTED' if location else '🔴 SEARCHING...'}")
with c2: st.markdown("🎵 **MUSIC:** 🟢 ONLINE")
with c3: st.markdown(f"🔥 **DB:** {'🟢 SYNCED' if firebase_admin._apps else '🔴 ERROR'}")
st.markdown("</div>", unsafe_allow_html=True)
# --- 3. ส่วนหัว (Header) และโลโก้ ---
st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE</h1>", unsafe_allow_html=True)

# ตรวจสอบไฟล์โลโก้ (Logo3.jpg)
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1,1,1])
    with col_m:
        st.image("logo3.jpg", width=300)
elif os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1,1,1])
    with col_m:
        st.image("logo3.jpg", width=150)

location = get_geolocation()

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 Experience", "📊 Global Map", "💬 Community"])

with tab1:
    user_display_name = st.text_input("👤 ระบุชื่อผู้ใช้ (เพื่ออัปเดตตำแหน่ง):", placeholder="พิมพ์ชื่อของคุณ")
    if st.button("🚀 อัปเดตพิกัดใหม่ (ล้างอันเก่า)"):
        if user_display_name and location:
            # ล้างข้อมูลชื่อนี้อันเก่าทิ้งก่อน (ป้องกันข้อมูลซ้อน)
            user_ref = db.reference(f'users/{user_display_name}')
            user_ref.delete() 
            
            # บันทึกอันใหม่เข้าไปแทน
            user_ref.set({
                'lat': location['coords']['latitude'],
                'lon': location['coords']['longitude'],
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.success("✅ อัปเดตตำแหน่งปัจจุบันเรียบร้อย! (ลบข้อมูลเก่าแล้ว)")
        else:
            st.warning("⚠️ กรุณาระบุชื่อและเปิด GPS ก่อนนะเพื่อน")

with tab2:
    st.subheader("📍 แผนที่ตรวจสอบพิกัดจริง")
    if firebase_admin._apps:
        # ปุ่มล้างแผนที่ทั้งหมด (สำหรับล้างขยะข้อมูล)
        if st.button("🗑️ ล้างข้อมูลทุกคนบนแผนที่ (Reset Map)"):
            db.reference('users').delete()
            st.rerun()

        users = db.reference('users').get()
        if users:
            # ใช้พิกัดล่าสุดที่ดึงได้เป็นจุดศูนย์กลางแผนที่
            center_lat = location['coords']['latitude'] if location else 13.75
            center_lon = location['coords']['longitude'] if location else 100.5
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
            
            for name, info in users.items():
                if isinstance(info, dict) and 'lat' in info:
                    folium.Marker(
                        [info['lat'], info['lon']], 
                        popup=f"{name} ({info.get('time')})",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
            st_folium(m, width="100%", height=500)

with tab3:
    # (ส่วนของระบบ Call และ Chat เหมือนเดิมที่แก้ให้ล่าสุดครับ)
    st.subheader("🎥 Community")
    room_id = st.text_input("🔑 ห้อง:", value="private-room-01")
    if user_display_name:
        webrtc_streamer(
            key=f"call-fixed-{room_id}",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": True, "audio": True}
        )
        st.markdown("---")
        chat_ref = db.reference(f'chats/{room_id}')
        # ระบบ Chat ล่าสุดอยู่ข้างล่าง...
        user_msg = st.chat_input("คุยกันตรงนี้...")
        if user_msg:
            chat_ref.push({'name': user_display_name, 'msg': user_msg})
            st.rerun()
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m_id in msgs:
                st.write(f"**{msgs[m_id].get('name')}**: {msgs[m_id].get('msg')}")
