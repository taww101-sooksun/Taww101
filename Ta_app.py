import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# 1. ตั้งค่าหน้าจอแอปแบบเปิดกว้างสุด
st.set_page_config(page_title="SYNAPSE", page_icon="🔮", layout="centered")

# --- 2. โค้ดลับสำหรับลบติ่ง Streamlit และทำพื้นหลังเป็นสีดำสนิท (ทำได้จริง 100%) ---
st.markdown("""
    <style>
    /* ซ่อนแถบเมนูด้านบนและ Footer ด้านล่างของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* บังคับให้พื้นหลังของหน้าเว็บเป็นสีดำสนิท */
    .stApp {
        background-color: #000000;
    }
    
    /* ดีไซน์กรอบไฟนีออนสีน้ำเงิน (สำหรับแชต) */
    .neon-box-blue {
        border: 2px solid #00d2ff;
        border-radius: 12px;
        padding: 20px;
        background-color: #050505;
        box-shadow: 0 0 10px #00d2ff, inset 0 0 5px #00d2ff;
        margin-bottom: 20px;
    }
    
    /* ดีไซน์กรอบไฟนีออนสีเขียว (สำหรับ GPS) */
    .neon-box-green {
        border: 2px solid #00ff66;
        border-radius: 12px;
        padding: 20px;
        background-color: #050505;
        box-shadow: 0 0 10px #00ff66, inset 0 0 5px #00ff66;
        margin-bottom: 20px;
    }
    
    /* ดีไซน์กรอบไฟนีออนสีแดง (สำหรับระบบแจ้งเตือน) */
    .neon-box-red {
        border: 2px solid #ff0055;
        border-radius: 12px;
        padding: 20px;
        background-color: #050505;
        box-shadow: 0 0 15px #ff0055, inset 0 0 5px #ff0055;
        margin-bottom: 20px;
    }
    
    /* ปรับแต่งข้อความทั่วไปให้เป็นสีขาว/สว่าง */
    h1, h2, h3, p, label {
        color: #ffffff !important;
        text-shadow: 0 0 5px rgba(255,255,255,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# คอนฟิกฐานข้อมูล Firebase และลิงก์ไฟล์ต่างๆ ของนาย
FIREBASE_DB_URL = "https://sooksun1-default-rtdb.firebaseio.com"
synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/Logo1.png"

# --- 3. แสดงโลโก้หลัก Logo1.png ---
try:
    st.image(logo_url, use_container_width=True)
except:
    st.write("🔮 [ไม่พบไฟล์ Logo1.png บน GitHub ของคุณ]")

# แยกบัญชีผู้ใช้งาน
my_name = st.selectbox("👤 ระบุบัญชีผู้ใช้ :", ["นายกานต์", "นายบาส"])
friend_name = "นายบาส" if my_name == "นายกานต์" else "นายกานต์"

st.markdown("<br>", unsafe_allow_html=True)

# จัดหน้าจอหน้าเดียวเป็น 2 ฝั่ง ซ้ายและขวา
col_left, col_right = st.columns([1, 1])

# ==========================================
# 💬 ฝั่งซ้าย: ระบบห้องแชต (กรอบนีออนสีน้ำเงิน)
# ==========================================
with col_left:
    st.markdown('<div class="neon-box-blue">', unsafe_allow_html=True)
    st.subheader("💬 โครงข่ายแชตสด")
    
    # ดึงข้อมูลแชตจาก Firebase
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
        chat_text = "*ยังไม่มีข้อความ*"
        
    st.markdown(chat_text)
    
    user_msg = st.text_input("พิมพ์ข้อความ...", key="input_chat_text")
    if st.button("✈️ ส่งข้อความ", key="btn_send_chat"):
        if user_msg:
            new_msg = {"sender": my_name, "text": user_msg}
            requests.post(f"{FIREBASE_DB_URL}/chats/{chat_room_id}.json", data=json.dumps(new_msg))
            # แจ้งเตือนเครื่องเพื่อน
            requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/chat_alert.json", data=json.dumps({"new_message": True, "sender": my_name}))
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🛰️ ฝั่งขวา: คลังเพลงบำบัด และ GPS (กรอบนีออนสีเขียว)
# ==========================================
with col_right:
    # ส่วนของ GPS
    st.markdown('<div class="neon-box-green">', unsafe_allow_html=True)
    st.subheader("🛰️ พิกัด GPS ความแม่นยำสูง")
    
    components.html(f"""
        <button onclick="getLocation()" style="padding: 10px; background-color: #00ff66; color: black; border: none; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer; box-shadow: 0 0 10px #00ff66;">📍 อัปเดตพิกัด GPS</button>
        <p id="geo_status" style="color: #fff; font-size: 13px; margin-top: 8px; text-align: center;"></p>
        <script>
        function getLocation() {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(function(pos) {{
                    var lat = pos.coords.latitude;
                    var lon = pos.coords.longitude;
                    document.getElementById("geo_status").innerHTML = "ละติจูด: " + lat + "<br>ลองจิจูด: " + lon;
                    
                    // ส่งตรงเข้า Firebase 
                    fetch('{FIREBASE_DB_URL}/users/{my_name}/gps.json', {{
                        method: 'PUT',
                        body: JSON.stringify({{lat: lat, lon: lon}})
                    }});
                }}, function(err) {{ document.getElementById("geo_status").innerHTML = "เข้าถึง GPS ไม่ได้"; }}, {{enableHighAccuracy: true}});
            }}
        }}
        </script>
    """, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    # ส่วนของเครื่องเล่นเพลง 70 เพลงจาก GitHub
    st.markdown('<div class="neon-box-blue">', unsafe_allow_html=True)
    st.subheader("🎵 เพลงบำบัดจาก GitHub")
    
    github_api_url = "https://api.github.com/repos/taww101-sooksun/Taww101/contents/"
    playlist = []
    try:
        res = requests.get(github_api_url)
        if res.status_code == 200:
            playlist = [f['name'] for f in res.json() if f['name'].endswith('.mp3') and f['name'] != "SYNAPSE RADAR.mp3"]
    except:
        playlist = ["เพลงบำบัด 01.mp3"]

    if playlist:
        selected_song = st.selectbox("เลือกเพลง:", playlist)
        raw_song_url = f"https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/{selected_song}"
        st.audio(raw_song_url, format="audio/mp3")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🚨 ส่วนล่างสุด: ระบบแจ้งเตือน (กรอบนีออนสีแดง)
# ==========================================
try:
    alert_status = requests.get(f"{FIREBASE_DB_URL}/users/{my_name}/chat_alert.json").json()
except:
    alert_status = None

if alert_status and alert_status.get("new_message") == True:
    st.markdown('<div class="neon-box-red">', unsafe_allow_html=True)
    st.subheader("🚨 มีข้อความใหม่เข้า!")
    st.write(f"ส่งมาจาก: บัญชีของ **{alert_status.get('sender')}**")
    
    if st.button("🔴 รับทราบและปิดสัญญาณเตือน"):
        requests.put(f"{FIREBASE_DB_URL}/users/{my_name}/chat_alert.json", data=json.dumps({"new_message": False, "sender": ""}))
        st.rerun()
        
    # สั่ง JavaScript เปิดเสียงเรดาร์วนลูป และสั่งมือถือสั่นทันทีตามบรีฟ
    components.html(f"""
        <script>
            if (navigator.vibrate) {{
                navigator.vibrate([400, 100, 400]); // สั่นเครื่อง
            }}
            var audio = new Audio('{synapse_radar_tone}');
            audio.loop = true;
            audio.play().catch(function(e) {{ console.log("รอการแตะหน้าจอ"); }});
        </script>
    """, height=0)
    st.markdown('</div>', unsafe_allow_html=True)
