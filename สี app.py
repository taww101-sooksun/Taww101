import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="GPS Real-time Tracker")

st.title("📍 ระบบระบุตำแหน่งเรียลไทม์")

# ดึงข้อมูล Location จากเซนเซอร์มือถือผ่าน Browser
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    accuracy = loc['coords']['accuracy']

    st.success(f"พบตำแหน่งปัจจุบัน (ความแม่นยำ: {accuracy:.2f} เมตร)")
    st.write(f"ละติจูด: {lat} | ลองจิจูด: {lon}")

    # สร้างแผนที่และปักหมุด
    m = folium.Map(location=[lat, lon], zoom_start=16)
    folium.Marker(
        [lat, lon], 
        popup="ตำแหน่งของคุณ",
        tooltip="You are here",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # แสดงผลแผนที่ในแอป
    st_folium(m, width=700, height=500)
    
    if st.button("อัปเดตตำแหน่งใหม่"):
        st.rerun()
else:
    st.warning("กำลังรอสัญญาณ GPS... กรุณากดอนุญาตให้เข้าถึงตำแหน่ง (Location Access)")
