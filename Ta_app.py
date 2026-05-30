import streamlit as st

# ตั้งค่าหน้าจอให้ออกโทนเข้ม ดุดัน เหมาะกับมือถือ
st.set_page_config(page_title="Yimzy - Phone Auth", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h2, h3, p, label { color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 ระบบยืนยันเบอร์โทรศัพท์ - ยิ้มซิ")
st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว ลงทะเบียนง่ายๆ ด้วยเบอร์มือถือของคุณ\"</p>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ส่วนสำคัญ: การฝังตัวล็อกอินด้วย JavaScript (Client-side) เพื่อความปลอดภัย
# -------------------------------------------------------------
# เราจะดึงข้อมูลจาก JSON ของต๊ะมาใส่ใน Firebase Config ตรงนี้เลย
firebase_html_logic = """
<div style="background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #10b981; color: white; font-family: sans-serif;">
    <h3 style="margin-top:0; color: #34d399;">ทดสอบระบบล็อกอิน (ผ่าน Firebase SDK)</h3>
    
    <label style="display:block; margin-bottom: 8px; font-size: 14px;">เบอร์โทรศัพท์ (รูปแบบสากล เช่น +66812345678):</label>
    <input type="text" id="phone-number" value="+66" style="width: 90%; padding: 10px; border-radius: 6px; border: 1px solid #4b5563; background-color: #374151; color: white; margin-bottom: 15px;">
    
    <div id="recaptcha-container"></div>
    
    <button id="sign-in-button" onclick="sendOTP()" style="width: 95%; background-color: #10b981; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 10px;">
        📲 ส่งรหัส OTP ไปที่มือถือ
    </button>

    <hr style="border-color: #4b5563; margin: 20px 0;">

    <label style="display:block; margin-bottom: 8px; font-size: 14px;">กรอกรหัส OTP 6 หลักที่ได้รับ:</label>
    <input type="text" id="verification-code" placeholder="xxxxxx" style="width: 90%; padding: 10px; border-radius: 6px; border: 1px solid #4b5563; background-color: #374151; color: white; margin-bottom: 15px;">
    
    <button id="verify-button" onclick="verifyOTP()" style="width: 95%; background-color: #3b82f6; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 6px; cursor: pointer;">
        ✅ ยืนยันรหัสเข้าสู่ระบบ
    </button>
    
    <p id="status-log" style="color: #f1f5f9; font-size: 13px; margin-top: 15px; background: #111827; padding: 10px; border-radius: 6px; min-height: 20px;"></p>
</div>

<script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-auth.js"></script>

<script>
  // การกำหนดค่าที่แกะมาจากไฟล์ JSON ของต๊ะ
  const firebaseConfig = {
    apiKey: "AIzaSyBsycwJ8wZ_SzVLyaikQHdg6KzFKKmvrfM",
    authDomain: "sooksun1.firebaseapp.com",
    databaseURL: "https://sooksun1-default-rtdb.firebaseio.com",
    projectId: "sooksun1",
    storageBucket: "sooksun1.firebasestorage.app",
    messagingSenderId: "1032465762625",
    appId: "1:1032465762625:android:b5008be8528877b7ab79c0"
  };
  
  // เริ่มการทำงานของ Firebase
  if (!firebase.apps.length) {
      firebase.initializeApp(firebaseConfig);
  }
  
  const auth = firebase.auth();
  auth.languageCode = 'th'; // ให้ส่ง SMS และแสดงผลเป็นภาษาไทย

  // สร้างระบบตรวจสอบความปลอดภัยแฝง (Invisible ReCAPTCHA)
  window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier('recaptcha-container', {
    'size': 'invisible'
  });

  let confirmationResultHolder = null;
  const statusLog = document.getElementById('status-log');

  // ฟังก์ชันส่งรหัส OTP
  function sendOTP() {
    const phoneNumber = document.getElementById('phone-number').value;
    statusLog.innerText = "⏳ กำลังดำเนินการตรวจสอบและส่ง SMS...";
    
    auth.signInWithPhoneNumber(phoneNumber, window.recaptchaVerifier)
      .then((confirmationResult) => {
        confirmationResultHolder = confirmationResult;
        statusLog.style.color = "#34d399";
        statusLog.innerText = "✅ ส่งรหัส OTP ไปที่เบอร์ " + phoneNumber + " สำเร็จแล้ว! ตรวจสอบ SMS ของคุณ";
      }).catch((error) => {
        statusLog.style.color = "#f87171";
        statusLog.innerText = "❌ เกิดข้อผิดพลาด: " + error.message + " (กรุณาเปิดระบบ Phone Sign-in ในหน้าเว็บ Firebase ก่อน)";
      });
  }

  // ฟังก์ชันตรวจสอบรหัส OTP ที่ผู้ใช้กรอก
  function verifyOTP() {
    const code = document.getElementById('verification-code').value;
    if (!confirmationResultHolder) {
        statusLog.style.color = "#f87171";
        statusLog.innerText = "❌ กรุณากดส่ง OTP ก่อนครับเพื่อน";
        return;
    }
    
    statusLog.style.color = "#f1f5f9";
    statusLog.innerText = "⏳ กำลังตรวจเช็ครหัสสัจจะ...";
    
    confirmationResultHolder.confirm(code)
      .then((result) => {
        const user = result.user;
        statusLog.style.color = "#60a5fa";
        statusLog.innerHTML = "🔓 ล็อกอินสำเร็จ! ยินดีต้อนรับ UID: <br>" + user.uid;
      }).catch((error) => {
        statusLog.style.color = "#f87171";
        statusLog.innerText = "❌ รหัสผิดพลาดหรือหมดอายุ: " + error.message;
      });
  }
</script>
"""

# เรียกใช้งาน HTML บนหน้าจอ Streamlit 
st.components.v1.html(firebase_html_logic, height=450, scrolling=False)

st.write("---")
st.info("💡 คำแนะนำสำหรับเพื่อนต๊ะ: เพื่อให้โค้ดนี้ยิง SMS ได้จริง ต๊ะต้องเข้าไปที่หน้า Firebase Console ของโปรเจกต์ sooksun1 จากนั้นไปที่เมนู Authentication > Sign-in method แล้วกด 'เปิดใช้งาน (Enable)' ในหัวข้อ Phone ด้วยนะครับ")
