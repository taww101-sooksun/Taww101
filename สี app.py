import streamlit as st
import os
import random
import platform
import streamlit.components.v1 as components

# --- 1. SET UP ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

if 'activated' not in st.session_state:
    st.session_state.activated = False
if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

# --- 2. SIDEBAR & SYSTEM INFO (ใช้ platform แทน psutil เพื่อลด error) ---
with st.sidebar:
    st.title("⚙️ SYSTEM CORE")
    st.write(f"**OS:** {platform.system()}")
    # ปุ่มเปิดระบบ (แก้ปัญหา Autoplay)
    if not st.session_state.activated:
        if st.button("🚀 ACTIVATE SYSTEM", use_container_width=True):
            st.session_state.activated = True
            st.rerun()
    else:
        st.success("SYSTEM ONLINE")
    
    st.write("---")
    st.markdown('*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 3. MUSIC ENGINE ---
# กวาดไฟล์ MP3 ทั้งหมดในโฟลเดอร์
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files and st.session_state.activated:
    current_song = music_files[st.session_state.song_index]
    base_name = os.path.splitext(current_song)[0] # ชื่อไฟล์แบบไม่มีนามสกุล
    
    st.title(f"🎵 NOW PLAYING: {current_song}")

    # --- ส่วนการแสดงภาพ/วิดีโอ (ปรับปรุงการตรวจสอบ) ---
    # ลองหาไฟล์ที่ชื่อเหมือนกันแต่เป็น .mp4, .jpg, หรือ .png
    video_file = base_name + ".mp4"
    image_file_jpg = base_name + ".jpg"
    image_file_png = base_name + ".png"

    if os.path.exists(video_file):
        st.video(video_file, loop=True, autoplay=True, muted=True)
    elif os.path.exists(image_file_jpg):
        st.image(image_file_jpg, use_container_width=True)
    elif os.path.exists(image_file_png):
        st.image(image_file_png, use_container_width=True)
    else:
        # ถ้าหาไม่เจอจริงๆ ให้โชว์ Visualizer จำลองแทน
        st.info(f"🔍 System Note: ไม่พบไฟล์วิดีโอหรือภาพที่ชื่อ {base_name}")
        st.markdown("""<div style='height:200px; background:black; border:1px solid #39FF14;'>
                    <p style='text-align:center; padding-top:80px;'>NO VISUAL DATA FOUND</p>
                    </div>""", unsafe_allow_html=True)

    # ตัวเล่นเพลง
    st.audio(current_song, autoplay=True)

    # ปุ่มควบคุม
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ NEXT TRACK"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 RANDOM"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

elif not st.session_state.activated:
    st.warning("กรุณากดปุ่ม 'ACTIVATE SYSTEM' ที่แถบด้านซ้ายเพื่อเริ่มการทำงานครับ")
else:
    st.error("ไม่พบไฟล์เพลงในโฟลเดอร์ กรุณาตรวจสอบไฟล์ .mp3")

# --- 4. JS AUTO-NEXT (ทำหน้าที่กดปุ่ม Next ให้เมื่อเพลงจบ) ---
js_fix = """
<script>
    function checkAudio() {
        var audio = window.parent.document.querySelector('audio');
        if (audio) {
            audio.onended = function() {
                var buttons = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.includes('NEXT TRACK')) {
                        buttons[i].click();
                        break;
                    }
                }
            };
        }
    }
    setInterval(checkAudio, 1000);
</script>
"""
components.html(js_fix, height=0)
