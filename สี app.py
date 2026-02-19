import streamlit as st

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Room Color Simulator", layout="centered")

st.title("🎨 ระบบทดลองสีห้อง (Streamlit Version)")

# 1. ส่วนควบคุม (Sidebar หรือ Columns)
col1, col2, col3 = st.columns(3)

with col1:
    room_color = st.color_picker("สีผนังห้อง", "#E0E0E0")
with col2:
    frame_color = st.color_picker("สีกรอบ", "#4A4A4A")
with col3:
    btn_color = st.color_picker("สีปุ่มกด", "#007BFF")

# 2. ส่วนการแสดงผล (ใช้ CSS ร่วมกับ Markdown)
# เราจะใช้ค่าตัวแปรจาก Python (room_color, frame_color, btn_color) ไปใส่ใน CSS
st.markdown(f"""
    <style>
    .room-container {{
        background-color: {room_color};
        height: 350px;
        width: 100%;
        border: 15px solid #333;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 10px;
        transition: 0.3s;
    }}
    .window-frame {{
        width: 200px;
        height: 150px;
        border: 10px solid {frame_color};
        background-color: white;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
    }}
    .custom-button {{
        background-color: {btn_color};
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        box-shadow: 0 4px #999;
    }}
    </style>

    <div class="room-container">
        <div class="window-frame">
            <div class="custom-button">ปุ่มตัวอย่าง</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 3. แสดงค่า Code สีที่เลือก (Hex Code)
st.info(f"**สรุปค่าสี:** ผนัง: `{room_color}` | กรอบ: `{frame_color}` | ปุ่ม: `{btn_color}`")
