import streamlit as st

# ตั้งค่าหน้าจอแอปให้ดุดัน โทนมืด สบายตาตอนเปิดกลางแดด
st.set_page_config(page_title="SYNAPSE COMMAND CENTER - AREA PRO", page_icon="🚜", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h1, h2, h3, p, label, span { color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🚜 ระบบวัดที่นาสัจจะ (เวอร์ชันแม่นยำสูงสุด)")
st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว วัดตามความจริง ไม่มีใครโกหกใครได้\"</p>", unsafe_allow_html=True)
st.write("---")

st.subheader("🛰️ แผนที่ดาวเทียมสเกลจริงความละเอียดสูง")
st.caption("คำแนะนำ: ใช้นิ้วจิ้มไอคอนรูป 'ห้าเหลี่ยม' หรือ 'สี่เหลี่ยม' ทางซ้ายมือ แล้วจิ้มลากไปตามขอบคันนาให้รอบ ระบบจะใช้สูตรคำนวณพื้นที่ผิวโลกจริง ไม่คลาดเคลื่อนแน่นอน")

# พิกัดเริ่มต้น (สามารถขยับตาม GPS จริงได้)
default_lat = 15.9513057
default_lng = 103.5796196

# โค้ดแผนที่เวอร์ชันอัปเกรด: ใช้ Turf.js ช่วยคำนวณพื้นที่ระดับสากล + ดึงดาวเทียม Esri World Imagery ที่เห็นคันนาชัดที่สุด
map_html_code = f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
<script src="https://unpkg.com/@turf/turf@6/turf.min.js"></script>

<div id="map" style="width: 100%; height: 400px; border-radius: 12px; border: 2px solid #10b981;"></div>
<div id="result-box" style="margin-top:15px; background:#1f2937; padding:15px; border-radius:8px; color:white; font-family:sans-serif;">
    <b style="color:#34d399; font-size:16px;"> 📐 หลักฐานขนาดพื้นที่นา (ตามจริง):</b>
    <p id="area-text" style="font-size:22px; margin:5px 0; font-weight:bold; color:#f59e0b;">ยังไม่ได้ลากแปลงนา</p>
</div>

<script>
    // ตั้งค่าแผนที่เริ่มต้น
    var map = L.map('map').setView([{default_lat}, {default_lng}], 15);

    // ใช้ภาพถ่ายดาวเทียมความละเอียดสูง ซูมเห็นดิน เห็นร่องคันนาชัดเจน
    var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        maxZoom: 19
    }}).addTo(map);

    // ซ้อนเส้นถนนและชื่อหมู่บ้านภาษาไทยเพื่อให้หาพิกัดง่าย ไม่หลงทิศ
    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);

    // ดึง GPS จริงของมือถือคนขับรถไถทันทีที่เปิดแอป
    if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(function(position) {{
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            map.setView([lat, lng], 17); // ซูมเข้าไปใกล้ๆ ที่นาที่อยู่ปัจจุบัน
            L.marker([lat, lng]).addTo(map).bindPopup('🚜 คุณอยู่ตรงนี้').openPopup();
        }}, function(err) {{
            console.log("GPS โหลดช้า หรือไม่ได้เปิดสิทธิ์");
        }}, {{enableHighAccuracy: true}});
    }}

    // ระบบวาดเส้นขอบแปลงนา
    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var drawControl = new L.Control.Draw({{
        draw: {{
            polygon: {{
                allowIntersection: false, // ห้ามลากเส้นตัดกันเอง (กันการมั่วพิกัด)
                shapeOptions: {{ color: '#10b981', weight: 3, fillOpacity: 0.3 }}
            }},
            rectangle: {{ shapeOptions: {{ color: '#10b981' }} }},
            polyline: false, circle: false, marker: false, circlemarker: false
        }},
        edit: {{ featureGroup: drawnItems }}
    }});
    map.addControl(drawControl);

    // เมื่อลากเส้นแปลงนาเสร็จสิ้น
    map.on(L.Draw.Event.CREATED, function (event) {{
        var layer = event.layer;
        drawnItems.clearLayers(); // ล้างแปลงเก่าออก เพื่อไม่ให้พื้นที่ทับซ้อนกัน
        drawnItems.addLayer(layer);

        // ดึงพิกัดที่ลากไปคำนวณด้วย Turf.js (มาตรฐานสากล)
        var geojson = layer.toGeoJSON();
        var areaSqMeters = turf.area(geojson); // คำนวณตารางเมตรแบบอิงผิวโลกโค้งจริง

        if (areaSqMeters > 0) {{
            // แปลงค่าเป็นระบบหน่วยวัดไทย (ไร่ - งาน - ตารางวา)
            var totalWa = areaSqMeters / 4;
            var rai = Math.floor(totalWa / 400);
            var remainingWa = totalWa % 400;
            var ngan = Math.floor(remainingWa / 100);
            var wa = Math.round(remainingWa % 100);

            // แสดงผลลัพธ์แบบชัดๆ ลบข้อกังขา
            document.getElementById('area-text').innerHTML = 
                "🌾 พื้นที่นาจริง: <span style='color:#34d399;'>" + rai + " ไร่ </span> " + 
                "<span style='color:#60a5fa;'>" + ngan + " งาน </span> " + 
                "<span style='color:#f59e0b;'>" + wa + " ตารางวา</span><br>" +
                "<span style='font-size:14px; color:#9ca3af; font-weight:normal;'>คำนวณสุทธิ: " + Math.round(areaSqMeters).toLocaleString() + " ตารางเมตร</span>";
        }}
    }});
</script>
"""

st.components.v1.html(map_html_code, height=580, scrolling=False)

st.info("💡 ข้อแนะนำเวลาไปคุยหน้างาน: พอนายลากพื้นที่เสร็จแล้ว ได้ตัวเลขไร่-งานที่เป๊ะแล้ว ให้เปิดหน้าจอนี้ให้เจ้าของนาดูตรงนั้นเลย พูดกันด้วยหลักฐานทางดาวเทียม ใครจะมาหัวหมอบอกนาตัวเองมีน้อยกว่าความจริงก็เถียงไม่ได้แน่นอนเพื่อน!")
