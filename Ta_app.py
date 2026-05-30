import streamlit as st
import time
import base64
# สมมติว่ามี db จาก firebase_admin เข้ามาแล้วตามที่คุณใช้

def room_private(db): # รับค่า db เข้ามาใช้งาน
    st.subheader("🔐 แชตส่วนตัวสายลับ (Secure Media Chat)")
    
    # ตรวจสอบตัวแปรความปลอดภัยเบื้องต้น
    if "user" not in st.session_state:
        st.error("❌ กรุณาเข้าสู่ระบบก่อนใช้งาน")
        return

    # ดึงรายชื่อ AGENT ทั้งหมดมาให้เลือก
    try:
        users = db.reference('users').get()
        friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    except Exception:
        friends = [] # ป้องกันกรณีฐานข้อมูลว่างเปล่า
    
    target = st.selectbox("🎯 เลือกคู่สาย AGENT:", ["-- เลือกเป้าหมาย --"] + friends)
    
    if target != "-- เลือกเป้าหมาย --":
        # สร้าง ID ห้องแชตเฉพาะระหว่าง 2 คน (เรียงชื่อตามตัวอักษร)
        rid = "_".join(sorted([st.session_state.user, target]))
        
        # 1. ส่วนส่งข้อความและลากไฟล์วาง
        with st.form("private_media_form", clear_on_submit=True):
            msg = st.text_input(f"🔒 ส่งข้อความลับถึง {target}...")
            uploaded_file = st.file_uploader("📸 ส่งรูป/คลิปส่วนตัว (จำกัดขนาดไม่เกิน 1MB)", type=['jpg', 'png', 'mp4', 'mov'])
            
            if st.form_submit_button("🚀 LOCK & SEND"):
                file_data = None
                file_type = None
                
                if uploaded_file is not None:
                    # เช็คขนาดไฟล์ตามความเป็นจริงเพื่อไม่ให้ Firebase พัง (จำกัดไว้ที่ 1MB สำหรับ Base64)
                    bytes_data = uploaded_file.getvalue()
                    if len(bytes_data) > 1 * 1024 * 1024:
                        st.error("⚠️ ไฟล์มีขนาดใหญ่เกิน 1MB (ฐานข้อมูล Realtime ไม่รองรับ Base64 ขนาดใหญ่)")
                    else:
                        file_data = base64.b64encode(bytes_data).decode()
                        file_type = uploaded_file.type

                if msg or file_data:
                    db.reference(f'private_rooms/{rid}').push({
                        'u': st.session_state.user,
                        'm': msg,
                        'file': file_data,
                        'ft': file_type,
                        'ts': time.time()
                    })
                    st.rerun()

        # 2. ส่วนแสดงผลข้อความในห้องลับ
        st.write("---")
        
        # ดึงข้อความและเรียงลำดับจากเก่าไปใหม่ เพื่อให้แชตไหลลงข้างล่างตามธรรมชาติของแอปแชต
        msgs_ref = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        
        if msgs_ref:
            # เรียงจากเก่าไปใหม่เพื่อแสดงผลใน Chat UI
            for k, v in msgs_ref.items():
                u_name = v.get('u', 'Unknown')
                msg_text = v.get('m', '')
                f_data = v.get('file')
                f_type = v.get('ft')
                
                # กำหนดบทบาทเพื่อแยกซ้ายขวาอัตโนมัติด้วย st.chat_message
                role = "user" if u_name == st.session_state.user else "assistant"
                avatar = "👤" if role == "user" else "🕵️"
                
                # ใช้ st.chat_message ตัวจริงของ streamlit ข้อความและมีเดียจะรวมอยู่ในกล่องเดียวกัน ไม่เบี้ยว
                with st.chat_message(role, avatar=avatar):
                    st.write(f"**{u_name}**")
                    if msg_text:
                        st.write(msg_text)
                    
                    # ถ้ามีไฟล์แนบ ให้ถอดรหัสและแสดงผลในกล่องข้อความนั้นๆ เลย
                    if f_data:
                        try:
                            decoded = base64.b64decode(f_data)
                            if "image" in f_type:
                                st.image(decoded, caption="รูปภาพลับ")
                            elif "video" in f_type:
                                st.video(decoded)
                        except Exception:
                            st.caption("⚠️ ไฟล์สื่อแสดงผลล้มเหลว")
        else:
            st.caption("🌑 ยังไม่มีการสนทนาในห้องลับนี้")
