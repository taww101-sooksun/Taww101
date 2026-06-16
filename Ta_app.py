import streamlit as st
import os
import random

# 1. ตั้งค่าหน้าจอแอปให้กว้างพิเศษ (Wide) 
st.set_page_config(page_title="SYNAPSE COMMAND CENTER - AREA PRO v2", page_icon="🚜", layout="wide")

# 2. ปรับแต่งสไตล์และโทนสีแอป (น้ำเงิน แดง ม่วง ขาว เขียวนีออน)
st.markdown("""
    <style>
    /* พื้นหลังหลักและฟอนต์ */
    .stApp { 
        background: linear-gradient(135deg, #090d16 0%, #111424 50%, #1a0b2e 100%); 
    }
    h1, h2, h3, p, label, span { color: #ffffff !important; font-family: 'Sans-serif'; }
    
    /* หัวข้อใหญ่สีเขียวนีออน */
    .neon-title {
        color: #00ffcc !important;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        font-weight: bold;
    }
    
    /* กล่องเครื่องเล่นเพลง */
    .music-box {
        background: rgba(26, 11, 46, 0.8);
        border: 2px solid #9d4edd;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(157, 78, 221, 0.5);
    }

    /* กล่องบันทึกประวัติข้อมูลนา */
    .history-box {
        background: rgba(17, 20, 36, 0.9);
        border: 1px solid #9d4edd;
        padding: 20px;
        border-radius: 12px;
        margin-top: 25px;
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
    st.markdown("<h1 class='neon-title'>🚜 ระบบวัดที่นาสัจจะ - AREA PRO v2</h1>", unsafe_allow_html=True)
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


# 5. 🛰️ แผนที่ดาวเทียมขยายขนาดใหญ่พิเศษ (MEGA SCALE 820px) พร้อมสไตล์พิเศษเพิ่มความเท่
st.subheader("🛰️ แผนที่ดาวเทียมสเกลใหญ่พิเศษ (เวอร์ชันอัปเกรดพิเศษความคมชัดสูง)")
st.caption("💡 วิธีใช้งาน: เปิดเป้าเล็งสีแดงเพื่อความแม่นยำ แพนหน้าจอให้มุมคันนาอยู่ตรงเป้า แล้วกดปุ่มปักหมุดสีม่วงได้ทันที")

default_lat = 15.9513057
default_lng = 103.5796196

map_html_code = f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
<script src="https://unpkg.com/@turf/turf@6/turf.min.js"></script>

<style>
    #map-container {{
        position: relative;
        width: 100%;
    }}
    /* เพิ่มสเกลความสูงแผนที่ความพิเศษเป็น 820px คมชัดเต็มจอ */
    #map {{
        width: 100%;
        height: 820px; 
        border-radius: 16px;
        border: 3px solid #00ffcc;
        z-index: 1;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.6);
    }}
    /* เป้าเล็งกึ่งกลางสีแดงนีออนสะท้อนแสง ออกแบบให้ล้ำขึ้น */
    .crosshair {{
        position: absolute;
        top: 50%;
        left: 50%;
        width: 40px;
        height: 40px;
        margin-top: -20px;
        margin-left: -20px;
        z-index: 9999;
        pointer-events: none;
        display: none;
    }}
    .crosshair::before, .crosshair::after {{
        content: '';
        position: absolute;
        background: #ff3333;
        box-shadow: 0 0 12px #ff3333, 0 0 4px #ffffff;
    }}
    .crosshair::before {{ top: 19px; left: 0; width: 40px; height: 2px; }}
    .crosshair::after {{ top: 0; left: 19px; width: 2px; height: 40px; }}
    
    .control-panel {{
        margin-top: 20px;
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }}

    /* ปุ่มกดสไตล์นีออนอัปเกรดพิเศษ */
    .map-btn {{
        background-color: #00ffcc;
        color: #000000 !important;
        border: 2px solid #00ffcc;
        padding: 14px 24px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        cursor: pointer;
        box-shadow: 0 0 10px #00ffcc;
        transition: all 0.3s ease;
        flex: 1;
        min-width: 160px;
        text-align: center;
    }}
    .map-btn:hover {{ background-color: #00cc99; box-shadow: 0 0 20px #00cc99; transform: translateY(-2px); }}
    
    .map-btn-danger {{ 
        background-color: #ff3333; border-color: #ff3333; color: white !important;
        box-shadow: 0 0 10px #ff3333;
    }}
    .map-btn-danger:hover {{ background-color: #cc0000; box-shadow: 0 0 20px #cc0000; }}
    
    .map-btn-success {{ 
        background-color: #9d4edd; border-color: #9d4edd; color: white !important;
        box-shadow: 0 0 10px #9d4edd;
    }}
    .map-btn-success:hover {{ background-color: #7b2cbf; box-shadow: 0 0 20px #7b2cbf; }}

    /* ความพิเศษ: กล่องแสดงผลลัพธ์แบบเรืองแสงสลับสีล้ำยุค */
    .neon-result-box {{
        background: #090d16;
        padding: 20px;
        border-radius: 12px;
        color: white;
        font-family: sans-serif;
        border: 2px solid #9d4edd;
        box-shadow: 0 0 15px rgba(157, 78, 221, 0.4);
        animation: neonPulse 3s infinite alternate;
    }}
    @keyframes neonPulse {{
        0% {{ border-color: #9d4edd; box-shadow: 0 0 12px rgba(157, 78, 221, 0.4); }}
        100% {{ border-color: #00ffcc; box-shadow: 0 0 20px rgba(0, 255, 204, 0.5); }}
    }}
</style>

<div id="map-container">
    <div id="map"></div>
    <div id="crosshair-target" class="crosshair"></div>
</div>

<div class="control-panel">
    <button type="button" class="map-btn" onclick="toggleCrosshair()">🎯 เปิด/ปิด เป้าเล็ง</button>
    <button type="button" class="map-btn map-btn-success" onclick="addPointFromCenter()">📌 ปักหมุดพิกัด</button>
    <button type="button" class="map-btn map-btn-success" style="background:#00ffcc; border-color:#00ffcc; color:black !important; box-shadow: 0 0 10px #00ffcc;" onclick="calculateFromPoints()">📐 คำนวณพื้นที่นาสัจจะ</button>
    <button type="button" class="map-btn map-btn-danger" onclick="clearAllDrawings()">🗑️ ล้างค่าเริ่มใหม่</button>
</div>

<div class="neon-result-box">
    <b style="color:#00ffcc; font-size:16px; text-shadow: 0 0 5px #00ffcc;">🛰️ พิกัดแปลงและขนาดพื้นที่จริง (ตรวจสอบแล้ว):</b>
    <p id="area-text" style="font-size:26px; margin:10px 0; font-weight:bold; color:#ff3333; text-shadow: 0 0 5px rgba(255,51,51,0.5);">ยังไม่ได้ลากแปลงนา</p>
</div>

<script>
    var map = L.map('map').setView([{default_lat}, {default_lng}], 16);

    // ใช้แผนที่ระดับอัปเกรดความชัดสูงตัดขอบคันนา
    var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        maxZoom: 19
    }}).addTo(map);

    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);

    if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(function(position) {{
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            map.setView([lat, lng], 18);
            L.marker([lat, lng]).addTo(map).bindPopup('🚜 หมุดปัจจุบันของคุณ').openPopup();
        }}, function(err) {{
            console.log("GPS กำลังค้นหาข้อมูลตำแหน่งพิกัดสัญญาณพายธอน");
        }}, {{enableHighAccuracy: true}});
    }}

    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var customPoints = [];
    var customPolygon = null;
    var crosshairMode = false;

    function toggleCrosshair() {{
        var ch = document.getElementById('crosshair-target');
        crosshairMode = !crosshairMode;
        ch.style.display = crosshairMode ? 'block' : 'none';
    }}

    function addPointFromCenter() {{
        var center = map.getCenter();
        customPoints.push([center.lat, center.lng]);

        L.circleMarker(center, {{radius: 7, color: '#ff3333', fillColor: '#ffffff', weight: 3, fillOpacity: 1}}).addTo(drawnItems);

        if (customPoints.length > 1) {{
            if (customPolygon) {{ map.removeLayer(customPolygon); }}
            customPolygon = L.polygon(customPoints, {{color: '#00ffcc', weight: 4, fillOpacity: 0.35}}).addTo(drawnItems);
        }}
    }}

    function calculateFromPoints() {{
        if (customPoints.length < 3) {{
            alert("⚠️ ต้องปักหมุดที่นาให้ได้อย่างน้อย 3 มุมแปลงขึ้นไปครับครับเพื่อน!");
            return;
        }}
        
        var turfCoords = [];
        customPoints.forEach(function(pt) {{
            turfCoords.push([pt[1], pt[0]]);
        }});
        turfCoords.push([customPoints[0][1], customPoints[0][0]]);

        var polygonGeoJSON = turf.polygon([turfCoords]);
        var areaSqMeters = turf.area(polygonGeoJSON);
        
        showAreaResult(areaSqMeters);
    }}

    function clearAllDrawings() {{
        drawnItems.clearLayers();
        customPoints = [];
        customPolygon = null;
        document.getElementById('area-text').innerHTML = "ยังไม่ได้ลากแปลงนา";
    }}

    function showAreaResult(areaSqMeters) {{
        if (areaSqMeters > 0) {{
            var totalWa = areaSqMeters / 4;
            var rai = Math.floor(totalWa / 400);
            var remainingWa = totalWa % 400;
            var ngan = Math.floor(remainingWa / 100);
            var wa = Math.round(remainingWa % 100);

            document.getElementById('area-text').innerHTML = 
                "🌾 วัดได้จริง: <span style='color:#00ffcc; text-shadow: 0 0 5px #00ffcc;'>" + rai + " ไร่ </span> " + 
                "<span style='color:#9d4edd; text-shadow: 0 0 5px #9d4edd;'>" + ngan + " งาน </span> " + 
                "<span style='color:#ff3333; text-shadow: 0 0 5px #ff3333;'>" + wa + " ตารางวา</span><br>" +
                "<span style='font-size:14px; color:#9ca3af; font-weight:normal; display:block; margin-top:5px;'>สุทธิประมวลผลดาวเทียม: " + Math.round(areaSqMeters).toLocaleString() + " ตร.ม.</span>";
        }}
    }}

    var drawControl = new L.Control.Draw({{
        draw: {{
            polygon: {{ allowIntersection: false, shapeOptions: {{ color: '#00ffcc', weight: 4, fillOpacity: 0.35 }} }},
            rectangle: {{ shapeOptions: {{ color: '#00ffcc' }} }},
            polyline: false, circle: false, marker: false, circlemarker: false
        }},
        edit: {{ featureGroup: drawnItems }}
    }});
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (event) {{
        var layer = event.layer;
        drawnItems.clearLayers();
        drawnItems.addLayer(layer);
        var geojson = layer.toGeoJSON();
        var areaSqMeters = turf.area(geojson);
        showAreaResult(areaSqMeters);
    }});
</script>
"""

# ตั้งความสูงพื้นที่รวมเป็น 1050px เพื่อให้ไม่เบียดและเก็บความกว้างของเป้าเล็งและกล่องนีออนได้เนียนสนิท
st.components.v1.html(map_html_code, height=1050, scrolling=False)

# 6. 📂 ส่วนความพิเศษเพิ่มเติม: ระบบบันทึกรายชื่อเจ้าของแปลงนาฝั่ง Python (ปลอดภัย ไร้ JSON)
if "history_list" not in st.session_state:
    st.session_state.history_list = []

st.markdown("<div class='history-box'>", unsafe_allow_html=True)
st.subheader("📂 สมุดลงทะเบียนบันทึกแปลงนาเก่า")

col_name, col_btn = st.columns([3, 1])
with col_name:
    farmer_name = st.text_input("✍️ ระบุชื่อเจ้าของที่นาสัจจะแปลงนี้:", placeholder="เช่น ตาดี ยายมี นายมั่น...")

with col_btn:
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    if st.button("💾 บันทึกเก็บข้อมูล", use_container_width=True):
        if farmer_name.strip() == "":
            st.warning("⚠️ เพื่อนลืมใส่ชื่อชาวนาเจ้าของแปลงครับ ระบุก่อนกดบันทึกนะ")
        else:
            st.session_state.history_list.append(farmer_name)
            st.success(f"บันทึกข้อมูลของคุณ '{farmer_name}' ลงระบบเซสชันฝั่ง Python เรียบร้อยแล้ว!")

if st.session_state.history_list:
    st.write("---")
    st.write("📊 **รายชื่อที่ดินที่ผ่านการลงทะเบียนรอบนี้:**")
    for i, name in enumerate(st.session_state.history_list):
        st.write(f"👤 ลำดับที่ {i+1}: คุณ {name} 🌾")
st.markdown("</div>", unsafe_allow_html=True)

st.success("⚡ ตัวท็อปเวอร์ชันพิเศษอัปเกรดสำเร็จ! สเกลใหญ่ คมชัด เรืองแสงนีออนเรียบร้อย เอาไปเปิดลุยใช้งานจริงได้เลยครับเพื่อน!")
