import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. เชื่อมต่อ Firebase (ส่วนนี้ต้องรันก่อนเสมอ) ---
if not firebase_admin._apps:
    try:
        # ใช้ Secrets สำหรับ Streamlit Cloud หรือใช้ไฟล์ตรงๆ สำหรับ Local
        if "firebase" in st.secrets:
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
        else:
            cred = credentials.Certificate("your-firebase-key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"การเชื่อมต่อ Firebase ผิดพลาด: {e}")

db = firestore.client()

# --- 2. ฟังก์ชันจัดการข้อมูล (LOGIC) ---

def login_user(username, password):
    """ตรวจสอบชื่อและรหัสผ่าน"""
    user_ref = db.collection("users").document(username).get()
    if user_ref.exists:
        if user_ref.to_dict().get("password") == password:
            return True
    return False

def register_user(username, password):
    """สมัครสมาชิกใหม่"""
    if not username or not password:
        return False, "กรุณากรอกข้อมูลให้ครบถ้วน"
    
    user_ref = db.collection("users").document(username)
    if user_ref.get().exists:
        return False, f"AGENT ID '{username}' นี้ถูกใช้ไปแล้ว"
    else:
        # บันทึกข้อมูลลง Firestore
        user_ref.set({
            "password": password,
            "created_at": firestore.SERVER_TIMESTAMP,
            "status": "active"
        })
        return True, "ลงทะเบียนสำเร็จ! ตอนนี้คุณสามารถ Login ได้แล้ว"

# --- 3. หน้าจอ UI ---

def auth_page():
    st.title("🛡️ SYNAPSE AUTHENTICATION")
    
    # สลับหน้า Login / Register
    choice = st.radio("เลือกรายการ", ["เข้าสู่ระบบ", "สมัครสมาชิกใหม่"], horizontal=True)
    
    if choice == "เข้าสู่ระบบ":
        with st.form("login_form"):
            user = st.text_input("AGENT ID")
            pw = st.text_input("PASSWORD", type="password")
            submit = st.form_submit_button("LOGIN")
            
            if submit:
                if login_user(user, pw):
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"ยินดีต้อนรับ AGENT {user}")
                    st.rerun()
                else:
                    st.error("ID หรือ รหัสผ่านไม่ถูกต้อง")

    else:
        with st.form("register_form"):
            new_user = st.text_input("สร้าง AGENT ID")
            new_pw = st.text_input("สร้าง PASSWORD", type="password")
            confirm_pw = st.text_input("ยืนยัน PASSWORD", type="password")
            submit_reg = st.form_submit_button("SIGN UP")
            
            if submit_reg:
                if new_pw != confirm_pw:
                    st.error("รหัสผ่านไม่ตรงกัน")
                else:
                    success, msg = register_user(new_user, new_pw)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

# --- 4. ฟังก์ชันหลัก (MAIN) ---

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        auth_page()
    else:
        # --- ถ้า Login ผ่านแล้ว จะแสดงโค้ดเดิมของคุณที่นี่ ---
        with st.sidebar:
            st.title("⚙️ SYSTEM")
            st.write(f"AGENT: **{st.session_state.user}**")
            if st.button("LOGOUT"):
                st.session_state.logged_in = False
                st.rerun()
            st.markdown("---")
            st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

        tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR", "🧬 LOGIC"])
        # ตัวอย่างการดึงฟังก์ชันห้องมาโชว์
        # with tabs[0]: room_core() ...
        with tabs[0]:
            st.write(f"สวัสดี {st.session_state.user} ระบบพร้อมทำงานครับ")

if __name__ == "__main__":
    main()
