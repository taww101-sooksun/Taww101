import streamlit as st
import webbrowser

st.set_page_config(page_title="GPS Search & Route", page_icon="📍")

# ตกแต่งหน้าตานิดหน่อยตามสไตล์ที่คุณชอบ
st.markdown("""
    <style>
    .main { background-color: #000000; color: #0ff; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_input_with_html=True)

st.title("🚀 ระบบค้นหาและนำทาง GPS")
st.write("พิมพ์ชื่อสถานที่ที่คุณจะไปด้านล่างนี้เลยครับ")

# ช่องพิมพ์ค้นหา
origin = st.text_input("📍 จุดเริ่มต้น (ถ้าว่างไว้จะใช้ตำแหน่งปัจจุบันของคุณ)", placeholder="เช่น เซ็นทรัลเวิลด์ หรือ บ้าน")
destination = st.text_input("🏁 จุดหมายที่จะไป", placeholder="เช่น สนามบินสุวรรณภูมิ หรือ วัดพระแก้ว")

col1, col2 = st.columns(2)

with col1:
    if st.button("🗺️ ดูเส้นทางบนแผนที่"):
        if destination:
            # สร้าง URL สำหรับ Google Maps Navigation
            # ถ้าไม่ระบุ origin Google จะใช้ Current Location ให้อัตโนมัติ
            if origin:
                nav_url = f"https://www.google.com/maps/dir/{origin}/{destination}"
            else:
                nav_url = f"https://www.google.com/maps/dir//{destination}"
            
            st.success(f"กำลังเปิดเส้นทางไป: {destination}")
            st.markdown(f"[🔗 คลิกตรงนี้เพื่อเปิด Google Maps นำทาง]({nav_url})")
            # ถ้าเปิดในคอมฯ บาง Browser จะ block pop-up ให้คลิกที่ Link แทน
        else:
            st.warning("กรุณาพิมพ์จุดหมายก่อนครับเพื่อน!")

with col2:
    if st.button("🏠 กลับไปที่ตั้งหลัก"):
        st.info("อยู่นิ่งๆ ไม่เจ็บตัว... พักตั้งสติก่อนครับ")

# ส่วนแสดงคำแนะนำการใช้งาน
with st.expander("💡 วิธีใช้งานไม่ให้หลง"):
    st.write("""
    1. **ช่องจุดหมาย:** พิมพ์ชื่อสถานที่ ภาษาไทยหรืออังกฤษก็ได้
    2. **การนำทาง:** เมื่อกดปุ่ม ระบบจะพาคุณไปที่ Google Maps ซึ่งจะคำนวณเส้นทางที่เร็วที่สุดให้ทันที
    3. **ความแม่นยำ:** ใช้ข้อมูลจาก Google โดยตรง ไม่ต้องกลัวแผนที่ไม่อัปเดต
    """)

st.divider()
st.caption("AGENT_X GPS Helper - ขอให้เดินทางปลอดภัยครับ")
