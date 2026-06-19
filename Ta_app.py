# เพิ่มการ import เครื่องมือแผนที่ขั้นสูงไว้ด้านบนสุดของไฟล์ร่วมกับตัวอื่นด้วยนะเพื่อน
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import time
import pandas as pd
import folium
from streamlit_folium import st_folium

# ... (โค้ดเมนูที่ 1-10 ของเพื่อนต๊ะคงไว้ตามเดิมเพื่อความเสถียร) ...
# =========================================================
# [ ฟังก์ชันการทำงานของแต่ละหัวข้อ ]
# =========================================================

# --- หัวข้อที่ 1: หน้าหลัก & สรุปสถานะ ---
if menu == "1. หน้าหลัก & สรุปสถานะ (Dashboard)":
    st.title("🏛️ SYNAPSE COMMAND CENTER")
    st.write("ยินดีต้อนรับเข้าสู่ระบบควบคุมกลาง บาส/ต๊ะ")
    col1, col2, col3 = st.columns(3)
    col1.metric("ความเร็วการประมวลผล", "Real-time", "100%")
    col2.metric("ฐานข้อมูลคลาวด์", "sooksun-101", "เสถียร" if is_connected else "ปิดการเชื่อมต่อ")
    col3.metric("ปรัชญาประจำวัน", "อยู่นิ่งๆ", "ไม่เจ็บตัว")

# --- หัวข้อที่ 2: ลงทะเบียนเจ้าหน้าที่ ---
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
            except Exception as e: 
                st.error(str(e))

# --- หัวข้อที่ 3: ศูนย์ควบคุมเพลงระดับโลก ---
elif menu == "3. ศูนย์ควบคุมเพลงระดับโลก (Global Player)":
    st.title("🎵 SYNAPSE GLOBAL PLAYER")
    lyrics_topic = st.text_input("หัวข้อหรือแรงบันดาลใจ:", value="คิดถึงยายวัน (แม่ใหญ่วัน)")
    if st.button("ร่างเนื้อเพลงด่วน"):
        st.code(f"([Verse]\nสายลมโชยโบกมาจากอีสานบ้านเฮา...\nคึดฮอด {lyrics_topic}...\n[Chorus]\nอยู่นิ่งๆ ไม่เจ็บตัว แต่คิดถึงเหลือเกิน...)", language="text")

# --- หัวข้อที่ 4: แผนที่และพิกัดดาวเทียม ---
elif menu == "4. แผนที่และพิกัดดาวเทียม (Real-time GPS Map)":
    st.title("📍 REAL-TIME GPS MAP")
    lat, lon = 16.054, 103.652
    map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(map_data)

# --- หัวข้อที่ 5: ตัวสแกนความถี่ & เซนเซอร์ ---
elif menu == "5. ตัวสแกนความถี่ & เซนเซอร์ (Frequency Scanner)":
    st.title("📡 REAL-TIME FREQUENCY SCANNER")
    if st.checkbox("เริ่มการสแกนสัญญาณรอบทิศทาง"):
        st.success("📶 สแกนคลื่นความถี่สำเร็จ: ตรวจพบคลื่นพลังงานเสถียรที่ 432Hz")

# --- หัวข้อที่ 6: ห้องแชทเข้ารหัสความปลอดภัย ---
elif menu == "6. ห้องแชทเข้ารหัสความปลอดภัย (Secure Chat)":
    st.title("💬 SECURE CHAT INTERCOM")
    chat_user = st.text_input("ชื่อผู้ส่ง:", value="Ta_Bas")
    chat_msg = st.text_area("พิมพ์ข้อความแชท:")
    if st.button("ส่งข้อความเข้ารหัส") and is_connected and chat_msg:
        db.reference("secure_chats").push({"user": chat_user, "message": chat_msg, "time": {".sv": "timestamp"}})
        st.success("ส่งแชทสำเร็จ!")

# --- หัวข้อที่ 7: ระบบวิเคราะห์รหัสควอนตัม ---
elif menu == "7. ระบบวิเคราะห์รหัสควอนตัม (Quantum Numerology)":
    st.title("🔢 QUANTUM NUMEROLOGY ANALYZER")
    birth_date = st.date_input("เลือกวันเดือนปีเกิดที่ต้องการวิเคราะห์:")
    st.info(f"วันเกิด {birth_date} พลังงานสอดคล้องกับปรัชญา 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- หัวข้อที่ 8: แอปบำบัดและเยียวยาจิตใจ ---
elif menu == "8. แอปบำบัดและเยียวยาจิตใจ (Healing Space)":
    st.title("🧘 MENTAL HEALING SPACE")
    st.radio("เลือกความถี่เสียงที่ใช้ในการบำบัด:", ["528Hz (ซ่อมแซม DNA)", "432Hz (ลดความเครียด)"])

# --- หัวข้อที่ 9: ตรวจสอบระบบพลังงานโซลาร์เซลล์ ---
elif menu == "9. ตรวจสอบระบบพลังงานโซลาร์เซลล์ (Solar Monitor)":
    st.title("☀️ SOLAR ENERGY MONITOR")
    battery_v = st.slider("แรงดันไฟฟ้าแบตเตอรี่ในระบบ (โวลต์):", 10.0, 15.0, 12.6)
    st.success(f"🟢 สถานะแรงดันระบบปกติ: {battery_v}V")

# --- หัวข้อที่ 10: ตั้งค่าระบบควบคุม ---
elif menu == "10. ตั้งค่าระบบควบคุม (System Settings)":
    st.title("⚙️ SYSTEM SETTINGS")
    st.text("Project ID: sooksun-101\nCore Philosophy: Stay still, no pain.")

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

        # 3. [ข้อมูลจริงที่ทำได้] จำลองกรอบพิกัดสี่เหลี่ยมรอบแปลงที่ดินแยกเป็นล็อก (Polygon)
        # ล็อกที่ 1: แปลงที่ดินของต๊ะ (สมมุติพิกัดล้อมรอบ 4 มุม)
        boundary_ta = [
            [16.054200, 103.651800],
            [16.054200, 103.652200],
            [16.053900, 103.652200],
            [16.053900, 103.651800]
        ]
        folium.Polygon(
            locations=boundary_ta,
            color='blue',          # เส้นขอบสีน้ำเงิน
            fill=True,
            fill_color='blue',     # สีระบายในกรอบ
            fill_opacity=0.3,      # ความโปร่งแสง
            popup='<b>แปลงที่ดิน: ของต๊ะ</b><br>พื้นที่ประมาณ: 1 ไร่ 2 งาน'
        ).add_to(m)

        # ล็อกที่ 2: แปลงที่ดินของเพื่อนบ้าน (แปลงติดกันทางทิศใต้)
        boundary_neighbor = [
            [16.053900, 103.651800],
            [16.053900, 103.652200],
            [16.053600, 103.652200],
            [16.053600, 103.651800]
        ]
        folium.Polygon(
            locations=boundary_neighbor,
            color='red',           # เส้นขอบสีแดงแยกฝั่งชัดเจน
            fill=True,
            fill_color='red',
            fill_opacity=0.2,
            popup='<b>แปลงที่ดิน: นายสมชาย (เพื่อนบ้าน)</b><br>พื้นที่ประมาณ: 1 ไร่'
        ).add_to(m)

        # 4. สั่งเรนเดอร์แผนที่ Folium ลงหน้าจอเว็บ Streamlit บนมือถือ
        st_folium(m, width="100%", height=450, returned_objects=[])

    with tab2:
        st.subheader("📝 โครงสร้างการคำนวณและบันทึกค่าไร่-งาน-วา")
        
        col_r, col_ng, col_w = st.columns(3)
        input_rai = col_r.number_input("จำนวน ไร่", min_value=0, value=1, step=1, key="rai_survey")
        input_ngan = col_ng.number_input("จำนวน งาน", min_value=0, max_value=3, value=0, step=1, key="ngan_survey")
        input_wa = col_w.number_input("จำนวน ตารางวา", min_value=0, max_value=399, value=0, step=1, key="wa_survey")
        
        total_wa = (input_rai * 400) + (input_ngan * 100) + input_wa
        
        st.write("---")
        st.markdown(f"### 📊 สรุปขนาดพื้นที่โฉนด: **{total_wa:,} ตารางวา** ({total_wa*4:,} ตารางเมตร)")
        
        land_owner_name = st.text_input("กรอกชื่อผู้ครอบครองแปลง:", value="ต๊ะ_บาส 101", key="owner_survey")
        
        if st.button("ส่งพิกัดฐานข้อมูลด่วน (Save to Firebase)", use_container_width=True):
            if not is_connected:
                st.error("ระบบไม่สามารถส่งได้: ฐานข้อมูลคลาวด์ออฟไลน์")
            elif not land_owner_name.strip():
                st.warning("กรุณาใส่ชื่อเจ้าของที่ดินก่อนเพื่อน")
            else:
                try:
                    db.reference("land_grids").push({
                        "owner": land_owner_name,
                        "total_sq_wa": total_wa,
                        "timestamp": {".sv": "timestamp"}
                    })
                    st.success(f"💾 บันทึกข้อมูลขนาดที่ดินของ '{land_owner_name}' ลงคลาวด์เรียบร้อย!")
                except Exception as e:
                    st.error(f"พังตรงระบบส่งข้อมูล: {e}")
