import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# ตั้งค่าหน้าจอแอป SYNAPSE ให้กว้างพอดีกับหน้าจอมือถือ
st.set_page_config(page_title="SYNAPSE ALL-IN-ONE", page_icon="🔮", layout="centered")

# --- 1. ส่วนหัวแอปพลิเคชัน และ โลโก้ตัวจริง ---
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/Logo1.png"
try:
    st.image(logo_url, use_container_width=True)
except:
    st.title("🔮 SYNAPSE SYSTEM")

st.markdown("---")

# คอนฟิกฐานข้อมูล Firebase ของนาย
FIREBASE_DB_URL = "https://sooksun1-default-rtdb.firebaseio.com"
synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"

# จำลองระบบชื่อผู้ใช้เพื่อไม่ให้ข้อมูลมั่วกัน 100 คน
my_name = st.selectbox("👤 บัญชีผู้ใช้งานปัจจุบัน :", ["นายกานต์", "นายบาส"])
friend_name = "นายบาส" if my_name == "นายกานต์" else "นายกานต์"

st.markdown("---")

#สร้างแถบเมนูหน้าเดียวแยกฝั่งซ้ายขวาเพื่อความสะอาดตา ไม่ต้องพับหน้าจอ
col_left, col_right = st.columns([1, 1])

# ==========================================
# 🛰️ ฝั่งซ้าย: ระบบ GPS แชต และ การส่งสัญญาณโทร
# ==========================================
with col_left:
    st.subheader("🛰️ ระบบ GPS ประจำตัว")
    st.write("กดปุ่มเพื่ออัปเดตพิกัดความแม่นยำสูงเข้าสู่ระบบ")
    
    # ใช้ JavaScript ดึงค่าพิกัดความแม่นยำสูงจากเครื่องมือถือตรงๆ
    gps_component = components.html("""
        <button onclick="getLocation()" style="padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; width: 100%;">📍 ดึงพิกัด GPS สด</button>
        <p id="geo_data" style="color: gray; font-size: 12px; margin-top: 5px;"></p>
        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition, showError, {enableHighAccuracy: true});
            } else { 
                document.getElementById("geo_data").innerHTML = "เบราว์เซอร์ไม่รองรับ GPS";
            }
        }
        function showPosition(position) {
            document.getElementById("geo_data").innerHTML = "ละติจูด: " + position.coords.latitude + "<br>ลองจิจูด: " + position.coords.longitude;
            // ส่งค่ากลับไปบันทึกได้ในระบบจริง
        }
        function showError(error) { document.getElementById("geo_data").innerHTML = "เข้าถึง GPS ไม่ได้"; }
        </script>
    """, height=90)

    st.markdown("---")
    
    st.subheader("🤙 ควบคุมสายโทรออก")
    if st.button(f"📞 กดโทรหา {friend_name}"):
        requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/call_status.json", data=json.dumps({"incoming_call": True, "caller": my_name}))
        st.success("กำลังส่งสัญญาณโทร...")
        
    if st.button("❌ วางสายทั้งหมด"):
        requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/call_status.json", data=json.dumps({"incoming_call": False, "caller": ""}))
        st.info("วางสายแล้ว")

# ==========================================
# 🎵 ฝั่งขวา: เครื่องเล่นเพลงบำบัด 70 เพลงจาก GitHub
# ==========================================
with col_right:
    st.subheader("🎵 คลังเพลงบำบัด 70 เพลง")
    st.write("ดึงข้อมูลสดจากคลังเสียง GitHub ของคุณ")
    
    # โค้ดนี้จะไปอ่านรายชื่อไฟล์ในคลัง GitHub ของนายอัตโนมัติ
    # (นายต้องเปลี่ยนชื่อ User และชื่อ Repo ให้ตรงกับของจริงนะครับ)
    github_api_url = "https://api.github.com/repos/taww101-sooksun/Taww101/contents/"
    
    playlist = []
    try:
        response = requests.get(github_api_url)
        if response.status_code == 200:
            files = response.json()
            # คัดเลือกเฉพาะไฟล์ที่เป็น .mp3 ออกมาโชว์
            playlist = [f['name'] for f in files if f['name'].endswith('.mp3')]
    except:
        playlist = ["SYNAPSE RADAR.mp3", "test_morning.mp3", "test_evening.mp3"] # ตัวอย่างเผื่อเน็ตหลุด

    if playlist:
        selected_song = st.selectbox("เลือกเพลงที่ต้องการฟัง:", playlist)
        # แปลงเป็น Raw Link เพื่อส่งให้เครื่องเล่นเพลงทำงาน
        raw_song_url = f"https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/{selected_song}"
        st.audio(raw_song_url, format="audio/mp3")
    else:
        st.warning("ไม่พบไฟล์เพลงในโฟลเดอร์ GitHub")

st.markdown("---")

# ==========================================
# 🚨 ส่วนล่างสุด: กระดานเช็คสัญญาณเรียกเข้า (กล่องข้อความโชว์ สั่น และเตือนเสียงเรดาร์)
# ==========================================
st.subheader("📥 กล่องรับสัญญาณและข้อความเตือน")

try:
    check_db = requests.get(f"{FIREBASE_DB_URL}/users/{my_name}/call_status.json").json()
except:
    check_db = None

if check_db and check_db.get("incoming_call") == True:
    caller = check_db.get("caller", "สายปริศนา")
    st.error(f"🚨 มีสายเรียกเข้าจาก: {caller} !!")
    
    if st.button("🟢 ตอบรับสาย"):
        st.success("เข้าสู่โหมดสนทนาเสียงสำเร็จ")
        
    # สั่งงาน JavaScript ระเบิดเสียงเรดาร์ทันทีเมื่อกล่องนี้ทำงาน และสั่งสั่นตัวเครื่องไปพร้อมกัน
    components.html(f"""
        <script>
            // สั่งสั่นสะเทือนตัวเครื่องมือถือ (สั่นจังหวะหนัก 3 ครั้ง)
            if (navigator.vibrate) {{
                navigator.vibrate([500, 200, 500, 200, 500]);
            }}
            // เล่นเสียง SYNAPSE RADAR วนลูป
            var audio = new Audio('{synapse_radar_tone}');
            audio.loop = true;
            audio.play().catch(function(e) {{ console.log("รอการแตะหน้าจอเพื่อเปิดเสียงสมัครสมาน"); }});
        </script>
    """, height=0)
else:
    st.write("🟢 สถานะตัวเครื่องปกติ: รอรับสายการเชื่อมต่อ...")
