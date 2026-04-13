import streamlit as st
import os
import datetime
import pandas as pd

# --- 0. ตั้งค่าพื้นฐาน (ทำครั้งเดียว) ---
st.set_page_config(page_title="SYNAPSE MULTI-SYSTEM", layout="wide")

# ระบบจำหน้า (Navigation)
if 'page' not in st.session_state:
    st.session_state.page = "0"

# --- แถบเมนูข้าง (Sidebar) ---
with st.sidebar:
    st.title("🛰️ SYNAPSE MENU")
    menu = {
        "0": "🏠 หน้าหลัก",
        "1": "🎵 เครื่องเล่นเพลง MP3",
        "2": "💬 ระบบแชต",
        "3": "🖼️ ค้นหารูปภาพ",
        "4": "🎬 ค้นหาวิดีโอ",
        "5": "✨ อักษรวิ้ง/สร้างวิดีโอ",
        "6": "🌍 นาฬิกาทั่วโลก",
        "7": "💖 ตรวจดวงคู่ขนาน",
        "8": "🔢 เช็ครหัสตัวเลขวัน",
        "9": "📝 บันทึกการใช้งาน",
        "10": "🎨 ปรับแต่งสีระบบ"
    }
    for key, label in menu.items():
        if st.button(label, use_container_width=True, key=f"menu_{key}"):
            st.session_state.page = key
            st.rerun()

# --- ส่วนเนื้อหาแต่ละแอป ---

# 0. แอปหน้าหลัก
if st.session_state.page == "0":
    st.title("🏠 SYNAPSE CORE")
    st.info("ยินดีต้อนรับสู่ระบบควบคุมกลาง เลือกเมนูจากด้านข้างเพื่อเริ่มงาน")
    # ใส่รูปคอมพิวเตอร์เท่ๆ ที่เราคุยกัน
    st.image("https://images.unsplash.com/photo-1550745165-9bc0b252726f", use_container_width=True)

# 1. แอปเพลง mp3
elif st.session_state.page == "1":
    st.title("🎵 SYNAPSE AUDIO")
    if os.path.exists("1.mp3"):
        st.audio("1.mp3")
    else:
        st.warning("⚠️ ไม่พบไฟล์ 1.mp3 ในระบบ")

# 2. แชต
elif st.session_state.page == "2":
    st.title("💬 SYNAPSE CHAT")
    msg = st.text_input("คุยกับระบบ:")
    if st.button("ส่ง", key="chat_btn"):
        st.write(f"คุณพูดว่า: {msg}")

# 3. ค้นหารูป
elif st.session_state.page == "3":
    st.title("🖼️ IMAGE SEARCH")
    query = st.text_input("อยากดูรูปอะไร (ภาษาอังกฤษ):", "cyberpunk")
    st.image(f"https://source.unsplash.com/featured/?{query}", use_container_width=True)

# 4. ค้นหาวิดีโอ
elif st.session_state.page == "4":
    st.title("🎬 VIDEO SEARCH")
    v_url = st.text_input("วาง Link วิดีโอ (YouTube/MP4):")
    if v_url: st.video(v_url)

# 5. สร้างวิดีโอตัวหนังสือวิ้ง
elif st.session_state.page == "5":
    st.title("✨ NEON TEXT GENERATOR")
    text = st.text_input("พิมพ์ข้อความวิ้งๆ:", "SYNAPSE")
    st.markdown(f"""<h1 style='color: #ff4b4b; text-shadow: 0 0 20px #ff4b4b;'>{text}</h1>""", unsafe_allow_html=True)

# 6. นาฬิกาทั่วโลก
elif st.session_state.page == "6":
    st.title("🌍 WORLD CLOCK")
    now = datetime.datetime.now()
    st.write(f"เวลาปัจจุบัน (BKK): {now.strftime('%H:%M:%S')}")

# 7. ตรวจดวงคู่ขนาน
elif st.session_state.page == "7":
    st.title("💖 PARALLEL DESTINY")
    name = st.text_input("ใส่ชื่อของคุณ:")
    if st.button("สแกนดวง"): st.write("ดวงของคุณในโลกคู่ขนานคือ... ผู้ควบคุมระบบ!")

# 8. เช็ครหัสตัวเลขของวัน
elif st.session_state.page == "8":
    st.title("🔢 DAILY CODE")
    code = datetime.datetime.now().strftime("%Y%m%d")
    st.metric("รหัสลับวันนี้", code)

# 9. แอปบันทึกการใช้งาน
elif st.session_state.page == "9":
    st.title("📝 SYSTEM LOGS")
    note = st.text_area("จดบันทึกที่นี่:")
    if st.button("บันทึก"): st.success("บันทึกข้อมูลเรียบร้อย")

# 10. แอปเปลี่ยนสีทุกอย่าง
elif st.session_state.page == "10":
    st.title("🎨 THEME CUSTOMIZER")
    color = st.color_picker("เลือกสีเนีออนที่ชอบ", "#ff4b4b")
    st.write(f"คุณเลือกสี: {color}")
    st.info("ใช้สีนี้ไปใส่ใน CSS ของหน้าอื่นๆ ได้เลย!")

