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
    
    /* ปุ่มกดสไตล์นีออน */
    .map-btn {
        background-color: #00ffcc;
        color: #000000 !important;
        border: 2px solid #00ffcc;
        padding: 12px 20px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 8px;
        cursor: pointer;
        margin-right: 10px;
        margin-bottom: 10px;
        box-shadow: 0 0 8px #00ffcc;
        transition: 0.3s;
    }
    .map-btn:hover { background-color: #00cc99; box-shadow: 0 0 15px #00cc99; }
    
    .map-btn-danger { 
        background-color: #ff3333; border-color: #ff3333; color: white !important;
        box-shadow: 0 0 8px #ff3333;
    }
    .map-btn-danger:hover { background-color: #cc0000; box-shadow: 0 0 15px #cc0000; }
    
    .map-btn-success { 
        background-color: #9d4edd; border-color: #9d4edd; color: white !important;
        box-shadow: 0 0 8px #9d4edd;
    }
    .map-btn-success:hover { background-color: #7b2cbf; box-shadow: 0 0 15px #7b2cbf; }

    /* กล่องเครื่องเล่นเพลง */
    .music-box {
        background: rgba(26, 11, 46, 0.8);
        border: 2px solid #9d4edd;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(157, 78, 221, 0.5);
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


# 5. 🛰️ แผนที่ดาวเทียมขยายขนาดใหญ่พิเศษ (MEGA SCALE 750px)
st.subheader("🛰️ แผนที่ดาวเทียมสเกลใหญ่พิเศษ (ลากเส้นและเล็งคันนาง่ายขึ้น)")
st.caption("💡 วิธีใช้งาน: แพนหน้าจอให้มุมแปลงนาอยู่ตรงกลางเป้าแดงพอดีเป๊ะ แล้วกดปุ่มปักหมุดสีม่วง")

default_lat = 15.9513057
default_lng = 103.5796196

# แก้ไขความสูงของตัว map ใน CSS เป็น 750px เพื่อให้ยาวลงมาเต็มที่หน้าจอมือถือ
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
    /* ขยายความสูงตรงนี้เป็น 750px เพื่อพื้นที่ที่กว้างกว่าเดิม */
    #map {{
        width: 100%;
        height: 750px; 
        border-radius: 14px;
        border: 2px solid #00ffcc;
        z-index: 1;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
    }}
    /* เป้าเล็งกึ่งกลางสีแดงนีออนสะท้อนแสง */
    .crosshair {{
        position: absolute;
        top: 50%;
        left: 50%;
        width: 30px;
        height: 30px;
        margin-top: -15px;
        margin-left: -15px;
        z-index: 9999;
        pointer-events: none;
        display: none;
    }}
    .crosshair::before, .crosshair::after {{
        content: '';
        position: absolute;
        background: #ff3333;
        box-shadow: 0 0 8px #ff3333;
    }}
    .crosshair::before {{ top: 14px; left: 0; width: 30px; height: 2px; }}
    .crosshair::after {{ top: 0; left: 14px; width: 2px; height: 30px; }}
    
    .control-panel {{
        margin-top: 15px;
        margin-bottom: 15px;
    }}
</style>

<div id="map-container">
    <div id="map"></div>
    <div id="crosshair-target" class="crosshair"></div>
</div>

<div class="control-panel">
    <button type="button" class="map-btn" onclick="toggleCrosshair()">🎯 เปิด/ปิด เป้าเล็งกึ่งกลาง</button>
    <button type="button" class="map-btn map-btn-success" onclick="addPointFromCenter()">📌 ปักหมุดตรงเป้า</button>
    <button type="button" class="map-btn map-btn-success" style="background:#ff3333; border-color:#ff3333;" onclick="calculateFromPoints()">💾 คำนวณพื้นที่จริง</button>
    <button type="button" class="map-btn map-btn-danger" onclick="clearAllDrawings()">🗑️ ล้างค่าเริ่มใหม่</button>
</div>

<div id="result-box" style="background:#111424; padding:15px; border-radius:10px; color:white; font-family:sans-serif; border: 1px solid #9d4edd;">
    <b style="color:#00ffcc; font-size:16px; text-shadow: 0 0 5px #00ffcc;"> 📐 หลักฐานขนาดพื้นที่นา (ตามจริง):</b>
    <p id="area-text" style="font-size:24px; margin:5px 0; font-weight:bold; color:#ff3333;">ยังไม่ได้ลากแปลงนา</p>
</div>

<script>
    var map = L.map('map').setView([{default_lat}, {default_lng}], 15);

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
            L.marker([lat, lng]).addTo(map).bindPopup('🚜 คุณอยู่ตรงนี้').openPopup();
        }}, function(err) {{
            console.log("GPS ช้า");
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

        L.circleMarker(center, {{radius: 6, color: '#ff3333', fillColor: '#ff3333', fillOpacity: 1}}).addTo(drawnItems);

        if (customPoints.length > 1) {{
            if (customPolygon) {{ map.removeLayer(customPolygon); }}
            customPolygon = L.polygon(customPoints, {{color: '#00ffcc', weight: 3, fillOpacity: 0.4}}).addTo(drawnItems);
        }}
    }}

    function calculateFromPoints() {{
        if (customPoints.length < 3) {{
            alert("ต้องปักหมุดอย่างน้อย 3 มุมขึ้นไปครับแปลงนาถึงจะสมบูรณ์!");
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
                "🌾 พื้นที่นาจริง: <span style='color:#00ffcc; text-shadow: 0 0 5px #00ffcc;'>" + rai + " ไร่ </span> " + 
                "<span style='color:#9d4edd; text-shadow: 0 0 5px #9d4edd;'>" + ngan + " งาน </span> " + 
                "<span style='color:#ff3333; text-shadow: 0 0 5px #ff3333;'>" + wa + " ตารางวา</span><br>" +
                "<span style='font-size:14px; color:#9ca3af; font-weight:normal;'>คำนวณสุทธิ: " + Math.round(areaSqMeters).toLocaleString() + " ตารางเมตร</span>";
        }}
    }}

    var drawControl = new L.Control.Draw({{
        draw: {{
            polygon: {{ allowIntersection: false, shapeOptions: {{ color: '#00ffcc', weight: 3, fillOpacity: 0.4 }} }},
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

# ขยายความสูงคอมโพเนนต์รวมของ Streamlit เป็น 960px เพื่อให้แสดงแผงควบคุมและผลลัพธ์ครบถ้วนโดยไม่ต้องเลื่อนสกอร์บาร์ซ้อนกัน
st.components.v1.html(map_html_code, height=960, scrolling=False)

st.success("⚡ เพิ่มสเกลแผนที่ให้ใหญ่ขึ้นเรียบร้อย! คราวนี้จิ้มมุมแปลงนาหรือเลื่อนเป้าแดงในมือถือได้ถนัด ชัดเจน คมชัด แน่นอนครับเพื่อน!")
