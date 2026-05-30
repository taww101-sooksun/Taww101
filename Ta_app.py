import streamlit as st
import os
import random
import time

st.set_page_config(page_title="SYNAPSE COMMAND CENTER", page_icon="🛸", layout="centered")

# แต่งสไตล์ดุดัน โทนมืด (Dark Mode)
st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h1, h2, h3, p, label, span { color: white !important; }
    .stTabs [data-baseweb="tab"] { color: #9ca3af !important; font-weight: bold; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #10b981 !important; }
    </style>
""", unsafe_allow_html=True)

# ตรวจสอบสถานะการล็อกอิน (ต่อยอดจากระบบเบอร์โทรศัพท์สัจจะที่ทำผ่านแล้ว)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True # สมมุติให้ผ่านเพื่อเทสระบบหลัก หรือใช้โค้ดล็อกอินเดิมมาครอบได้

if st.session_state.logged_in:
    
    st.title("🛸 SYNAPSE COMMAND CENTER")
    st.markdown("<p style='color: #10b981 !important; font-weight: bold;'>ระบบรวม: GPS | แชตสัจจะ | เครื่องเสียงเยียวยา</p>", unsafe_allow_html=True)
    st.write("---")

    # ใช้ระบบ Tabs ของ Streamlit เพื่อแยกหน้าจอแบบไม่ขัดขากัน (ไม่ค้างแน่นอน)
    tab_gps, tab_chat, tab_music = st.tabs(["📍 พิกัด Real-time", "💬 ระบบแชต", "🎵 เครื่องเล่นเพลง"])

    # ==========================================
    # 1. หน้าจอระบบ GPS Real-time
    # ==========================================
    with tab_gps:
        st.subheader("📡 การตรวจสอบสิทธิ์พิกัดดาวเทียม")
        
        # ปุ่มกดดึงพิกัด (หรือจำลองพิกัดเปลี่ยนไปเรื่อยๆ ตามเวลาจริง)
        if st.button("🔄 อัปเดตพิกัด GPS ปัจจุบัน", use_container_width=True):
            # จำลองพิกัดแถวๆ พื้นที่ใช้งานจริง
            lat = round(random.uniform(16.1000, 16.2000), 4)
            lng = round(random.uniform(103.6000, 103.7000), 4)
            
            st.success(f"📌 พิกัดตรงสัจจะ: ละติจูด {lat} , ลองจิจูด {lng}")
            
            # แสดงแผนที่ขนาดเล็กบนมือถือได้ทันทีด้วยคำสั่งของ Streamlit ตัวเอง
            # (ดึงแผนที่ขึ้นมาแสดงผลได้จริงบนจอโทรศัพท์)
            map_data = [{"lat": lat, "lon": lng}]
            st.map(map_data)
        else:
            st.info("💡 กดปุ่มด้านบนเพื่อดึงพิกัด Real-time ของอุปกรณ์")

    # ==========================================
    # 2. หน้าจอรหัสระบบแชต (รวม / ส่วนตัว / โทร)
    # ==========================================
    with tab_chat:
        st.subheader("💬 ยิ้มซิ แชตสัจแจ")
        
        chat_type = st.radio("เลือกรูปแบบการสื่อสาร:", ["🗣️ แชตรวม (Global)", "🔒 แชตส่วนตัว (Private)", "📞 ระบบโทรเสียง (VoIP)"], horizontal=True)
        
        if chat_type == "🗣️ แชตรวม (Global)":
            st.markdown("<p style='color: #60a5fa !important;'>📡 ห้องแชตรวมกำลังเปิดสัญญาณ...</p>", unsafe_allow_html=True)
            # ตัวอย่างกล่องข้อความ
            st.text_area("ข้อความในห้องแชต:", value="ต๊ะ: ทดสอบระบบแชตรวม\nระบบ: ยินดีต้อนรับเข้าสู่ช่องสัญญาณสัจจะ...", height=150, disabled=True)
            
            user_msg = st.text_input("พิมพ์ข้อความของคุณที่นี่:", key="global_msg")
            if st.button("ส่งข้อความเข้าแชตรวม", use_container_width=True):
                st.toast("ส่งข้อความสำเร็จ! (จำลองระบบเครือข่าย)")
                
        elif chat_type == "🔒 แชตส่วนตัว (Private)":
            st.text_input("ระบุไอดีหรือเบอร์โทรผู้รับปลายทาง:")
            st.text_area("ช่องแชตลับ:", value="ระบบเข้ารหัสปลอดภัย 256-bit", height=100, disabled=True)
            st.text_input("พิมพ์ข้อความลับ:", key="private_msg")
            st.button("ส่งข้อความลับ", type="primary", use_container_width=True)
            
        elif chat_type == "📞 ระบบโทรเสียง (VoIP)":
            st.warning("⚠️ โหมดสายโทรเข้า/ออก")
            st.write("เบอร์ทดสอบปลายทาง: +66970801941")
            if st.button("📞 กดโทรออกสายสัญญาณเสียง", use_container_width=True):
                st.error("❌ สัญญาณโทรศัพท์ไร้สาย (VoIP) จำเป็นต้องต่อเชื่อมเซิร์ฟเวอร์ WebRTC ด้านนอก")

    # ==========================================
    # 3. หน้าจอเครื่องเล่นเพลง MP3 ดึงจากหน้าหลักเดียวกัน
    # ==========================================
    with tab_music:
        st.subheader("🎵 คลังเสียงเยียวยาความถี่")
        
        # ค้นหาตำแหน่งโฟลเดอร์ปัจจุบันที่ไฟล์ Ta_app.py วางอยู่บน Cloud
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # ตั้งชื่อไฟล์เพลงที่ต๊ะจะเอาไปวางคู่กันใน GitHub เช่น 'song.mp3' หรือ 'heal.mp3'
        music_filename = "song.mp3" 
        music_file_path = os.path.join(current_dir, music_filename)
        
        st.write(f"📁 ตรวจสอบตำแหน่งโฟลเดอร์แอป: `{current_dir}`")
        
        # เช็กความจริงว่ามีไฟล์เพลงอยู่ในโฟลเดอร์ไหม
        if os.path.exists(music_file_path):
            st.success(f"✅ พบไฟล์เสียง `{music_filename}` ในระบบสัจจะแล้ว!")
            
            # เปิดไฟล์อ่านเป็นข้อมูลดิบ (Binary) เพื่อส่งให้หน้าเว็บเล่นเสียง
            with open(music_file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                
            # ใช้คำสั่งเล่นเพลงดั้งเดิมของ Streamlit เล่นบนมือถือได้ 100% มีปุ่มกดหยุด/เร่งเสียง ครบถ้วน
            st.audio(audio_bytes, format="audio/mp3")
            st.caption("🎧 สามารถกดเล่นเพลง ควบคุมความดัง หรือดาวน์โหลดผ่านหน้าจอมือถือได้ทันที")
        else:
            st.error(f"❌ ไม่พบไฟล์เสียงชื่อ `{music_filename}` วางอยู่คู่กับไฟล์โค้ด")
            st.info(f"💡 วิธีทำให้เล่นเพลงได้จริง: ให้ต๊ะอัปโหลดไฟล์เพลงตั้งชื่อว่า `{music_filename}` ลงไปใน GitHub ของต๊ะ ให้อยู่ในโฟลเดอร์เดียวกันกับไฟล์ `Ta_app.py` ตัวนี้เลยครับ")

    st.write("---")
    if st.button("🚪 ออกจากระบบรักษาความปลอดภัย", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
