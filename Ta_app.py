import streamlit as st

# ตั้งค่าหน้าจอแอปให้กว้าง (Wide) เพื่อให้แผนที่ขยายใหญ่ได้เต็มที่
st.set_page_config(page_title="SYNAPSE COMMAND CENTER - AREA PRO", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h1, h2, h3, p, label, span { color: white !important; }
    /* ปรับแต่งปุ่มกดของเป้าเล็งให้เด่นๆ */
    .map-btn {
        background-color: #10b981;
        color: white;
        border: none;
        padding: 10px 16px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 6px;
        cursor: pointer;
        margin-right: 10px;
    }
    .map-btn-danger { background-color: #ef4444; }
    .map-btn-success { background-color: #f59e0b; }
    </style>
""", unsafe_allow_html=True)

st.title("🚜 ระบบวัดที่นาสัจจะ (เวอร์ชันกว้างพิเศษ + เป้าเล็งกึ่งกลางแม่นยำสูง)")
st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว วัดตามความจริง ไม่มีใครโกหกใครได้\"</p>", unsafe_allow_html=True)
st.write("---")

st.subheader("🛰️ แผนที่ดาวเทียมสเกลจริงระบบความแม่นยำสูง")
st.caption("💡 วิธีการใหม่: เปิดระบบเป้าเล็ง เลื่อนแผนที่ให้มุมคันนาอยู่ตรงเป้าแดงกึ่งกลางจอ แล้วกด 'ปักหมุด' จะแม่นยำกว่าการใช้นิ้วจิ้มธรรมดามาก!")

# พิกัดเริ่มต้น
default_lat = 15.9513057
default_lng = 103.5796196

# โค้ด HTML + JavaScript แผนที่ตัวใหม่ ขยายความสูงเป็น 550px และเพิ่มกลไก Crosshair
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
    /* กล่องแผนที่ใหญ่ขึ้น */
    #map {{
        width: 100%;
        height: 550px; 
        border-radius: 12px;
        border: 2px solid #10b981;
        z-index: 1;
    }}
    /* เป้าเล็งกึ่งกลางจอ (Crosshair) */
    .crosshair {{
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin-top: -10px;
        margin-left: -10px;
        z-index: 9999;
        pointer-events: none; /* ยอมให้ทะลุไปกดลากแผนที่ข้างหลังได้ */
        display: none; /* ปิดไว้ก่อน จะเปิดเมื่อผู้ใช้กดปุ่ม */
    }}
    .crosshair::before, .crosshair::after {{
        content: '';
        position: absolute;
        background: #ef4444;
    }}
    .crosshair::before {{ top: 9px; left: 0; width: 20px; height: 2px; }} /* เส้นแนวนอน */
    .crosshair::after {{ top: 0; left: 9px; width: 2px; height: 20px; }} /* เส้นแนวตั้ง */
    
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
    <button type="button" class="map-btn map-btn-success" style="background:#60a5fa;" onclick="calculateFromPoints()">💾 คำนวณพื้นที่จริง</button>
    <button type="button" class="map-btn map-btn-danger" onclick="clearAllDrawings()">🗑️ ล้างค่าเริ่มใหม่</button>
</div>

<div id="result-box" style="background:#1f2937; padding:15px; border-radius:8px; color:white; font-family:sans-serif;">
    <b style="color:#34d399; font-size:16px;"> 📐 หลักฐานขนาดพื้นที่นา (ตามจริง):</b>
    <p id="area-text" style="font-size:24px; margin:5px 0; font-weight:bold; color:#f59e0b;">ยังไม่ได้ลากแปลงนา</p>
</div>

<script>
    var map = L.map('map').setView([{default_lat}, {default_lng}], 15);

    // ดึงดาวเทียมความละเอียดสูงเห็นคันนาชัดๆ
    var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        maxZoom: 19
    }}).addTo(map);

    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);

    // เช็ค GPS รถไถด่วนๆ
    if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(function(position) {{
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            map.setView([lat, lng], 18); // ซูมใกล้สุดๆ ให้เห็นคันนาชัดขึ้น
            L.marker([lat, lng]).addTo(map).bindPopup('🚜 คุณอยู่ตรงนี้').openPopup();
        }}, function(err) {{
            console.log("GPS โหลดช้า");
        }}, {{enableHighAccuracy: true}});
    }}

    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // เก็บพิกัดชั่วคราวเวลาใช้ระบบเป้าเล็ง
    var customPoints = [];
    var customPolygon = null;
    var crosshairMode = false;

    // เปิด-ปิด เป้าเล็งกลางจอ
    function toggleCrosshair() {{
        var ch = document.getElementById('crosshair-target');
        crosshairMode = !crosshairMode;
        if(crosshairMode) {{
            ch.style.display = 'block';
        }} else {{
            ch.style.display = 'none';
        }}
    }}

    // ระบบปักหมุดจากกึ่งกลางจอ
    function addPointFromCenter() {{
        var center = map.getCenter();
        customPoints.push([center.lat, center.lng]);

        // สร้างจุดกลมแดงเล็กๆ ไว้เป็นหลักฐานว่าปักตรงไหนไปแล้วบ้าง
        L.circleMarker(center, {{radius: 5, color: '#ef4444', fillColor: '#ef4444', fillOpacity: 1}}).addTo(drawnItems);

        // วาดเส้นเชื่อมสดๆ ให้เห็นภาพพจน์เลย
        if (customPoints.length > 1) {{
            if (customPolygon) {{ map.removeLayer(customPolygon); }}
            customPolygon = L.polygon(customPoints, {{color: '#10b981', weight: 3, fillOpacity: 0.3}}).addTo(drawnItems);
        }}
    }}

    // กดคำนวณเมื่อปักหมุดครบรอบแปลงแล้ว
    function calculateFromPoints() {{
        if (customPoints.length < 3) {{
            alert("เพื่อน! ต้องปักหมุดอย่างน้อย 3 มุมขึ้นไปถึงจะคำนวณเป็นรูปแปลงนาได้นะ");
            return;
        }}
        
        // เติมจุดแรกเข้าท้ายสุดเพื่อปิดลูปสำหรับ Turf.js
        var turfCoords = [];
        customPoints.forEach(function(pt) {{
            turfCoords.push([pt[1], pt[0]]); // Turf ใช้ [lng, lat]
        }});
        turfCoords.push([customPoints[0][1], customPoints[0][0]]); // ปิดหัวท้าย

        var polygonGeoJSON = turf.polygon([turfCoords]);
        var areaSqMeters = turf.area(polygonGeoJSON);
        
        showAreaResult(areaSqMeters);
    }}

    // ล้างค่าเริ่มใหม่ทั้งหมด
    function clearAllDrawings() {{
        drawnItems.clearLayers();
        customPoints = [];
        customPolygon = null;
        document.getElementById('area-text').innerHTML = "ยังไม่ได้ลากแปลงนา";
    }}

    // แสดงผลตัวเลขระบบไทย
    function showAreaResult(areaSqMeters) {{
        if (areaSqMeters > 0) {{
            var totalWa = areaSqMeters / 4;
            var rai = Math.floor(totalWa / 400);
            var remainingWa = totalWa % 400;
            var ngan = Math.floor(remainingWa / 100);
            var wa = Math.round(remainingWa % 100);

            document.getElementById('area-text').innerHTML = 
                "🌾 พื้นที่นาจริง: <span style='color:#34d399;'>" + rai + " ไร่ </span> " + 
                "<span style='color:#60a5fa;'>" + ngan + " งาน </span> " + 
                "<span style='color:#f59e0b;'>" + wa + " ตารางวา</span><br>" +
                "<span style='font-size:14px; color:#9ca3af; font-weight:normal;'>คำนวณสุทธิ: " + Math.round(areaSqMeters).toLocaleString() + " ตารางเมตร</span>";
        }}
    }}

    // เปิดระบบวาดด้วยนิ้วจิ้มแบบเดิมควบคู่ไปด้วย (เผื่อคนถนัดแบบเก่า)
    var drawControl = new L.Control.Draw({{
        draw: {{
            polygon: {{ allowIntersection: false, shapeOptions: {{ color: '#10b981', weight: 3, fillOpacity: 0.3 }} }},
            rectangle: {{ shapeOptions: {{ color: '#10b981' }} }},
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

# ยิง HTML แผนที่ขึ้นจอ (เพิ่มความสูงกล่องสตรีมลิตเป็น 750 เพื่อรองรับแผงควบคุมและกล่องสรุป)
st.components.v1.html(map_html_code, height=750, scrolling=False)

st.info("📌 หน้าจอปรับเป็นสเกลใหญ่เต็มตาเรียบร้อยแล้วเพื่อน เวลาอยู่หน้างานแค่แพนแผนที่ให้คันนาเข้าเป้าแดงแล้วกดปุ่มปักหมุดได้เลย ทีนี้ใครจะหัวหมอมาโกหกค่าจ้างรถไถไม่ได้แน่นอน!")
