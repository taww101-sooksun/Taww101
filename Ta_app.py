import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# ตั้งค่าหน้าจอแอป SYNAPSE
st.set_page_config(page_title="SYNAPSE CALL", page_icon="🔮", layout="centered")

# --- 1. ดึงรูปโลโก้ Logo1.png จาก GitHub ของนาย ---
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/Logo1.png"
try:
    st.image(logo_url, use_container_width=True)
except:
    st.title("🔮 SYNAPSE CALL")

st.markdown("---")

# --- 2. ตั้งค่าการเชื่อมต่อ Firebase (อิงจากฐานข้อมูลของนาย) ---
# ใช้ URL ฐานข้อมูลที่นายให้มาในตอนแรก
FIREBASE_DB_URL = "https://sooksun1-default-rtdb.firebaseio.com"

# สมมติระบบล็อกอิน (นายกานต์ และ นายบาส) เพื่อให้เห็นภาพการแยกแยะ 100 คนไม่ให้มั่วกัน
st.subheader("👤 ข้อมูลผู้ใช้งานปัจจุบัน")
my_name = st.selectbox("คุณคือใครในระบบ :", ["นายกานต์", "นายบาส"])
friend_name = "นายบาส" if my_name == "นายกานต์" else "นายกานต์"

st.info(f"ตอนนี้คุณล็อกอินเป็น: **{my_name}** | เพื่อนของคุณคือ: **{friend_name}**")

st.markdown("---")

# --- 3. ฝั่งคนโทร (กดโทรหาเพื่อน) ---
st.subheader("🤙 โทรหาเพื่อน")
if st.button(f"📞 กดโทรหา {friend_name}"):
    st.warning(f"กำลังส่งสัญญาณเรียกเข้าไปยังเครื่องของ {friend_name}...")
    
    # ยิงข้อมูลไปที่ Firebase เพื่อเปลี่ยนสถานะเครื่องของเพื่อนว่ามีสายเข้า
    call_data = {
        "incoming_call": True,
        "caller": my_name
    }
    # ส่งข้อมูลไปบันทึกในกล่องของเพื่อน
    response = requests.put(
        f"{FIREBASE_DB_URL}/users/{friend_name}/call_status.json", 
        data=json.dumps(call_data)
    )
    if response.status_code == 200:
        st.success("ส่งสัญญาณแจ้งเตือนสำเร็จแล้ว! (รอเพื่อนกดรับสาย)")

if st.button("❌ วางสาย / ยกเลิกการโทร"):
    # ล้างสถานะใน Firebase ให้กลับเป็นปกติ
    clear_data = {"incoming_call": False, "caller": ""}
    requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/call_status.json", data=json.dumps(clear_data))
    st.info("ยกเลิกสายแล้ว")


st.markdown("---")

# --- 4. ฝั่งคนรับ (โค้ดตรวจจับสัญญาณและเปิดเสียงแจ้งเตือน) ---
st.subheader("🔔 สถานะการรับสายของคุณ")

# โค้ดส่วนนี้จะวิ่งไปเช็คที่ Firebase ของตัวเองตลอดเวลาว่ามีคนโทรมาไหม
try:
    check_response = requests.get(f"{FIREBASE_DB_URL}/users/{my_name}/call_status.json")
    status = check_response.json()
except:
    status = None

# ลิงก์เสียงเรดาร์ดิบจาก GitHub ของนาย (ไม่มีการสั่นตามที่แจ้งไว้)
synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"

if status and status.get("incoming_call") == True:
    caller_name = status.get("caller", "ไม่ทราบชื่อ")
    st.error(f"🚨 มีสายเรียกเข้าจาก: **{caller_name}**")
    
    # ปุ่มควบคุมสำหรับฝั่งคนรับสาย
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 กดรับสาย"):
            st.success("เชื่อมต่อสัญญาณเสียงสำเร็จ (ระบบ WebRTC เริ่มทำงาน)")
            # ในอนาคตจะใส่โค้ดเปิดไมค์คุยกันตรงนี้
            
    with col2:
        if st.button("🔴 ปฏิเสธสาย"):
            clear_data = {"incoming_call": False, "caller": ""}
            requests.put(f"{FIREBASE_DB_URL}/users/{my_name}/call_status.json", data=json.dumps(clear_data))
            st.experimental_rerun()

    # สั่งให้บราวเซอร์เปิดเสียงเรดาร์ทันทีเมื่อตรวจเจอ incoming_call: True
    components.html(f"""
        <script>
            var audio = new Audio('{synapse_radar_tone}');
            audio.loop = true; // เล่นวนลูปไปเรื่อยๆ จนกว่าจะกดรับหรือตัดสาย
            audio.play().catch(function(error) {{
                console.log("ตามกฎความปลอดภัยของมือถือ ต้องเคยแตะหน้าจอแอปอย่างน้อย 1 ครั้ง เสียงถึงจะดังอัตโนมัติได้");
            }});
        </script>
    """, height=0)
else:
    st.write("🟢 ไม่มีสายเรียกเข้าในขณะนี้ (สแตนด์บายปกติ)")
