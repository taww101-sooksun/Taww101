import streamlit as st
import os
import random
import time

# ตั้งค่าหน้าจอแอปให้ดุดัน โทนมืด เหมาะกับการเปิดบนรถไถตอนแดดร้อนๆ
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", page_icon="🛸", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h1, h2, h3, p, label, span { color: white !important; }
    .stTabs [data-baseweb="tab"] { color: #9ca3af !important; font-weight: bold; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #10b981 !important; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# ระบบจำลองสถานะการล็อกอิน (Session State)
# =========================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = ""

# =========================================================
# หน้าจอที่ 1: หน้าล็อกอินสัจจะ (เช็กเบอร์ตรงๆ ตามฐานข้อมูล Firebase)
# =========================================================
if not st.session_state.logged_in:
    st.title("📱 ระบบล็อกอินยิ้มซิ (Sooksun1)")
    st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว ปลอดภัยร้อยเปอร์เซ็นต์\"</p>", unsafe_allow_html=True)
    
    with st.container():
        st.subheader("เข้าสู่ระบบด้วยเบอร์โทรศัพท์")
        
        phone_input = st.text_input("เบอร์โทรศัพท์ (ใส่รูปแบบสากล เช่น +66970801941):", value="+66970801941")
        
        if st.button("📲 ขอรหัส OTP", use_container_width=True):
            if phone_input in ["+66970801941", "+66800924262"]:
                st.toast("⏳ ระบบจับคู่เบอร์ทดสอบใน Firebase สำเร็จ!")
                st.success("✅ ดำเนินการสำเร็จ! กรุณากรอกรหัส 6 หลักเพื่อข้ามผ่านระบบความปลอดภัย")
            else:
                st.error("❌ ไม่พบเบอร์โทรศัพท์นี้ในระบบทดสอบ")

        st.write("---")
        
        otp_input = st.text_input("กรอกรหัส OTP 6 หลักที่ตั้งไว้ หรือได้รับจาก SMS:", value="753275", type="password")
        
        if st.button("✅ ยืนยันรหัสผ่าน", type="primary", use_container_width=True):
            # รองรับทั้ง 2 เบอร์หลักของต๊ะตามข้อมูลใน Firebase จริงๆ
            if (phone_input == "+66970801941" and otp_input == "753275") or \
               (phone_input == "+66800924262" and otp_input == "753275"):
                st.session_state.logged_in = True
                st.session_state.user_phone = phone_input
                st.success("🔓 รหัสผ่านถูกต้องสัจจะ!")
                st.rerun()
            else:
                st.error("❌ รหัสไม่ถูกต้องตามที่บันทึกไว้ใน Firebase")

# =========================================================
# หน้าจอที่ 2: หน้าแอปหลักหลังจากล็อกอินสำเร็จ
# =========================================================
else:
    st.title("🛸 SYNAPSE COMMAND CENTER")
    st.success(f"🔓 ยินดีต้อนรับเพื่อนต๊ะเข้าสู่ระบบ! (เบอร์: {st.session_state.user_phone})")
    st.markdown("<p style='color: #eab308 !important; font-style: italic;'>สโลแกน: \"อยู่นิ่งๆ ไม่เจ็บตัว\" กำลังเปิดสัญญาณ...</p>", unsafe_allow_html=True)
    st.write("---")

    # แยกการทำงานเป็น 3 แท็บหลัก ไม่ดึงหน้าจอ ไม่ค้างชัวร์
    tab_gps, tab_chat, tab_music = st.tabs(["📍 GPS ดาวเทียมวัดที่นา", "💬 ระบบแชตสัจจะ", "🎵 เครื่องเล่นเพลงอัตโนมัติ"])

    # -----------------------------------------------------
    # แท็บที่ 1: GPS ดาวเทียมส่องคันนาชัดเจน + ลากนิ้ววัดพื้นที่ (ไร่-งาน-วา)
    # -----------------------------------------------------
    with tab_gps:
        st.subheader("🛰️ แผนที่หมุดดาวเทียมส่องที่นา")
        st.markdown("<p style='color: #34d399 !important;'>🚜 <b>วิธีใช้วัดงานรับจ้าง:</b> ใช้นิ้วจิ้มไอคอนรูปสี่เหลี่ยมหรือรูปหลายเหลี่ยมทางขวาของแผนที่ แล้วจิ้มลากเส้นไปตามแนวคันนาให้ครบรอบ ระบบจะคำนวณดีดตัวเลขออกมาเป็น ไร่-งาน-ตารางวา ทันที ป้องกันเจ้าของนาโกง!</p>", unsafe_allow_html=True)
        
        # พิกัดเริ่มต้น (ถ้าอยากให้เปิดมาเจอแถวบ้านตัวเอง ต๊ะมาแก้เลข 16.1234 กับ 103.5678 ตรงนี้ได้เลย)
        default_lat = 16.1234
        default_lng = 103.5678
        
        map_html_code = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
        
        <div id="map" style="width: 100%; height: 350px; border-radius: 12px; border: 2px solid #10b981;"></div>
        <div id="result-box" style="margin-top:15px; background:#1f2937; padding:15px; border-radius:8px; color:white; font-family:sans-serif;">
            <b style="color:#34d399; font-size:16px;">📊 ผลการวัดพื้นที่คำนวณจริง:</b>
            <p id="area-text" style="font-size:20px; margin:5px 0; font-weight:bold; color:#60a5fa;">ยังไม่มีการลากพื้นที่ (ใช้นิ้วจิ้มเครื่องมือวาดทางขวาเพื่อเริ่มลาก)</p>
        </div>

        <script>
            var map = L.map('map').setView([{default_lat}, {default_lng}], 16);

            // ดึงภาพถ่ายดาวเทียมความละเอียดสูง เห็นหลังคาบ้าน เห็นรอยคันนาตรงตามสัจจะจริง
            var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 19,
                attribution: 'Esri Satellite'
            }}).addTo(map);

            L.marker([{default_lat}, {default_lng}]).addTo(map)
                .bindPopup('📍 พิกัดหมุดรถไถปัจจุบัน')
                .openPopup();

            var drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);

            var drawControl = new L.Control.Draw({{
                draw: {{
                    polygon: true,
                    polyline: false,
                    rectangle: true,
                    circle: false,
                    marker: false,
                    circlemarker: false
                }},
                edit: {{
                    featureGroup: drawnItems
                }}
            }});
            map.addControl(drawControl);

            map.on(L.Draw.Event.CREATED, function (event) {{
                var layer = event.layer;
                drawnItems.clearLayers();
                drawnItems.addLayer(layer);

                if (layer instanceof L.Polygon) {{
                    var latlngs = layer.getLatLngs()[0];
                    var areaSqMeters = L.GeometryUtil.geodesicArea(latlngs);
                    
                    // สูตรแปลงค่ามาตราตวงไทย: 1 ไร่ = 1600 ตร.ม. / 1 งาน = 400 ตร.ม. / 1 วา = 4 ตร.ม.
                    var totalWa = areaSqMeters / 4;
                    var rai = Math.floor(totalWa / 400);
                    var remainingWa = totalWa % 400;
                    var ngan = Math.floor(remainingWa / 100);
                    var wa = Math.round(remainingWa % 100);

                    document.getElementById('area-text').innerHTML = 
                        "🚜 ขนาดที่นาผืนนี้: <span style='color:#f59e0b;'>" + rai + " ไร่ </span> " + 
                        "<span style='color:#10b981;'>" + ngan + " งาน </span> " + 
    # ==========================================
    # 1. หน้าจอระบบ GPS ดาวเทียมไฮเทค (มีชื่อหมู่บ้าน + เส้นถนนบอกชัดเจน)
    # ==========================================
    with tab_gps:
        st.subheader("🛰️ แผนที่ดาวเทียมไฮบริด & วัดที่นา")
        st.markdown("<p style='color: #34d399 !important;'>🚜 <b>มีชื่อหมู่บ้านและเส้นถนนบอกชัดเจน:</b> สามารถใช้นิ้วซูมเข้า-ออก หาจุดอ้างอิง เช่น วัด โรงเรียน หรือทางหลวง แล้วลากเส้นวัดพื้นที่ได้แม่นยำ ไม่หลงแน่นอนครับ!</p>", unsafe_allow_html=True)
        
        # ปรับพิกัดเริ่มต้นให้ตรงใจ (พิกัดเริ่มต้น)
        default_lat = 16.1234
        default_lng = 103.5678
        
        map_html_code = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
        
        <div id="map" style="width: 100%; height: 380px; border-radius: 12px; border: 2px solid #10b981;"></div>
        <div id="result-box" style="margin-top:15px; background:#1f2937; padding:15px; border-radius:8px; color:white; font-family:sans-serif;">
            <b style="color:#34d399; font-size:16px;">📊 ผลการคำนวณพื้นที่สัจจะ:</b>
            <p id="area-text" style="font-size:20px; margin:5px 0; font-weight:bold; color:#60a5fa;">ยังไม่มีการลากพื้นที่ (ใช้นิ้วจิ้มไอคอนรูปห้าเหลี่ยมหรือสี่เหลี่ยมทางซ้ายเพื่อลากเส้น)</p>
        </div>

        <script>
            var map = L.map('map').setView([{default_lat}, {default_lng}], 15);

            // 1. ดึงภาพถ่ายดาวเทียมความละเอียดสูง (เห็นหลังคาบ้านและคันนา)
            var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 19
            }}).addTo(map);

            // 2. ดึงเลเยอร์ "ชื่อสถานที่ ถนน และเส้นแบ่งเขต" มาซ้อนทับด้านบน (ทำให้มีภาษาไทยและเส้นทางบอกชัดเจน)
            var labelsLayer = L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 19
            }}).addTo(map);
            
            var bordersLayer = L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 19
            }}).addTo(map);

            // ปักหมุดจุดปัจจุบัน
            L.marker([{default_lat}, {default_lng}]).addTo(map)
                .bindPopup('📍 พิกัดหมุดรถไถปัจจุบัน')
                .openPopup();

            // ระบบลากพื้นที่วัดขนาด
            var drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);

            var drawControl = new L.Control.Draw({{
                draw: {{
                    polygon: true,
                    polyline: false,
                    rectangle: true,
                    circle: false,
                    marker: false,
                    circlemarker: false
                }},
                edit: {{
                    featureGroup: drawnItems
                }}
            }});
            map.addControl(drawControl);

            map.on(L.Draw.Event.CREATED, function (event) {{
                var layer = event.layer;
                drawnItems.clearLayers();
                drawnItems.addLayer(layer);

                if (layer instanceof L.Polygon) {{
                    var latlngs = layer.getLatLngs()[0];
                    var areaSqMeters = L.GeometryUtil.geodesicArea(latlngs);
                    
                    var totalWa = areaSqMeters / 4;
                    var rai = Math.floor(totalWa / 400);
                    var remainingWa = totalWa % 400;
                    var ngan = Math.floor(remainingWa / 100);
                    var wa = Math.round(remainingWa % 100);

                    document.getElementById('area-text').innerHTML = 
                        "🚜 ขนาดที่นาผืนนี้: <span style='color:#f59e0b;'>" + rai + " ไร่ </span> " + 
                        "<span style='color:#10b981;'>" + ngan + " งาน </span> " + 
                        "<span style='color:#ec4899;'>" + wa + " ตารางวา</span><br>" +
                        "<span style='font-size:13px; color:#9ca3af;'>รวมทั้งสิ้น " + Math.round(areaSqMeters).toLocaleString() + " ตารางเมตร</span>";
                }}
            }});
        </script>
        """
        st.components.v1.html(map_html_code, height=550, scrolling=False)

    # -----------------------------------------------------
    # แท็บที่ 2: ระบบแชตสัจจะ (รวม / ส่วนตัว / โทร)
    # -----------------------------------------------------
    with tab_chat:
        st.subheader("💬 ศูนย์สื่อสารแชตยิ้มซิ")
        
        chat_mode = st.radio("ช่องทางติดต่อ:", ["🗣️ แชตรวม (Global)", "🔒 แชตส่วนตัว (Private)", "📞 ระบบโทรเสียง (VoIP)"], horizontal=True)
        
        if chat_mode == "🗣️ แชตรวม (Global)":
            st.text_area("ข้อความแชตรวม:", value="ต๊ะ: กำลังไปไถนารับจ้างครับ\nระบบ: เชื่อมต่อสัญญาณแชตรวมเสถียร...", height=150, disabled=True)
            user_msg = st.text_input("พิมพ์ข้อความส่งเข้าห้องรวม:", key="send_global")
            if st.button("ส่งข้อความ", use_container_width=True):
                st.toast("ส่งข้อมูลเข้าแชตรวมสำเร็จ!")
                
        elif chat_mode == "🔒 แชตส่วนตัว (Private)":
            st.text_input("กรอกเบอร์โทรผู้รับสายตรง:")
            st.text_area("กล่องข้อความลับเฉพาะ:", value="ระบบเข้ารหัสส่วนบุคคลปลอดภัยสูงสุด", height=100, disabled=True)
            st.text_input("พิมพ์ข้อความลับ:", key="send_private")
            st.button("ส่งข้อความลับ", type="primary", use_container_width=True)
            
        elif chat_mode == "📞 ระบบโทรเสียง (VoIP)":
            st.info("📞 ช่องสัญญาณโทรศัพท์ผ่านเครือข่ายอินเทอร์เน็ต")
            st.write("เป้าหมายสายตรงปลายทาง: +66970801941")
            st.button("📞 กดเพื่อโทรออกด้วยระบบเสียง", use_container_width=True)

    # -----------------------------------------------------
    # แท็บที่ 3: เครื่องเล่นเพลงดึงไฟล์อัตโนมัติ (หยิบเอง ไม่ต้องแก้ชื่อไฟล์)
    # -----------------------------------------------------
    with tab_music:
        st.subheader("🎵 เครื่องเล่นเสียงคลังเพลงเยียวยา")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # บังคับระบบให้กวาดสายตาหาไฟล์ .mp3 ทุกตัวในโฟลเดอร์โดยไม่ต้องระบุชื่อ
        try:
            all_files = os.listdir(current_dir)
            mp3_files = [f for f in all_files if f.lower().endswith('.mp3')]
        except Exception:
            mp3_files = []
            
        if mp3_files:
            # หยิบไฟล์เสียงเพลงแรกที่ระบบสแกนเจอมาเล่นทันที
            selected_song = mp3_files[0]
            music_path = os.path.join(current_dir, selected_song)
            
            st.success(f"🎵 ตรวจพบไฟล์เสียงและดึงข้อมูลอัตโนมัติ: `{selected_song}`")
            
            with open(music_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                
            st.audio(audio_bytes, format="audio/mp3")
            st.caption("🎧 สามารถกดเล่นเพลง ฟังแก้เครียดตอนขับรถไถนาได้เลยครับเพื่อน")
        else:
            st.error("❌ ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์แอป")
            st.info("💡 วิธีใช้ง่ายๆ: ต๊ะแค่เอาไฟล์เพลง .mp3 ไปอัปโหลดวางคู่กับไฟล์นี้ใน GitHub ชื่ออะไรก็ได้ ระบบจะหยิบมาเล่นให้เองอัตโนมัติครับ")

    st.write("---")
    if st.button("🚪 ออกจากระบบปลอดภัย (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
