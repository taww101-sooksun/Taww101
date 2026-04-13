import streamlit as st
import base64

# --- 1. ตั้งค่าหน้าเว็บ & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

def setup_ui():
    st.markdown("""
        def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }

        /* ตัวหนังสือวิ้งแบบ Animation */
        .neon-text { 
            text-align: center; 
            color: #fff; 
            font-size: 30px; 
            font-weight: bold;
            text-transform: uppercase;
            /* เพิ่มเงาหลายชั้นเพื่อให้มันฟุ้ง */
            text-shadow: 
                0 0 5px #fff, 
                0 0 10px #fff, 
                0 0 20px #00f2fe, 
                0 0 40px #00f2fe, 
                0 0 80px #00f2fe;
            /* ทำให้มันกระพริบเบาๆ เหมือนไฟนีออน */
            animation: flicker 1.5s infinite alternate;
        }

        @keyframes flicker {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
            10% { text-shadow: 0 0 5px #fff, 0 0 20px #ff1744; } /* แอบมีแสงสีแดงแทรก */
        }
        
        .stButton>button { border-radius: 10px; border: 1px solid #ff1744; background: rgba(0,0,0,0.5); color: white; }
        </style>
    """, unsafe_allow_html=True)


def display_logo(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{data}" style="width: 140px; filter: drop-shadow(0 0 10px #ff1744);"></div>', unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #ff1744;'>SYNAPSE</h1>", unsafe_allow_html=True)

def draw_box(title, target_level):
    if st.button(title, key=target_level, use_container_width=True):
        st.session_state.nav_level = target_level
        st.rerun()

# --- 2. เริ่มระบบ ---
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

setup_ui()

# เรียกใช้โลโก้ (ดึงไฟล์จากหน้าแรก ไม่ต้องมีคำว่า static/)
display_logo("logo1.png") 

# ปุ่มย้อนกลับ
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        if "." in st.session_state.nav_level:
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

st.write(f"LOCATION: **{st.session_state.nav_level}**")
st.markdown("---")

# --- 3. เนื้อหาแต่ละชั้น ---

if st.session_state.nav_level == "HOME":
    c1, c2 = st.columns(2)
    with c1: draw_box("🚀 CORE (MUSIC/LYRICS)", "1")
    with c2: draw_box("📺 MEDIA (VIDEO)", "2")

elif st.session_state.nav_level == "1":
    st.subheader("🚀 CORE SYSTEM: AUDIO & LYRICS")
    
    # ดึงไฟล์เพลงจากหน้าแรก (ชื่อไฟล์ต้องตรงกับใน GitHub นะเพี้ยน)
    try:
        st.audio("วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp4") 
    except:
        st.error("หาไฟล์ วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp3 ไม่เจอ ตรวจสอบชื่อไฟล์ใน GitHub อีกรอบนะ")
    
    # เนื้อเพลงวิ้งๆ
    st.markdown("""
        <div class="neon-text">
            <br>✨ อยู่นิ่งๆ ไม่เจ็บตัว... ✨<br>
            ✨ วันหนึ่งถ้าเธอมองย้อนกลับมา
อาจจะเห็นสิ่งที่เคยทำพังลงไป
แต่ถึงตอนนั้น ฉันคงเดินไกล
ทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้

ขอบคุณถ้อยคำที่เคยทำฉันร้าว
คำที่ทำให้ใจฉันแทบไม่เหลืออะไร
คืนที่ร้องไห้จนไม่รู้จะไปทางไหนกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง
เคยนอนบนกองน้ำตาเป็นเดือนเป็นปีไม่มีใครรู้
หัวใจข้างในมันพังยับ มากแค่ไหนใครเลยจะมารู้
ยิ้มทั้งที่แผลยังสด
กอดตัวเองเพราะไม่มีใครอยู่
ถ้าเธอได้เห็นข้างในฉัน
จะยังกล้ารักคนอย่างฉันไหม (บอกฉันที)

ปล่อยวางความโลภที่เผาใจ... ทิ้งความโกรธที่ไม่มีวันพอ

วันหนึ่งถ้าเธอมองย้อนกลับมา
อาจจะเห็นสิ่งที่เคยทำพังลงไป
แต่ถึงตอนนั้น ฉันคงเดินไกล
ทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้

ขอบคุณถ้อยคำที่เคยทำฉันร้าว
คำที่ทำให้ใจฉันแทบไม่เหลืออะไร
คืนที่ร้องไห้จนไม่รู้จะไปทางไหนกลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง
เคยนอนบนกองน้ำตาเป็นเดือนเป็นปีไม่มีใครรู้
หัวใจข้างในมันพังยับ มากแค่ไหนใครเลยจะมารู้
ยิ้มทั้งที่แผลยังสด
กอดตัวเองเพราะไม่มีใครอยู่
ถ้าเธอได้เห็นข้างในฉัน
จะยังกล้ารักคนอย่างฉันไหม (บอกฉันที)

ปล่อยวางความโลภที่เผาใจ... ทิ้งความโกรธที่ไม่มีวันพอ ✨
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.nav_level == "2":
    st.subheader("📺 MEDIA SYSTEM")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

else:
    st.warning(f"⚠️ พิกัด {st.session_state.nav_level} กำลังพัฒนา...")
