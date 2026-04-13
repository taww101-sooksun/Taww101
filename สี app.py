import streamlit as st

# --- 1. SET UP ธีมนีออนตามสไตล์คุณ ---
st.set_page_config(page_title="SYNAPSE IMAGE HUB", layout="wide")
theme_color = "#39FF14" 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #000 !important; color: {theme_color} !important; }}
    .source-label {{ 
        background: {theme_color}; color: black; padding: 2px 10px; 
        border-radius: 5px; font-weight: bold; font-size: 12px; 
    }}
    .img-container {{ border: 1px solid {theme_color}55; border-radius: 10px; padding: 10px; margin-bottom: 20px; }}
    </style>
""", unsafe_allow_html=True)

st.title("🔍 SYNAPSE IMAGE FINDER")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# --- 2. ระบบค้นหา ---
query = st.text_input("ระบุสิ่งที่ต้องการค้นหา (ภาษาอังกฤษ)", placeholder="เช่น: Neon City, Dark Soul, Abstract")

if query:
    # แก้ไขคำค้นหาให้พร้อมสำหรับ URL
    q = query.replace(" ", "+")
    
    # --- 3. 5 แหล่งข้อมูล (5 LINKS) ที่มีความสามารถต่างกัน ---
    # เราจะใช้ลิงก์ที่ดึงรูปได้ทันทีโดยไม่ต้องใช้ API Key เพื่อความง่ายในการรันบนมือถือ
    image_sources = [
        {"name": "UNSPLASH (High Quality)", "url": f"https://source.unsplash.com/featured/800x600?{q}&1"},
        {"name": "PICSUM (Random Style)", "url": f"https://picsum.photos/seed/{q}1/800/600"},
        {"name": "LOREM FLICKR (Creative)", "url": f"https://loremflickr.com/800/600/{q}"},
        {"name": "PLACE IMG (Nature/Tech)", "url": f"https://picsum.photos/seed/{q}2/800/600"}, # สำรองจาก Picsum
        {"name": "UNSPLASH (Alternative)", "url": f"https://source.unsplash.com/featured/800x600?{q}&2"}
    ]

    st.write(f"### 📡 ผลลัพธ์จาก 5 แหล่งข้อมูลสำหรับ: {query}")
    
    # จัดหน้าจอ 2 คอลัมน์ให้เหมาะกับมือถือ
    cols = st.columns(2)
    
    for i, source in enumerate(image_sources):
        with cols[i % 2]:
            st.markdown(f'<div class="img-container">', unsafe_allow_html=True)
            st.markdown(f'<span class="source-label">{source["name"]}</span>', unsafe_allow_html=True)
            st.image(source["url"], use_container_width=True)
            st.markdown(f"🔗 [เปิดลิงก์ตรง]({source['url']})")
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("กรุณาพิมพ์คำค้นหา เพื่อเริ่มการทำงานของระบบ 5 แหล่งข้อมูลครับ")

st.write("---")
st.caption("SYNAPSE PROJECT | พัฒนาโดย Ta/Bas")
