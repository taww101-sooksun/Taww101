import streamlit as st
import os
import random

# 1. ตั้งค่าหน้าจอแอปให้กว้างพิเศษ (Wide)
st.set_page_config(page_title="SYNAPSE COMMAND CENTER - AREA PRO v5", page_icon="🚜", layout="wide")

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
    
    .map-btn {
        background-color: #00ffcc; color: #000000; border: 2px solid #00ffcc;
        padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 8px;
        cursor: pointer; margin-right: 10px; margin-bottom: 10px; box-shadow: 0 0 8px #00ffcc;
    }
    .map-btn-danger { background-color: #ff3333; border-color: #ff3333; color: white !important; box-shadow: 0 0 8px #ff3333; }
    .map-btn-success { background-color: #9d4edd; border-color: #9d4edd; color: white !important; box-shadow: 0 0 8px #9d4edd; }
    
    .history-box {
        background: #1a0b2e; border: 1px solid #9d4edd; padding: 15px; 
        border-radius: 10px; margin-top: 15px; color: white;
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
    st.markdown("<h1 class='neon-title'>🚜 ระบบวัดที่นาสัจจะ - AREA PRO v5 (แก้ไขแผนที่)</h1>", unsafe_allow_html=True)
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


# 5. ระบบแผนที่ดาวเทียม (แก้ปัญหาสตริงและล็อคค่าพิกัดตรงตัวเพื่อป้องกันจอดำ)
st.subheader("🛰️ แผนที่ดาวเทียมระบบเป้าเล็งกึ่งกลาง (ความละเอียดสูง)")
st.caption("💡 วิธีใช้งาน: เลื่อนหน้าจอให้มุมแปลงนาอยู่ตรงเป้าแดงพอดี แล้วกดปุ่มปักหมุดสีม่วง")

# แก้ไขสคริปต์หน้าบ้านโดยตรง ป้องกันการพังจากการแปลง String ของ Python
map_html_code = """
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/@turf/turf@6/turf.min.js"></script>

<style>
    #map-container {
        position: relative;
        width: 100%;
    }
    #map {
        width: 100%;
        height: 650px; 
        border-radius: 14px;
        border: 2px solid #00ffcc;
        z-index: 1;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
    }
    .crosshair {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 30px;
        height: 30px;
        margin-top: -15px;
        margin-left: -15px;
        z-index: 9999;
        pointer-events: none;
    }
    .crosshair::before, .crosshair::after {
        content: '';
        position: absolute;
        background: #ff3333;
        box-shadow: 0 0 8px #ff3333;
    }
    .crosshair::before { top: 14px; left: 0; width: 30px; height: 2px; }
    .crosshair::after { top: 0; left: 14px; width: 2px; height: 30px; }
    
    .map-btn {
        background-color: #00ffcc; color: #000000; border: 2px solid #00ffcc;
        padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 8px;
        cursor: pointer; margin-right: 10px; margin-bottom: 10px; box-shadow: 0 0 8px #00ffcc;
    }
    .map-btn-danger { background-color: #ff3333; border-color: #ff3333; color: white; box-shadow: 0 0 8px #ff3333; }
    .map-btn-success { background-color: #9d4edd; border-color: #9d4edd; color: white; box-shadow: 0 0 8px #9d4edd; }
    
    .history-box {
        background: #1a0b2e; border: 1px solid #9d4edd; padding: 15px; 
        border-radius: 10px; margin-top: 15px; color: white; font-family: sans-serif;
    }
    .history-item {
        background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;
        margin-bottom: 8px; border-left: 4px solid #00ffcc; display: flex; justify-content: space-between; align-items: center;
    }
</style>

<div id="map-container">
    <div id="map"></div>
    <div id="crosshair-target" class="crosshair"></div>
</div>

<div style="margin-top: 15px;">
    <button type="button" class="map-btn map-btn-success" onclick="addPointFromCenter()">📌 ปักหมุดตรงเป้าแดง</button>
    <button type="button" class="map-btn map-btn-success" style="background:#2a9d8f; border-color:#2a9d8f;" onclick="calculateFromPoints()">📐 คำนวณพื้นที่จริง</button>
    <button type="button" class="map-btn map-btn-danger" onclick="clearAllDrawings()">🗑️ ล้างค่าเริ่มใหม่</button>
</div>

<div id="result-box" style="background:#111424; padding:15px; border-radius:10px; color:white; font-family:sans-serif; border: 1px solid #9d4edd;">
    <b style="color:#00ffcc; font-size:16px;"> 📐 หลักฐานขนาดพื้นที่นา (ตามจริง):</b>
    <p id="area-text" style="font-size:24px; margin:5px 0; font-weight:bold; color:#ff3333;">ยังไม่ได้ลากแปลงนา</p>
    
    <div style="margin-top:10px;" id="save-panel">
        <input type="text" id="owner-name" placeholder="ระบุชื่อเจ้าของนา เช่น ตาสี ยายมี" style="padding: 10px; border-radius: 5px; border: 1px solid #9d4edd; width: 220px; background: #090d16; color: white;">
        <button type="button" class="map-btn" style="padding: 8px 15px; font-size:14px; margin-left:10px;" onclick="saveCurrentData()">💾 บันทึกข้อมูลแปลงนา</button>
    </div>
</div>

<div class="history-box">
    <h3 style="color:#00ffcc; margin-top:0;">📂 บันทึกประวัติที่นาเก่า (กดเปิดดูซ้ำให้เจ้าของดูได้ตลอด)</h3>
    <div id="history-list">ไม่มีประวัติการบันทึก</div>
</div>

<script>
    // หยอดพิกัดตัวเลขตรงๆ แก้ปัญหาจอดำ และปรับ Zoom เริ่มต้นเป็น 17
    var map = L.map('map').setView([15.9513057, 103.5796196], 17);

    var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 20,
        maxNativeZoom: 19
    }).addTo(map);

    // พยายามดึง GPS หน้างานจริงของมือถือ ถ้าดึงได้ แผนที่จะวาร์ปไปหาผู้ใช้ทันที
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            map.setView([lat, lng], 18);
            L.marker([lat, lng]).addTo(map).bindPopup('🚜 พิกัดปัจจุบันของคุณ').openPopup();
        }, function(err) {
            console.log("GPS โหลดช้า ใช้พิกัดเริ่มต้นแทน");
        }, {enableHighAccuracy: true, timeout: 5000});
    }

    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var customPoints = [];
    var customPolygon = null;
    var lastCalculatedText = "";
    var lastAreaSqMeters = 0;

    window.onload = function() {
        loadHistoryList();
    };

    function addPointFromCenter() {
        var center = map.getCenter();
        customPoints.push([center.lat, center.lng]);

        L.circleMarker(center, {radius: 6, color: '#ff3333', fillColor: '#ff3333', fillOpacity: 1}).addTo(drawnItems);

        if (customPoints.length > 1) {
            if (customPolygon) { map.removeLayer(customPolygon); }
            customPolygon = L.polygon(customPoints, {color: '#00ffcc', weight: 3, fillOpacity: 0.4}).addTo(drawnItems);
        }
    }

    function calculateFromPoints() {
        if (customPoints.length < 3) {
            alert("ต้องปักหมุดอย่างน้อย 3 มุมขึ้นไปครับ!");
            return;
        }
        
        var turfCoords = [];
        customPoints.forEach(function(pt) {
            turfCoords.push([pt[1], pt[0]]);
        });
        turfCoords.push([customPoints[0][1], customPoints[0][0]]);

        var polygonGeoJSON = turf.polygon([turfCoords]);
        var areaSqMeters = turf.area(polygonGeoJSON);
        lastAreaSqMeters = areaSqMeters;
        
        showAreaResult(areaSqMeters);
    }

    function showAreaResult(areaSqMeters) {
        if (areaSqMeters > 0) {
            var totalWa = areaSqMeters / 4;
            var rai = Math.floor(totalWa / 400);
            var remainingWa = totalWa % 400;
            var ngan = Math.floor(remainingWa / 100);
            var wa = Math.round(remainingWa % 100);

            lastCalculatedText = rai + " ไร่ " + ngan + " งาน " + wa + " ตารางวา (" + Math.round(areaSqMeters).toLocaleString() + " ตร.ม.)";

            document.getElementById('area-text').innerHTML = 
                "🌾 พื้นที่นาจริง: <span style='color:#00ffcc;'>" + rai + " ไร่ </span> " + 
                "<span style='color:#9d4edd;'>" + ngan + " งาน </span> " + 
                "<span style='color:#ff3333;'>" + wa + " ตารางวา</span><br>" +
                "<span style='font-size:14px; color:#9ca3af;'>คำนวณสุทธิ: " + Math.round(areaSqMeters).toLocaleString() + " ตารางเมตร</span>";
        }
    }

    function saveCurrentData() {
        var name = document.getElementById('owner-name').value.trim();
        if (!name) {
            alert("กรุณาพิมพ์ชื่อเจ้าของนาก่อนกดบันทึกครับ!");
            return;
        }
        if (customPoints.length === 0 || lastAreaSqMeters === 0) {
            alert("กรุณาปักหมุดและกดคำนวณพื้นที่ก่อนบันทึกครับ!");
            return;
        }

        var historyData = localStorage.getItem('synapse_farm_history');
        var historyArr = historyData ? JSON.parse(historyData) : [];

        var newRecord = {
            id: Date.now(),
            owner: name,
            areaText: lastCalculatedText,
            points: customPoints
        };

        historyArr.push(newRecord);
        localStorage.setItem('synapse_farm_history', JSON.stringify(historyArr));
        
        document.getElementById('owner-name').value = "";
        alert("💾 บันทึกประวัติที่นาของ " + name + " เรียบร้อยแล้ว!");
        loadHistoryList();
    }

    function loadHistoryList() {
        var historyData = localStorage.getItem('synapse_farm_history');
        var container = document.getElementById('history-list');
        
        if (!historyData || JSON.parse(historyData).length === 0) {
            container.innerHTML = "ไม่มีประวัติการบันทึก";
            return;
        }

        var historyArr = JSON.parse(historyData);
        var html = "";
        
        historyArr.forEach(function(item) {
            html += "<div class='history-item'>" +
                    "<div>👤 <b>" + item.owner + "</b> - " + item.areaText + "</div>" +
                    "<div>" +
                        "<button type='button' class='map-btn' style='padding:5px 10px; font-size:12px; margin:0 5px 0 0;' onclick='viewOldRecord(" + JSON.stringify(item.points) + ", \"" + item.areaText + "\")'>👁️ เปิดดูแปลง</button>" +
                        "<button type='button' class='map-btn map-btn-danger' style='padding:5px 10px; font-size:12px; margin:0;' onclick='deleteRecord(" + item.id + ")'>🗑️ ลบ</button>" +
                    "</div>" +
                   "</div>";
        });
        container.innerHTML = html;
    }

    function viewOldRecord(points, areaText) {
        clearAllDrawings();
        customPoints = points;
        
        customPoints.forEach(function(pt) {
            L.circleMarker([pt[0], pt[1]], {radius: 6, color: '#ff3333', fillColor: '#ff3333', fillOpacity: 1}).addTo(drawnItems);
        });

        customPolygon = L.polygon(customPoints, {color: '#00ffcc', weight: 3, fillOpacity: 0.4}).addTo(drawnItems);
        map.panTo(new L.LatLng(customPoints[0][0], customPoints[0][1]));
        document.getElementById('area-text').innerHTML = "📂 กำลังแสดงข้อมูลเก่าของ: " + areaText;
    }

    function deleteRecord(id) {
        if(confirm("ยืนยันที่จะลบประวัตินี้ใช่ไหมเพื่อน?")) {
            var historyData = localStorage.getItem('synapse_farm_history');
            var historyArr = JSON.parse(historyData);
            var filtered = historyArr.filter(function(item) { return item.id !== id; });
            localStorage.setItem('synapse_farm_history', JSON.stringify(filtered));
            loadHistoryList();
        }
    }

    function clearAllDrawings() {
        drawnItems.clearLayers();
        customPoints = [];
        customPolygon = null;
        lastAreaSqMeters = 0;
        document.getElementById('area-text').innerHTML = "ยังไม่ได้ลากแปลงนา";
    }
</script>
"""

st.components.v1.html(map_html_code, height=1050, scrolling=False)
st.success("⚡ แก้ไขปัญหาการเชื่อมต่อพิกัดเรียบร้อย! คราวนี้แผนที่และเป้าเล็งสีแดงจะแสดงผลขึ้นมาอย่างถูกต้องแน่นอนครับเพื่อน!")
