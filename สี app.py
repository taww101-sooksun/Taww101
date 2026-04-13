import streamlit as st
import random

# --- 1. SET UPธีมนีออน ---
st.set_page_config(page_title="SYNAPSE IMAGE HUB", layout="wide")
theme_color = "#39FF14" 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #000 !important; color: {theme_color} !important; }}
    .img-box {{ border: 2px solid {theme_color}; border-radius: 15px; margin-bottom: 10px; padding: 5px; }}
    h1 {{ text-align: center; text-shadow: 0 0 15px {theme_color}; }}
    </style>
""", unsafe_allow_html=True)

st.title("🔍 SYNAPSE IMAGE FINDER")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# --- 2. INPUT ---
query = st.text_input("ค้นหาสิ่งที่ต้องการ (เช่น: Nature, Space, Art)", placeholder="พิมพ์ชื่อรูปภาษาอังกฤษที่นี่...")

if query:
    st.write(f"### 🚀 ค้นพบผลลัพธ์สำหรับ: {query}")
    
    # --- 3. 5-LINK SOURCES (ดึงจาก 5 แหล่ง) ---
    sources = [
        f"https://source.unsplash.com/featured/800x600?{query}&1",
        f"https://source.unsplash.com/featured/800x600?{query}&2",
        f"https://source.unsplash.com/featured/800x600?{query}&3",
        f"https://loremflickr.com/800/600/{query}",
        f"https://picsum.photos/seed/{query}/800/600"
    ]

    # แสดงผลแบบ Grid
    cols = st.columns(2)
    for i, link in enumerate(sources):
        with cols[i % 2]:
            st.markdown(f'<div class="img-box">', unsafe_allow_html=True)
            st.image(link, caption=f"Source {i+1}", use_container_width=True)
            st.markdown(f"🔗 [เปิดลิงก์รูปภาพ]({link})")
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("ลองใส่คำค้นหาดูครับ แล้วแอปจะไปดึงรูปจาก 5 แหล่งมาให้ทันที!")

st.write("---")
st.caption("พัฒนาโดย Ta/Bas • SYNAPSE 2026")
