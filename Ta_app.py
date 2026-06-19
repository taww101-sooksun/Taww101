import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import time
import pandas as pd
import folium
from streamlit_folium import st_folium

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

# เรียกใช้งานการเชื่อมต่อระบบ
is_connected, system_message = init_firebase_system()

# =========================================================
# [ โครงสร้างเมนูอัปเดตใหม่ 11 หัวข้อหลัก (Sidebar Navigation) ]
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
# [ ฟังก์ชันการทำงานของแต่ละหัวข้อ - ชิดซ้ายระนาบเดียวกันทั้งหมด ]
# =========================================================

# --- หัวข้อที่ 1: หน้าหลัก & สรุปสถานะ ---
if menu == "1. หน้าหลัก & สรุปสถานะ (Dashboard)":
    st.title("🏛️ SYNAPSE COMMAND CENTER")
    st.write("ยินดีต้อนรับเข้าสู่ระบบควบคุมกลาง บาส/ต๊ะ แอปพลิเคชันถูกรันผ่านอุปกรณ์พกพาอย่างสมบูรณ์แบบ")
    col1, col2, col3 = st.columns(3)
    col1.metric("ความเร็วการประมวลผล", "Real-time", "100%")
    col2.metric("ฐานข้อมูลคลาวด์", "sooksun-101", "เสถียร" if is_connected else "ปิดการเชื่อมต่อ")
    col3.metric("ปรัชญาประจำวัน", "อยู่นิ่งๆ", "ไม่เจ็บตัว")
    if is_connected:
        st.info("💡 ข้อมูลระบบ: สัญญาณเครือข่ายพร้อมใช้งาน พร้อมเชื่อมต่ออัปเดตข้อมูลแบบทันทีอนุกรมเวลา")
    else:
        st.error(f"เกิดปัญหาเชื่อมต่อระบบฐานข้อมูล: {system_message}")

# --- หัวข้อที่ 2: ลงทะเบียนเจ้าหน้าที่ ---
elif menu == "2. ลงทะเบียนเจ้าหน้าที่ (Register Agent)":
    st.title("⚠️ REGISTER AGENT SYSTEM")
    st.write("บันทึกรหัสสัญญาณเจ้าหน้าที่เข้าสู่ฐานข้อมูลคลาวด์ Firebase เพื่อยืนยันตน")
    agent_name = st.text_input("ENTER AGENT NAME", value="Ta101")
    if st.button("ส่งข้อมูลขึ้นคลาวด์ (Save to Firebase)", use_container_width=True):
        if not is_connected:
            st.error(f"ระบบเชื่อมต่อหลังบ้านตรวจพบปัญหา: {system_message}")
        elif not agent_name.strip():
            st.warning("กรุณากรอกรหัสชื่อก่อน")
        else:
            try:
                ref = db.reference("agents")
                ref.child(agent_name).set({
                    "status": "Active",
                    "slogan": "อยู่นิ่งๆ ไม่เจ็บตัว",
                    "timestamp": {".sv": "timestamp"}
                })
                st.success(f"🎉 สำเร็จ! บันทึกรหัสเอเจนต์ '{agent_name}' เรียบร้อย")
                st.balloons()
            except Exception as e:
                st.error(f"ระบบไม่สามารถเข้าถึงฐานข้อมูลคลาวด์ได้: {e}")

# --- หัวข้อที่ 3: ศูนย์ควบคุมเพลงระดับโลก ---
elif menu == "3. ศูนย์ควบคุมเพลงระดับโลก (Global Player)":
    st.title("🎵 SYNAPSE GLOBAL PLAYER")
    st.write("ห้องควบคุมเสียงเพลงและเนื้อร้องสำหรับนำข้อความไปใช้ในเครื่องมือสร้างเพลง AI (เช่น Suno AI)")
    genre = st.selectbox("เลือกแนวเพลงที่ต้องการแต่ง:", ["R&B", "Rap / Hip Hop", "ลูกทุ่งหมอลำ", "Alternative"])
    lyrics_topic = st.text_input("หัวข้อหรือแรงบันดาลใจ:", value="คิดถึงยายวัน (แม่ใหญ่วัน)")
    if st.button("ร่างเนื้อเพลงด่วน"):
        st.write("🤖 **เนื้อร้องตัวอย่างที่ระบบประมวลผลให้:**")
        st.code(f"([Verse]\nสายลมโชยโบกมาจากอีสานบ้านเฮา...\nหัวใจเหงาคึดฮอดคนที่อยู่บนฟ้า...\n{lyrics_topic} ในใจไม่เคยเลือนลา...\n[Chorus]\nอยู่นิ่งๆ ไม่เจ็บตัว แต่คิดถึงเหลือเกิน...)", language="text")

# --- หัวข้อที่ 4: แผนที่และพิกัดดาวเทียม ---
elif menu == "4. แผนที่และพิกัดดาวเทียม (Real-time GPS Map)":
    st.title("📍 REAL-TIME GPS MAP")
    st.write("จำลองการแสดงพิกัดและการติดตามตำแหน่งผ่านสัญญาณดาวเทียม")
    lat, lon = 16.054, 103.652
    map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(map_data)
    st.metric("พิกัดปัจจุบัน (ละติจูด, ลองจิจูด)", f"{lat}, {lon}")

# --- หัวข้อที่ 5: ตัวสแกนความถี่ & เซนเซอร์ ---
elif menu == "5. ตัวสแกนความถี่ & เซนเซอร์ (Frequency Scanner)":
    st.title("📡 REAL-TIME FREQUENCY SCANNER")
    st.write("หน้าต่างจำลองการทำงานของเซนเซอร์ความสั่นสะเทือนและการอ่านค่าความถี่จิตสำนึก")
    scan_active = st.checkbox("เริ่มการสแกนสัญญาณรอบทิศทาง")
    if scan_active:
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)
        st.success("📶 สแกนคลื่นความถี่สำเร็จ: ตรวจพบคลื่นพลังงานเสถียรที่ 432Hz (คลื่นบำบัด)")

# --- หัวข้อที่ 6: ห้องแชทเข้ารหัสความปลอดภัย ---
elif menu == "6. ห้องแชทเข้ารหัสความปลอดภัย (Secure Chat)":
    st.title("💬 SECURE CHAT INTERCOM")
    st.write("กล่องข้อความสื่อสารภายในเครือข่าย (ข้อมูลจะถูกซิงค์ผ่าน Firebase)")
    chat_user = st.text_input("ชื่อผู้ส่ง:", value="Ta_Bas")
    chat_msg = st.text_area("พิมพ์ข้อความแชท:")
    if st.button("ส่งข้อความเข้ารหัส"):
        if is_connected and chat_msg:
            try:
                db.reference("secure_chats").push({
                    "user": chat_user,
                    "message": chat_msg,
                    "time": {".sv": "timestamp"}
                })
                st.success("ส่งแชทเข้ารหัสสำเร็จ!")
            except Exception as e:
                st.error(f"แชทล้มเหลว: {e}")
        else:
            st.warning("กรุณาพิมพ์ข้อความหรือตรวจสอบการเชื่อมต่อฐานข้อมูล")

# --- หัวข้อที่ 7: ระบบวิเคราะห์รหัสควอนตัม ---
elif menu == "7. ระบบวิเคราะห์รหัสควอนตัม (Quantum Numerology)":
    st.title("🔢 QUANTUM NUMEROLOGY ANALYZER")
    st.write("คำนวณและวิเคราะห์ความสัมพันธ์ของตัวเลข พลังงานดวงดาว และลำดับรหัสควอนตัมของชีวิต")
    birth_date = st.date_input("เลือกวันเดือนปีเกิดที่ต้องการวิเคราะห์:")
    lucky_num = st.number_input("รหัสตัวเลขประจำตัว (ถ้ามี):", value=101)
    if st.button("ถอดรหัสความถี่ควอนตัม"):
        st.write("🔮 **ผลการวิเคราะห์รูปแบบพลังงานดวงดาว:**")
        st.info(f"วันเกิด {birth_date} ร่วมกับรหัสเลข {lucky_num} สะท้อนคลื่นพลังงานเชิงรับที่แข็งแกร่ง สอดคล้องกับปรัชญา 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- หัวข้อที่ 8: แอปบำบัดและเยียวยาจิตใจ ---
elif menu == "8. แอปบำบัดและเยียวยาจิตใจ (Healing Space)":
    st.title("🧘 MENTAL HEALING SPACE")
    st.write("พื้นที่สำหรับปรับแต่งคลื่นความถี่เสียงและเสียงดนตรีเพื่อการเยียวยาจิตใจ")
    frequency_mode = st.radio("เลือกความถี่เสียงที่ใช้ในการบำบัดตามอาการ:", 
                              ["528Hz (ซ่อมแซม DNA และยกระดับจิตใจ)", 
                               "432Hz (ลดความเครียดและความกังวล)", 
                               "396Hz (ปลดปล่อยความกลัวและความรู้สึกผิด)"])
    st.write(f"🎧 ขณะนี้ระบบจำลองการปล่อยสัญญานคลื่นความถี่เสียง: **{frequency_mode}**")

# --- หัวข้อที่ 9: ตรวจสอบระบบพลังงานโซลาร์เซลล์ ---
elif menu == "9. ตรวจสอบระบบพลังงานโซลาร์เซลล์ (Solar Monitor)":
    st.title("☀️ SOLAR ENERGY MONITOR")
    st.write("หน้าจอตรวจสอบแรงดันไฟฟ้าและแบตเตอรี่ 12V ร่วมกับคอนโทรลเลอร์ Lebento")
    battery_v = st.slider("แรงดันไฟฟ้าแบตเตอรี่ในระบบ (โวลต์):", 10.0, 15.0, 12.6)
    if battery_v < 11.5:
        st.error(f"⚡ แรงดันต่ำผิดปกติ ({battery_v}V): กรุณาตรวจสอบอินเวอร์เตอร์!")
    elif battery_v >= 14.2:
        st.warning(f"🔋 แบตเตอรี่เต็มกำลังชาร์จตัด ({battery_v}V): ระบบควบคุม Lebento ทำงานปกติ")
    else:
        st.success(f"🟢 สถานะระบบปกติ ({battery_v}V): พลังงานแสงอาทิตย์ไหลเวียนคงที่")

# --- หัวข้อที่ 10: ตั้งค่าระบบควบคุม ---
elif menu == "10. ตั้งค่าระบบควบคุม (System Settings)":
    st.title("⚙️ SYSTEM SETTINGS")
    st.write("ปรับแต่งและดูแลรักษาความปลอดภัยของระบบ Command Center")
    st.checkbox("เปิดโหมดการเข้ารหัสข้อมูลระดับสูง (High Encryption)", value=True)
    st.checkbox("เปิดโหมดใช้งานประหยัดพลังงานบนมือถือ (Mobile Optimized)", value=True)
    st.write("---")
    st.write("**สถานะการติดตั้งระบบ:**")
    st.text(f"Project ID: sooksun-101\nPlatform: Streamlit Mobile Web App\nCore Philosophy: Stay still, no pain.")

# --- หัวข้อที่ 11: ระบบรางวัดและแผนที่วาดกรอบแปลงที่ดินจริง ---
elif menu == "11. ระบบคำนวณและรางวัดที่ดิน (Land Surveyor)":
    st.title("📐 LAND BOUNDARY CONTROL CENTER")
    st.write("ระบบแผนที่ดาวเทียมจำลองการวาดกรอบขอบเขตที่ดินเป็นล็อกแยกรายบุคคล")

    tab1, tab2 = st.tabs(["🗺️ แผนที่แสดงกรอบที่ดินรวม", "➕ บันทึกกรอบที่ดินใหม่"])

    with tab1:
        st.subheader("🌐 ผังแปลงที่ดินดาวเทียม (เห็นขอบเขตชัดเจน)")
        center_lat, center_lon = 16.054000, 103.652000
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=18, tiles='OpenStreetMap')
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='แผนที่ดาวเทียม (Satellite)',
            overlay=False,
            control=True
        ).add_to(m)
        folium.LayerControl().add_to(m)

        # จำลองล็อกกรอบที่ดินต๊ะ
        boundary_ta = [
            [16.054200, 103.651800],
            [16.054200, 103.652200],
            [16.053900, 103.652200],
            [16.053900, 103.651800]
        ]
        folium.Polygon(
            locations=boundary_ta,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.3,
            popup='<b>แปลงที่ดิน: ของต๊ะ</b><br>พื้นที่ประมาณ: 1 ไร่ 2 งาน'
        ).add_to(m)

        # จำลองล็อกกรอบที่ดินเพื่อนบ้าน
        boundary_neighbor = [
            [16.053900, 103.651800],
            [16.053900, 103.652200],
            [16.053600, 103.652200],
            [16.053600, 103.651800]
        ]
        folium.Polygon(
            locations=boundary_neighbor,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.2,
            popup='<b>แปลงที่ดิน: นายสมชาย</b><br>พื้นที่ประมาณ: 1 ไร่'
        ).add_to(m)

        st_folium(m, width="100%", height=450, returned_objects=[])

    with tab2:
        st.subheader("📝 โครงสร้างการคำนวณและบันทึกค่าไร่-งาน-วา")
        col_r, col_ng, col_w = st.columns(3)
        input_rai = col_r.number_input("จำนวน ไร่", min_value=0, value=1, step=1, key="rai_survey")
        input_ngan = col_ng.number_input("จำนวน งาน", min_value=0, max_value=3, value=0, step=1, key="ngan_survey")
        input_wa = col_w.number_input("จำนวน ตารางวา", min_value=0, max_value=399, value=0, step=1, key="wa_survey")
        
        total_wa = (input_rai * 400) + (input_ngan * 100) + input_wa
        st.write("---")
        st.markdown(f"### 📊 ขนาดพื้นที่: **{total_wa:,} ตารางวา**")
        
        land_owner_name = st.text_input("กรอกชื่อผู้ครอบครองแปลง:", value="ต๊ะ_บาส 101", key="owner_survey")
        if st.button("ส่งพิกัดฐานข้อมูลด่วน (Save to Firebase)", use_container_width=True):
            if is_connected and land_owner_name.strip():
                try:
                    db.reference("land_grids").push({
                        "owner": land_owner_name, "total_sq_wa": total_wa, "timestamp": {".sv": "timestamp"}
                    })
                    st.success("💾 บันทึกข้อมูลเรียบร้อย!")
                except Exception as e: 
                    st.error(str(e))
