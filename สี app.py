def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    
    # --- ส่วนที่เพิ่มใหม่: นาฬิกาและ Progress Bar ---
    now = datetime.now()
    # คำนวณวินาทีที่ผ่านไปของวัน (0.0 - 86400.0)
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    day_percent = (seconds_since_midnight / 86400) # ทำเป็นค่า 0.0 - 1.0 สำหรับ st.progress
    
    col_t1, col_t2 = st.columns([1, 3])
    with col_t1:
        # แสดงเวลาปัจจุบันแบบ Digital Metric
        st.metric("SYSTEM TIME", now.strftime("%H:%M:%S"))
    with col_t2:
        # แสดงหลอดพลังงานของวัน
        st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
        st.progress(day_percent)
    
    st.markdown("---") # ขีดเส้นคั่นให้ดูเป็นระเบียบ
    # -------------------------------------------

    # --- ของเดิมของคุณ ---
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **Ta101**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
    
    st.write("📊 สถิติระบบวันนี้:")
    # ใช้ f-string แสดงค่าจากตัวแปร now ที่เราประกาศไว้ด้านบนได้เลย
    st.code(f"Time: {now.strftime('%H:%M:%S')}\nUser: Ta101\nStatus: Active")
