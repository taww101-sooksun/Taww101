import streamlit as st
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pandas as pd

# 1. ตั้งค่าหน้ากระดาษ (แก้ปัญหาภาษาไทยเพี้ยน)
st.set_page_config(page_title="Global GPS Tracker", layout="centered")

# 2. หัวข้อแอป (ใช้ Markdown เพื่อความสวยงาม)
st.markdown("## 🌍 เช็กพิกัดและเวลาท้องถิ่นจริง")

# 3. ดึงพิกัดจากเบราว์เซอร์
location = get_geolocation()

if location is not None:
    try:
        curr_coords = location.get('coords', {})
        lat = curr_coords.get('latitude')
        lon = curr_coords.get('longitude')
        
        if lat and lon:
            # --- หาเขตเวลา (Timezone) ---
            tf = TimezoneFinder()
            local_zone_name = tf.timezone_at(lng=lon, lat=lat)
            
            # --- หาชื่อสถานที่ (City/State) ---
            try:
                geolocator = Nominatim(user_agent="my_gps_app_v2")
                # ระบุภาษาเป็น 'th' เพื่อให้แสดงชื่อจังหวัดเป็นภาษาไทยถ้าเป็นไปได้
                loc_data = geolocator.reverse(f"{lat}, {lon}", language='th')
                address = loc_data.raw.get('address', {})
                city = address.get('city') or address.get('state') or address.get('province') or "ไม่ทราบชื่อเมือง"
            except:
                city = "ระบุชื่อเมืองไม่ได้"

            if local_zone_name:
                actual_tz = pytz.timezone(local_zone_name)
                now_actual = datetime.now(actual_tz)
                
                st.success(f"📍 ตำแหน่งที่ตรวจพบ: **{city}**")
                
                col1, col2 = st.columns(2)
                col1.metric("ละติจูด", f"{lat:.4f}")
                col2.metric("ลองจิจูด", f"{lon:.4f}")
                
                st.subheader(f"⏰ เวลาท้องถิ่น: {now_actual.strftime('%H:%M:%S น.')}")
                st.caption(f"เขตเวลาอ้างอิง: {local_zone_name}")
                
                # แสดงแผนที่
                map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.map(map_data, zoom=13)
        else:
            st.warning("⚠️ กำลังพยายามดึงพิกัด...")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("💡 โปรดอนุญาต (Allow) การเข้าถึงพิกัดเพื่อแสดงผล")

st.divider()
st.caption("หมายเหตุ: ข้อมูลจะปรับเปลี่ยนตามตำแหน่งจริงของผู้ใช้ทั่วโลก")
