import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- 1. SETTING & RAINBOW STYLE ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

# [ระบบภาษาที่เพิ่มเข้ามา]
languages = {
    "TH": {
        "status_info": "STAY STILL & HEAL : 'อยู่นิ่งๆ ไม่เจ็บตัว'",
        "allow_gps": "💡 โปรดกดยืนยัน 'Allow' เพื่อเข้าสู่ Command Center",
        "connecting": "📡 กำลังเชื่อมต่อสัญญาณ...",
        "temp": "🌡️ อุณหภูมิ",
        "wind": "💨 ลม",
        "time": "⏰ เวลา",
        "map_title": "🗺️ แผนที่พิกัดปัจจุบันของคุณ",
        "music_title": "🎵 Sound Therapy (เล่นอัตโนมัติ)",
        "footer": "SYNAPSE V1.6 | ระบบ 2 ภาษา | 'อยู่นิ่งๆ' ไม่เจ็บตัว"
    },
    "EN": {
        "status_info": "STAY STILL & HEAL : 'Stay Still & No Pain'",
        "allow_gps": "💡 Please click 'Allow' to enter Command Center",
        "connecting": "📡 Connecting to Satellite...",
        "temp": "🌡️ Temp",
        "wind": "💨 Wind",
        "time": "⏰ Time",
        "map_title": "🗺️ Your Current Location Map",
        "music_title": "🎵 Sound Therapy (Autoplay)",
        "footer": "SYNAPSE V1.6 | Dual Language | 'Stay Still' No Pain"
    }
}

# ส่วนเลือกภาษาที่ Sidebar
sel_lang = st.sidebar.selectbox("SELECT LANGUAGE / เลือกภาษา", ["TH", "EN"])
t = languages[sel_lang]

st.markdown("""
    <style>
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
    .stMetric, .stInfo, .stSuccess, .stWarning {
        background-color: rgba(0, 0, 0, 0.6) !important;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    h1, h2, h3, p, span { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
try:
    st.image("logo.jpg", width=300)
except:
    st.markdown("<h1 style='text-align: center;'>S Y N A P S E</h1>", unsafe_allow_html=True)
st.info(t["status_info"])

# --- 3. CORE LOGIC (GPS, WEATHER & TIME) ---
location = get_geolocation()

if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    
    if lat and lon:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        
        try:
            geolocator = Nominatim(user_agent="synapse_bilingual_v1")
            loc_th = geolocator.reverse(f"{lat}, {lon}", language='th')
            name_th = loc_th.raw.get('address', {}).get('province') or loc_th.raw.get('address', {}).get('state') or "พิกัดไทย"
            loc_en = geolocator.reverse(f"{lat}, {lon}", language='en')
            name_en = loc_en.raw.get('address', {}).get('state') or loc_en.raw.get('address', {}).get('province') or "Location"
            
            display_loc = f"📍 {name_th} | {name_en}"
        except:
            display_loc = f"📍 {lat:.4f}, {lon:.4f}"

        try:
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            w_data = requests.get(w_url).json()
            temp = w_data['current_weather']['temperature']
            wind = w_data['current_weather']['windspeed']
        except:
            temp, wind = "--", "--"
        
        st.success(display_loc)

        c1, c2, c3 = st.columns(3)
        with c1: st.metric(t["temp"], f"{temp} °C")
        with c2: st.metric(t["wind"], f"{wind} km/h")
        with c3:
            if tz_name:
                now_ = datetime.now(pytz.timezone(tz_name))
                st.metric(t["time"], now_.strftime('%H:%M'))

        # --- 4. MAP ---
        st.write("---")
        st.subheader(t["map_title"]) # เพิ่มข้อความหัวข้อแผนที่ตามภาษาที่เลือก
        m = folium.Map(location=[lat, lon], zoom_start=18, 
                       tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
                       attr='Google Satellite')
        folium.Marker([lat, lon], 
                      popup=display_loc, # คลิกที่จุดแดงแล้วจะขึ้นชื่อสถานที่
                      icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(m)
        st_folium(m, width=700, height=350, returned_objects=[])

    else:
        st.warning(t["connecting"])
else:
    st.info(t["allow_gps"])

# --- 5. MUSIC (ปรับให้พยายาม Autoplay ดีขึ้น) ---
st.write("---")
st.subheader(t["music_title"])
pid = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
# เพิ่ม mute=1 เพื่อช่วยให้ Autoplay ทำงานได้ใน Browser ส่วนใหญ่
embed = f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/videoseries?list={pid}&autoplay=1&loop=1&playlist={pid}&mute=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
st.markdown(embed, unsafe_allow_html=True)

st.divider()
st.caption(t["footer"])
