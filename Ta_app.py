import streamlit as st
import os
import random

# 1. ตั้งค่าหน้าจอแอปให้กว้างพิเศษ (Wide) 
st.set_page_config(page_title="SYNAPSE COMMAND CENTER - AREA PRO v2", page_icon="🚜", layout="wide")

# 2. ปรับแต่งสไตล์และโทนสีแอป
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #090d16 0%, #111424 50%, #1a0b2e 100%); 
    }
    h1, h2, h3, p, label, span { color: #ffffff !important; font-family: 'Sans-serif'; }
    
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


# 5. 🛰️ แผนที่ดาวเทียมขยายขนาดใหญ่พิเศษ (MEGA SCALE) + ระบบบันทึกประวัติที่ทำงานได้จริงในหน้าจอเดียว
st.subheader("🛰️ แผนที่ดาวเทียมสเกลใหญ่ (ระบบคำนวณและบันทึกประวัติจริงหน้างาน)")
st.caption("💡 วิธีใช้งาน: เล็งเป้าแดงให้ตรงมุมแปลงนา กดปุ่มปักหมุดจนครบแปลง พิมพ์ชื่อเจ้าของแล้วกดบันทึก ข้อมูลจะแสดงในตารางประวัติด้านล่างทันที")

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
    #map {{
        width: 100%;
        height: 500px; 
        border-radius: 16px;
        border: 3px solid #00ffcc;
        z-index: 1;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.6);
    }}
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
        min-width: 150px;
        text-align: center;
    }}
    .map-btn:hover {{ background-color: #00cc99; box-shadow: 0 0 20px #00cc99; transform: translateY(-2px); }}
    .map-btn-danger {{ background-color: #ff3333; border-color: #ff3333; color: white !important; box-shadow: 0 0 10px #ff3333;}}
    .map-btn-danger:hover {{ background-color: #cc0000; box-shadow: 0 0 20px #cc0000; }}
    .map-btn-success {{ background-color: #9d4edd; border-color: #9d4edd; color: white !important; box-shadow: 0 0 10px #9d4edd;}}
    .map-btn-success:hover {{ background-color: #7b2cbf; box-shadow: 0 0 20px #7b2cbf; }}

    .neon-result-box {{
        background: #090d16;
        padding: 20px;
        border-radius: 12px;
        color: white;
        font-family: sans-serif;
        border: 2px solid #9d4edd;
        box-shadow: 0 0 15px rgba(157, 78, 221, 0.4);
        margin-bottom: 20px;
    }}

    /* สไตล์ส่วนกล่องบันทึกข้อมูลของจริง */
    .save-panel {{
        background: rgba(26, 11, 46, 0.6);
        border: 1px solid #9d4edd;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 25px;
        display: flex;
        gap: 15px;
        align-items: center;
    }}
    .save-input {{
        background: #111424;
        border: 1px solid #00ffcc;
        color: white;
        padding: 12px;
        border-radius: 8px;
        font-size: 16px;
        flex: 2;
    }}
    .history-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        background: #111424;
        color: white;
        border-radius: 8px;
        overflow: hidden;
        font-family: sans-serif;
    }}
    .history-table th, .history-table td {{
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #1a0b2e;
    }}
    .history-table th {{
        background-color: #9d4edd;
        color: white;
    }}
</style>

<div id="map-container">
    <div id="map"></div>
    <div id="crosshair-target" class="crosshair"></div>
</div>

<div class="control-panel">
    <button type="button" class="map-btn" onclick="toggleCrosshair()">🎯 เปิด/ปิด เป้าเล็ง</button>
    <button type="button" class="map-btn map-btn-success" onclick="addPointFromCenter()">📌 ปักหมุดพิกัด</button>
    <button type="button" class="map-btn map-btn-success" style="background:#00ffcc; border-color:#00ffcc; color:black !important; box-shadow: 0 0 10px #00ffcc;" onclick="calculateFromPoints()">📐 คำนวณพื้นที่นาแปลงนี้</button>
    <button type="button" class="map-btn map-btn-danger" onclick="clearAllDrawings()">🗑️ ล้างค่าเริ่มใหม่</button>
</div>

<div class="neon-result-box">
    <b style="color:#00ffcc; font-size:16px; text-shadow: 0 0 5px #00ffcc;">🛰️ ขนาดพื้นที่นาปัจจุบัน (วัดตามจริง):</b>
    <p id="area-text" style="font-size:26px; margin:10px 0; font-weight:bold; color:#ff3333;">ยังไม่ได้ลากแปลงนา</p>
</div>

<div class="save-panel">
    <input type="text" id="farmer-name" class="save-input" placeholder="พิมพ์ชื่อเจ้าของที่นาเพื่อบันทึกประวัติ...">
    <button type="button" class="map-btn map-btn-success" style="margin:0; flex:1;" onclick="saveToHistoryTable()">💾 บันทึกประวัติแปลงนี้</button>
</div>

<div style="background: rgba(17, 20, 36, 0.9); padding:15px; border-radius:12px; border: 1px solid #9d4edd;">
    <b style="color:#00ffcc; font-size:16px;">📊 ตารางประวัติการวัดที่นาสัจจะ (บันทึกแล้วกดดูได้ทันที):</b>
    <table class="history-table">
        <thead>
            <tr>
                <th>ลำดับ</th>
                <th>ชื่อเจ้าของที่นา</th>
                <th>ขนาดพื้นที่นาที่วัดได้จริง</th>
                <th>ขนาดพื้นที่ (ตร.ม.)</th>
            </tr>
        </thead>
        <tbody id="history-rows">
            <tr>
                <td colspan="4" style="text-align:center; color:#9ca3af;">ยังไม่มีประวัติการบันทึกในรอบนี้</td>
            </tr>
        </tbody>
    </table>
</div>

<script>
    var map = L.map('map').setView([{default_lat}, {default_lng}], 16);

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
            console.log("GPS กำลังค้นหา");
        }}, {{enableHighAccuracy: true}});
    }}

    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var customPoints = [];
    var customPolygon = null;
    var crosshairMode = false;
    
    // ตัวแปรเก็บค่าผลลัพธ์ล่าสุดเพื่อเอาไปบันทึกลงตารางจริง
    var currentCalculatedText = "";
    var currentCalculatedSqM = 0;
    var historyData = [];

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
            alert("⚠️ ต้องปักหมุดที่นาให้ได้อย่างน้อย 3 มุมแปลงขึ้นไปก่อนครับ!");
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
        currentCalculatedText = "";
        currentCalculatedSqM = 0;
        document.getElementById('area-text').innerHTML = "ยังไม่ได้ลากแปลงนา";
    }}

    function showAreaResult(areaSqMeters) {{
        if (areaSqMeters > 0) {{
            var totalWa = areaSqMeters / 4;
            var rai = Math.floor(totalWa / 400);
            var remainingWa = totalWa % 400;
            var ngan = Math.floor(remainingWa / 100);
            var wa = Math.round(remainingWa % 100);

            currentCalculatedSqM = Math.round(areaSqMeters);
            currentCalculatedText = rai + " ไร่ " + ngan + " งาน " + wa + " ตารางวา";

            document.getElementById('area-text').innerHTML = 
                "🌾 วัดได้จริง: <span style='color:#00ffcc; text-shadow: 0 0 5px #00ffcc;'>" + rai + " ไร่ </span> " + 
                "<span style='color:#9d4edd; text-shadow: 0 0 5px #9d4edd;'>" + ngan + " งาน </span> " + 
                "<span style='color:#ff3333; text-shadow: 0 0 5px #ff3333;'>" + wa + " ตารางวา</span><br>" +
                "<span style='font-size:14px; color:#9ca3af; font-weight:normal; display:block; margin-top:5px;'>สุทธิประมวลผลดาวเทียม: " + currentCalculatedSqM.toLocaleString() + " ตร.ม.</span>";
        }}
    }}

    // ฟังก์ชันบันทึกข้อมูลและอัปเดตลงตารางประวัติให้เห็นทันที ไม่มีการหลอกตา
    function saveToHistoryTable() {{
        var nameInput = document.getElementById('farmer-name');
        var name = nameInput.value.trim();
        
        if (name === "") {{
            alert("⚠️ กรุณาพิมพ์ชื่อเจ้าของที่นาก่อนกดบันทึกครับเพื่อน!");
            return;
        }}
        if (currentCalculatedSqM === 0 || currentCalculatedText === "") {{
            alert("⚠️ แปลงนายังไม่มีการคำนวณพื้นที่เลย ปักหมุดแล้วกด 'คำนวณพื้นที่นาแปลงนี้' ก่อนบันทึกครับ!");
            return;
        }}

        // บันทึกเข้า Array ของระบบหน้าบ้านจริง
        historyData.push({{
            name: name,
            areaText: currentCalculatedText,
            sqm: currentCalculatedSqM
        }});

        // ล้างช่องกรอกชื่อหลังจากบันทึกแล้ว
        nameInput.value = "";

        // วาดตารางใหม่ทันทีให้เห็นตรงหน้า
        var tbody = document.getElementById('history-rows');
        tbody.innerHTML = "";

        historyData.forEach(function(item, index) {{
            var row = document.createElement('tr');
            row.innerHTML = 
                "<td>" + (index + 1) + "</td>" +
                "<td style='color:#00ffcc; font-weight:bold;'>" + item.name + "</td>" +
                "<td style='color:#ffffff;'>" + item.areaText + "</td>" +
                "<td style='color:#9ca3af;'>" + item.sqm.toLocaleString() + " ตร.ม.</td>";
            tbody.appendChild(row);
        }});
        
        alert("💾 บันทึกประวัติที่ดินของคุณ " + name + " ลงตารางเรียบร้อยแล้ว ดูข้อมูลด้านล่างได้ทันทีครับ!");
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

# ใช้ความสูง 1250px เพื่อให้มีพื้นที่เหลือเฟือสำหรับแสดงตารางประวัติด้านล่างแบบเห็นชัดๆ ไม่ต้องซ้อนกันครับ
st.components.v1.html(map_html_code, height=1250, scrolling=False)
