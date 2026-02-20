import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- 1. SETTING & STYLE ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .weather-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
try:
    st.image("logo.jpg", width=300)
except:
    st.markdown("<h3 style='color: #00FFCC; text-align: center;'>S Y N A P S E</h1>", unsafe_allow_html=True)
st.info("STAY STILL & HEAL : 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- 3. CORE LOGIC (GPS & WEATHER) ---
location = get_geolocation()

if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    
    if lat and lon:
        # ดึงเวลาความจริง
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        
        # --- [NEW] ดึงสภาพอากาศความจริง (Real-time Weather) ---
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        current_temp = weather_data['current_weather']['temperature']
        wind_speed = weather_data['current_weather']['windspeed']
        
        # แสดงข้อมูลความจริงในแถบเดียว
        st.write("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ อุณหภูมิ", f"{current_temp} °C")
        with col2:
            st.metric("💨 ลมแรง", f"{wind_speed} km/h")
        with col3:
            if tz_name:
                now_actual = datetime.now(pytz.timezone(tz_name))
                st.metric("⏰ เวลา", now_actual.strftime('%H:%M'))

        # --- 4. SATELLITE MAP ---
        m = folium.Map(location=[lat, lon], zoom_start=18, 
                       tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
                       attr='Google Satellite')
        folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(m)
        st_folium(m, width=700, height=350, returned_objects=[])

    else:
        st.warning("📡 กำลังเชื่อมต่อข้อมูลความจริง...")
else:
    st.info("💡 โปรดกดยืนยัน 'Allow' เพื่อเข้าสู่ Command Center")

# --- 5. MUSIC THERAPY ---
st.write("---")
playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
st.markdown(f'<iframe width="100%" height="180" src="https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&loop=1&playlist={playlist_id}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', unsafe_allow_html=True)

st.divider()
st.caption("SYNAPSE V1.5 | 'อยู่นิ่งๆ' เพื่อรับรู้ความจริงที่เกิดขึ้นรอบตัว")
