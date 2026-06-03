import streamlit as st
import streamlit.components.v1 as components
import requests
import json

FIREBASE_DB_URL = "https://sooksun1-default-rtdb.firebaseio.com"

# สมมติชื่อผู้ใช้เพื่อแยกข้อมูล
my_name = st.selectbox("เลือกบัญชีของคุณเพื่ออัปเดต GPS:", ["นายกานต์", "นายบาส"])
friend_name = "นายบาส" if my_name == "นายกานต์" else "นายกานต์"

st.subheader("🛰️ ระบบติดตามพิกัด GPS ความแม่นยำสูง")

# 1. ดึงพิกัดล่าสุดของเพื่อนจาก Firebase มาโชว์บนหน้าจอเรา
try:
    friend_gps = requests.get(f"{FIREBASE_DB_URL}/users/{friend_name}/gps.json").json()
except:
    friend_gps = None

if friend_gps:
    st.info(f"📍 พิกัดล่าสุดของ **{friend_name}**: Lat: {friend_gps.get('lat')}, Lon: {friend_gps.get('lon')} (อัปเดตเมื่อ: {friend_gps.get('time')})")
    # นายนสามารถเอาค่า Lat, Lon นี้ไปเปิดใน Google Maps ดูตำแหน่งเพื่อนได้เลย
else:
    st.write(f"⚪ ยังไม่มีข้อมูลพิกัดของ {friend_name}")

st.markdown("---")

# 2. ปุ่มกดของตัวเราเองเพื่อส่งพิกัดขึ้น Firebase
st.write("กดปุ่มด้านล่างเพื่อส่งพิกัดปัจจุบันของคุณให้เพื่อนเห็น:")

# ตัวรับค่าที่ส่งมาจาก JavaScript (Hidden input เพื่อส่งค่ากลับเข้า Python)
lat_input = st.hidden_input(label="lat", key="my_lat")
lon_input = st.hidden_input(label="lon", key="my_lon")

# ส่วนประกอบ HTML/JavaScript ที่คุยกับฮาร์ดแวร์ GPS ของมือถือโดยตรง
components.html(f"""
    <div style="text-align: center;">
        <button onclick="getLocation()" style="padding: 12px; background-color: #4CAF50; color: white; border: none; border-radius: 8px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer;">
            📍 อัปเดตและแชร์พิกัด GPS ของฉัน
        </button>
        <p id="status" style="color: #888; font-size: 13px; margin-top: 8px;"></p>
    </div>

    <script>
    function getLocation() {{
        var statusText = document.getElementById("status");
        if (navigator.geolocation) {{
            statusText.innerHTML = "กำลังค้นหาสัญญาณดาวเทียม...";
            // enableHighAccuracy: true สั่งให้เปิดใช้ GPS จริงจากเครื่อง ไม่ใช้พิกัดสุ่มจากอินเทอร์เน็ต
            navigator.geolocation.getCurrentPosition(sendPosition, showError, {{
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }});
        }} else {{ 
            statusText.innerHTML = "เบราว์เซอร์นี้ไม่รองรับระบบ GPS";
        }}
    }}

    function sendPosition(position) {{
        var lat = position.coords.latitude;
        var lon = position.coords.longitude;
        var timeNow = new Date().toLocaleTimeString();
        
        document.getElementById("status").innerHTML = "จับพิกัดสำเร็จ! กำลังบันทึกข้อมูล...";
        
        // ยิงข้อมูลพิกัดตรงเข้า Firebase Realtime Database ของผู้ใช้คนนี้ทันที
        var data = {{
            lat: lat,
            lon: lon,
            time: timeNow
        }};
        
        fetch('{FIREBASE_DB_URL}/users/{my_name}/gps.json', {{
            method: 'PUT',
            body: JSON.stringify(data)
        }}).then(response => {{
            document.getElementById("status").innerHTML = "แชร์พิกัดเรียบร้อยแล้ว (Lat: " + lat + ")";
        }}).catch(error => {{
            document.getElementById("status").innerHTML = "บันทึกข้อมูลล้มเหลว";
        }});
    }}

    function showError(error) {{
        var statusText = document.getElementById("status");
        switch(error.code) {{
            case error.PERMISSION_DENIED:
                statusText.innerHTML = "คุณต้องกด 'อนุญาต' ให้แอปเข้าถึง GPS ก่อนนะครับ";
                break;
            case error.POSITION_UNAVAILABLE:
                statusText.innerHTML = "ไม่สามารถระบุตำแหน่งได้ (สัญญาณขาดหาย)";
                break;
            case error.TIMEOUT:
                statusText.innerHTML = "หมดเวลารอสัญญาณ GPS";
                break;
            default:
                statusText.innerHTML = "เกิดข้อผิดพลาดลึกลับเกี่ยวกับระบบพิกัด";
        }}
    }}
    </script>
""", height=100)
