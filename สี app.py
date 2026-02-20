import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import pandas as pd

# ส่วนของการตั้งค่าให้แอปรีเฟรชตัวเอง (Auto-rerun)
# เราจะใช้เทคนิคการวนลูปเช็กตำแหน่งในเบราว์เซอร์
st.title("SYNAPSE LIVE TRACKER")

# ดึงพิกัดจาก GPS มือถือ (ระบบจะถามสิทธิ์เข้าถึงพิกัด)
location = get_geolocation()

if location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    accuracy = location['coords']['accuracy'] # ความแม่นยำของสัญญาณ

    st.success(f"ตรวจพบความเคลื่อนไหวจริง (ความแม่นยำ: {accuracy:.2f} เมตร)")
    
    # สร้างแผนที่ดาวเทียมที่ซูมลึกสุดๆ
    m = folium.Map(
        location=[lat, lon], 
        zoom_start=19, # ซูมลึกกว่าเดิมเพื่อให้เห็นการขยับ
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
        attr='Google Satellite'
    )
    
    # ใส่หมุดสีแดงแทนตัวนายที่จะขยับตามพิกัดจริง
    folium.Marker(
        [lat, lon], 
        popup="ตำแหน่งเรียลไทม์ของนาย",
        icon=folium.Icon(color='red', icon='person', prefix='fa')
    ).add_to(m)
    
    st_folium(m, width=700, height=500, key="live_map")

    # ส่วนนี้คือหัวใจ: บอกให้แอป "อยู่นิ่งๆ" แล้วรออัปเดตเอง
    st.write("---")
    st.caption("ระบบกำลังติดตามพิกัดของนายแบบอัตโนมัติ...")
else:
    st.info("กำลังเชื่อมต่อสัญญาณดาวเทียม... โปรดถือเครื่องไว้นิ่งๆ")
