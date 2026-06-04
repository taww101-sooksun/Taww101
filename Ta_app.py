import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# 1. ตั้งค่าหน้าจอแอปและลบติ่ง Streamlit
st.set_page_config(page_title="SYNAPSE NETWORK", page_icon="🔮", layout="centered")

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

# เรียกใช้ความลับจากระบบ Secrets
try:
    FIREBASE_AUTH_KEY = st.secrets["firebase"]["api_key"]
    FIREBASE_DB_URL = st.secrets["firebase"]["firebase_url"]
except Exception as e:
    st.error("🚨 ระบบยังไม่ได้ตั้งค่ากุญแจความลับ (Secrets) บน Streamlit Cloud ครับนาย")
    st.stop()

synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/logo1.png"

try:
    st.image(logo_url, use_container_width=True)
except:
    st.write("🔮 [SYNAPSE NETWORK]")

# เช็คสถานะการล็อกอินในเซสชั่น
if 'username' not in st.session_state:
    st.session_state.username = None

# --- หน้าจอเข้าสู่ระบบด้วยชื่อยูสเซอร์ ---
if st.session_state.username is None:
    st.markdown('<div class="neon-box-white">', unsafe_allow_html=True)
    st.subheader("🔑 เชื่อมต่อโครงข่ายด้วย Username")
    
    # เปลี่ยนจากอีเมลเป็นชื่อยูสเซอร์เพียวๆ (ห้ามใส่ภาษาไทยหรือเว้นวรรคนะนาย เป็นภาษาอังกฤษหรือตัวเลขจะดีที่สุด)
    user_input = st.text_input("ชื่อยูสเซอร์ของคุณ (Username เช่น bas101, taww101) :").strip()
    password = st.text_input("รหัสผ่าน (Password) :", type="password")
    
    col_login, col_reg = st.columns(2)
    
    # ความจริงหลังบ้าน: แอบเอาชื่อยูสเซอร์มาต่อท้ายด้วยระบบเมลปลอมเพื่อให้ Firebase ยอมทำงาน
    fake_email = f"{user_input}@synapse.com" if user_input else ""
    
    with col_login:
        if st.button("🔒 ล็อกอิน"):
            if not user_input or not password:
                st.error("❌ กรุณากรอกชื่อยูสเซอร์และรหัสผ่าน")
            else:
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_AUTH_KEY}"
                payload = {"email": fake_email, "password": password, "returnSecureToken": True}
                res = requests.post(url, json=payload)
                
                if res.status_code == 200:
                    st.session_state.username = user_input  # บันทึกชื่อยูสเซอร์เพียวๆ ไว้ใช้งาน
                    st.success("ลงชื่อเข้าใช้สำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ ไม่พบชื่อยูสเซอร์นี้ หรือรหัสผ่านไม่ถูกต้อง")
                    
    with col_reg:
        if st.button("📝 สมัครยูสเซอร์ใหม่"):
            if not user_input or not password:
                st.error("❌ กรุณากรอกชื่อและรหัสผ่านที่ต้องการสมัคร")
            else:
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_AUTH_KEY}"
                payload = {"email": fake_email, "password": password, "returnSecureToken": True}
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    st.success(f"สร้างยูสเซอร์ '{user_input}' สำเร็จ! กดปุ่มล็อกอินได้เลยนาย")
                else:
                    st.error("❌ สมัครไม่สำเร็จ (ชื่อนี้อาจมีคนใช้แล้ว หรือรหัสสั้นกว่า 6 ตัว)")
                    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- หน้าตาแอปหลักหลังล็อกอินด้วยชื่อยูสเซอร์สำเร็จ ---
my_name = st.session_state.username

st.write(f"🟢 ยูสเซอร์ปัจจุบัน: **{my_name}**")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.username = None
    st.rerun()

st.markdown("---")

# พิมพ์ชื่อยูสเซอร์ของเพื่อนตรงๆ ไม่ต้องใส่อีเมลแล้ว
friend_name = st.text_input("🎯 พิมพ์ชื่อยูสเซอร์ของเพื่อนที่ต้องการเชื่อมต่อ (เช่น bas101) :").strip()

if friend_name:
    col_left, col_right = st.columns([1, 1])

    # ห้องแชตนีออนน้ำเงิน
    with col_left:
        st.markdown('<div class="neon-box-blue">', unsafe_allow_html=True)
        st.subheader("💬 ห้องแชต")
        
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
            chat_text = "*ห้องแชตว่างเปล่า*"
            
        st.markdown(chat_text)
        
        user_msg = st.text_input("พิมพ์ข้อความ...", key="secure_chat_box")
        if st.button("✈️ ส่งข้อความ"):
            if user_msg:
                new_msg = {"sender": my_name, "text": user_msg}
                requests.post(f"{FIREBASE_DB_URL}/chats/{chat_room_id}.json", data=json.dumps(new_msg))
                # ยิงเตือนเพื่อนด้วยชื่อยูสเซอร์ตรงๆ
                requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/chat_alert.json", data=json.dumps({"new_message": True, "sender": my_name}))
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # GPS นีออนเขียว
    with col_right:
        st.markdown('<div class="neon-box-green">', unsafe_allow_html=True)
        st.subheader("🛰️ อัปเดตพิกัด GPS")
        
        components.html(f"""
            <button onclick="getLocation()" style="padding: 10px; background-color: #00ff66; color: black; border: none; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer;">📍 แชร์พิกัด GPS ปัจจุบัน</button>
            <p id="geo_status" style="color: #fff; font-size: 13px; margin-top: 8px; text-align: center;"></p>
            <script>
            function getLocation() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(function(pos) {{
                        var lat = pos.coords.latitude; var lon = pos.coords.longitude;
                        document.getElementById("geo_status").innerHTML = "Lat: " + lat + "<br>Lon: " + lon;
                        
                        fetch('{FIREBASE_DB_URL}/users/{my_name}/gps.json', {{
                            method: 'PUT',
                            body: JSON.stringify({{lat: lat, lon: lon, user: '{my_name}'}})
                        }});
                    }}, function(err) {{ document.getElementById("geo_status").innerHTML = "สัญญาณขัดข้อง"; }}, {{enableHighAccuracy: true}});
                }}
            }}
            </script>
        """, height=90)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. ระบบตรวจข้อความเข้าแผดเสียงเรดาร์ ---
try:
    alert_status = requests.get(f"{FIREBASE_DB_URL}/users/{my_name}/chat_alert.json").json()
except:
    alert_status = None

if alert_status and alert_status.get("new_message") == True:
    st.markdown('<div class="neon-box-red">', unsafe_allow_html=True)
    st.subheader("🚨 สัญญาณแชตเข้า!")
    st.write(f"ผู้ส่ง: **{alert_status.get('sender')}**")
    
    if st.button("🔴 ปิดสัญญาณเตือน"):
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
