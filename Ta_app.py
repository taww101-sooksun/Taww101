import streamlit as st
import os

# --- [ บรรทัดแรกสุดของไฟล์ ห้ามย้ายเด็ดขาด ] ---
st.set_page_config(page_title="SYNAPSE NEON PLAYER", layout="centered")

# =========================================================
# 🎨 ตกแต่งหน้าตาแอปด้วย CSS คุมโทน แดง น้ำเงิน ม่วง เขียว ขาว ดำ นีออน
# =========================================================
st.markdown("""
    <style>
    /* ซ่อนแถบเมนูขยะที่ไม่จำเป็น */
    header, footer, #MainMenu {visibility: hidden;}
    
    /* พื้นหลังดำสนิท และตั้งค่าตัวอักษรสีขาว */
    .stApp {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        border-top: 5px solid #bd00ff; /* เส้นขอบบนสีม่วงนีออน */
    }
    
    /* กล่องครอบสไตล์ไซไฟ */
    .neon-box {
        background: #0d0d11;
        border: 2px solid #00f3ff;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
        margin-bottom: 20px;
    }
    
    /* หัวข้อเรืองแสงสีม่วง-แดง */
    .neon-title {
        color: #FFFFFF;
        text-shadow: 0 0 10px #bd00ff, 0 0 20px #ff0055;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        letter-spacing: 2px;
    }
    
    /* ตัวหนังสือสีเขียวนีออน */
    .neon-status {
        color: #00ff66;
        text-shadow: 0 0 5px #00ff66;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🎵 ส่วนการทำงานหลักของระบบ (ทำได้จริง 100%)
# =========================================================

st.markdown('<h1 class="neon-title" style="text-align:center;">SYNAPSE NEON PLAYER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#aaa;">AGENT AUDIO HUB | อยู่นิ่งๆ ไม่เจ็บตัว</p>', unsafe_allow_html=True)
st.write("---")

# ค้นหาไฟล์ .mp3 ในโฟลเดอร์เดียวกันอัตโนมัติ
current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
song_list = sorted([f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")])

# ดีไซน์กล่องเครื่องเล่นหลัก
with st.container():
    st.markdown('<div class="neon-box">', unsafe_allow_html=True)
    
    # 1. แสดงโลโก้ logo1.png
    logo_path = os.path.join(current_dir, "logo1.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        # ถ้าไม่มีรูป ให้ขึ้นสัญลักษณ์ข้อความนีออนแทน โค้ดจะไม่พัง
        st.markdown('<h1 style="color:#00f3ff; text-shadow: 0 0 10px #00f3ff;">[ 🧬 ]</h1>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# 2. ส่วนเลือกเพลงและเปิดเล่น
if not song_list:
    st.error("❌ ไม่พบไฟล์ .mp3 ในโฟลเดอร์แอปหลัก กรุณาอัปโหลดเพลงขึ้น GitHub ไว้ในโฟลเดอร์เดียวกันก่อนนะเพื่อน")
else:
    # หน้าต่างเลือกเพลงแบบ Dropdown สีเข้าธีม
    selected_song = st.selectbox("🎯 เลือกสัญญาณเสียงที่ต้องการเจาะจง (SELECT SONG):", song_list)
    
    if selected_song:
        st.markdown(f"**กำลังประมวลผลระบบสัญญาณ:** `{selected_song}`")
        st.markdown('<span class="neon-status">STATUS: ONLINE & STREAMING...</span>', unsafe_allow_html=True)
        
        # ตัวเล่นเพลงของ Streamlit แท้ๆ เล่นบนมือถือหรือคอมก็ดังชัวร์
        song_bytes = open(os.path.join(current_dir, selected_song), "rb").read()
        st.audio(song_bytes, format="audio/mp3")

    st.write("---")
    st.markdown("### 📂 รายชื่อคลังเพลงทั้งหมดในเซิร์ฟเวอร์")
    for song in song_list:
        st.markdown(f"- 🎵 {song}")
