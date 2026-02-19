import streamlit as st
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim # ตัวดึงชื่อที่อยู่
import pandas as pd

st.set_page_config(page_title="Global GPS Tracker", layout="centered")
st.markdown("## 🌍 ตรวจสอบพิกัดและเวลาจริง (ทั่วโลก)")

location = get_geolocation()

if location is not None:
    curr_coords = location.get('coords', {})
    lat = curr_coords.get('latitude')
    lon = curr_coords.get('longitude')
    
    if lat and lon:
        # 1. หาชื่อ Timezone
        tf = TimezoneFinder()
        local_zone = tf.timezone_at(lng=lon, lat=lat)
        
        # 2. หาชื่อเมือง/จังหวัด (Reverse Geocoding)
        try:
            geolocator = Nominatim(user_agent="my_gps_app")
            loc_data = geolocator.reverse(f"{lat}, {lon}", language='en')
            address = loc_data.raw.get('address', {})
            city_name = address.get('city') or address.get('state') or address.get('province')
        except:
            city_name = "Unknown City"

        if local_zone:
            actual_tz = pytz.timezone(local_zone)
            now_actual = datetime.now(actual_tz)
            
            st.success(f"📍 ตรวจพบตำแหน่งที่: **{city_name}** ({local_zone})")
            
            col1, col2 = st.columns(2)
            col1.metric("Latitude", f"{lat:.4f}")
            col2.metric("Longitude", f"{lon:.4f}")
            
            st.markdown(f"### ⏰ เวลาท้องถิ่น: **{now_actual.strftime('%H:%M:%S น.')}**")
            st.write(f"📅 วันที่: {now_actual.strftime('%d/%m/%Y')}")
            
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)
else:
    st.info("💡 กรุณากด 'Allow' เพื่อเช็คพิกัดและเวลาจริงครับ")
