import streamlit as st

# 1. ตั้งค่าธีมนีออน
st.set_page_config(page_title="SYNAPSE VIDEO", layout="wide")
theme_color = "#39FF14" 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #121212 !important; color: {theme_color} !important; }}
    .video-box {{ border: 2px solid {theme_color}; border-radius: 15px; padding: 15px; margin-bottom: 20px; }}
    h1 {{ text-align: center; text-shadow: 0 0 10px {theme_color}; }}
    </style>
""", unsafe_allow_html=True)

st.title("📹 SYNAPSE VIDEO FINDER")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# 2. ระบบค้นหา
query = st.text_input("ค้นหาวิดีโอ (ภาษาอังกฤษ)", placeholder="เช่น City, Space, Neon")

if query:
    q = query.replace(" ", "+")
    st.write(f"### ผลการค้นหาสำหรับ: {query}") # แก้ไขวงเล็บจุดนี้แล้ว

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="video-box">
            <h4>Pexels Video</h4>
            <a href="https://www.pexels.com/search/video/{q}/" target="_blank">
                <button style="width:100%; border-radius:10px; border:1px solid {theme_color}; background:transparent; color:{theme_color}; padding:10px;">กดเปิดดูวิดีโอ</button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="video-box">
            <h4>Pixabay Video</h4>
            <a href="https://pixabay.com/videos/search/{q}/" target="_blank">
                <button style="width:100%; border-radius:10px; border:1px solid {theme_color}; background:transparent; color:{theme_color}; padding:10px;">กดเปิดดูวิดีโอ</button>
            </a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("ระบุคำค้นหาเพื่อเริ่มระบบครับ")

st.write("---")
st.caption("SYNAPSE PROJECT | 2026")
