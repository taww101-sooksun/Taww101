import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="SYNAPSE DJ", layout="wide")

music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'idx' not in st.session_state: st.session_state.idx = 0
    curr = music_files[st.session_state.idx]

    st.title("🎧 SYNAPSE DJ STATION")
    
    html_code = f"""
    <div style="background:#111; padding:20px; border-radius:15px; text-align:center; border:2px solid #00f2fe;">
        <h2 style="color:#00f2fe; font-family:sans-serif;">กำลังเล่น: {curr}</h2>
        <audio id="myAudio" controls style="width:100%; margin-top:10px;">
            <source src="./{curr}" type="audio/mpeg">
            เบราว์เซอร์ของคุณไม่รองรับการเล่นเสียง
        </audio>
        <p style="color:#666; font-size:12px; margin-top:10px;">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
    </div>
    <script>
        // พยายามสั่ง Auto Play หลังจากผู้ใช้คลิกอะไรบางอย่างบนหน้าจอ
        const audio = document.getElementById('myAudio');
        audio.play().catch(() => {{
            console.log("ต้องการการแตะจากผู้ใช้ก่อนเล่น");
        }});
    </script>
    """
    components.html(html_code, height=200)
else:
    st.error("ไม่พบไฟล์เพลงในระบบครับ")
