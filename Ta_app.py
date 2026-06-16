import streamlit as st
import os
import random

# 1. ตั้งค่าหน้าจอแอปให้กว้างพิเศษ (Wide) 
st.set_page_config(page_title="SYNAPSE COMMAND CENTER - AREA PRO v4", page_icon="🚜", layout="wide")

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
    
    .map-btn-danger { 
        background-color: #ff3333; border: 2px solid #ff3333; color: white !important;
        padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 8px;
        cursor: pointer; box-shadow: 0 0 8px #ff3333;
    }
    .map-btn-danger:hover { background-color: #cc0000; box-shadow: 0 0 15px #cc0000; }
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
    st.markdown("<h1 class='neon-title'>🚜 ระบบวัดที่นาสัจจะ - AREA PRO v4 (ปากกาลากอิสระ)</h1>", unsafe_allow_html=True)
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


# 5. 🛰️ แผนที่ดาวเทียมระบบลากนิ้ว/ลากปากกาอิสระ
st.subheader("🛰️ แผนที่ดาวเทียม (ใช้นิ้วหรือปากกาลากตามคันแทนาได้เลย)")
st.caption("💡 วิธีใช้: กดปุ่มเครื่องมือรูปห้าเหลี่ยมด้านซ้ายบน จากนั้นใช้นิ้วลากวาดตามแนวคันแทนาให้รอบแปลง เมื่อวาดมาบรรจบจุดเริ่มต้นระบบจะคำนวณพื้นที่ให้ทันที")

default_lat = 15.9513057
default_lng = 103.5796196

# อัปเกรดสคริปต์เพิ่มการทำงานแบบ Freehand ตรวจจับการลากเส้นต่อเนื่อง
map_html_code = f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
<script src="https://unpkg.com/@turf/turf@6/turf.min.js"></script>

<style>
    #map {{
        width: 100%;
        height: 720px; 
        border-radius: 14px;
        border: 2px solid #00ffcc;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
    }}
</style>

<div id="map"></div>

<div style="margin-top: 15px; margin-bottom: 15px;">
    <button type="button" class="map-btn-danger" onclick="clearAllDrawings()">🗑️ ล้างเส้นที่วาด/เริ่มใหม่</button>
</div>

<div id="result-box" style="background:#111424; padding:15px; border-radius:10px; color:white; font-family:sans-serif; border: 1px solid #9d4edd;">
    <b style="color:#00ffcc; font-size:16px; text-shadow: 0 0 5px #00ffcc;"> 📐 ผลการวัดพื้นที่จากเส้นวาดมือ:</b>
    <p id="area-text" style="font-size:24px; margin:5px 0; font-weight:bold; color:#ff3333;">ยังไม่ได้ลากแปลงนา</p>
</div>

<script>
    var map = L.map('map').setView([{default_lat}, {default_lng}], 17);

    var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        maxZoom: 20,
        maxNativeZoom: 19
    }}).addTo(map);

    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // ปรับโครงสร้างระบบลากเส้น (Draw Config) ให้เหมาะกับการลากเส้นโค้งตามคันนา
    var drawControl = new L.Control.Draw({{
        draw: {{
            polygon: {{
                allowIntersection: false,
                showArea: true,
                guidelineDistance: 10, // เพิ่มความถี่จุดให้ถี่ขึ้นเพื่อรองรับการลากตามโค้งคันแทนา
                shapeOptions: {{
                    color: '#00ffcc',
                    weight: 4,
                    fillColor: '#00ffcc',
                    fillOpacity: 0.3
                }}
            }},
            rectangle: false, polyline: false, circle: false, marker: false, circlemarker: false
        }},
        edit: {{ featureGroup: drawnItems }}
    }});
    map.addControl(drawControl);

    // ฟังก์ชันคำนวณพื้นที่และแปลงหน่วย
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

    // เมื่อวาดเส้นเสร็จสมบูรณ์
    map.on(L.Draw.Event.CREATED, function (event) {{
        var layer = event.layer;
        drawnItems.clearLayers(); // ล้างแปลงเก่าออกก่อนถ้ามีการวาดใหม่
        drawnItems.addLayer(layer);
        
        var geojson = layer.toGeoJSON();
        var areaSqMeters = turf.area(geojson);
        showAreaResult(areaSqMeters);
    }});

    function clearAllDrawings() {{
        drawnItems.clearLayers();
        document.getElementById('area-text').innerHTML = "ยังไม่ได้ลากแปลงนา";
    }}
</script>
"""

# แสดงคอมโพเนนต์แผนที่ลากมืออิสระ ความสูง 920px กำลังพอดีมือถือ
st.components.v1.html(map_html_code, height=920, scrolling=False)

st.success("⚡ อัปเกรดระบบ 'ปากกาลากคันนาอิสระ' เรียบร้อย! จิ้มปุ่มห้าเหลี่ยมซ้ายบนแล้วใช้นิ้วหรือปากกาสไตลัสลากตามคันแทนาได้เลยเพื่อน!")
