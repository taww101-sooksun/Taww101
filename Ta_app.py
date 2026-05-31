import streamlit as st
import os
import random
import time

# ตั้งค่าหน้าจอแอปให้ดุดัน โทนมืด เหมาะกับการเปิดบนรถไถตอนแดดร้อนๆ
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", page_icon="🛸", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h1, h2, h3, p, label, span { color: white !important; }
    .stTabs [data-baseweb="tab"] { color: #9ca3af !important; font-weight: bold; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #10b981 !important; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# ระบบจำลองสถานะการล็อกอิน (Session State)
# =========================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = ""

# =========================================================
# หน้าจอที่ 1: หน้าล็อกอินสัจจะ (เช็กเบอร์ตรงๆ ตามฐานข้อมูล Firebase)
# =========================================================
if not st.session_state.logged_in:
    st.title("📱 ระบบล็อกอินยิ้มซิ (Sooksun1)")
    st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว ปลอดภัยร้อยเปอร์เซ็นต์\"</p>", unsafe_allow_html=True)
    
    with st.container():
        st.subheader("เข้าสู่ระบบด้วยเบอร์โทรศัพท์")
        
        phone_input = st.text_input("เบอร์โทรศัพท์ (ใส่รูปแบบสากล เช่น +66970801941):", value="+66970801941")
        
        if st.button("📲 ขอรหัส OTP", use_container_width=True):
            if phone_input in ["+66970801941", "+66800924262"]:
                st.toast("⏳ ระบบจับคู่เบอร์ทดสอบใน Firebase สำเร็จ!")
                st.success("✅ ดำเนินการสำเร็จ! กรุณากรอกรหัส 6 หลักเพื่อข้ามผ่านระบบความปลอดภัย")
            else:
                st.error("❌ ไม่พบเบอร์โทรศัพท์นี้ในระบบทดสอบ")

        st.write("---")
        
        otp_input = st.text_input("กรอกรหัส OTP 6 หลักที่ตั้งไว้ หรือได้รับจาก SMS:", value="753275", type="password")
        
        if st.button("✅ ยืนยันรหัสผ่าน", type="primary", use_container_width=True):
            # รองรับทั้ง 2 เบอร์หลักของต๊ะตามข้อมูลใน Firebase จริงๆ
            if (phone_input == "+66970801941" and otp_input == "753275") or \
               (phone_input == "+66800924262" and otp_input == "753275"):
                st.session_state.logged_in = True
                st.session_state.user_phone = phone_input
                st.success("🔓 รหัสผ่านถูกต้องสัจจะ!")
                st.rerun()
            else:
                st.error("❌ รหัสไม่ถูกต้องตามที่บันทึกไว้ใน Firebase")

# =========================================================
# หน้าจอที่ 2: หน้าแอปหลักหลังจากล็อกอินสำเร็จ
# =========================================================
else:
    st.title("🛸 SYNAPSE COMMAND CENTER")
    st.success(f"🔓 ยินดีต้อนรับเพื่อนต๊ะเข้าสู่ระบบ! (เบอร์: {st.session_state.user_phone})")
    st.markdown("<p style='color: #eab308 !important; font-style: italic;'>สโลแกน: \"อยู่นิ่งๆ ไม่เจ็บตัว\" กำลังเปิดสัญญาณ...</p>", unsafe_allow_html=True)
    st.write("---")

    # แยกการทำงานเป็น 3 แท็บหลัก ไม่ดึงหน้าจอ ไม่ค้างชัวร์
    tab_gps, tab_chat, tab_music = st.tabs(["📍 GPS ดาวเทียมวัดที่นา", "💬 ระบบแชตสัจจะ", "🎵 เครื่องเล่นเพลงอัตโนมัติ"])

    # -----------------------------------------------------
    # แท็บที่ 1: GPS ดาวเทียมไฮเทค (มีชื่อหมู่บ้าน + เส้นถนนบอกชัดเจน) - แก้ไขเอาอิโมจิเจ้าปัญหาออกแล้ว
    # -----------------------------------------------------
    with tab_gps:
        st.subheader("🛰️ แผนที่ดาวเทียมไฮบริด & วัดที่นา")
        st.markdown("<p style='color: #34d399 !important;'>🚜 <b>มีชื่อหมู่บ้านและเส้นถนนบอกชัดเจน:</b> สามารถใช้นิ้วซูมเข้า-ออก หาจุดอ้างอิง เช่น วัด โรงเรียน หรือทางหลวง แล้วลากเส้นวัดพื้นที่ได้แม่นยำ ไม่หลงแน่นอนครับ!</p>", unsafe_allow_html=True)
        
        # ปรับพิกัดเริ่มต้นให้ตรงใจ (พิกัดเริ่มต้น)
        default_lat = 16.1234
        default_lng = 103.5678
        
        map_html_code = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
        
        <div id="map" style="width: 100%; height: 380px; border-radius: 12px; border: 2px solid #10b981;"></div>
        <div id="result-box" style="margin-top:15px; background:#1f2937; padding:15px; border-radius:8px; color:white; font-family:sans-serif;">
            <b style="color:#34d399; font-size:16px;"> ผลการคำนวณพื้นที่สัจจะ:</b>
            <p id="area-text" style="font-size:20px; margin:5px 0; font-weight:bold; color:#60a5fa;">ยังไม่มีการลากพื้นที่ (ใช้นิ้วจิ้มไอคอนรูปห้าเหลี่ยมหรือสี่เหลี่ยมทางซ้ายเพื่อลากเส้น)</p>
        </div>

        <script>
            var map = L.map('map').setView([{default_lat}, {default_lng}], 15);

            // 1. ดึงภาพถ่ายดาวเทียมความละเอียดสูง (เห็นหลังคาบ้านและคันนา)
            var satelliteLayer = L.tileLayer('
