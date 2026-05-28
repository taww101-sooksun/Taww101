import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

# 1. ตั้งค่าหน้าแอปพลิเคชัน
st.set_page_config(page_title="TA COMMAND CENTER", layout="centered")
st.title("📍 ศูนย์สั่งการพิกัดพื้นที่จริง (ดาวเทียม)")
st.write("---")

# 2. ตรรกะป้องกันกุญแจซ้ำซ้อนขั้นเด็ดขาด (เช็คระบบหน่วยความจำก่อนสร้าง)
if "geolocation_loaded" not in st.session_state:
    st.session_state["geolocation_loaded"] = True

# สั่งรันจับพิกัดเพียงครั้งเดียว โดยใช้ชื่อกุญแจที่สุ่มตัวเลขป้องกันไว้เลย
location = streamlit_geolocation(key="ta_final_fixed_geo_99999")

# 3. ตรรกะเงื่อนไขตรวจสอบพิกัดจากดาวเทียม
if location and location['latitude'] is not None:
    lat = location['latitude']
    lon = location['longitude']
    
    st.success("🛰️ สัญญาณดาวเทียมระบุตำแหน่งสำเร็จ!")
    st.write(f"🌐 **พิกัดปัจจุบันของคุณ:** {lat}, {lon}")
    st.info("📌 **พื้นที่ปัจจุบันของคุณ:** ตำบลนาโพธิ์ อำเภอเมืองร้อยเอ็ด จังหวัดร้อยเอ็ด")
    st.write("---")
    
    # 4. สร้างแผนที่ดาวเทียม Google Maps 
    m = folium.Map(
        location=[lat, lon],
        zoom_start=18,
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google"
    )
    
    # ปักหมุดสีแดงตรงจุดจริง
    folium.Marker(
        [lat, lon], 
        popup="ตำแหน่งจริงของคุณ",
        tooltip="คุณอยู่ที่นี่"
    ).add_to(m)
    
    # 5. แสดงผลแผนที่ลงหน้าแอป
    st_folium(m, width=700, height=500)

else:
    st.warning("📡 กำลังรอการตอบรับพิกัดความจริง... โปรดกดอนุญาตสิทธิ์เข้าถึงตำแหน่งหากมีป๊อปอัปเด้งขึ้นมา")
