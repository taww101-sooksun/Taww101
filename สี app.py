import streamlit as st

try:
    st.title("🎙️ SYNAPSE: Voice Engine (Debug Mode)")
    
    # ลองรันทีละส่วน
    st.write("ตรวจสอบระบบ...")
    
    file1 = st.file_uploader("ไฟล์ที่ 1 (จังหวะสั้น)", type=['wav', 'mp3'])
    file2 = st.file_uploader("ไฟล์ที่ 2 (จังหวะยาว)", type=['wav', 'mp3'])
    
    if file1 and file2:
        st.success("โหลดไฟล์สำเร็จ เตรียมประมวลผล...")
        # ใส่ Logic การผสมเสียงตรงนี้
    else:
        st.info("กรุณาใส่ไฟล์ให้ครบทั้ง 2 ชุดเพื่อป้องกันหน้าจอขาวครับ")

except Exception as e:
    st.error(f"ระบบตรวจพบข้อผิดพลาด: {e}")
