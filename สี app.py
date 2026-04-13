import streamlit as st
import os
import datetime
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
elif st.session_state.page == "1":
    import streamlit.components.v1 as components

    st.markdown("<h2 class='neon-text'>🎵 SYNAPSE AUDIO PRO</h2>", unsafe_allow_html=True)
    st.info("💡 ระบบรองรับ Crossfade 10 วินาที, ตัดเสียงร้อง (Karaoke) และ Visualizer")

    # --- ดึงโค้ด HTML ที่เพี้ยนส่งมาใส่ในตัวแปร ---
    # ผมย่อโค้ดให้เหลือส่วนสำคัญเพื่อให้เพี้ยนเห็นภาพการเชื่อมต่อ
    player_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background: transparent; color: #00f2fe; font-family: sans-serif; }
            /* ใส่ CSS ที่เพี้ยนส่งมาทั้งหมดที่นี่ */
        </style>
    </head>
    <body>
        <div class="p-4 bg-gray-900 rounded-xl border border-cyan-500">
             </div>

        <script>
            // ... (ก๊อปปี้ส่วน <script> จากไฟล์ HTML ของเพี้ยนมาใส่ที่นี่) ...
        </script>
    </body>
    </html>
    """

    # --- แสดงผลหน้าจอ HTML ใน Streamlit ---
    components.html(player_html, height=800, scrolling=True)


# (เพิ่ม elif ไปจนครบหน้า 10 ตามโครงเดิมได้เลยครับ...)
