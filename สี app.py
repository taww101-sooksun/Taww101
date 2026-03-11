import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SYNAPSE - Admin Secure", layout="wide")

# 2. เชื่อมต่อ Firebase (เช็คความถูกต้องของ Key)
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            # แก้ไขเรื่องขึ้นบรรทัดใหม่ใน Private Key ที่มักจะมีปัญหาบน Cloud
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': st.secrets["firebase"]["databaseURL"]
            })
    except Exception as e:
        st.error(f"Firebase Setup Error: {e}")

# ฟังก์ชันคำนวณเวลาจากพิกัด (อิงจากเส้นลองจิจูด)
def get_time_by_coords(lon):
    try:
        if lon is None: return datetime.datetime.now()
        offset = round(float(lon) / 15)
        # ใช้ timezone-aware datetime เพื่อความแม่นยำ
        return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=offset)
    except:
        return datetime.datetime.now()

# --- ส่วนหัว ---
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo3.jpg"): 
        st.image("logo3.jpg", width=150) # ปรับขนาดให้พอดี
    else: 
        st.write("### 🌐 SYNAPSE")
with col2:
    st.title("SYNAPSE - Music Therapy")

# ดึงพิกัด (อาจใช้เวลาโหลดนิดนึง)
location = get_geolocation()

# --- ระบบแจ้งเตือน (Notification) ---
if 'last_chat_count' not in st.session_state:
    st.session_state.last_chat_count = 0

def check_notifications():
    try:
        chats_ref = db.reference('chats').get()
        if chats_ref:
            current_count = len(chats_ref)
            if current_count > st.session_state.last_chat_count:
                if st.session_state.last_chat_count != 0:
                    st.toast("💬 มีข้อความใหม่!", icon="🔔")
                    if os.path.exists("notification.mp3"):
                        # แอบใส่เสียงเตือน (แต่ Browser อาจจะบล็อกถ้ายังไม่มีการ Interact)
                        st.audio("notification.mp3", format="audio/mp3", autoplay=True)
                st.session_state.last_chat_count = current_count
    except: 
        pass

check_notifications()

# 3. Tabs
tab1, tab2, tab3 = st.tabs(["🚀 เช็คอิน & ฟังเพลง", "📊 แผนที่", "💬 ห้องสนทนา"])

with tab1:
    user_display_name = st.text_input("ระบุชื่อของคุณ:", placeholder="เช่น Ta101", key="user_input")
    admin_key = st.text_input("รหัสผ่านผู้ดูแล (Admin Only):", type="password")

    if st.button("Start Journey"):
        if not user_display_name:
            st.warning("กรุณาใส่ชื่อก่อนเพื่อน!")
        elif location and 'coords' in location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            true_dt = get_time_by_coords(lon)
            true_time_str = true_dt.strftime("%H:%M")
            
            # บันทึกข้อมูลลง Firebase
            try:
                db.reference(f'users/{user_display_name}').set({
                    'last_seen': true_time_str, 
                    'lat': lat, 
                    'lon': lon,
                    'timestamp': datetime.datetime.now().timestamp()
                })
                st.success(f"เช็คอินสำเร็จ! เวลาพิกัดโลก: {true_time_str}")
            except Exception as e:
                st.error(f"บันทึกข้อมูลไม่สำเร็จ: {e}")
        else:
            st.error("ไม่สามารถดึงพิกัดได้ กรุณากดยอมรับการแชร์ Location บน Browser")

    # --- เช็คสิทธิ์แอดมิน ---
    if user_display_name == "Ta101" and admin_key == "Ta101@0970801941":
        st.divider()
        st.subheader("🎛️ แผงควบคุมดีเจ (Admin Mode)")
        
        # คำนวณเวลาเพื่อเลือกเพลง
        lon_now = location['coords']['longitude'] if (location and 'coords' in location) else 100
        true_dt_now = get_time_by_coords(lon_now)
        
        # เลือกไฟล์เพลงตามช่วงเวลา
        song_file = "test_morning.mp3" if 6 <= true_dt_now.hour < 18 else "test_evening.mp3"
        
        if os.path.exists(song_file):
            st.audio(song_file, loop=True)
            st.caption(f"กำลังเล่น: {song_file} (อิงจากเวลา {true_dt_now.strftime('%H:%M')})")
        else:
            st.error(f"ไม่พบไฟล์เพลง {song_file} ในระบบ (อย่าลืม Upload ขึ้น GitHub นะ)")
    else:
        if user_display_name:
            st.divider()
            st.info("🎧 สถานะ: เพลงบำบัดกำลังทำงานในระบบ... (เฉพาะแอดมินที่เห็นเครื่องเล่น)")

with tab2:
    # แสดงแผนที่ผู้ใช้งาน
    try:
        users_data = db.reference('users').get()
        if users_data:
            # ดึงพิกัดล่าสุดมาตั้งค่า Center ของแผนที่
            first_user = list(users_data.values())[0]
            m = folium.Map(location=[first_user.get('lat', 13), first_user.get('lon', 100)], zoom_start=12)
            
            for name, info in users_data.items():
                if 'lat' in info and 'lon' in info:
                    folium.Marker(
                        [info['lat'], info['lon']], 
                        popup=f"{name} ({info.get('last_seen', '??')})",
                        tooltip=name
                    ).add_to(m)
            st_folium(m, width="100%", height=500)
        else:
            st.write("ยังไม่มีข้อมูลตำแหน่งผู้ใช้งาน")
    except Exception as e:
        st.error(f"โหลดแผนที่พลาด: {e}")

with tab3:
    st.header("💬 ห้องสนทนา")
    # ฟอร์มส่งข้อความ
    with st.form("chat_form", clear_on_submit=True):
        msg_input = st.text_input("พิมพ์ข้อความที่นี่:")
        submit_button = st.form_submit_button("ส่ง")
        
        if submit_button and user_display_name and msg_input:
            lon = location['coords']['longitude'] if (location and 'coords' in location) else 100
            time_now = get_time_by_coords(lon).strftime("%H:%M")
            db.reference('chats').push({
                'name': user_display_name, 
                'msg': msg_input, 
                'time': time_now,
                'timestamp': datetime.datetime.now().timestamp()
            })
            st.rerun()

    # แสดงข้อความ (ย้อนหลัง 15 ข้อความ)
    try:
        chats = db.reference('chats').order_by_child('timestamp').limit_to_last(15).get()
        if chats:
            # จัดเรียงให้ข้อความใหม่ล่าสุดอยู่ด้านบน
            sorted_chats = sorted(chats.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
            for _, data in sorted_chats:
                st.markdown(f"**{data.get('name')}** <small style='color:gray'>{data.get('time')}</small>", unsafe_allow_html=True)
                st.write(data.get('msg'))
                st.divider()
    except:
        st.write("เริ่มการสนทนาได้เลย!")
