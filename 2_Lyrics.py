import streamlit as st
import streamlit.components.v1 as components
import base64

def get_base64_img(img_path):
    try:
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

img_data = get_base64_img("static/โลโก้1.png")

# ส่วนหัวและโลโก้
st.markdown(f"""
    <style> #MainMenu, footer, header {{visibility: hidden;}} </style>
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{img_data}' style='width:80px; filter: drop-shadow(0 0 5px rgba(255, 75, 75, 0.5));'>
        <h3 style='color: #FF4B4B;'>📡 LYRIC SYNC</h3>
    </div>
""", unsafe_allow_html=True)

# ใส่โค้ด HTML Lyric Sync (อันที่มีเนื้อเพลง 3:39 นาที) ตรงนี้
sync_lyrics_html = """...ใส่โค้ด HTML ที่ผมเคยให้ของ Lyric Sync..."""
components.html(sync_lyrics_html, height=600)
