import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="TA GPS", layout="centered")
st.title("📍 ศูนย์จับพิกัดความจริง")

# มีบรรทัดนี้ "แค่นี้ที่เดียว" ทั้งไฟล์ ห้ามมีคำว่า streamlit_geolocation ซ้ำอีกเด็ดขาด!
location = streamlit_geolocation(key="ta_the_only_one_geo_2026")

if location and location['latitude'] is not None:
    lat = location['latitude']
    lon = location['longitude']
    
    st.success(f"🛰️ พิกัดความจริง: {lat}, {lon}")
    st.info("📌 ตำบลนาโพธิ์ อำเภอเมืองร้อยเอ็ด จังหวัดร้อยเอ็ด")
    
    # สร้างแผนที่ดาวเทียม Google
    m = folium.Map(
        location=[lat, lon],
        zoom_start=18,
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google"
    )
    folium.Marker([lat, lon], tooltip="คุณอยู่ที่นี่").add_to(m)
    st_folium(m, width=700, height=500)
else:
    st.warning("📡 กำลังรอสัญญาณพิกัดจริงจากอุปกรณ์ของคุณ... โปรดกดอนุญาตสิทธิ์เข้าถึงตำแหน่ง")
