import streamlit as st

st.set_page_config(page_title="Sooksun1 Command Center", page_icon="📱", layout="centered")

# ตกแต่งหน้าจอโทนเข้มตามสไตล์แอป SYNAPSE
st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h2, h3, p, label { color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 ระบบล็อกอินยิ้มซิ (Sooksun1)")
st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว ปลอดภัยร้อยเปอร์เซ็นต์\"</p>", unsafe_allow_html=True)

# โครงสร้างโค้ดหน้ากาก Firebase JavaScript SDK 
# ดึงค่ามาจาก JSON และเปิดรับเบอร์ทดสอบที่ต๊ะเพิ่งบันทึกไป
firebase_html_logic = """
<div style="background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #10b981; color: white; font-family: sans-serif;">
    <h3 style="margin-top:0; color: #34d399;">เข้าสู่ระบบด้วยเบอร์โทรศัพท์</h3>
    
    <label style="display:block; margin-bottom: 8px; font-size: 14px;">เบอร์โทรศัพท์ (ใส่รูปแบบสากล เช่น +66970801941):</label>
    <input type="text" id="phone-number" value="+66" style="width: 90%; padding: 10px; border-radius: 6px; border: 1px solid #4b5563; background-color: #374151; color: white; margin-bottom: 15px;">
    
    <div id="recaptcha-container"></div>
    
    <button id="sign-in-button" onclick="sendOTP()" style="width: 95%; background-color: #10b981; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 10px;">
        📲 ขอรหัส OTP
    </button>

    <hr style="border-color: #4b5563; margin: 20px 0;">

    <label style="display:block; margin-bottom: 8px; font-size: 14px;">กรอกรหัส OTP 6 หลักที่ตั้งไว้ หรือได้รับจาก SMS:</label>
    <input type="text" id="verification-code" placeholder="xxxxxx" style="width: 90%; padding: 10px; border-radius: 6px; border: 1px solid #4b5563; background-color: #374151; color: white; margin-bottom: 15px;">
    
    <button id="verify-button" onclick="verifyOTP()" style="width: 95%; background-color: #3b82f6; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 6px; cursor: pointer;">
        ✅ ยืนยันรหัสผ่าน
    </button>
    
    <p id="status-log" style="color: #f1f5f9; font-size: 13px; margin-top: 15px; background: #111827; padding: 10px; border-radius: 6px; min-height: 20px;"></p>
</div>

<script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-auth.js"></script>

<script>
  // ข้อมูลสัจจะจาก JSON ของต๊ะ
  const firebaseConfig = {
    apiKey: "AIzaSyBsycwJ8wZ_SzVLyaikQHdg6KzFKKmvrfM",
    authDomain: "sooksun1.firebaseapp.com",
    databaseURL: "https://sooksun1-default-rtdb.firebaseio.com",
    projectId: "sooksun1",
    storageBucket: "sooksun1.firebasestorage.app",
    messagingSenderId: "1032465762625",
    appId: "1:1032465762625:android:b5008be8528877b7ab79c0"
  };
  
  if (!firebase.apps.length) {
      firebase.initializeApp(firebaseConfig);
  }
  
  const auth = firebase.auth();
  auth.languageCode = 'th';

  window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier('recaptcha-container', {
    'size': 'invisible'
  });

  let confirmationResultHolder = null;
  const statusLog = document.getElementById('status-log');

  function sendOTP() {
    const phoneNumber = document.getElementById('phone-number').value;
    statusLog.style.color = "#f1f5f9";
    statusLog.innerText = "⏳ กำลังส่งคำขอไปยังระบบ Firebase...";
    
    auth.signInWithPhoneNumber(phoneNumber, window.recaptchaVerifier)
      .then((confirmationResult) => {
        confirmationResultHolder = confirmationResult;
        statusLog.style.color = "#34d399";
        statusLog.innerText = "✅ ดำเนินการสำเร็จ! กรุณากรอกรหัส 6 หลักเพื่อข้ามผ่านระบบความปลอดภัย";
      }).catch((error) => {
        statusLog.style.color = "#f87171";
        statusLog.innerText = "❌ เกิดข้อผิดพลาด: " + error.message;
      });
  }

  function verifyOTP() {
    const code = document.getElementById('verification-code').value;
    if (!confirmationResultHolder) {
        statusLog.style.color = "#f87171";
        statusLog.innerText = "❌ กรุณากดปุ่มขอรหัส OTP ก่อนครับเพื่อน";
        return;
    }
    
    statusLog.style.color = "#f1f5f9";
    statusLog.innerText = "⏳ กำลังตรวจสอบรหัสผ่านสากล...";
    
    confirmationResultHolder.confirm(code)
      .then((result) => {
        statusLog.style.color = "#60a5fa";
        statusLog.innerHTML = "🔓 ล็อกอินสำเร็จ! ยินดีต้อนรับเพื่อนต๊ะเข้าสู่ระบบอย่างเป็นทางการ";
      }).catch((error) => {
        statusLog.style.color = "#f87171";
        statusLog.innerText = "❌ รหัสไม่ถูกต้องตามที่บันทึกไว้ใน Firebase: " + error.message;
      });
  }
</script>
"""

# แสดงผลกล่องล็อกอินฝั่ง HTML บนแอป Streamlit
st.components.v1.html(firebase_html_logic, height=450, scrolling=False)
