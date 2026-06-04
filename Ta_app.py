import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# 1. ตั้งค่าหน้าจอแอป
st.set_page_config(page_title="SYNAPSE SECURE", page_icon="🔮", layout="centered")

# --- 2. ลบติ่ง Streamlit และทำพื้นหลังนีออนดำ ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000000; }
    
    /* กรอบไฟนีออน */
    .neon-box-blue { border: 2px solid #00d2ff; border-radius: 12px; padding: 20px; background-color: #050505; box-shadow: 0 0 10px #00d2ff; margin-bottom: 20px; }
    .neon-box-green { border: 2px solid #00ff66; border-radius: 12px; padding: 20px; background-color: #050505; box-shadow: 0 0 10px #00ff66; margin-bottom: 20px; }
    .neon-box-white { border: 2px solid #ffffff; border-radius: 12px; padding: 20px; background-color: #050505; box-shadow: 0 0 10px #ffffff; margin-bottom: 20px; }
    .neon-box-red { border: 2px solid #ff0055; border-radius: 12px; padding: 20px; background-color: #050505; box-shadow: 0 0 15px #ff0055; margin-bottom: 20px; }
    
    h1, h2, h3, p, label { color: #ffffff !important; text-shadow: 0 0 5px rgba(255,255,255,0.5); }
    </style>
""", unsafe_allow_html=True)

# คอนฟิกฐานข้อมูลของนาย
FIREBASE_DB_URL = "https://sooksun1-default-rtdb.firebaseio.com"
# **ความจริงสำคัญ**: นายต้องเอา Web API Key ของ Firebase Project นายมาใส่ตรงนี้เพื่อใช้ล็อกอินจริง
FIREBASE_AUTH_KEY = "AIzaSyA... (เอา API Key จากตั้งค่า Firebase ของนายมาใส่ตรงนี้)" 

synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/Logo1.png"

# แสดงโลโก้หลัก
try:
    st.image(logo_url, use_container_width=True)
except:
    st.write("🔮 [SYNAPSE SYSTEM]")

# --- 3. ระบบล็อกอินจริง (Firebase Auth หลังบ้าน) ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_local_id' not in st.session_state:
    st.session_state.user_local_id = None

if st.session_state.user_email is None:
    st.markdown('<div class="neon-box-white">', unsafe_allow_html=True)
    st.subheader("🔑 เข้าสู่ระบบโครงข่าย SYNAPSE")
    
    email = st.text_input("อีเมลผู้ใช้ (Email) :")
    password = st.text_input("รหัสผ่าน (Password) :", type="password")
    
    col_login, col_reg = st.columns(2)
    
    with col_login:
        if st.button("🔒 ล็อกอิน"):
            # ยิงตรวจสอบบัญชีกับเซิร์ฟเวอร์ Firebase ตัวจริง
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_AUTH_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            res = requests.post(url, json=payload)
            
            if res.status_code == 200:
                data = res.json()
                st.session_state.user_email = data['email']
                st.session_state.user_local_id = data['localId']
                st.success("ลงชื่อเข้าใช้สำเร็จ!")
                st.rerun()
            else:
                st.error("❌ อีเมลหรือรหัสผ่านไม่ถูกต้องตามฐานข้อมูลจริง")
                
    with col_reg:
        if st.button("📝 สมัครสมาชิกใหม่"):
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_AUTH_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                st.success("สร้างบัญชีสำเร็จ! กดปุ่มล็อกอินได้เลยนาย")
            else:
                st.error("❌ สมัครไม่สำเร็จ (รหัสต้อง 6 ตัวขึ้นไป หรืออีเมลนี้มีคนใช้แล้ว)")
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # หยุดทำงานตรงนี้จนกว่าจะล็อกอินผ่าน

# --- 4. หน้าตาแอปหลังจากล็อกอินสำเร็จแล้ว ---
# แปลงชื่ออีเมลมาทำเป็น ID สื่อสาร (ตัดเครื่องหมายพิเศษออกเพื่อป้องกันฐานข้อมูลพัง)
my_name = st.session_state.user_email.replace(".", "_").replace("@", "_")

st.write(f"🟢 บัญชีใช้งานจริง: **{st.session_state.user_email}**")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.user_email = None
    st.session_state.user_local_id = None
    st.rerun()

st.markdown("---")

# เลือกเพื่อนที่เราจะแชตหรือเช็คตำแหน่งด้วย (อิงจากข้อมูลที่มีอยู่ในระบบ)
friend_name = st.text_input("🎯 พิมพ์ ID อีเมลของเพื่อนที่ต้องการเชื่อมต่อ (เช่น bas_gmail_com) :")

if friend_name:
    col_left, col_right = st.columns([1, 1])

    # ==========================================
    # 💬 ฝั่งซ้าย: ห้องแชตล็อกอินจริง (กรอบนีออนน้ำเงิน)
    # ==========================================
    with col_left:
        st.markdown('<div class="neon-box-blue">', unsafe_allow_html=True)
        st.subheader("💬 โครงข่ายแชตล็อกอินจริง")
        
        chat_room_id = f"chat_{min(my_name, friend_name)}_{max(my_name, friend_name)}"
        try:
            chat_res = requests.get(f"{FIREBASE_DB_URL}/chats/{chat_room_id}.json").json()
        except:
            chat_res = None

        chat_text = ""
        if chat_res:
            for msg_id, msg_data in chat_res.items():
                chat_text += f"**{msg_data['sender']}**: {msg_data['text']}\n\n"
        else:
            chat_text = "*ระบบพร้อมเชื่อมต่อ ไร้ข้อความค้างคา*"
            
        st.markdown(chat_text)
        
        user_msg = st.text_input("พิมพ์ข้อความแชต...", key="input_secure_chat")
        if st.button("✈️ ส่งข้อความ"):
            if user_msg:
                new_msg = {"sender": st.session_state.user_email, "text": user_msg}
                requests.post(f"{FIREBASE_DB_URL}/chats/{chat_room_id}.json", data=json.dumps(new_msg))
                # ส่งสัญญาณเตือนเพื่อน
                requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/chat_alert.json", data=json.dumps({"new_message": True, "sender": st.session_state.user_email}))
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 🛰️ ฝั่งขวา: คลังเพลง และ GPS (กรอบนีออนเขียว)
    # ==========================================
    with col_right:
        st.markdown('<div class="neon-box-green">', unsafe_allow_html=True)
        st.subheader("🛰️ ระบบพิกัดเฉพาะบุคคล")
        
        components.html(f"""
            <button onclick="getLocation()" style="padding: 10px; background-color: #00ff66; color: black; border: none; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer;">📍 อัปเดตพิกัดจริงเข้าชื่อฉัน</button>
            <p id="geo_status" style="color: #fff; font-size: 13px; margin-top: 8px; text-align: center;"></p>
            <script>
            function getLocation() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(function(pos) {{
                        var lat = pos.coords.latitude; var lon = pos.coords.longitude;
                        document.getElementById("geo_status").innerHTML = "ละติจูด: " + lat + "<br>ลองจิจูด: " + lon;
                        
                        fetch('{FIREBASE_DB_URL}/users/{my_name}/gps.json', {{
                            method: 'PUT',
                            body: JSON.stringify({{lat: lat, lon: lon, user: '{st.session_state.user_email}'}})
                        }});
                    }}, function(err) {{ document.getElementById("geo_status").innerHTML = "สัญญาณ GPS ขัดข้อง"; }}, {{enableHighAccuracy: true}});
                }}
            }}
            </script>
        """, height=90)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🚨 ระบบเตือนเสียงเรดาร์ (กรอบนีออนแดง)
# ==========================================
try:
    alert_status = requests.get(f"{FIREBASE_DB_URL}/users/{my_name}/chat_alert.json").json()
except:
    alert_status = None

if alert_status and alert_status.get("new_message") == True:
    st.markdown('<div class="neon-box-red">', unsafe_allow_html=True)
    st.subheader("🚨 สัญญาณข้อความเข้า!")
    st.write(f"ส่งมาจาก: **{alert_status.get('sender')}**")
    
    if st.button("🔴 รับทราบและหยุดเสียงเรดาร์"):
        requests.put(f"{FIREBASE_DB_URL}/users/{my_name}/chat_alert.json", data=json.dumps({"new_message": False, "sender": ""}))
        st.rerun()
        
    components.html(f"""
        <script>
            if (navigator.vibrate) {{ navigator.vibrate([400, 100, 400]); }}
            var audio = new Audio('{synapse_radar_tone}');
            audio.loop = true;
            audio.play().catch(function(e) {{ console.log("รอสัมผัสหน้าจอ"); }});
        </script>
    """, height=0)
    st.markdown('</div>', unsafe_allow_html=True)
