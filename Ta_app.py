import streamlit as st
import os
import random
import json
from streamlit_folium import st_folium
import folium

# 1. ตั้งค่าหน้าจอแอปให้กว้างพิเศษ (Wide)
st.set_page_config(page_title="SYNAPSE COMMAND CENTER - AREA PRO v5", page_icon="🚜", layout="wide")

# 2. ปรับแต่งสไตล์และโทนสีแอป
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #090d16 0%, #111424 50%, #1a0b2e 100%); 
    }
    h1, h2, h3, p, label, span, button { color: #ffffff !important; font-family: 'Sans-serif'; }
    
    .neon-title {
        color: #00ffcc !important;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        font-weight: bold;
    }
    
    .music-box {
        background: rgba(26, 11, 46, 0.8);
        border: 2px solid #9d4edd;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(157, 78, 221, 0.5);
    }
    
    /* กล่องประวัติ */
    .history-container {
        background: #1a0b2e;
        border: 1px solid #9d4edd;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. ส่วนหัวของแอปและการแสดงโลโก้
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo1.png"):
        st.image("logo1.png", width=120)
    else:
        st.write("🛰️ [SYNAPSE]")

with col_title:
    st.markdown("<h1 class='neon-title'>🚜 ระบบวัดที่นาสัจจะ - AREA PRO v5 (Streamlit Native)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #ff3333 !important; font-style: italic; font-weight: bold; text-shadow: 0 0 5px #ff3333;'>\"อยู่นิ่งๆ ไม่เจ็บตัว วัดตามความจริง ไม่มีใครโกหกใครได้\"</p>", unsafe_allow_html=True)

st.write("---")

# 4. ระบบเครื่องเล่นเพลงสุ่มอัตโนมัติ
st.markdown("<div class='music-box'>", unsafe_allow_html=True)
st.subheader("🎵 SYNAPSE AUDIO STREAM")

music_files = [f for f in os.listdir('.') if f.endswith('.mp3')]

if music_files:
    if "playlist" not in st.session_state or len(st.session_state.playlist) == 0:
        random.shuffle(music_files)
        st.session_state.playlist = music_files
        st.session_state.current_track_index = 0

    current_track = st.session_state.playlist[st.session_state.current_track_index]
    st.write(f"🎧 **กำลังเล่นตอนนี้:** {current_track}")
    
    with open(current_track, "rb") as audio_file:
        audio_bytes = audio_file.read()
    
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    
    if st.button("⏭️ ข้ามไปเพลงถัดไป"):
        st.session_state.current_track_index = (st.session_state.current_track_index + 1) % len(st.session_state.playlist)
        st.rerun()
else:
    st.info("💡 ไม่มีไฟล์เพลง .mp3 ในโฟลเดอร์นี้ นำไฟล์เพลงมาวางคู่กับไฟล์โค้ดแล้วระบบจะเปิดเพลงอัตโนมัติทันที")

st.markdown("</div>", unsafe_allow_html=True)

# 5. ระบบบันทึกข้อมูลและพิกัดลงใน Session State ของ Python เพื่อความชัวร์
if "points" not in st.session_state:
    st.session_state.points = []
if "history" not in st.session_state:
    st.session_state.history = []
if "area_result" not in st.session_state:
    st.session_state.area_result = "ยังไม่ได้ลากแปลงนา"

st.subheader("🛰️ แผนที่ดาวเทียมระบบเซ็นเตอร์ (ดึงตรงผ่านเซิร์ฟเวอร์ ไม่โดนบล็อก)")
st.caption("💡 วิธีใช้งานแบบชัวร์ที่สุด: เลื่อนดูแผนที่ ยืดซูมเข้าออกด้วยนิ้วมือได้ตามต้องการ เมื่อได้มุมคันนาแล้วให้ 'จิ้มไปที่หน้าจอแผนที่ตรงคันนานั้นโดยตรง' เพื่อปักหมุดสีแดงได้เลยครับ")

# พิกัดเริ่มต้น (ร้อยเอ็ด)
start_lat = 15.9513057
start_lng = 103.5796196

# สร้างแผนที่ Folium โดยใช้ภาพดาวเทียมของ Esri ผ่านระบบหลังบ้าน Python
m = folium.Map(
    location=[start_lat, start_lng], 
    zoom_start=17, 
    max_zoom=20,
    control_scale=True
)

# ดึง Layer ดาวเทียมแท้
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite',
    max_zoom=20,
    overlay=False,
    control=True
).addTo(m)

# วาดหมุดสีแดงตามพิกัดที่คนจิ้มไว้
for idx, pt in enumerate(st.session_state.points):
    folium.CircleMarker(
        location=[pt[0], pt[1]],
        radius=6,
        color='red',
        fill=True,
        fill_color='red',
        popup=f"จุดที่ {idx+1}"
    ).addTo(m)

# วาดเส้นเชื่อมแปลงนาถ้ามีมากกว่า 2 จุดขึ้นไป
if len(st.session_state.points) > 1:
    folium.Polygon(
        locations=st.session_state.points,
        color='#00ffcc',
        weight=3,
        fill=True,
        fill_color='#00ffcc',
        fill_opacity=0.3
    ).addTo(m)

# ปุ่มสั่งการฝั่ง Python เพื่อให้กดง่ายและแสดงผลไวบนมือถือ
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🗑️ ล้างค่าเริ่มใหม่", use_container_width=True):
        st.session_state.points = []
        st.session_state.area_result = "ยังไม่ได้ลากแปลงนา"
        st.rerun()

with col_btn2:
    if st.button("📐 คำนวณพื้นที่นาจริง", use_container_width=True):
        if len(st.session_state.points) < 3:
            st.error("⚠️ ต้องจิ้มปักหมุดบนแผนที่อย่างน้อย 3 มุมขึ้นไปถึงจะคำนวณแปลงนาได้ครับ!")
        else:
            # ใช้สูตรคำนวณพื้นที่แบบ Shoelace บนพิกัดภูมิศาสตร์ (ทำได้จริงบน Python ไม่พึ่งพาคลังภายนอก)
            import math
            def get_area(pts):
                # แปลงพิกัดเป็นเมตรคร่าวๆ เพื่อความแม่นยำทางพื้นที่แปลงนาไทย
                R = 6378137
                x = []
                y = []
                for p in pts:
                    lat_rad = math.radians(p[0])
                    lng_rad = math.radians(p[1])
                    x.append(R * lng_rad * math.cos(math.radians(start_lat)))
                    y.append(R * lat_rad)
                # ปิดลูป
                x.append(x[0])
                y.append(y[0])
                
                area = 0.0
                for i in range(len(pts)):
                    area += (x[i] * y[i+1]) - (x[i+1] * y[i])
                return abs(area) / 2.0

            area_sqm = get_area(st.session_state.points)
            total_wa = area_sqm / 4
            rai = int(total_wa // 400)
            remaining_wa = total_wa % 400
            ngan = int(remaining_wa // 100)
            wa = round(remaining_wa % 100)
            
            st.session_state.area_result = f"{rai} ไร่ {ngan} งาน {wa} ตารางวา (สุทธิ {round(area_sqm, 1):,} ตร.ม.)"
            st.rerun()

# แสดงผลแผนที่ดาวเทียมของจริง และจับค่าการคลิกหน้าจอ
map_data = st_folium(m, height=600, width=1300, returned_objects=["last_clicked"])

# ถ้าผู้ใช้มีการ "จิ้ม" ที่แผนที่ดาวเทียม ให้เอาพิกัดเข้าคิวปักหมุดทันที
if map_data and map_data.get("last_clicked"):
    clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
    # ป้องกันไม่ให้จุดมันแอดซ้ำๆ ตอนรีรัน
    if not st.session_state.points or st.session_state.points[-1] != clicked_coords:
        st.session_state.points.append(clicked_coords)
        st.rerun()

# แสดงผลพื้นที่ที่คำนวณได้
st.markdown(f"""
    <div style='background:#111424; padding:20px; border-radius:10px; border: 1px solid #9d4edd; margin-top:15px;'>
        <b style='color:#00ffcc; font-size:16px;'>📐 หลักฐานขนาดพื้นที่นา (ตามจริง):</b>
        <h2 style='color:#ff3333; margin:10px 0;'>🌾 {st.session_state.area_result}</h2>
    </div>
""", unsafe_allow_html=True)

# 6. ฟอร์มเซฟประวัติและเรียกดูย้อนหลังให้กับเจ้าของนา
st.write("")
col_input, col_save = st.columns([3, 1])
with col_input:
    owner_name = st.text_input("ระบุชื่อเจ้าของนา เช่น ตาดี ยายมี (เพื่อบันทึกประวัติ)", placeholder="พิมพ์ชื่อตรงนี้...")
with col_save:
    st.write("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    if st.button("💾 บันทึกข้อมูลแปลงนา", use_container_width=True):
        if owner_name.strip() == "":
            st.warning("⚠️ โปรดระบุชื่อเจ้าของนาก่อนบันทึกครับ")
        elif st.session_state.area_result == "ยังไม่ได้ลากแปลงนา":
            st.warning("⚠️ โปรดกดปุ่มคำนวณพื้นที่ให้เรียบร้อยก่อนบันทึก")
        else:
            st.session_state.history.append({
                "owner": owner_name,
                "result": st.session_state.area_result,
                "points": list(st.session_state.points)
            })
            st.success(f"💾 บันทึกที่นาของ {owner_name} ลงฐานข้อมูลเรียบร้อย!")
            st.rerun()

# ส่วนแสดงกล่องประวัติย้อนหลังให้เจ้าของนาดูอีกรอบ
st.markdown("<div class='history-container'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00ffcc; margin-top:0;'>📂 บันทึกประวัติที่นาเก่า (เปิดดูซ้ำให้เจ้าของดูย้อนหลัง)</h3>", unsafe_allow_html=True)

if not st.session_state.history:
    st.write("ยังไม่มีข้อมูลประวัติการบันทึกในเซสชันนี้")
else:
    for idx, item in enumerate(st.session_state.history):
        col_hist_txt, col_hist_btn = st.columns([4, 1])
        with col_hist_txt:
            st.write(f"👤 **{item['owner']}** — {item['result']}")
        with col_hist_btn:
            if st.button(f"👁️ เปิดดูแปลง", key=f"load_{idx}", use_container_width=True):
                st.session_state.points = item["points"]
                st.session_state.area_result = item["result"]
                st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
