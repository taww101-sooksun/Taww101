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
from math import radians, cos, sin, asin, sqrt
from folium.features import DivIcon

# ==========================================
# 0. ฟังก์ชันสนับสนุน (Helper Functions)
# ==========================================

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d = 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2)) 
    return d * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

# ==========================================
# 1. ระบบจัดการ AGENT (Login/Register)
# ==========================================

def room_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo1.jpg", use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center;'>🔐 เข้ารหัสการเข้าถึงระบบ</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียน AGENT"])
    
    with tab1:
        with st.form("login_form"):
            u_id = st.text_input("AGENT ID")
            u_pw = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("UNLOCK SYSTEM", use_container_width=True):
                user_data = db.reference(f'users/{u_id}').get()
                if user_data and user_data.get('pw') == u_pw:
                    st.session_state.user = u_id
                    st.session_state.logged_in = True
                    st.success(f"ยินดีต้อนรับ AGENT {u_id}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ ข้อมูลไม่ถูกต้อง")
                    
    with tab2:
        with st.form("reg_form"):
            new_id = st.text_input("ตั้งชื่อ AGENT ID")
            new_pw = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("REGISTER AGENT", use_container_width=True):
                if new_id and new_pw:
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")

# ==========================================
# 2. ฟังก์ชันห้องต่างๆ (Room Functions)
# ==========================================

def room_core():
    st.subheader("🚀 SYNAPSE COMMAND CENTER")
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div style="border: 2px solid {st.session_state.theme_color}; padding: 20px; border-radius: 15px; text-align: center; background: rgba(0,0,0,0.3);">
            <h1 style="color: {st.session_state.theme_color}; font-size: 3.5em; margin:0;">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 5px; opacity:0.7; color: {st.session_state.theme_color};">SYSTEM ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"👤 AGENT ID: **{st.session_state.user}**")
    st.write(f"🚩 SLOGAN: **'อยู่นิ่งๆ ไม่เจ็บตัว'**")

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม (Satellite View)")
    loc = get_geolocation()
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    else:
        my_lat, my_lon = 13.7367, 100.5231
        st.info("📡 กำลังซิงค์สัญญาณดาวเทียม...")

    google_satellite_hybrid = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    m = folium.Map(location=[my_lat, my_lon], zoom_start=18, tiles=google_satellite_hybrid, attr='Google Maps Satellite')
    
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)

    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color='lightgray')).add_to(m)
                    folium.Marker([u_lat - 0.0001, u_lon], icon=DivIcon(html=f'<div style="font-size:10pt; color:white; font-weight:bold; background:rgba(0,0,0,0.5); padding:2px;">{uid} ({dist:.2f}km)</div>')).add_to(m)
    except: pass

    st_folium(m, width="100%", height=500)
    if st.button("📡 แชร์ตำแหน่งปัจจุบันลงกลุ่ม", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("อัปเดตพิกัดแล้ว!")

def room_public():
    st.subheader("🌐 แชตรวมระบบส่งไฟล์ (Public)")
    with st.form("media_chat", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความ...")
        uploaded_file = st.file_uploader("📸 ลากรูปภาพหรือคลิปมาวาง", type=['jpg', 'png', 'mp4'])
        if st.form_submit_button("📢 ส่งเข้าเครือข่าย"):
            f_data, f_type = None, None
            if uploaded_file:
                f_data = base64.b64encode(uploaded_file.getvalue()).decode()
                f_type = uploaded_file.type
            if msg or f_data:
                db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'file': f_data, 'ft': f_type, 'ts': time.time()})
                st.rerun()

    data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
    if data:
        for v in reversed(list(data.values())):
            st.markdown(f"**{v.get('u')}**: {v.get('m','')}")
            if v.get('file'):
                decoded = base64.b64decode(v['file'])
                if "image" in v['ft']: st.image(decoded)
                elif "video" in v['ft']: st.video(decoded)

def room_private():
    st.subheader("🔐 แชตส่วนตัวสายลับ")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 เลือกคู่สาย AGENT:", ["-- เลือก --"] + friends)
    
    if target != "-- เลือก --":
        rid = "_".join(sorted([st.session_state.user, target]))
        with st.form("private_form", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความลับ...")
            if st.form_submit_button("🚀 LOCK & SEND") and msg:
                db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                st.rerun()
        
        msgs = db.reference(f'private_rooms/{rid}').limit_to_last(15).get()
        if msgs:
            for v in reversed(list(msgs.values())):
                side = "right" if v['u'] == st.session_state.user else "left"
                st.markdown(f"<div style='text-align:{side}; color:{st.session_state.theme_color};'>{v['u']}: {v['m']}</div>", unsafe_allow_html=True)

def room_call():
    st.subheader("📞 ระบบโทร P2P")
    my_call_ref = db.reference(f'calls/{st.session_state.user}')
    call_data = my_call_ref.get()
    if call_data and call_data.get('status') == 'ringing':
        st.warning(f"🚨 AGENT {call_data['caller']} กำลังโทรหา...")
        if st.button("✅ รับสาย"): my_call_ref.update({'status': 'connected'})
        if st.button("❌ ปฏิเสธ"): my_call_ref.update({'status': 'missed'})

    target = st.text_input("ID เป้าหมายที่จะโทรหา:")
    if target and st.button("📞 เริ่มการโทร"):
        db.reference(f'calls/{target}').set({'caller': st.session_state.user, 'status': 'ringing', 'ts': time.time()})

def room_music():
    st.subheader("🎧 ระบบเพลงต่อเนื่อง")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files: 
        st.warning("ไม่พบไฟล์เพลง")
        return
    
    current = music_files[st.session_state.song_index]
    with open(current, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    st.components.v1.html(f'<audio controls autoplay style="width:100%"><source src="data:audio/mp3;base64,{audio_b64}"></audio>', height=100)
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️"): st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files); st.rerun()
    if col3.button("⏭️"): st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files); st.rerun()

def room_bio():
    st.subheader("🩺 ศูนย์วิเคราะห์สภาวะร่างกาย (Bio-Analysis)")
    st.write("📡 **หลักการทำงาน:** วัดพัลส์เบื้องต้นผ่านกล้อง")
    # (HTML/JS Bio Sensor ของนาย)
    st.info("💡 ความจริงจากระบบ: เป็นการวิเคราะห์เบื้องต้นเท่านั้น ไม่สามารถใช้แทนอุปกรณ์การแพทย์ได้")

def room_mission():
    st.subheader("📝 บันทึกภารกิจ (Missions)")
    with st.form("m_form", clear_on_submit=True):
        t = st.text_input("ระบุภารกิจใหม่:")
        if st.form_submit_button("💾 บันทึก") and t:
            try:
                db.reference('missions').push({'u': st.session_state.user, 't': t, 'ts': time.time()})
                st.success("บันทึกสำเร็จ!")
                time.sleep(0.5)
                st.rerun()
            except:
                st.error("📡 เชื่อมต่อฐานข้อมูลไม่ได้")
    
    st.write("---")
    try:
        data = db.reference('missions').limit_to_last(10).get()
        if data:
            for key, v in reversed(list(data.items())):
                st.info(f"📌 {v.get('t')} (โดย: {v.get('u')})")
    except: pass

# ==========================================
# 3. Main Execution (ล่างสุดของไฟล์)
# ==========================================

def main():
    st.set_page_config(page_title="SYNAPSE PRO", layout="wide")
    init_system()

    if not st.session_state.logged_in:
        room_login()
        return

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.write("---")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", st.session_state.bg_color)

    st.markdown(f"<style>.stApp {{ background-color: {st.session_state.bg_color}; }}</style>", unsafe_allow_html=True)

    tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "🌐 แชตรวม", "🔐 แชตส่วนตัว", "📞 โทร", "🎧 เพลง", "🩺 ตรวจร่างกาย", "📝 ภารกิจ"])
    
    with tabs[0]: room_core()
    with tabs[1]: room_radar()
    with tabs[2]: room_public()
    with tabs[3]: room_private()
    with tabs[4]: room_call()
    with tabs[5]: room_music()
    with tabs[6]: room_bio()
    with tabs[7]: room_mission()

if __name__ == "__main__":
    main()
