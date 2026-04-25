import streamlit as st
import os
import datetime

# --- 1. SETUP & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        /* ลบ Header, Footer และเมนูเดิมของ Streamlit */
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        
        /* สไตล์ปุ่มเมนู */
        .stButton>button {
            border-radius: 15px;
            border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1);
            color: white;
            height: 100px;
            font-size: 18px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00f2fe;
            color: #000;
            box-shadow: 0 0 20px #00f2fe;
        }
        
        /* ตัวหนังสือวิ้ง */
        .neon-text {
            text-align: center;
            color: #fff;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. การจัดการหน้าจอ (Navigation) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ฟังก์ชันย้อนกลับ
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# --- 3. เนื้อหาแต่ละหน้า ---

# [ หน้าแรก: ศูนย์รวม 10 แอป ]
if st.session_state.page == "HOME":
    # วาง LOGO แทนที่ติ่ง
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    # สร้าง Grid 10 แอป (แบ่งเป็น 2 คอลัมน์)
    c1, c2 = st.columns(2)

    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        st.caption("ความสามารถ: เล่นไฟล์เสียง 1.mp3 และระบบควบคุมเสียงผ่านหน้าเว็บ")

        if st.button("🖼️ 3. IMAGE SEARCH\nค้นหาภาพจากดาวเทียม", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        st.caption("ความสามารถ: ดึงรูปภาพจากคลัง Unsplash ตามคำค้นหาที่ต้องการ")

        if st.button("✨ 5. NEON GENERATOR\nสร้างตัวอักษรเรืองแสง", use_container_width=True):
            st.session_state.page = "5"; st.rerun()
        st.caption("ความสามารถ: แปลงข้อความธรรมดาให้เป็นศิลปะนีออนวิ้งๆ")

        if st.button("💖 7. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        st.caption("ความสามารถ: วิเคราะห์ดวงชะตาในมิติที่ 4 ผ่านระบบฐานข้อมูลชื่อ")

        if st.button("📝 9. SYSTEM LOG\nบันทึกข้อมูลการใช้งาน", use_container_width=True):
            st.session_state.page = "9"; st.rerun()
        st.caption("ความสามารถ: จดบันทึกข้อความและเหตุการณ์สำคัญลงในหน่วยความจำ")

    with c2:
        if st.button("💬 2. CHAT SYSTEM\nระบบสื่อสารอัจฉริยะ", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        st.caption("ความสามารถ: โต้ตอบผ่านข้อความกับระบบจัดการ AI")

        if st.button("🎬 4. VIDEO HUB\nศูนย์รวมวิดีโอวงจรปิด", use_container_width=True):
            st.session_state.page = "4"; st.rerun()
        st.caption("ความสามารถ: เชื่อมต่อและฉายภาพวิดีโอจาก YouTube หรือ Link ตรง")

        if st.button("🌍 6. WORLD CLOCK\nเวลาโลกแบบเรียลไทม์", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        st.caption("ความสามารถ: ตรวจสอบเวลาปัจจุบันในโซนต่างๆ ทั่วโลก")

        if st.button("🔢 8. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        st.caption("ความสามารถ: เจนรหัสตัวเลขนำโชคและรหัสรักษาความปลอดภัยรายวัน")

        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()
        st.caption("ความสามารถ: เปลี่ยนสีสันของ Interface เพื่อความสวยงามตามใจชอบ")

# --- ส่วนนี้คือที่วางโค้ดของแต่ละแอปย่อย (ทำเหมือนเดิม) ---
import streamlit as st
import os
import base64

# 1. การตั้งค่าระบบ (System Configuration)
st.set_page_config(page_title="SYNAPSE MASTER", layout="wide")

def load_local_image(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# เลือกรูปโลโก้ที่สวยที่สุดของพี่
logo_b64 = load_local_image("โลโก้1.png") 

# 2. ส่วนของ CSS (ความพิเศษด้านดีไซน์)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #000000; color: #ffffff; }}
    
    /* เอฟเฟกต์เรืองแสงให้โลโก้ */
    .logo-container {{
        text-align: center;
        padding: 10px;
        filter: drop-shadow(0 0 15px #ff00ea);
    }}
    
    /* สไตล์การ์ด Deck A/B */
    .deck-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #00ff00;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        margin-bottom: 10px;
    }}
    
    /* ปรับแต่งปุ่ม Selectbox */
    div[data-baseweb="select"] > div {{
        background-color: #111 !important;
        color: white !important;
        border: 1px solid #ff00ea !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 3. ส่วนแสดงผล Header
if logo_b64:
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" width="180"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ff00ea; text-shadow: 0 0 10px #ff00ea;'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00ff00;'>สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)

# 4. ส่วนจัดการไฟล์เพลง (Core Logic)
songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if songs:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="deck-card">', unsafe_allow_html=True)
        st.subheader("🎵 DECK A")
        song_a = st.selectbox("เลือกแทร็ก", songs, key="deck_a")
        st.audio(song_a)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="deck-card" style="border-color: #ff00ea; box-shadow: 0 0 10px rgba(255, 0, 234, 0.2);">', unsafe_allow_html=True)
        st.subheader("🎵 DECK B")
        # เลือกเพลงถัดไปให้อัตโนมัติในช่อง B
        default_b = 1 if len(songs) > 1 else 0
        song_b = st.selectbox("เลือกแทร็ก", songs, index=default_b, key="deck_b")
        st.audio(song_b)
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. ฟีเจอร์พิเศษ: Global Playlist Navigator
    with st.expander(f"📂 GLOBAL PLAYLIST ({len(songs)} TRACKS)"):
        for i, s in enumerate(songs, 1):
            st.write(f"{i}. {s}")

else:
    st.error("⚠️ ไม่พบไฟล์เพลงในระบบ กรุณาเช็คโฟลเดอร์บน GitHub")

# 6. แถบสถานะด้านล่าง
st.markdown(f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #000; border-top: 1px solid #00ff00; padding: 5px;">
        <marquee style="color: #00ff00;">
            SYSTEM ONLINE | {len(songs)} TRACKS READY | PLAYING: {song_a if songs else 'NONE'} & {song_b if songs else 'NONE'} | MASTERED BY TA101
        </marquee>
    </div>
""", unsafe_allow_html=True)


# (เพิ่ม elif ไปจนครบหน้า 10 ตามโครงเดิมได้เลยครับ...)
