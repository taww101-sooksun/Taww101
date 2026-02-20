import streamlit as st
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าพื้นฐาน (SYNAPSE STYLE)
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

# 2. แสดงโลโก้ (ความภูมิใจของนาย)
try:
    st.image("logo.jpg", width=200)
except:
    st.markdown("<h1 style='color: red; text-align: center;'>S Y N A P S E</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>COMMAND CENTER</h3>", unsafe_allow_html=True)
st.info("STAY STILL & HEAL : 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# 3. ระบบดึงพิกัดและความจริงของตำแหน่ง
location = get_geolocation()

if location is not None:
    curr_coords = location.get('coords', {})
    lat = curr_coords.get('latitude')
    lon = curr_coords.get('longitude')
    
    if lat and lon:
        # --- ดึง "เวลาความจริง" ตามตำแหน่งพิกัด ---
        tf = TimezoneFinder()
        local_zone_name = tf.timezone_at(lng=lon, lat=lat)
        
        # ค้นหาชื่อสถานที่ภาษาไทย
        try:
            geolocator = Nominatim(user_agent="synapse_final")
            loc_data = geolocator.reverse(f"{lat}, {lon}", language='th')
            city_name = loc_data.raw.get('address', {}).get('city') or loc_data.raw.get('address', {}).get('state') or "พิกัดนิรนาม"
        except:
            city_name = "กำลังระบุตำแหน่ง..."

        st.success(f"📍 ความจริงปรากฏที่: **{city_name}**")

        # แสดงเวลาท้องถิ่นจริงๆ
        if local_zone_name:
            actual_tz = pytz.timezone(local_zone_name)
            now_actual = datetime.now(actual_tz)
            st.subheader(f"⏰ เวลาความจริง: {now_actual.strftime('%H:%M:%S น.')}")
            st.caption(f"เขตเวลา: {local_zone_name} (อัปเดตตามพิกัดจริง)")

        # 4. แผนที่ดาวเทียม (Real-time Tracking)
        st.write("---")
        m = folium.Map(
            location=[lat, lon], 
            zoom_start=19, 
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
            attr='Google Satellite'
        )
        folium.Marker([lat, lon], popup="ตัวตนของนาย", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
        st_folium(m, width=700, height=450)

    else:
        st.warning("⚠️ รอการเชื่อมต่อกับดาวเทียม...")
else:
    st.info("💡 โปรดกด 'Allow' เพื่อให้แอปดึง 'เวลาและความจริง' ของนายออกมา")

# 5. ระบบเพลงวนลูปตลอดกาล (ปิดไม่ได้ถ้าไม่ปิดแอป)
st.write("---")
st.subheader("Sound Therapy (Looping Forever)")
# ฝัง Playlist ของนายโดยตรง พร้อมคำสั่ง Loop และ Autoplay
playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
embed_code = f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/videoseries?list={playlist_id}&loop=1&playlist={playlist_id}&autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
st.markdown(embed_code, unsafe_allow_html=True)

st.divider()
st.caption("ข้อมูลนี้คือความจริงที่ไม่มีใครกำกับได้ | พัฒนาโดยตะเกียบวาร์ปไปดวงจันทร์")
