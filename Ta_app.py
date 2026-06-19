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
# 🔥 [ หัวข้อที่ 11: ระบบรางวัดและแผนที่วาดกรอบแปลงที่ดินจริง ]
# =========================================================
elif menu == "11. ระบบคำนวณและรางวัดที่ดิน (Land Surveyor)":
    st.title("📐 LAND BOUNDARY CONTROL CENTER")
    st.write("ระบบแผนที่ดาวเทียมจำลองการวาดกรอบขอบเขตที่ดินเป็นล็อกแยกรายบุคคล")

    tab1, tab2 = st.tabs(["🗺️ แผนที่แสดงกรอบที่ดินรวม", "➕ บันทึกกรอบที่ดินใหม่"])

    with tab1:
        st.subheader("🌐 ผังแปลงที่ดินดาวเทียม (เห็นขอบเขตชัดเจน)")
        st.write("💡 *คำแนะนำสำหรับมือถือ: สามารถใช้นิ้วซูมเข้า-ออก หรือกดเปลี่ยนโหมดเป็นแผนที่ดาวเทียมเพื่อดูตำแหน่งดินจริงได้*")

        # 1. ตั้งค่าจุดกึ่งกลางแฝดแผนที่เริ่มต้น (พิกัดเริ่มต้น)
        center_lat, center_lon = 16.054000, 103.652000
        
        # 2. สร้างแผนที่ฐานด้วย Folium และเปิดชั้นข้อมูลแบบดาวเทียม (Esri Satellite) เพื่อความจริงในการดูที่ดิน
        m = folium.Map(location=[center_lat, center_lon], zoom_start=18, tiles='OpenStreetMap')
        
        # เพิ่มชั้นข้อมูลแผนที่ดาวเทียมให้เลือกกดเปลี่ยนได้บนขวา
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='แผนที่ดาวเทียม (Satellite)',
            overlay=False,
            control=True
        ).add_to(m)
        folium.LayerControl().add_to(m)

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
