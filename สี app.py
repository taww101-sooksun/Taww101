import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

# 2. แสดงโลโก้จริงจากเครื่องนาย
# บรรทัดนี้แหละที่จะดึงไฟล์ logo.jpg ขึ้นมาโชว์
try:
    st.image("logo.jpg", use_container_width=True)
except:
    st.error("ไม่พบไฟล์ logo.jpg ในโฟลเดอร์เดียวกับแอป กรุณาเช็กชื่อไฟล์อีกครั้ง")

st.markdown("<h3 style='text-align: center;'>COMMAND CENTER</h3>", unsafe_allow_html=True)
st.write("---")

# 3. ส่วนพิกัดและเวลา (ความจริงที่ไม่มีใครกำกับได้)
now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
lat, lon = 13.7200, 100.6500  # พิกัดประเวศที่ชัดที่สุดที่เราคุยกัน

col1, col2 = st.columns(2)
with col1:
    st.metric("REAL-TIME", now)
with col2:
    st.metric("LOCATION", f"{lat}, {lon}")

# 4. แผนที่ความชัดสูง (ซูมเห็นหลังคาบ้าน)
st.subheader("Visualizing Reality")
m = folium.Map(location=[lat, lon], zoom_start=16)
folium.Marker([lat, lon], popup="SYNAPSE POINT", icon=folium.Icon(color='red')).add_to(m)
st_folium(m, width=700, height=450)

# 5. เพลงจากประสบการณ์ชีวิตจริง
st.write("---")
st.video("https://www.youtube.com/watch?v=lNVwQTIC-pQ")

st.caption("STAY STILL & HEAL | พัฒนาด้วยตะเกียบแรงกว่าจรวด")
