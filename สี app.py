import streamlit as st
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าหน้าจอ (สไตล์ SYNAPSE)
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

# 2. ส่วนหัวและโลโก้ (ดึงจากไฟล์ logo.jpg ในเครื่องนาย)
try:
    st.image("logo.jpg", width=200)
except:
    st.markdown("<h1 style='color: red;'>S Y N A P S E</h1>", unsafe_allow_html=True)

st.markdown("### COMMAND CENTER")
st.info("STAY STILL & HEAL : 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# 3. ดึงพิกัดจากเบราว์เซอร์มือถือจริง ๆ
location = get_geolocation()

if location is not None:
    try:
        curr_coords = location.get('coords', {})
        lat = curr_coords.get('latitude')
        lon = curr_coords.get('longitude')
        
        if lat and lon:
            # --- หาเขตเวลาและชื่อสถานที่จริง ---
            tf = TimezoneFinder()
            local_zone_name = tf.timezone_at(lng=lon, lat=lat)
            
            try:
                geolocator = Nominatim(user_agent="synapse_tracker")
                loc_data = geolocator.reverse(f"{lat}, {lon}", language='th')
                address = loc_data.raw.get('address', {})
                city = address.get('city') or address.get('state') or address.get('province') or "ไม่ทราบพิกัด"
            except:
                city = "กำลังค้นหาชื่อสถานที่..."

            #แสดงผลข้อมูลพิกัดและเวลา
            st.success(f"📍 พิกัดปัจจุบัน: **{city}**")
            col1, col2 = st.columns(2)
            col1.metric("LATITUDE", f"{lat:.4f}")
            col2.metric("LONGITUDE", f"{lon:.4f}")

            if local_zone_name:
                actual_tz = pytz.timezone(local_zone_name)
                now_actual = datetime.now(actual_tz)
                st.subheader(f"⏰ เวลาท้องถิ่น: {now_actual.strftime('%H:%M:%S น.')}")

            # 4. แผนที่ดาวเทียมซูมชัด (Satellite View)
            st.write("---")
            st.subheader("Visualizing Reality (Satellite Mode)")
            
            # สร้างแผนที่ดาวเทียม Google
            m = folium.Map(
                location=[lat, lon], 
                zoom_start=18, 
                tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
                attr='Google Satellite'
            )
            folium.Marker([lat, lon], popup="คุณอยู่ที่นี่", icon=folium.Icon(color='red')).add_to(m)
            
            st_folium(m, width=700, height=450)
            
        else:
            st.warning("⚠️ กำลังรอสัญญาณพิกัดจากดาวเทียม...")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
else:
    st.info("💡 โปรดกด 'Allow' หรือ 'อนุญาต' ให้เข้าถึงตำแหน่ง เพื่อแสดงความจริง")

# 5. ส่วนบำบัดด้วยเสียง (Sound Therapy)
st.write("---")
st.subheader("Sound Therapy")
st.video("https://www.youtube.com/watch?v=lNVwQTIC-pQ")

st.divider()
st.caption("SYNAPSE | ข้อมูลจริงที่ปรากฏบนมือถือเครื่องเดียวของนาย")
