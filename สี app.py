import streamlit as st
import time
from firebase_admin import credentials, db, initialize_app, _apps

# --- 1. SETUP FIREBASE (รวมข้อมูลแบบไม่ตัดออก และแก้ Error Certificate) ---
if not _apps:
    try:
        # ดึงข้อมูลจากหลังบ้าน (Secrets) มาประกอบเป็น Service Account ที่สมบูรณ์
        firebase_info = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key": st.secrets["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["client_email"],
            "token_uri": "https://oauth2.googleapis.com/token", # เพิ่มเพื่อให้ครบถ้วนตามหลักความจริง
        }
        
        cred = credentials.Certificate(firebase_info)
        initialize_app(cred, {
            'databaseURL': "https://notty-101-default-rtdb.firebaseio.com/"
        })
        st.toast("✅ เชื่อมต่อ Firebase สำเร็จ")
    except Exception as e:
        st.error(f"การเชื่อมต่อ Firebase ผิดพลาด: {e}")

# --- 2. ฟังก์ชันเล่นเสียง (ยกมาทั้งกะบิ ไม่เอาออก) ---
def play_audio():
    link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    # ระบบ Auto-play
    st.components.v1.html(f"""
        <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{link}" type="audio/mpeg"></audio>
        <script>
            var audio = document.getElementById("synapse-audio");
            window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
        </script>
    """, height=0)
    return link

# --- 3. ระบบแชทส่วนตัว (Logic เดิมของคุณเป๊ะๆ) ---
def private_chat_logic(my_name, target_name, p_msg=None):
    # สร้างชื่อห้องจากชื่อคนสองคนเรียงกัน (กันชื่อสลับที่กันแล้วหาห้องไม่เจอ)
    pair = sorted([my_name, target_name])
    room_id = f"priv_{pair[0]}_{pair[1]}"
    
    if p_msg:
        db.reference(f'private_rooms/{room_id}').push({
            'name': my_name, 'msg': p_msg, 'ts': time.time()
        })
    
    raw_p_msgs = db.reference(f'private_rooms/{room_id}').get()
    if raw_p_msgs:
        # แปลงข้อมูลจาก Firebase Dict เป็น List และเรียงลำดับตามเวลา
        if isinstance(raw_p_msgs, dict):
            msgs_list = list(raw_p_msgs.values())
        else:
            msgs_list = [m for m in raw_p_msgs if m is not None]
        return sorted(msgs_list, key=lambda x: x.get('ts', 0))[-10:]
    return []

# --- 4. การประกอบหน้าจอ (UI แบบรวมทุกอย่าง) ---
st.set_page_config(page_title="GPS & Private Chat Real-time", layout="wide")
play_audio() # รันฟังก์ชันเสียง

st.markdown("### 📍 แผนที่เรียวทาม GPS & นาฬิกาบ่งบอกตามตำแหน่ง")

# ส่วนประกอบ GPS และเวลา (Real-time จริง)
st.components.v1.html("""
    <div style="background: #000; color: #00ff00; padding: 20px; border-radius: 10px; font-family: monospace; border: 2px solid #333;">
        <div style="display: flex; justify-content: space-between;">
            <div>🛰️ พิกัด (LAT/LONG): <span id="gps-display">รอสัญญาณ...</span></div>
            <div>⏰ เวลาปัจจุบันที่ยืนอยู่: <span id="time-display">00:00:00</span></div>
        </div>
    </div>
    <script>
        function updateRealtime() {
            navigator.geolocation.getCurrentPosition(function(pos) {
                document.getElementById('gps-display').innerText = pos.coords.latitude.toFixed(6) + ", " + pos.coords.longitude.toFixed(6);
            });
            document.getElementById('time-display').innerText = new Date().toLocaleTimeString('th-TH');
        }
        setInterval(updateRealtime, 1000);
    </script>
""", height=100)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 ระบบแชทส่วนตัว (Private Chat)")
    my_name = st.text_input("ชื่อของคุณ", value="User1")
    target_name = st.text_input("แชทกับใคร", value="User2")
    
    if my_name and target_name:
        # แสดงแชท
        chat_data = private_chat_logic(my_name, target_name)
        for c in chat_data:
            with st.chat_message("user" if c['name'] == my_name else "assistant"):
                st.write(f"**{c['name']}**: {c['msg']}")
        
        # ส่งข้อความ
        with st.form("chat_form", clear_on_submit=True):
            p_msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง") and p_msg:
                private_chat_logic(my_name, target_name, p_msg)
                st.rerun()

with col2:
    st.subheader("📹 วิดีโอคอล")
    st.info("ใครที่มีลิ้งสามารถแชทกันเได้ทุกคนเฉพาะลิ้งนี้")
    
    if st.button("เปิดวิดีโอคอล"):
        st.components.v1.html("""
            <video id="v" autoplay playsinline style="width:100%; border-radius:15px; border:2px solid #00ff00; background:#000;"></video>
            <script>
                navigator.mediaDevices.getUserMedia({video: true, audio: true})
                .then(s => { document.getElementById('v').srcObject = s; });
            </script>
        """, height=350)
    else:
        st.write("อยู่นิ่งๆ ไม่เจ็บตัว... กดปุ่มเพื่อเปิดกล้อง")

# ระบบรีเฟรชหน้าจอ (ถ้าต้องการให้แชทอัปเดตเอง)
if st.button("🔄 อัปเดตข้อมูล"):
    st.rerun()
