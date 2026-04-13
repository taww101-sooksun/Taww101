import streamlit as st

# --- 1. SET UP & NEON THEME ---
st.set_page_config(page_title="SYNAPSE VIDEO", layout="wide")
theme_color = "#39FF14" 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #121212 !important; color: {theme_color} !important; }}
    .video-card {{ border: 2px solid {theme_color}; border-radius: 15px; padding: 10px; margin-bottom: 20px; }}
    h1 {{ text-align: center; text-shadow: 0 0 10px {theme_color}; }}
    </style>
""", unsafe_allow_html=True)

st.title("📹 SYNAPSE VIDEO FINDER")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# --- 2. SEARCH INPUT ---
query = st.text_input("ค้นหาวิดีโอที่คุณต้องการ (ภาษาอังกฤษ)", placeholder="เช่น City, Ocean, Cyberpunk")

if query:
    q = query.replace(" ", "+")
    
    # 5 ลิงก์แหล่งวิดีโอ (Stock Video) ที่แสดงผลได้ทันที
    # ใช้ Pexels API แบบง่าย (ไม่ต้องใช้ Key สำหรับดูพรีวิวบางส่วน)
    video_sources = [
        {"name": "PEXELS VIDEO 1", "url": f"https://www.pexels.com/search/video/{q}/"},
        {"name": "PIXABAY VIDEO", "url": f"https://pixabay.com/videos/search/{q}/"},
    ]

    st.write(
