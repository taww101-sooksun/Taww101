import streamlit as st
import time
from firebase_admin import credentials, db, initialize_app

# --- 1. SETUP FIREBASE (ใช้ข้อมูลหลังบ้านของคุณ) ---
if not st.session_state.get("firebase_init"):
    try:
        # ดึงข้อมูลจาก st.secrets ที่คุณเอาไปไว้หลังบ้านแล้ว
        cred = credentials.Certificate({
            "project_id": st.secrets["project_id"],
            "private_key": st.secrets["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["client_email"],
        })
        initialize_app(cred, {
            'databaseURL': st.secrets["database_url"]
        })
        st.session_state["firebase_init"] = True
    except Exception as e:
        st.error(f"การเชื่อมต่อ Firebase ผิดพลาด: {e}")

# --- 2. ฟังก์ชันเล่นเสียง (Auto-play ตามที่คุณส่งมา) ---
def play_audio():
    link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.components.v1.html(f"""
        <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{link}" type="audio/mpeg"></audio>
        <script>
            var audio = document.getElementById("synapse-audio");
            window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
        </script>
    """, height=0)

# --- 3. LOGIC แชทส่วนตัว (จากโค้ดที่คุณส่งมา) ---
def private_chat_logic(my_name, target_name, p_msg=None):
    pair = sorted([my_name, target_name])
    room_id = f"priv_{pair[0]}_{pair[1]}"
    
    ref = db.reference(f'private_rooms/{room_id}')
    
    if p_msg:
        ref.push({
            'name': my_name, 
            'msg': p_msg, 
            'ts': time.time()
        })
    
    raw_p_msgs = ref.get()
    if raw_p_msgs:
        return sorted(raw_p_msgs.values(), key=lambda x: x.get('ts', 0))[-15:]
    return []

# --- 4. หน้าจอหลัก (UI) ---
st.set_page_config(page_title="GPS Chat System", layout="wide")
play_audio() # รันระบบเสียง

# ส่วน GPS และเวลา (Real-time จริงตามตำแหน่งที่ยืน)
st.markdown("### 📍 ระบบพิกัดและเวลาเรียลไทม์")
st.components.v1.html("""
    <div style="background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 10px; font-family: monospace; border: 1px solid #333;">
        <div style="display: flex; justify-content: space-around;">
            <div>📡 LAT/LONG: <span id="gps-val">กำลังรับสัญญาณ...</span></div>
            <div>⏰ LOCAL TIME: <span id="clock-val">00:00:00</span></div>
        </div>
    </div>
    <script>
        function updateInfo() {
            navigator.geolocation.getCurrentPosition(pos => {
                document.getElementById('gps-val').innerText = pos.coords.latitude.toFixed(6) + ", " + pos.coords.longitude.toFixed(6);
            });
            document.getElementById('clock-val').innerText = new Date().toLocaleTimeString('th-TH');
        }
        setInterval(updateInfo, 1000);
    </script>
""", height=80)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 ระบบแชทส่วนตัว")
    my_name = st.text_input("ชื่อของคุณ", value="User1")
    target_name = st.text_input("ชื่อคู่สนทนา", value="User2")
    
    if my_name and target_name:
        # ดึงข้อความจาก Firebase
        messages = private_chat_logic(my_name, target_name)
        
        # กล่องแสดงข้อความ
        chat_placeholder = st.empty()
        with chat_placeholder.container():
            for m in messages:
                align = "text-align:right;" if m['name'] == my_name else "text-align:left;"
                bg = "#dcf8c6" if m['name'] == my_name else "#ffffff"
                st.markdown(f"""
                    <div style="{align} margin-bottom: 10px;">
                        <div style="display: inline-block; background: {bg}; padding: 8px 12px; border-radius: 10px; border: 1px solid #ddd; color: black;">
                            <b>{m['name']}</b>: {m['msg']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # ช่องส่งข้อความ
        with st.form("send_msg", clear_on_submit=True):
            user_input = st.text_input("พิมพ์อะไรบางอย่าง...")
            if st.form_submit_button("ส่งข้อความ") and user_input:
                private_chat_logic(my_name, target_name, p_msg=user_input)
                st.rerun()

with col2:
    st.subheader("📹 วิดีโอคอล")
    if st.button("🔴 เปิดกล้องเชื่อมต่อ"):
        st.warning("ระบบกำลังเรียกใช้งาน WebRTC ผ่านพิกัดปัจจุบันของคุณ...")
        st.components.v1.html("""
            <div style="display:flex; gap:10px;">
                <video id="localVideo" autoplay playsinline muted style="width:100%; border-radius:10px; background:black;"></video>
            </div>
            <script>
                navigator.mediaDevices.getUserMedia({video: true, audio: true})
                .then(stream => { document.getElementById('localVideo').srcObject = stream; })
                .catch(err => { console.error("ไม่สามารถเปิดกล้องได้", err); });
            </script>
        """, height=300)
    else:
        st.info("อยู่นิ่งๆ ไม่เจ็บตัว... กดปุ่มด้านบนเพื่อเริ่มวิดีโอ")

# ระบบ Refresh ข้อมูลอัตโนมัติเพื่อให้แชทดูเรียลไทม์
if st.button("🔄 อัปเดตแชท"):
    st.rerun()
