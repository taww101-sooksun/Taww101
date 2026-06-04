import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# 1. ตั้งค่าหน้าจอแอปและลบติ่ง Streamlit ออกให้หมดตามบรีฟเดิม
st.set_page_config(page_title="SYNAPSE SECURE", page_icon="🔮", layout="centered")

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

# --- 2. การเรียกใช้ความลับอย่างปลอดภัยผ่าน st.secrets ---
# โค้ดส่วนนี้จะไปดึงข้อมูลจากหน้าต่าง Secrets บนเว็บ Streamlit Cloud เองโดยอัตโนมัติ ทำให้นายไม่ต้องแปะคีย์ในนี้
try:
    FIREBASE_AUTH_KEY = st.secrets["firebase"]["api_key"]
    FIREBASE_DB_URL = st.secrets["firebase"]["firebase_url"]
except Exception as e:
    st.error("🚨 ระบบยังไม่ได้ตั้งค่ากุญแจความลับ (Secrets) บน Streamlit Cloud ครับนาย")
    st.stop()

synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"

# ดึงโลโก้ดั้งเดิมโดยใช้ชื่อไฟล์ตัวเล็กลงท้ายตามคำสั่ง: logo1.png
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/logo1.png"

# แสดงโลโก้หลักตัวเล็ก
try:
    st.image(logo_url, use_container_width=True)
except:
    st.write("🔮 [SYNAPSE CALL CENTER]")

# --- 3. ตรวจสอบสถานะการล็อกอิน ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_email is None:
    st.markdown('<div class="neon-box-white">', unsafe_allow_html=True)
    st.subheader("🔑 เข้าสู่ระบบโครงข่าย SYNAPSE")
    
    email = st.text_input("อีเมลผู้ใช้ (Email) :")
    password = st.text_input("รหัสผ่าน (Password) :", type="password")
    
    col_login, col_reg = st.columns(2)
    
    with col_login:
        if st.button("🔒 ล็อกอิน"):
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_AUTH_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            res = requests.post(url, json=payload)
            
            if res.status_code == 200:
                data = res.json()
                st.session_state.user_email = data['email']
                st.success("ยินดีต้อนรับเข้าสู่ระบบพิกัด!")
                st.rerun()
            else:
                st.error("❌ อีเมลหรือรหัสผ่านไม่ถูกต้อง หรือนายยังไม่ได้สมัครสมาชิก")
                
    with col_reg:
        if st.button("📝 สมัครสมาชิกใหม่"):
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_AUTH_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                st.success("สร้างบัญชีเสร็จสิ้น! นายกดปุ่มล็อกอินซ้ายมือได้เลยครับ")
            else:
                st.error("❌ สมัครไม่สำเร็จ (รหัสผ่านต้องมี 6 ตัวขึ้นไป หรือเปิดสิทธิ์ใน Firebase หรือยัง?)")
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. หน้าตาแอปหลักหลังล็อกอินผ่านฉลุย ---
my_name = st.session_state.user_email.replace(".", "_").replace("@", "_")

st.write(f"🟢 รหัสเข้าใช้งานสำเร็จ: **{st.session_state.user_email}**")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.user_email = None
    st.rerun()

st.markdown("---")
friend_name = st.text_input("🎯 พิมพ์ ID ของเพื่อนที่ต้องการเชื่อมต่อ (เช่น bas_gmail_com) :")

if friend_name:
    col_left, col_right = st.columns([1, 1])

    # ห้องแชตนีออนน้ำเงิน
    with col_left:
        st.markdown('<div class="neon-box-blue">', unsafe_allow_html=True)
        st.subheader("💬 ห้องแชตเครือข่าย")
        
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
            chat_text = "*ห้องแชตว่างเปล่า ไม่มีข้อมูลตกค้าง*"
            
        st.markdown(chat_text)
        
        user_msg = st.text_input("พิมพ์ข้อความเพื่อส่ง...", key="secure_chat_box")
        if st.button("✈️ ส่งข้อความ"):
            if user_msg:
                new_msg = {"sender": st.session_state.user_email, "text": user_msg}
                requests.post(f"{FIREBASE_DB_URL}/chats/{chat_room_id}.json", data=json.dumps(new_msg))
                requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/chat_alert.json", data=json.dumps({"new_message": True, "sender": st.session_state.user_email}))
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # GPS นีออนเขียว
    with col_right:
        st.markdown('<div class="neon-box-green">', unsafe_allow_html=True)
        st.subheader("🛰️ อัปเดตตำแหน่งระบุตัวตน")
        
        components.html(f"""
            <button onclick="getLocation()" style="padding: 10px; background-color: #00ff66; color: black; border: none; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer;">📍 กดแชร์พิกัด GPS จริง</button>
            <p id="geo_status" style="color: #fff; font-size: 13px; margin-top: 8px; text-align: center;"></p>
            <script>
            function getLocation() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(function(pos) {{
                        var lat = pos.coords.latitude; var lon = pos.coords.longitude;
                        document.getElementById("geo_status").innerHTML = "Lat: " + lat + "<br>Lon: " + lon;
                        
                        fetch('{FIREBASE_DB_URL}/users/{my_name}/gps.json', {{
                            method: 'PUT',
                            body: JSON.stringify({{lat: lat, lon: lon, user: '{st.session_state.user_email}'}})
                        }});
                    }}, function(err) {{ document.getElementById("geo_status").innerHTML = "ระบุสัญญาณล้มเหลว"; }}, {{enableHighAccuracy: true}});
                }}
            }}
            </script>
        """, height=90)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. ระบบตรวจข้อความเข้าแผดเสียงเรดาร์อนิเมชั่นสีแดง ---
try:
    alert_status = requests.get(f"{FIREBASE_DB_URL}/users/{my_name}/chat_alert.json").json()
except:
    alert_status = None

if alert_status and alert_status.get("new_message") == True:
    st.markdown('<div class="neon-box-red">', unsafe_allow_html=True)
    st.subheader("🚨 สายตรวจจับสัญญาณแชตเข้า!")
    st.write(f"ผู้ส่งข้อความ: **{alert_status.get('sender')}**")
    
    if st.button("🔴 ปิดสัญญาณเรดาร์"):
        requests.put(f"{FIREBASE_DB_URL}/users/{my_name}/chat_alert.json", data=json.dumps({"new_message": False, "sender": ""}))
        st.rerun()
        
    components.html(f"""
        <script>
            if (navigator.vibrate) {{ navigator.vibrate([400, 100, 400]); }}
            var audio = new Audio('{synapse_radar_tone}');
            audio.loop = true;
            audio.play().catch(function(e) {{ console.log("รอสัมผัส"); }});
        </script>
    """, height=0)
    st.markdown('</div>', unsafe_allow_html=True)
