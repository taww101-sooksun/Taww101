import streamlit as st
import os

# --- 1. SETUP UI ---
st.set_page_config(page_title="SYNAPSE SUPER APP", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        /* คุมขนาดรูปใน Sidebar ให้คงที่ */
        [data-testid="stSidebar"] img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100px; /* ปรับขนาดตรงนี้ถ้าอยากให้เล็กกว่านี้อีก */
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. SIDEBAR (ส่วนที่โชว์ตลอดเวลา) ---
with st.sidebar:
    # แสดงโลโก้ขนาด 100px ที่ด้านบนสุดของเมนูข้าง
    if os.path.exists("logo1.png"):
        st.image("logo1.png") 
    else:
        st.markdown("<h2 style='text-align:center;'>SYNAPSE</h2>", unsafe_allow_html=True)
    
    st.divider() # เส้นคั่นสวยๆ
    
    # ปุ่มเมนูทางลัด (ใส่เผื่อไว้ให้กดจากหน้าไหนก็ได้)
    if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
        st.session_state.page = "HOME"
        st.rerun()

# --- 3. หน้าหลัก (HOME) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    st.markdown("<h1 style='text-align: center;'>CENTRAL HUB</h1>", unsafe_allow_html=True)
    
    # (วางปุ่มเมนู 10 แอป และคำอธิบายตามโค้ดเดิมได้เลยครับ)
    # ...
