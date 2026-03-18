import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import db, credentials

# --- 1. ตั้งค่าหน้าตาแอป ---
st.title("📍 SYNAPSE GPS MONITOR")
st.write("ระบบดึงพิกัดเรียลไทม์และบันทึกข้อมูล")

# --- 2. สั่งดึงพิกัดจากเครื่อง ---
loc = get_geolocation()

# --- 3. ส่วนการทำงานเมื่อพบพิกัด ---
if loc:
    # โชว์พิกัดแบบตัวเลข
    st.write("พบพิกัดของคุณแล้ว:")
    st.info(f"ละติจูด: {loc['coords']['latitude']}")
    st.info(f"ลองจิจูด: {loc['coords']['longitude']}")

    # สร้างแผนที่และปักหมุด
    # m คือตัวแปรเก็บแผนที่, zoom_start=15 คือระยะซูมที่เห็นหลังคาบ้าน
    m = folium.Map(
        location=[loc['coords']['latitude'], loc['coords']['longitude']], 
        zoom_start=15
    )
    
    folium.Marker(
        [loc['coords']['latitude'], loc['coords']['longitude']], 
        popup="คุณอยู่ที่นี่"
    ).add_to(m)

    # แสดงแผนที่บนหน้าเว็บ
    st_folium(m, width=700)

    # --- 4. บันทึกข้อมูลลง Firebase ---
    # (หมายเหตุ: อย่าลืมเช็คว่าคุณ Initialize Firebase ไว้ที่ส่วนต้นของโปรเจกต์แล้วหรือยัง)
    try:
        data = {
            "lat": loc['coords']['latitude'],
            "lon": loc['coords']['longitude']
        }
        # บันทึกลงโฟลเดอร์ชื่อ 'tracking'
        db.reference('tracking').push(data)
        st.success("บันทึกพิกัดลงระบบ SYNAPSE เรียบร้อย!")
    except Exception as e:
        st.error(f"ไม่สามารถบันทึกข้อมูลได้: {e}")

else:
    # ถ้ายังหาพิกัดไม่เจอ ให้โชว์ข้อความรอ
    st.warning("กำลังรอสัญญาณ GPS... กรุณากด 'Allow' หรือ 'อนุญาต' เพื่อเข้าถึงพิกัด")

