import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="GPS Navigator", layout="wide")

st.title("📍 ระบบระบุเส้นทาง GPS (Version ใช้งานง่าย)")

# สร้าง Sidebar รับพิกัด
with st.sidebar:
    st.header("ระบุจุดหมาย")
    s_lat = st.number_input("จุดเริ่ม (Lat)", value=13.7563, format="%.4f")
    s_lng = st.number_input("จุดเริ่ม (Lng)", value=100.5018, format="%.4f")
    e_lat = st.number_input("จุดหมาย (Lat)", value=13.7367, format="%.4f")
    e_lng = st.number_input("จุดหมาย (Lng)", value=100.5231, format="%.4f")

# สร้างแผนที่
m = folium.Map(location=[s_lat, s_lng], zoom_start=13)

# ใส่ JavaScript สำหรับคำนวณเส้นทาง (OSRM)
# วิธีนี้ไม่ต้องใช้ OSMnx ใน Python แต่ใช้ Browser คำนวณให้แทน
routing_script = f"""
<script>
    var map = L.map('map').setView([{s_lat}, {s_lng}], 13);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);

    L.Routing.control({{
        waypoints: [
            L.latLng({s_lat}, {s_lng}),
            L.latLng({e_lat}, {e_lng})
        ],
        routeWhileDragging: true
    }}).addTo(map);
</script>
"""

# ใช้คำสั่งวาดเส้นทางแบบง่ายๆ ของ Folium ไปก่อน
folium.PolyLine(locations=[(s_lat, s_lng), (e_lat, e_lng)], color="blue", weight=5, opacity=0.8).add_to(m)
folium.Marker([s_lat, s_lng], tooltip="ต้นทาง", icon=folium.Icon(color='green')).add_to(m)
folium.Marker([e_lat, e_lng], tooltip="ปลายทาง", icon=folium.Icon(color='red')).add_to(m)

# แสดงผล
st_folium(m, width=1000, height=600)

st.info("ถ้าจะเอาแบบคำนวณเลี้ยวซ้ายเลี้ยวขวาจริงจังบน Cloud ต้องใช้ Google Maps API หรือลง OSMnx ให้ผ่านครับ")
