import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- 1. SETTING & RAINBOW STYLE (ความภูมิใจของนาย) ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

st.markdown("""
    <style>
    /* อนิเมชั่นสีรุ้งที่นายให้มา */
    @keyframes RainbowFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
        color: #ffffff;
    }
    
    /* ปรับแต่งกล่องเนื้อหาให้อ่านง่ายขึ้นท่ามกลางสีรุ้ง */
    .stMetric, .stInfo, .stSuccess, .stWarning {
        background-color: rgba(0, 0, 0, 0.6) !important;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    h1, h2, h3, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
try:
    st.image("logo.jpg", width=180)
except:
    st.markdown("<h1 style='text-align: center;'>S Y N A P S E</h1>", unsafe_allow_html=True)
st.info("STAY STILL & HEAL : 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- 3. CORE LOGIC (GPS, WEATHER & TIME) ---
location = get_geolocation()

if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    
    if lat and lon:
        # ดึงเวลาความจริง
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        
        # --- ระบบดึงพิกัด 2 ภาษา (ไทย + อังกฤษ) ---
try:
    geolocator = Nominatim(user_agent="synapse_bilingual_v1")
    
    # ดึงชื่อภาษาไทย
    loc_th = geolocator.reverse(f"{lat}, {lon}", language='th')
    addr_th = loc_th.raw.get('address', {})
    name_th = addr_th.get('province') or addr_th.get('state') or "ไม่ทราบชื่อ"
    
    # ดึงชื่อภาษาอังกฤษ
    loc_en = geolocator.reverse(f"{lat}, {lon}", language='en')
    addr_en = loc_en.raw.get('address', {})
    name_en = addr_en.get('state') or addr_en.get('province') or "Unknown Location"
    
    full_location = f"📍 {name_th} | {name_en}"
except:
    full_location = f"📍 Lat: {lat:.4f}, Lon: {lon:.4f}"

st.success(full_location)
     # ดึงสภาพอากาศเรียลไทม์
        try:
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_data = requests.get(weather_url).json()
            current_temp = weather_data['current_weather']['temperature']
            wind_speed = weather_data['current_weather']['windspeed']
        except:
            current_temp, wind_speed = "--", "--"
        
        st.success(f"📍 ความจริงปรากฏที่: **{city_name}**")

        # แสดง Metric (อุณหภูมิ, ลม, เวลา)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ อุณหภูมิ", f"{current_temp} °C")
        with col2:
            st.metric("💨 ลมแรง", f"{wind_speed} km/h")
        with col3:
            if tz_name:
                now_actual = datetime.now(pytz.timezone(tz_name))
                st.metric("⏰ เวลาท้องถิ่น", now_actual.strftime('%H:%M'))

        # --- 4. SATELLITE MAP ---
        st.write("---")
        m = folium.Map(location=[lat, lon], zoom_start=18, 
                       tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
                       attr='Google Satellite')
        folium.Marker([lat, lon], popup="ตำแหน่งปัจจุบัน", 
                      icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(m)
        st_folium(m, width=700, height=350, returned_objects=[])

    else:
        st.warning("📡 กำลังเชื่อมต่อดาวเทียมเพื่อดึงพิกัด...")
else:
    st.info("💡 โปรดกดยืนยัน 'Allow' เพื่อให้ Command Center เริ่มทำงาน")

# --- 5. MUSIC THERAPY (Looping Forever) ---
st.write("---")
st.subheader("🎵 Sound Therapy (Non-stop)")
playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
embed_code = f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&loop=1&playlist={playlist_id}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
st.markdown(embed_code, unsafe_allow_html=True)

st.divider()
st.caption("SYNAPSE V1.5 | 'อยู่นิ่งๆ' ความจริงจะปรากฏเอง | พัฒนาโดยตะเกียบวาร์ปไปดวงจันทร์")
