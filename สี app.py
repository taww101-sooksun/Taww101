import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# 1. ตั้งค่าเริ่มต้นและซ่อนส่วนเกินของ Streamlit ให้ดูเป็นแอปจริง
st.set_page_config(layout="wide", page_title="SYNAPSE Mobile")

st.markdown("""
    <style>
    header, footer { visibility: hidden; }
    .stApp { background-color: #000; }
    
    /* ปุ่มจัดการแอปที่มุมขวาล่างแบบในรูป */
    .manage-btn {
        position: fixed; bottom: 20px; right: 20px;
        background-color: #1a1c24; color: white;
        padding: 10px 20px; border-radius: 5px;
        display: flex; align-items: center; gap: 10px;
        font-size: 14px; z-index: 999; border: 1px solid #333;
    }
    
    /* Custom Scrollbar สำหรับรายชื่อเพลง 70 เพลง */
    [data-testid="stVerticalBlock"] > div:has(div.song-list-container) {
        overflow-y: auto; max-height: 500px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. ฟังก์ชันหลักสำหรับดึงเพลงและเล่นเพลง
def main_app():
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0

    # สแกนเพลงรอบข้าง (ในโฟลเดอร์เดียวกัน)
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return

    # ส่วนหัว: สไตล์ Neon ตามรูปที่คุณส่งมา
    st.markdown("""
        <div style="border: 2px solid #00f2fe; border-radius: 15px; width: fit-content; padding: 5px 15px; margin-bottom: 20px;">
            <span style="color: white; font-size: 14px;">⬅️ กลับหน้าหลัก</span>
        </div>
        <h1 style="color: #00f2fe; text-shadow: 0 0 10px #00f2fe; font-size: 35px; margin: 0;">✨ NEON</h1>
        <h1 style="color: #00f2fe; text-shadow: 0 0 10px #00f2fe; font-size: 35px; margin-top: -10px;">GENERATOR</h1>
    """, unsafe_allow_html=True)

    # จัดเลย์เอาต์: รายชื่อเพลงอยู่รอบข้าง (ซ้าย) เครื่องเล่นอยู่ตรงกลาง
    col_list, col_player = st.columns([1, 1.5])

    with col_list:
        st.markdown("<p style='color: #555;'>คลังเพลงของคุณ</p>", unsafe_allow_html=True)
        # สร้างรายการเพลงที่เลื่อนได้
        with st.container(height=450):
            for i, song in enumerate(music_files):
                is_active = i == st.session_state.song_index
                label = f"🔥 {song}" if is_active else f"🎵 {song}"
                if st.button(label, key=f"s_{i}", use_container_width=True):
                    st.session_state.song_index = i
                    st.rerun()

    with col_player:
        current_song = music_files[st.session_state.song_index]
        
        # แปลงเพลงเป็น Base64 เพื่อส่งเข้า Player
        with open(current_song, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_url = f"data:audio/mp3;base64,{b64}"

        # 4. กล่อง UI เครื่องเล่นตามสเปก 400x500
        player_html = f"""
        <div style="
            width: 100%; max-width: 400px; height: 500px;
            border: 4px solid; border-image: linear-gradient(to bottom right, #8b00ff, #ff0000) 1;
            background: rgba(0,0,0,0.5); box-shadow: 0 0 15px #00f2fe;
            padding: 15px; display: flex; flex-direction: column; align-items: center;
            position: relative; box-sizing: border-box;
        ">
            <div style="color: #00f2fe; font-size: 14px; margin-bottom: 10px;">NOW SCANNING...</div>
            <div style="color: #f0f0f0; font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 20px;">{current_song}</div>
            
            <div style="width: 100%; height: 200px; background: #111; border: 1px solid #333; display: flex; align-items: flex-end; gap: 2px; padding: 5px;">
                <div style="flex:1; height: 60%; background: hsl(0,100%,50%);"></div>
                <div style="flex:1; height: 80%; background: hsl(50,100%,50%);"></div>
                <div style="flex:1; height: 40%; background: hsl(100,100%,50%);"></div>
                <div style="flex:1; height: 90%; background: hsl(200,100%,50%);"></div>
                <div style="flex:1; height: 70%; background: hsl(280,100%,50%);"></div>
            </div>

            <audio id="ap" src="{audio_url}" controls autoplay style="width: 100%; margin-top: 20px;"></audio>
            
            <script>
                var a = document.getElementById('ap');
                a.onended = function() {{
                    window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
                }};
            </script>

            <div style="position: absolute; bottom: 10px; color: rgba(255,255,255,0.3); font-size: 12px;">
                อยู่นิ่งๆ ไม่เจ็บตัว
            </div>
        </div>
        """
        result = components.html(player_html, height=520)

        # รับค่าจาก JS เพื่อเปลี่ยนเพลงอัตโนมัติ
        if result == 'next':
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()

    # ปุ่มจัดการแอปมุมล่าง
    st.markdown('<div class="manage-btn"><span>❮</span> จัดการแอป</div>', unsafe_allow_html=True)

# รันแอป
main_app()
