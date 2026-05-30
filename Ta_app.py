import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import base64

# ==========================================
# 1. ตั้งค่าหน้าแอป และสไตล์เบื้องต้น
# ==========================================
st.set_page_config(page_title="Secure Chat App", page_icon="🔐", layout="centered")

# ==========================================
# 2. จำลองระบบ Log-in และสมาสิก (เพื่อไม่ให้โค้ดพัง)
# ==========================================
# สมมติชื่อคุณเองเป็น Agent_001
if "user" not in st.session_state:
    st.session_state.user = "Agent_001"

# ==========================================
# 3. เชื่อมต่อ Firebase Admin SDK (ใช้ความจริงจากคอนฟิกคุณ)
# ==========================================
if not firebase_admin._apps:
    try:
        # ใช้คอนฟิกแบบอ้างอิง URL ฐานข้อมูลตามที่คุณให้มาในตอนแรก
        # หมายเหตุ: ในความเป็นจริงถ้าเป็น Admin SDK ควรใช้คู่กับไฟล์ serviceAccountKey.json
        # แต่เพื่อความรวดเร็วในการทดสอบ เราจะดึงสิทธิ์จากสิ่งที่ระบบเปิดไว้ครับ
        firebase_url = st.secrets["firebase"]["firebase_url"]
        
        # เชื่อมต่อฐานข้อมูล
        firebase_admin.initialize_app(options={
            'databaseURL': firebase_url
        })
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {e}")

# ==========================================
# 4. ฟังก์ชันห้องแชตสายลับ (ปรับปรุงใหม่ตามหลักความจริง)
# ==========================================
def room_private():
    st.subheader("🔐 แชตส่วนตัวสายลับ (Secure Media Chat)")
    st.write(f"👤 คุณกำลังใช้งานในชื่อ: **{st.session_state.user}**")
    
    # ดึงรายชื่อผู้ใช้จาก Firebase มาแสดง (จำลองเพิ่มชื่อทดสอบเข้าไปด้วยเพื่อความชัวร์ว่าจะมีให้เลือก)
    try:
        users_ref = db.reference('users')
        users = users_ref.get()
        
        # ถ้าใน Firebase ยังไม่มีข้อมูลยูสเซอร์เลย เราจะบังคับสร้าง ID ทดสอบให้เลือกใช้งานได้จริง
        if not users:
            users_ref.child("Agent_001").set({"status": "online"})
            users_ref.child("Agent_002").set({"status": "online"})
            users_ref.child("Target_X").set({"status": "online"})
            users = users_ref.get()
            
        friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    except Exception as e:
        st.error(f"ไม่สามารถดึงรายชื่อผู้ใช้ได้: {e}")
        friends = ["Agent_002", "Target_X"] # ตัวเลือกสำรองกรณีฐานข้อมูลเชื่อมต่อติดขัด

    # กล่องเลือกคู่สายแชต
    target = st.selectbox("🎯 เลือกคู่สาย AGENT:", ["-- เลือกเป้าหมาย --"] + friends)
    
    if target != "-- เลือกเป้าหมาย --":
        # สร้าง ID ห้องแชตแบบคู่ (เรียงตามตัวอักษร)
        rid = "_".join(sorted([st.session_state.user, target]))
        
        # --- [ส่วนที่ 1: ส่วนส่งข้อความและลากไฟล์วาง] ---
        with st.form("private_media_form", clear_on_submit=True):
            msg = st.text_input(f"🔒 ส่งข้อความลับถึง {target}...")
            uploaded_file = st.file_uploader("📸 ส่งรูป/คลิปส่วนตัว (จำกัดขนาดไม่เกิน 1MB)", type=['jpg', 'png', 'mp4', 'mov'])
            
            if st.form_submit_button("🚀 LOCK & SEND"):
                file_data = None
                file_type = None
                
                if uploaded_file is not None:
                    bytes_data = uploaded_file.getvalue()
                    # ดักจับขนาดไฟล์จริง ไม่ให้เกินสิทธิ์ที่ Realtime Database รับไหว
                    if len(bytes_data) > 1 * 1024 * 1024:
                        st.error("⚠️ ไฟล์ใหญ่เกิน 1MB ฐานข้อมูลไม่รองรับข้อความยาวขนาดนี้")
                    else:
                        file_data = base64.b64encode(bytes_data).decode()
                        file_type = uploaded_file.type

                # บันทึกข้อมูลลง Firebase
                if msg or file_data:
                    try:
                        db.reference(f'private_rooms/{rid}').push({
                            'u': st.session_state.user,
                            'm': msg,
                            'file': file_data,
                            'ft': file_type,
                            'ts': time.time()
                        })
                        st.success("ส่งข้อมูลเข้าชั้นความลับแล้ว!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"ส่งไม่สำเร็จ: {e}")

        # --- [ส่วนที่ 2: ส่วนแสดงผลข้อความในห้องลับ] ---
        st.write("---")
        try:
            msgs_ref = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        except Exception:
            msgs_ref = None
        
        if msgs_ref:
            # วนลูปการแสดงผลแชตเรียงตามธรรมชาติ (เก่าไปใหม่)
            for k, v in msgs_ref.items():
                u_name = v.get('u', 'Unknown')
                msg_text = v.get('m', '')
                f_data = v.get('file')
                f_type = v.get('ft')
                
                # แยกซ้ายขวาด้วยระบบ Chat Message ของ Streamlit เอง ไม่พึ่ง HTML ที่ทำให้จอดับ
                role = "user" if u_name == st.session_state.user else "assistant"
                avatar = "👤" if role == "user" else "🕵️"
                
                with st.chat_message(role, avatar=avatar):
                    st.write(f"**{u_name}**")
                    if msg_text:
                        st.write(msg_text)
                    
                    # ถ้ามีไฟล์ภาพหรือวิดีโอ Base64 แนบมา ให้ถอดรหัสและแสดงผลในกล่องข้อความ
                    if f_data:
                        try:
                            decoded = base64.b64decode(f_data)
                            if "image" in f_type:
                                st.image(decoded, caption="รูปภาพจากสายลับ")
                            elif "video" in f_type:
                                st.video(decoded)
                        except Exception:
                            st.caption("⚠️ ไม่สามารถถอดรหัสไฟล์สื่อนี้ได้")
        else:
            st.caption("🌑 ยังไม่มีการสนทนาในห้องลับนี้")

# ==========================================
# 5. รันฟังก์ชันหลักบนหน้าเว็บ
# ==========================================
room_private()
