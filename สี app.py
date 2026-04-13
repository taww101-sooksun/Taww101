import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import streamlit as st
import base64

# สร้างปุ่มเลือกไฟล์จากมือถือ
uploaded_file = st.file_uploader("เลือกเพลงจากเครื่องของคุณ", type=["mp3"])

if uploaded_file is not None:
    # อ่านไฟล์เพลงและแปลงเป็น Base64 เพื่อให้ Player เล่นได้
    file_bytes = uploaded_file.read()
    b64_audio = base64.b64encode(file_bytes).decode()
    audio_url = f"data:audio/mp3;base64,{b64_audio}"
    
    # ส่ง audio_url เข้าไปใน UI Player ที่เราทำไว้
    st.success(f"โหลดเพลง {uploaded_file.name} สำเร็จ!")

# ซ่อนส่วนประกอบดั้งเดิมของ Streamlit เพื่อให้ดูเป็นแอปจริง
st.markdown("""
    <style>
    /* ซ่อน Header และ Footer ของ Streamlit */
    header, footer { visibility: hidden; }
    .stApp { background-color: #000; }
    
    /* สไตล์ปุ่ม "จัดการแอป" ที่มุมขวาล่าง */
    .manage-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #1a1c24;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        z-index: 999;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันแสดงหน้าตา UI แบบมือถือ
def mobile_player_ui():
    # 1. โหลดรายชื่อเพลง (โค้ดเดิมของคุณ)
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง")
        return

    # 2. ส่วนหัวแอป (ปุ่มกลับหน้าหลัก)
    st.markdown("""
        <div style="border: 2px solid #00f2fe; border-radius: 15px; width: fit-content; padding: 10px 20px; margin-bottom: 30px;">
            <span style="color: white; font-size: 18px;">⬅️ กลับหน้าหลัก</span>
        </div>
    """, unsafe_allow_html=True)

    # 3. ชื่อแอปและสโลแกน (Neon Style)
    st.markdown("""
        <h1 style="color: #00f2fe; text-shadow: 0 0 10px #00f2fe; font-size: 40px; margin-bottom: 0;">✨ NEON</h1>
        <h1 style="color: #00f2fe; text-shadow: 0 0 10px #00f2fe; font-size: 40px; margin-top: 0;">GENERATOR</h1>
        <p style="color: #555; font-size: 14px;">พิมพ์ข้อความที่ต้องการให้วิ่ง:</p>
    """, unsafe_allow_html=True)

    # 4. กล่อง UI ของ Music Player (ปรับจากสเปกที่คุณให้มาก่อนหน้า)
    current_song = music_files[st.session_state.get('song_index', 0)]
    
    # ดึงรูปปกหรือใช้ Default
    # ในกรณีนี้เราใช้ CSS สร้างกรอบ 400x500 ตามที่คุณสั่งไว้
    player_html = f"""
    <div style="
        width: 100%; 
        max-width: 400px; 
        height: 500px; 
        border: 4px solid; 
        border-image: linear-gradient(to bottom right, #8b00ff, #ff0000) 1;
        background: rgba(0,0,0,0.5);
        box-shadow: 0 0 15px #00f2fe;
        padding: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
    ">
        <div style="color: #f0f0f0; font-size: 18px; font-weight: bold; margin-bottom: 20px;">{current_song}</div>
        <div style="width: 250px; height: 250px; background: #222; border-radius: 0px; border: 1px solid #00f2fe; box-shadow: inset 0 0 10px #00f2fe;">
            </div>
        <div style="position: absolute; bottom: 10px; color: rgba(255,255,255,0.3); font-size: 12px;">อยู่นิ่งๆ ไม่เจ็บตัว</div>
    </div>
    """
    st.write(player_html, unsafe_allow_html=True)

    # 5. ปุ่มจัดการแอป (เลียนแบบ Floating Button ในรูป)
    st.markdown("""
        <div class="manage-btn">
            <span>❮</span> จัดการแอป
        </div>
    """, unsafe_allow_html=True)

# รันแอป
if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

mobile_player_ui()
