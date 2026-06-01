import streamlit as st
import os

# ตั้งค่าหน้าจอแอป
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", page_icon="🛸", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h1, h2, h3, p, label, span { color: white !important; }
    .stTabs [data-baseweb="tab"] { color: #9ca3af !important; font-weight: bold; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #10b981 !important; }
    </style>
""", unsafe_allow_html=True)

# จำลองฐานข้อมูลแชตให้อยู่ในระบบจำลอง (ในใช้งานจริงจะผูกกับ Firebase)
if 'global_chats' not in st.session_state:
    st.session_state.global_chats = [
        {"user": "ระบบ", "msg": "ยินดีต้อนรับสู่ห้องแชตสัจจะ"},
        {"user": "+66970801941", "msg": "กำลังไปไถนารับจ้างครับ"}
    ]
if 'private_chats' not in st.session_state:
    st.session_state.private_chats = {}

# สมมุติตัวตนผู้ใช้ล็อกอิน (สืบทอดจากระบบเดิมของนาย)
user_phone = "+66970801941"

st.title("🛸 SYNAPSE COMMAND CENTER")
st.write("---")

tab_gps, tab_chat, tab_music = st.tabs(["📍 GPS ตำแหน่งจริง", "💬 ระบบแชตสัจจะ", "🎵 คลังเพลงในเครื่อง"])

# -----------------------------------------------------
# แท็บที่ 1: GPS ดึงพิกัดจริงจากมือถือคนใช้งาน
# -----------------------------------------------------
with tab_gps:
    st.subheader("🛰️ แผนที่ดาวเทียมจาก GPS จริงของนาย")
    st.caption("ระบบจะขอสิทธิ์เข้าถึงตำแหน่งจากมือถือ กรุณากด 'อนุญาต' เพื่อให้แผนที่เลื่อนไปจุดที่นายอยู่จริง")
    
    # JavaScript ดึงพิกัดจริงจากเบราว์เซอร์มือถือ
    gps_html = """
    <div id="status" style="color:#10b981; font-weight:bold; margin-bottom:10px;">กำลังค้นหาพิกัดดาวเทียม...</div>
    <div id="map" style="width: 100%; height: 350px; border-radius: 12px; border: 2px solid #10b981; background:#1f2937;"></div>
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <script>
        var map = L.map('map').setView([15.9513, 103.5796], 6); // พิกัดสำรองระหว่างรอโหลด
        
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19
        }).addTo(map);
        
        L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}').addTo(map);

        // คำสั่งขอพิกัดจริงจากอุปกรณ์มือถือ
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                
                document.getElementById('status').innerHTML = "📍 เชื่อมต่อ GPS สำเร็จ! พิกัดปัจจุบันของคุณ: " + lat.toFixed(5) + ", " + lng.toFixed(5);
                
                map.setView([lat, lng], 16);
                L.marker([lat, lng]).addTo(map).bindPopup('🚜 ตำแหน่งรถไถของนาย').openPopup();
            }, function(error) {
                document.getElementById('status').innerHTML = "❌ ดึงพิกัดล้มเหลว: โปรดเปิด GPS ที่มือถือและอนุญาตสิทธิ์เว็บ";
            }, {enableHighAccuracy: true});
        } else {
            document.getElementById('status').innerHTML = "❌ เครื่องนี้ไม่รองรับระบบ GPS ผ่านเว็บ";
        }
    </script>
    """
    st.components.v1.html(gps_html, height=420)

# -----------------------------------------------------
# แท็บที่ 2: ระบบแชตที่โต้ตอบขึ้นหน้าจอได้จริง
# -----------------------------------------------------
with tab_chat:
    st.subheader("💬 ศูนย์สื่อสารแชตยิ้มซิ")
    chat_mode = st.radio("เลือกห้องคุย:", ["🗣️ แชตรวม (Global)", "🔒 แชตส่วนตัว (Private)"], horizontal=True)
    
    if chat_mode == "🗣️ แชตรวม (Global)":
        st.write("**กระดานข้อความล่าสุด:**")
        # แสดงโพสต์/แชตเรียงลงมาให้เห็นจริง
        for chat in st.session_state.global_chats:
            st.markdown(f"**🟢 {chat['user']}:** {chat['msg']}")
            
        with st.form("global_form", clear_on_submit=True):
            user_msg = st.text_input("พิมพ์ข้อความส่งเข้าห้องรวม:")
            if st.form_submit_button("ส่งข้อความเข้าแชตรวม") and user_msg:
                st.session_state.global_chats.append({"user": user_phone, "msg": user_msg})
                st.rerun()
                
    elif chat_mode == "🔒 แชตส่วนตัว (Private)":
        friend_name = st.text_input("ใส่ชื่อเพื่อนหรือเบอร์โทรที่ต้องการคุยด้วย:", value="+66800924262")
        
        if friend_name:
            st.write(f"**🔒 ห้องคุยส่วนตัวกับ {friend_name}:**")
            # ดึงประวัติแชตเฉพาะของเพื่อนคนนี้
            room_id = tuple(sorted([user_phone, friend_name]))
            if room_id in st.session_state.private_chats:
                for chat in st.session_state.private_chats[room_id]:
                    st.markdown(f"**👤 {chat['user']}:** {chat['msg']}")
            else:
                st.caption("ยังไม่มีข้อความคุยกันในห้องนี้ เริ่มพิมพ์ด้านล่างได้เลย")
                
            with st.form("private_form", clear_on_submit=True):
                priv_msg = st.text_input("พิมพ์ข้อความลับ:")
                if st.form_submit_button("ส่งข้อความส่วนตัว") and priv_msg:
                    if room_id not in st.session_state.private_chats:
                        st.session_state.private_chats[room_id] = []
                    st.session_state.private_chats[room_id].append({"user": user_phone, "msg": priv_msg})
                    st.rerun()

# -----------------------------------------------------
# แท็บที่ 3: เครื่องเล่นเพลง ดึงไฟล์ทั้งหมดในเครื่อง
# -----------------------------------------------------
with tab_music:
    st.subheader("🎵 เครื่องเล่นเสียงคลังเพลง")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        # สแกนหาไฟล์ .mp3 ทั้งหมดที่อยู่ในโฟลเดอร์เดียวกันกับตัวโค้ด .py
        mp3_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.mp3')]
    except Exception:
        mp3_files = []
        
    if mp3_files:
        st.success(f"📂 ตรวจพบเพลงในโฟลเดอร์ทั้งหมด {len(mp3_files)} เพลง")
        # แสดงรายการเพลงทั้งหมดให้คนขับรถไถเลือกกดฟังเองได้เลย
        selected_song = st.selectbox("เลือกเพลงที่ต้องการฟัง:", mp3_files)
        
        music_path = os.path.join(current_dir, selected_song)
        with open(music_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            
        st.audio(audio_bytes, format="audio/mp3")
        st.caption(f"กำลังเล่น: {selected_song} (หมายเหตุ: การเล่นเพลงถัดไปอัตโนมัติบนหน้าเว็บมือถือจะติดระบบบล็อกเสียงของ Google Chrome/Safari แนะนำให้ใช้นิ้วกดเลือกเปลี่ยนเพลงตามใจชอบตรงเมนูด้านบนได้เลยเพื่อน)")
    else:
        st.error("❌ ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์แอป")
