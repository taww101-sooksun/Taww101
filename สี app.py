import streamlit as st

# ตั้งค่าหน้าจอแบบเรียบง่ายที่สุดเพื่อลดโอกาสเกิด Error
st.set_page_config(page_title="GPS Navigator", page_icon="📍")

st.title("📍 ระบบค้นหาเส้นทาง (กันหลง)")
st.write("พิมพ์ชื่อสถานที่ที่ต้องการไป แล้วกดปุ่มเพื่อเปิดแผนที่นำทางครับ")

# ส่วนรับข้อมูลจากผู้ใช้
destination = st.text_input("🏁 พิมพ์ชื่อจุดหมาย (เช่น ชื่อวัด, ห้าง, หรือที่อยู่):", placeholder="ระบุที่หมายที่นี่...")

# สร้างปุ่มกด
if st.button("🗺️ นำทางเดี๋ยวนี้"):
    if destination:
        # สร้างลิงก์ Google Maps โดยตรง (ใช้การค้นหาจากชื่อสถานที่)
        # วิธีนี้ชัวร์ที่สุด เพราะ Google จะคำนวณเส้นทางจากจุดที่คุณอยู่ปัจจุบันให้เอง
        nav_url = f"https://www.google.com/maps/dir/?api=1&destination={destination}"
        
        st.success(f"กำลังเตรียมเส้นทางไป: {destination}")
        
        # แสดงลิงก์ให้กด
        st.markdown(f"### [👉 คลิกที่นี่เพื่อเปิดการนำทางบน Google Maps]({nav_url})")
        
        st.info("แนะนำให้เปิดในมือถือเพื่อใช้ GPS นำทางแบบเรียลไทม์ครับ")
    else:
        st.error("ช่วยพิมพ์ชื่อสถานที่ก่อนนะครับ เดี๋ยวหลงทางจริงๆ นะ!")

# ส่วนเสริม: กรณีอยากระบุพิกัด Latitude/Longitude เอง
with st.expander("🌐 ใช้พิกัดละติจูด/ลองจิจูด (ถ้ามี)"):
    lat = st.text_input("Latitude")
    lng = st.text_input("Longitude")
    if st.button("📍 ไปตามพิกัด"):
        if lat and lng:
            coord_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
            st.markdown(f"[🔗 นำทางไปที่พิกัด {lat}, {lng}]({coord_url})")

st.divider()
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว... แต่ถ้าต้องไป ก็ต้องไปให้ถูกทางครับเพื่อน!")
