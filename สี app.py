import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx

st.set_page_config(page_title="GPS Route Finder", layout="wide")

st.title("📍 ระบบระบุเส้นทาง GPS (Real Road Network)")
st.write("เลือกจุดเริ่มต้นและจุดหมายเพื่อดูเส้นทางจริงบนแผนที่")

# สร้าง Sidebar สำหรับกรอกพิกัด (ลองใช้พิกัดในกรุงเทพฯ เป็นตัวอย่าง)
with st.sidebar:
    st.header("กำหนดพิกัด")
    start_lat = st.number_input("ละติจูดเริ่มต้น", value=13.7563, format="%.4f")
    start_lng = st.number_input("ลองจิจูดเริ่มต้น", value=100.5018, format="%.4f")
    
    end_lat = st.number_input("ละติจูดปลายทาง", value=13.7367, format="%.4f")
    end_lng = st.number_input("ลองจิจูดปลายทาง", value=100.5231, format="%.4f")
    
    search_btn = st.button("คำนวณเส้นทาง")

# ส่วนการคำนวณและแสดงแผนที่
if search_btn:
    with st.spinner("กำลังคำนวณเส้นทางจากโครงข่ายถนนจริง..."):
        try:
            # 1. ดึงข้อมูลโครงข่ายถนนรอบๆ จุดที่เลือก (รัศมี 2 กม.)
            center_point = (start_lat, start_lng)
            G = ox.graph_from_point(center_point, dist=2000, network_type='drive')
            
            # 2. หา Node (จุดบนถนน) ที่ใกล้พิกัดที่ระบุมากที่สุด
            orig_node = ox.nearest_nodes(G, start_lng, start_lat)
            dest_node = ox.nearest_nodes(G, end_lng, end_lat)
            
            # 3. คำนวณเส้นทางที่สั้นที่สุดด้วย Dijkstra (ใช้ NetworkX)
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            
            # 4. สร้างแผนที่ Folium และวาดเส้นทาง
            m = ox.plot_route_folium(G, route, route_color="red", route_width=5)
            
            # เพิ่ม Marker จุดเริ่มและจุดจบ
            folium.Marker([start_lat, start_lng], popup="จุดเริ่มต้น", icon=folium.Icon(color='green')).add_to(m)
            folium.Marker([end_lat, end_lng], popup="จุดหมาย", icon=folium.Icon(color='blue')).add_to(m)
            
            # แสดงแผนที่ใน Streamlit
            st_folium(m, width=1000, height=600)
            st.success("คำนวณเส้นทางสำเร็จ!")
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e} (อาจเป็นเพราะพิกัดอยู่ไกลกันเกินไป หรือไม่มีข้อมูลถนนในบริเวณนั้น)")
else:
    # แสดงแผนที่ว่างๆ เริ่มต้นที่กรุงเทพฯ
    m = folium.Map(location=[13.7563, 100.5018], zoom_start=13)
    st_folium(m, width=1000, height=600)

st.info("คำแนะนำ: 'อยู่นิ่งๆ ไม่เจ็บตัว' แต่ถ้าจะเดินทางต้องระบุเส้นทางให้เป๊ะนะครับเพื่อน!")
