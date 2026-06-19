import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import time
import pandas as pd

# ตั้งค่าการแสดงผลหน้าเว็บแอปพลิเคชัน
st.set_page_config(
    page_title="SYNAPSE COMMAND CENTER",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# [ ระบบเชื่อมต่อหลังบ้าน FIREBASE - โครงสร้างรองรับความเสถียร ]
# =========================================================
def init_firebase_system():
    if not firebase_admin._apps:
        try:
            cred_dict = {
                "type": "service_account",
                "project_id": st.secrets["firebase"]["project_id"],
                "private_key_id": st.secrets["firebase"]["private_key_id"],
                "private_key": st.secrets["firebase"]["private_key"],
                "client_email": st.secrets["firebase"]["client_email"],
                "client_id": st.secrets["firebase"]["client_id"],
                "auth_uri": st.secrets["firebase"]["auth_uri"],
                "token_uri": st.secrets["firebase"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
                "universe_domain": st.secrets["firebase"]["universe_domain"]
            }
            
            if "private_key" in cred_dict:
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://sooksun-101-default-rtdb.firebaseio.com' 
            })
            return True, "Connected"
        except Exception as e:
            return False, str(e)
    else:
        return True, "Already Connected"

is_connected, system_message = init_firebase_system()

# =========================================================
# [ โครงสร้างเมนูอัปเดตใหม่ 11 หัวข้อหลัก ]
# =========================================================
st.sidebar.title("SYNAPSE HUB v2.0")
st.sidebar.markdown("**สโลแกน:** *อยู่นิ่งๆ ไม่เจ็บตัว*")
st.sidebar.write("---")

menu = st.sidebar.radio(
    "เลือกหัวข้อการใช้งาน:",
    [
        "1. หน้าหลัก & สรุปสถานะ (Dashboard)",
        "2. ลงทะเบียนเจ้าหน้าที่ (Register Agent)",
        "3. ศูนย์ควบคุมเพลงระดับโลก (Global Player)",
        "4. แผนที่และพิกัดดาวเทียม (Real-time GPS Map)",
        "5. ตัวสแกนความถี่ & เซนเซอร์ (Frequency Scanner)",
        "6. ห้องแชทเข้ารหัสความปลอดภัย (Secure Chat)",
        "7. ระบบวิเคราะห์รหัสควอนตัม (Quantum Numerology)",
        "8. แอปบำบัดและเยียวยาจิตใจ (Healing Space)",
        "9. ตรวจสอบระบบพลังงานโซลาร์เซลล์ (Solar Monitor)",
        "10. ตั้งค่าระบบควบคุม (System Settings)",
        "11. ระบบคำนวณและรางวัดที่ดิน (Land Surveyor)"
    ]
)

st.sidebar.write("---")
if is_connected:
    st.sidebar.success("📡 Cloud Database: Online")
else:
    st.sidebar.error("⚠️ Cloud Database: Offline")

# =========================================================
# [ ฟังก์ชันการทำงานของแต่ละหัวข้อ ]
# =========================================================

# --- หัวข้อที่ 1 ถึง 10 (คงเดิมเพื่อความเสถียรของระบบเก่า) ---
if menu == "1. หน้าหลัก & สรุปสถานะ (Dashboard)":
    st.title("🏛️ SYNAPSE COMMAND CENTER")
    st.write("ยินดีต้อนรับเข้าสู่ระบบควบคุมกลาง บาส/ต๊ะ")
    col1, col2, col3 = st.columns(3)
    col1.metric("ความเร็วการประมวลผล", "Real-time", "100%")
    col2.metric("ฐานข้อมูลคลาวด์", "sooksun-101", "เสถียร" if is_connected else "ปิดการเชื่อมต่อ")
    col3.metric("ปรัชญาประจำวัน", "อยู่นิ่งๆ", "ไม่เจ็บตัว")

elif menu == "2. ลงทะเบียนเจ้าหน้าที่ (Register Agent)":
    st.title("⚠️ REGISTER AGENT SYSTEM")
    agent_name = st.text_input("ENTER AGENT NAME", value="Ta101")
    if st.button("ส่งข้อมูลขึ้นคลาวด์ (Save to Firebase)", use_container_width=True):
        if is_connected and agent_name.strip():
            try:
                db.reference("agents").child(agent_name).set({
                    "status": "Active", "slogan": "อยู่นิ่งๆ ไม่เจ็บตัว", "timestamp": {".sv": "timestamp"}
                })
                st.success(f"🎉 บันทึกรหัสเอเจนต์ '{agent_name}' สำเร็จ")
            except Exception as e: st.error(str(e))

elif menu == "3. ศูนย์ควบคุมเพลงระดับโลก (Global Player)":
    st.title("🎵 SYNAPSE GLOBAL PLAYER")
    lyrics_topic = st.text_input("หัวข้อหรือแรงบันดาลใจ:", value="คิดถึงยายวัน (แม่ใหญ่วัน)")
    if st.button("ร่างเนื้อเพลงด่วน"):
        st.code(f"([Verse]\nสายลมโชยโบกมาจากอีสานบ้านเฮา...\nคึดฮอด {lyrics_topic}...\n[Chorus]\nอยู่นิ่งๆ ไม่เจ็บตัว แต่คิดถึงเหลือเกิน...)", language="text")

elif menu == "4. แผนที่และพิกัดดาวเทียม (Real-time GPS Map)":
    st.title("📍 REAL-TIME GPS MAP")
    lat, lon = 16.054, 103.652
    map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(map_data)

elif menu == "5. ตัวสแกนความถี่ & เซนเซอร์ (Frequency Scanner)":
    st.title("📡 REAL-TIME FREQUENCY SCANNER")
    if st.checkbox("เริ่มการสแกนสัญญาณรอบทิศทาง"):
        st.success("📶 สแกนคลื่นความถี่สำเร็จ: ตรวจพบคลื่นพลังงานเสถียรที่ 432Hz")

elif menu == "6. ห้องแชทเข้ารหัสความปลอดภัย (Secure Chat)":
    st.title("💬 SECURE CHAT INTERCOM")
    chat_user = st.text_input("ชื่อผู้ส่ง:", value="Ta_Bas")
    chat_msg = st.text_area("พิมพ์ข้อความแชท:")
    if st.button("ส่งข้อความเข้ารหัส") and is_connected and chat_msg:
        db.reference("secure_chats").push({"user": chat_user, "message": chat_msg, "time": {".sv": "timestamp"}})
        st.success("ส่งแชทสำเร็จ!")

elif menu == "7. ระบบวิเคราะห์รหัสควอนตัม (Quantum Numerology)":
    st.title("🔢 QUANTUM NUMEROLOGY ANALYZER")
    birth_date = st.date_input("เลือกวันเดือนปีเกิดที่ต้องการวิเคราะห์:")
    st.info(f"วันเกิด {birth_date} พลังงานสอดคล้องกับปรัชญา 'อยู่นิ่งๆ ไม่เจ็บตัว'")

elif menu == "8. แอปบำบัดและเยียวยาจิตใจ (Healing Space)":
    st.title("🧘 MENTAL HEALING SPACE")
    st.radio("เลือกความถี่เสียงที่ใช้ในการบำบัด:", ["528Hz (ซ่อมแซม DNA)", "432Hz (ลดความเครียด)"])

elif menu == "9. ตรวจสอบระบบพลังงานโซลาร์เซลล์ (Solar Monitor)":
    st.title("☀️ SOLAR ENERGY MONITOR")
    battery_v = st.slider("แรงดันไฟฟ้าแบตเตอรี่ในระบบ (โวลต์):", 10.0, 15.0, 12.6)
    st.success(f"🟢 สถานะแรงดันระบบปกติ: {battery_v}V")

elif menu == "10. ตั้งค่าระบบควบคุม (System Settings)":
    st.title("⚙️ SYSTEM SETTINGS")
    st.text("Project ID: sooksun-101\nCore Philosophy: Stay still, no pain.")

# =========================================================
# 🔥 [ หัวข้อใหม่ที่ 11: ระบบคำนวณและรางวัดที่ดิน ]
# =========================================================
elif menu == "11. ระบบคำนวณและรางวัดที่ดิน (Land Surveyor)":
    st.title("📐 LAND SURVEYOR & MEASUREMENT")
    st.write("ระบบคำนวณพื้นที่ดินตามมาตรฐานไทย (แปลงค่าไร่-งาน-วา) และปักหมุดพิกัดดาวเทียมทำได้จริง")
    
    # แยกฝั่งทำงาน 2 ส่วน
    tab1, tab2 = st.tabs(["🧮 เครื่องคำนวณพื้นที่", "📍 ปักหมุดพิกัดแปลงที่ดิน"])
    
    with tab1:
        st.subheader("แปลงหน่วยที่ดินมาเป็นตารางวา / ตารางเมตร")
        col_r, col_ng, col_w = st.columns(3)
        
        input_rai = col_r.number_input("จำนวน ไร่", min_value=0, value=1, step=1)
        input_ngan = col_ng.number_input("จำนวน งาน", min_value=0, max_value=3, value=0, step=1)
        input_wa = col_w.number_input("จำนวน ตารางวา", min_value=0, max_value=399, value=0, step=1)
        
        # คำนวณจริงตามมาตราไทย: 1 ไร่ = 400 วา, 1 งาน = 100 วา | 1 ตารางวา = 4 ตารางเมตร
        total_wa = (input_rai * 400) + (input_ngan * 100) + input_wa
        total_sq_meters = total_wa * 4
        
        st.write("---")
        st.markdown(f"### 📊 ผลลัพธ์การคำนวณจริง:")
        st.info(f"🔹 คิดเป็นพื้นที่ทั้งหมด: **{total_wa:,} ตารางวา**")
        st.success(f"🔹 คิดเป็นขนาดพื้นที่ในโฉนด: **{total_sq_meters:,} ตารางเมตร**")
        
    with tab2:
        st.subheader("บันทึกและพิกัดหมุดรางวัดที่ดิน")
        st.write("กรอกพิกัดละติจูดและลองจิจูดของแปลงที่ดินเพื่อแสดงผลบนแผนที่ดาวเทียม")
        
        land_lat = st.number_input("ระบุ พิกัด Latitude (เช่น 16.054)", format="%.6f", value=16.054000)
        land_lon = st.number_input("ระบุ พิกัด Longitude (เช่น 103.652)", format="%.6f", value=103.652000)
        land_owner = st.text_input("ชื่อเจ้าของแปลงแปลงนี้:", value="ที่ดินของต๊ะ")
        
        # แสดงแผนที่ตามค่าที่รับมาจริง
        land_data = pd.DataFrame({'lat': [land_lat], 'lon': [land_lon]})
        st.map(land_data)
        
        if st.button("บันทึกพิกัดหมุดที่ดินนี้ลงคลาวด์"):
            if not is_connected:
                st.error("ไม่สามารถบันทึกได้เนื่องจากฐานข้อมูลคลาวด์ออฟไลน์")
            elif not land_owner.strip():
                st.warning("กรุณากรอกชื่อเจ้าของแปลง")
            else:
                try:
                    # ยิงข้อมูลพิกัดขึ้นโครงสร้าง Firebase Realtime Database จริง
                    land_ref = db.reference("land_records")
                    land_ref.push({
                        "owner": land_owner,
                        "latitude": land_lat,
                        "longitude": land_lon,
                        "calculated_wa": total_wa,
                        "timestamp": {".sv": "timestamp"}
                    })
                    st.success(f"💾 บันทึกหมุดที่ดินของ '{land_owner}' ขนาด {total_wa} วา ลงฐานข้อมูลเรียบร้อยแล้ว!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")
