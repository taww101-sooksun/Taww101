import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าหน้าแอปและซ่อนส่วนที่ไม่จำเป็น
st.set_page_config(page_title="GPS Real-time", layout="wide")

# CSS สำหรับซ่อน Streamlit Branding และปรับแต่ง UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ส่วนของ Sidebar และ Logo
with st.sidebar:
    try:
        st.image("logo1.png", use_container_width=True)
    except:
        st.subheader("LOGO")
    st.markdown("---")
    st.write("สถานะระบบ: **ออนไลน์**")
    if st.button("🔄 อัปเดตตำแหน่ง"):
        st.rerun()

st.title("📍 ระบบระบุตำแหน่งเรียลไทม์")

# 3. ส่วนการดึงพิกัด GPS
loc = get_geolocation()

if loc is not None:
    if 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        acc = loc['coords']['accuracy']

        # แสดงค่าตัวเลข
        col1, col2 = st.columns(2)
        col1.metric("ละติจูด", f"{lat:.6f}")
        col2.metric("ลองจิจูด", f"{lon:.6f}")
        st.write(f"🎯 ความแม่นยำ: {acc:.2f} เมตร")

        # 4. สร้างและแสดงแผนที่
        m = folium.Map(location=[lat, lon], zoom_start=17, control_scale=True)
        folium.Marker(
            [lat, lon],
            popup="คุณอยู่ที่นี่",
            icon=folium.Icon(color='red', icon='screenshot', prefix='fa')
        ).add_to(m)
        
        # วาดวงกลมแสดงรัศมีพิกัด (ความแม่นยำ)
        folium.Circle(
            radius=acc,
            location=[lat, lon],
            color="blue",
            fill=True,
        ).add_to(m)

        st_folium(m, width="100%", height=500)
    else:
        st.info("กำลังรับสัญญาณจากดาวเทียม...")
else:
    st.warning("⚠️ กรุณาอนุญาตให้แอปเข้าถึงตำแหน่ง (Location Access) ในเบราว์เซอร์มือถือด้วยครับ")

# สโลแกนเท่ๆ ปิดท้าย
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE COMMAND CENTER")
