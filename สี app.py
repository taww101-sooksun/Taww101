import streamlit as st
import base64

# ต้องเริ่มด้วย set_page_config เสมอ
st.set_page_config(page_title="SYNAPSE 4-1", layout="centered")

# ฟังก์ชันดึงรูปจากโฟลเดอร์ static (ห้ามเปลี่ยนชื่อฟังก์ชันเป็นไทย)
def get_base64_img(img_path):
    try:
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# ดึงรูป "โลโก้1.png" จากโฟลเดอร์ static
img_data = get_base64_img("static/โลโก้1.png")

st.markdown(f"""
    <style>
    /* ซ่อนแถบด้านบนและล่าง */
    #MainMenu, footer, header {{visibility: hidden;}}
    [data-testid="stAppViewContainer"] {{background-color: #000000;}}
    </style>
    
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{img_data}' style='width:120px; filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.5));'>
        <h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B; margin-top:10px;'>SYNAPSE 4-1</h1>
        <p style='color: #888;'>อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
    <hr style="border: 1px solid #333;">
    """, unsafe_allow_html=True)

st.info("💡 เลือกเมนูที่แถบด้านข้าง (Sidebar) เพื่อสลับหน้า")
