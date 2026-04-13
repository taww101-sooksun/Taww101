import streamlit as st

# --- 1. SET UP & NEON THEME ---
st.set_page_config(page_title="SYNAPSE VIDEO", layout="wide")
theme_color = "#39FF14" # สีเขียวนีออนที่คุณชอบ

st.markdown(f"""
    <style>
    .stApp {{ background-color: #121212 !important; color: {theme_color} !important; }}
    .video-card {{ border: 2px solid {theme_color}; border-radius: 15px; padding: 15px; margin-bottom: 20px; }}
    h1 {{ text-align: center; text-shadow: 0 0 10px {theme_color}; }}
    </style>
""", unsafe_allow_html=True)

st.title("📹 SYNAPSE VIDEO FINDER")
st.markdown(f"<p style='text-align:center;'><i>'อยู่นิ่งๆ ไม่เจ็บตัว'</i></p>", unsafe_allow_html=True)

# --- 2. SEARCH INPUT ---
query = st.text_input("ค้นหาวิดีโอ (ภาษาอังกฤษ)", placeholder="เช่น City, Cyberpunk, Nature")

if query:
    q = query.replace(" ", "+")
    
    # ดึงความสามารถของแอปโดยการเชื่อมต่อแหล่งวิดีโอภายนอก
    st.write(f"### 🚀 กำลังค้นหาวิดีโอสำหรับ: {query}") # ปิดวงเล็บให้เรียบร้อยแล้วครับ
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="video-card">
            <h4>Pexels Library</h4>
            <p>คลังวิดีโอคุณภาพสูง</p>
            <a href="https://www.pexels.com/search/video/{q}/" target="_blank">
                <button style="width:100%; border-radius:10px; border:1px solid {theme_color}; background:transparent; color:{theme_color}; padding:10px;">เปิดดูวิดีโอ</button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="video-card">
            <h4>Pixabay Stock</h4>
            <p>คลังวido ฟรีระดับโลก</p>
            <a href="https://pixabay.com/videos/search/{q}/" target="_blank">
                <button style="width:100%; border-radius:10px; border:1px solid {theme_color}; background:transparent; color:{theme_color}; padding:10px;">เปิดดูวิดีโอ</button>
