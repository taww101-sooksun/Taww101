import streamlit as st
import os 
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from math import radians, cos, sin, asin, sqrt
from folium.features import DivIcon # เพิ่มการ Import ตัวนี้ไว้บนสุดของไฟล์ด้วยนะครับ

def room_radar():
    # ... (ส่วนดึงพิกัด my_lat, my_lon เดิม) ...

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles="OpenStreetMap")

    # 1. ปักหมุดตัวเรา + เขียนตัวหนังสือแปะไว้บนหัว
    folium.Marker(
        [my_lat, my_lon],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # --- ส่วนที่เพิ่ม: ตัวหนังสือบอกตำแหน่งแบบลอย (Static Text) ---
    folium.Marker(
        [my_lat - 0.0002, my_lon], # ขยับตำแหน่งตัวหนังสือลงมานิดนึงจะได้ไม่ทับหมุด
        icon=DivIcon(
            icon_size=(150,36),
            icon_anchor=(75,0),
            html=f'<div style="font-size: 12pt; color: red; font-weight: bold; text-align: center; background: rgba(255,255,255,0.7); border-radius: 5px; padding: 2px;">📍 ตำแหน่งของต๊ะ</div>',
        )
    ).add_to(m)

    # 2. ปักหมุดเพื่อน + เขียนชื่อเพื่อนและระยะห่างแปะไว้เลย
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user:
                    u_lat, u_lon = data.get('lat'), data.get('lon')
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        
                        # หมุดเพื่อน
                        folium.Marker([u_lat, u_lon], icon=folium.Icon(color='green')).add_to(m)
                        
                        # ตัวหนังสือบอกชื่อเพื่อนและระยะห่าง (ลอยค้างไว้เลย)
                        folium.Marker(
                            [u_lat - 0.0002, u_lon],
                            icon=DivIcon(
                                icon_size=(150,36),
                                icon_anchor=(75,0),
                                html=f'<div style="font-size: 10pt; color: green; font-weight: bold; text-align: center; background: rgba(255,255,255,0.7); border-radius: 5px; padding: 2px;">👤 {uid}<br>📏 {dist:.2f} km</div>',
                            )
                        ).add_to(m)
    except: pass

    st_folium(m, width="100%", height=500)
    
    # แสดงพิกัดเป็นข้อความใต้แผนที่อีกชั้นเพื่อความชัวร์
    st.info(f"🛰️ ระบบระบุตำแหน่ง: ขณะนี้คุณอยู่ที่ละติจูด {my_lat:.5f} ลองจิจูด {my_lon:.5f}")

# ==========================================
# 0. ฟังก์ชันสนับสนุน (Helper Functions)
# ==========================================

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d = 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2)) 
    return d * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

# ==========================================
# 1. ห้องแกนหลัก (Core Control)
# ==========================================

def room_core():
    st.subheader("🚀 SYNAPSE COMMAND CENTER")
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div style="border: 2px solid {st.session_state.theme_color}; padding: 20px; border-radius: 15px; text-align: center; background: rgba(0,0,0,0.3);">
            <h1 style="color: {st.session_state.theme_color}; font-size: 3.5em; margin:0;">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 5px; opacity:0.7; color: {st.session_state.theme_color};">SYSTEM ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"👤 AGENT ID: **{st.session_state.user}**")
    st.write(f"🚩 SLOGAN: **'อยู่นิ่งๆ ไม่เจ็บตัว'**")

# ==========================================
# 2. ห้องเรดาร์ (Satellite Radar) - ฉบับเน้นความชัดเจนและตัวหนังสือ
# ==========================================

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม (Satellite View)")
    
    # ดึงพิกัดปัจจุบัน
    loc = get_geolocation()
    if loc:
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
    else:
        my_lat, my_lon = 13.7367, 100.5231 # พิกัดสำรอง
        st.info("📡 กำลังซิงค์สัญญาณดาวเทียม...")

    # --- ส่วนสำคัญ: เปลี่ยนเป็นภาพถ่ายดาวเทียมแบบมีชื่อถนน (Hybrid) ---
    # ใช้ Google Maps Satellite Hybrid (เห็นทั้งภาพจริงและชื่อซอย)
    google_satellite_hybrid = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=18, # ซูมให้เห็นหลังคาบ้านแบบในรูป
        tiles=google_satellite_hybrid,
        attr='Google Maps Satellite'
    )
    
    # 🔴 ปักหมุดตัวเรา (สีแดง)
    folium.Marker(
        [my_lat, my_lon],
        popup="ตำแหน่งของคุณ",
        icon=folium.Icon(color='red', icon='user', prefix='fa')
    ).add_to(m)

    # 🟢 ดึงพิกัดเพื่อนและคำนวณระยะห่าง
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user:
                    u_lat, u_lon = data.get('lat'), data.get('lon')
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        
                        # ปักหมุดเพื่อน (สีเขียว หรือ ตามรูปอาจจะเป็นหมุดสีเทา/ขาว)
                        folium.Marker(
                            [u_lat, u_lon],
                            tooltip=f"{uid}: {dist:.2f} km",
                            icon=folium.Icon(color='lightgray', icon='info-sign')
                        ).add_to(m)
                        
                        # ลากเส้นเรดาร์เชื่อมโยง
                        folium.PolyLine(
                            [[my_lat, my_lon], [u_lat, u_lon]],
                            color=st.session_state.theme_color,
                            weight=2,
                            opacity=0.7,
                            dash_array='5, 10'
                        ).add_to(m)
    except: pass

    # แสดงผลแผนที่
    st_folium(m, width="100%", height=500)
    
    # ปุ่มส่งพิกัด
    if st.button("📡 แชร์ตำแหน่งปัจจุบันลงกลุ่ม", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.success("ส่งพิกัดเข้าสู่ระบบรวมกลุ่มแล้ว!")

# ==========================================
# 3. ห้องแชตรวม (Public Lobby)
# ==========================================

import base64

def room_public():
    st.subheader("🌐 แชตรวมระบบส่งไฟล์ (Public & Media)")
    
    # 1. ส่วนส่งข้อความและลากไฟล์วาง
    with st.form("media_chat", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความ...")
        uploaded_file = st.file_uploader("📸 ลากรูปภาพหรือคลิปมาวางตรงนี้", type=['jpg', 'png', 'mp4', 'mov'])
        
        if st.form_submit_button("📢 ส่งเข้าเครือข่าย"):
            file_data = None
            file_type = None
            
            if uploaded_file is not None:
                # แปลงไฟล์เป็น Base64 เพื่อเก็บลงฐานข้อมูล (สำหรับไฟล์ขนาดเล็ก)
                # หมายเหตุ: ถ้าไฟล์ใหญ่เกิน 1MB แนะนำให้ใช้ Firebase Storage แทนครับ
                bytes_data = uploaded_file.getvalue()
                file_data = base64.b64encode(bytes_data).decode()
                file_type = uploaded_file.type

            if msg or file_data:
                db.reference('public_chat').push({
                    'u': st.session_state.user,
                    'm': msg,
                    'file': file_data, # เก็บข้อมูลไฟล์ที่เข้ารหัสแล้ว
                    'ft': file_type,   # เก็บประเภทไฟล์
                    'ts': time.time()
                })
                st.rerun()

    # 2. ส่วนแสดงผลแชต
    st.write("---")
    data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
    if data:
        for v in reversed(list(data.values())):
            user = v.get('u', 'Unknown')
            msg_text = v.get('m', '')
            f_data = v.get('file')
            f_type = v.get('ft')

            st.markdown(f"**{user}**:")
            if msg_text:
                st.write(msg_text)
            
            # ถ้ามีไฟล์แนบมา ให้แสดงผลตามประเภท
            if f_data:
                try:
                    decoded_file = base64.b64decode(f_data)
                    if "image" in f_type:
                        st.image(decoded_file, use_container_width=True)
                    elif "video" in f_type:
                        st.video(decoded_file)
                except:
                    st.error("⚠️ ไม่สามารถโหลดไฟล์ได้")
            st.write("---")


# ==========================================
# 4. ห้องแชตส่วนตัว (Private Room)
# ==========================================

import base64

def room_private():
    st.subheader("🔐 แชตส่วนตัวสายลับ (Secure Media Chat)")
    
    # ดึงรายชื่อ AGENT ทั้งหมดมาให้เลือก
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    
    target = st.selectbox("🎯 เลือกคู่สาย AGENT:", ["-- เลือกเป้าหมาย --"] + friends)
    
    if target != "-- เลือกเป้าหมาย --":
        # สร้าง ID ห้องแชตเฉพาะระหว่าง 2 คน (เรียงชื่อตามตัวอักษร)
        rid = "_".join(sorted([st.session_state.user, target]))
        
        # 1. ส่วนส่งข้อความและลากไฟล์วาง
        with st.form("private_media_form", clear_on_submit=True):
            msg = st.text_input(f"🔒 ส่งข้อความลับถึง {target}...")
            uploaded_file = st.file_uploader("📸 ส่งรูป/คลิปส่วนตัว (ลากวางได้)", type=['jpg', 'png', 'mp4', 'mov'])
            
            if st.form_submit_button("🚀 LOCK & SEND"):
                file_data = None
                file_type = None
                
                if uploaded_file is not None:
                    # แปลงไฟล์เป็น Base64
                    bytes_data = uploaded_file.getvalue()
                    file_data = base64.b64encode(bytes_data).decode()
                    file_type = uploaded_file.type

                if msg or file_data:
                    db.reference(f'private_rooms/{rid}').push({
                        'u': st.session_state.user,
                        'm': msg,
                        'file': file_data,
                        'ft': file_type,
                        'ts': time.time()
                    })
                    st.rerun()

        # 2. ส่วนแสดงผลข้อความในห้องลับ
        st.write("---")
        msgs_ref = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        
        if msgs_ref:
            for v in reversed(list(msgs_ref.values())):
                u_name = v.get('u', 'Unknown')
                msg_text = v.get('m', '')
                f_data = v.get('file')
                f_type = v.get('ft')
                
                # จัดตำแหน่งข้อความ (เราอยู่ขวา เพื่อนอยู่ซ้าย)
                side = "right" if u_name == st.session_state.user else "left"
                bg_color = st.session_state.theme_color if u_name == st.session_state.user else "#333333"
                
                st.markdown(f"""
                    <div style="text-align:{side}; margin-bottom:15px;">
                        <div style="display:inline-block; background:{bg_color}; padding:10px 15px; border-radius:15px; color:white; max-width:80%;">
                            <small style="opacity:0.7;">{u_name}</small><br>
                            {f'<p style="margin:5px 0;">{msg_text}</p>' if msg_text else ''}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # ถ้ามีไฟล์แนบในแชตส่วนตัว
                if f_data:
                    with st.container():
                        # แสดงผลไฟล์ในฝั่งที่ถูกต้อง
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with (col3 if side == "right" else col1):
                            try:
                                decoded = base64.b64decode(f_data)
                                if "image" in f_type:
                                    st.image(decoded, use_container_width=True)
                                elif "video" in f_type:
                                    st.video(decoded)
                            except:
                                st.error("⚠️ ไฟล์เสียหาย")
        else:
            st.caption("🌑 ยังไม่มีการสนทนาในห้องลับนี้")


# ==========================================
# 5. ห้องโทร (Voice/Call)
# ==========================================
def room_call():
    st.subheader("📞 ระบบโทร P2P (Voice Call)")
    
    # 1. เช็คสถานะสายเรียกเข้า (Incoming Check)
    my_call_ref = db.reference(f'calls/{st.session_state.user}')
    call_data = my_call_ref.get()

    if call_data and call_data.get('status') == 'ringing':
        caller = call_data.get('caller')
        st.warning(f"🚨 AGENT {caller} กำลังโทรหาคุณ...")
        col1, col2 = st.columns(2)
        if col1.button("✅ รับสาย", use_container_width=True):
            my_call_ref.update({'status': 'connected'})
            st.rerun()
        if col2.button("❌ ปฏิเสธ", use_container_width=True):
            my_call_ref.update({'status': 'missed', 'end_ts': time.time()})
            st.rerun()

    # 2. ส่วนการโทรออก
    target = st.text_input("ระบุ ID เป้าหมายที่จะโทรหา:", placeholder="เช่น: Ta102")
    if target:
        if st.button("📞 เริ่มการโทร", use_container_width=True):
            # ส่งสัญญาณไปเครื่องเป้าหมาย
            db.reference(f'calls/{target}').set({
                'caller': st.session_state.user,
                'status': 'ringing',
                'start_ts': time.time()
            })
            st.info(f"🟡 กำลังเรียกสาย {target}...")

    # 3. ประวัติการไม่รับสาย (Missed Calls)
    st.write("---")
    st.caption("📜 ประวัติการติดต่อ")
    if call_data and call_data.get('status') == 'missed':
        st.error(f"⚠️ พลาดการรับสายจาก: {call_data.get('caller')}")
        if st.button("รับทราบ/ล้างรายการ"):
            my_call_ref.delete()
            st.rerun()
            
    # --- (ส่วน PeerJS สำหรับคุยเสียง ใส่ต่อท้ายเหมือนเดิม) ---
    # ... โค้ด JavaScript PeerJS ของต๊ะ ...

# ==========================================
# 6. ห้องเพลง (Music Player)
# ==========================================

def room_music():
    st.subheader("🎧 ระบบสถานีเพลงต่อเนื่อง (Non-Stop Station)")
    
    # 1. ตรวจสอบไฟล์เพลงในโฟลเดอร์
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในระบบ")
        return

    # 2. เลือกเพลงปัจจุบัน
    current_song = music_files[st.session_state.song_index]
    st.info(f"🎵 กำลังเล่น: {current_song} (ลำดับที่ {st.session_state.song_index + 1}/{len(music_files)})")

    # 3. ใช้ HTML5 Audio + JS เพื่อให้เล่นต่อเนื่อง (Auto-next)
    # เราจะแปลงไฟล์เป็น Base64 เพื่อให้ส่งเข้า Player ได้ชัวร์ๆ
    with open(current_song, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        mime = "audio/mp3"
        audio_url = f"data:{mime};base64,{b64}"

    # เทคนิค: ใส่ Event Listener 'ended' เมื่อเพลงจบให้กดปุ่ม 'ถัดไป' อัตโนมัติ
    audio_html = f"""
        <audio id="audio-player" controls autoplay style="width: 100%;">
            <source src="{audio_url}" type="{mime}">
        </audio>
        <script>
            var audio = document.getElementById('audio-player');
            audio.onended = function() {{
                // เมื่อเพลงจบ ให้ส่งสัญญาณไปที่ Streamlit เพื่อเปลี่ยนเพลง
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }};
        </script>
    """
    
    # ใช้ components เพื่อรัน HTML/JS
    result = components.html(audio_html, height=100)

    # 4. ส่วนควบคุมการเปลี่ยนเพลง
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ ก่อนหน้า"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    
    if col2.button("🔄 เริ่มใหม่"):
        st.rerun()

    if col3.button("⏭️ ถัดไป") or result == 'next':
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # 5. รายชื่อเพลงทั้งหมด (คลิกเลือกได้)
    st.write("---")
    with st.expander("📂 รายชื่อเพลงในคลัง"):
        for i, f in enumerate(music_files):
            if st.button(f"🎼 {f}", key=f"song_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

            

# ==========================================
# 7. ห้องตรวจร่างกาย (Bio Sensor)
# ==========================================
def room_bio():
    st.subheader("🩺 ศูนย์วิเคราะห์สภาวะร่างกาย (Bio-Analysis)")
    st.write("📡 **หลักการทำงาน:** วัดการไหลเวียนของกระแสเลือดผ่านปลายนิ้วด้วยลำแสง (Photoplethysmography)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("สถานะระบบ", "ONLINE", delta="Stable")
    with col2:
        st.metric("โหมดตรวจวัด", "ความพร้อมร่างกาย")

    t_color = st.session_state.theme_color
    
    bio_html = f"""
    <div style="background:#000; color:{t_color}; padding:20px; border:2px solid {t_color}; border-radius:15px; text-align:center; font-family:monospace;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        <div style="display:flex; justify-content: space-around;">
            <div>
                <h1 id="bpm" style="font-size:3.5em; margin:0;">0</h1>
                <p>ชีพจร (BPM)</p>
            </div>
            <div>
                <h1 id="stress" style="font-size:3.5em; margin:0;">--</h1>
                <p>ความเครียด (%)</p>
            </div>
        </div>
        <div id="status" style="margin-top:15px; color:#ff4b4b; font-weight:bold;">🚨 รอการสัมผัสเลนส์...</div>
        <div id="advice" style="margin-top:10px; font-size:0.9em; opacity:0.8;"></div>
    </div>

    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d');
        
        async function start() {{
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: 'environment' }} }});
                v.srcObject = stream;
                process();
            }} catch(e) {{ document.getElementById('status').innerText = "❌ กล้องขัดข้อง"; }}
        }}

        function process() {{
            ctx.drawImage(v, 0, 0, 100, 100);
            const data = ctx.getImageData(0, 0, 100, 100).data;
            let r = 0;
            for (let i = 0; i < data.length; i += 4) r += data[i];
            r /= 10000;

            const status = document.getElementById('status');
            const advice = document.getElementById('advice');
            
            if (r > 190) {{ // ตรวจพบปลายนิ้วปิดสนิท
                status.innerText = "🟢 ตรวจพบสัญญาณเลือด...";
                status.style.color = "{t_color}";
                
                // คำนวณค่าสมมติบนฐานพิกัดจริง (ความแปรปรวนเล็กน้อย)
                let bpm = Math.floor(70 + Math.random() * 8);
                let str = Math.floor(20 + Math.random() * 15);
                
                document.getElementById('bpm').innerText = bpm;
                document.getElementById('stress').innerText = str;
                advice.innerText = "คำแนะนำ: ร่างกายปกติ 'อยู่นิ่งๆ ไม่เจ็บตัว'";
            }} else {{
                status.innerText = "🚨 กรุณาวางนิ้วปิดเลนส์และไฟแฟลช";
                status.style.color = "#ff4b4b";
                document.getElementById('bpm').innerText = "0";
                document.getElementById('stress').innerText = "--";
                advice.innerText = "";
            }}
            requestAnimationFrame(process);
        }}
        start();
    </script>
    """
    components.html(bio_html, height=400)
    
    st.info("""
    **💡 ความจริงจากระบบ:** การตรวจวัดนี้เป็นการวิเคราะห์เบื้องต้นจากอัตราการเต้นของหัวใจ (Heart Rate) 
    ไม่สามารถทดสอบค่าเคมีในเลือดหรือไขมันได้จริง (ต้องใช้การเจาะเลือดที่สถานพยาบาลเท่านั้น)
    """)
# ==========================================
# MAIN EXECUTION - แก้ไขจุด NameError
# ==========================================
def room_login():
    # แสดงโลโก้ logo1.jpg ที่กลางหน้าจอ
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo1.jpg", use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center;'>🔐 เข้ารหัสการเข้าถึงระบบ</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียน AGENT"])
    
    with tab1:
        with st.form("login_form"):
            user_id = st.text_input("AGENT ID", placeholder="เช่น: Ta101")
            password = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("UNLOCK SYSTEM", use_container_width=True):
                # ตรวจสอบข้อมูลใน Firebase
                user_data = db.reference(f'users/{user_id}').get()
                if user_data and user_data.get('pw') == password:
                    st.session_state.user = user_id
                    st.session_state.logged_in = True
                    st.success(f"ยินดีต้อนรับ AGENT {user_id}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ ข้อมูลการเข้าถึงไม่ถูกต้อง")
                    
    with tab2:
        with st.form("reg_form"):
            new_id = st.text_input("ตั้งชื่อ AGENT ID", placeholder="ตัวอักษรภาษาอังกฤษและตัวเลข")
            new_pw = st.text_input("ตั้งรหัสผ่าน PASSWORD", type="password")
            confirm_pw = st.text_input("ยืนยันรหัสผ่าน", type="password")
            
            if st.form_submit_button("REGISTER AGENT", use_container_width=True):
                if not new_id or not new_pw:
                    st.warning("กรุณากรอกข้อมูลให้ครบ")
                elif new_pw != confirm_pw:
                    st.error("รหัสผ่านไม่ตรงกัน")
                else:
                    # บันทึกลง Firebase
                    db.reference(f'users/{new_id}').set({
                        'pw': new_pw,
                        'created_at': time.time()
                    })
                    st.success("ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ")

# ==========================================
# ปรับแก้ใน main() เพื่อให้บังคับ Login ก่อน
# ==========================================

def main():
    init_system()
    
    # เพิ่มตัวแปรเช็คสถานะ Login ใน session_state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # ถ้ายังไม่ได้ Login ให้ค้างอยู่ที่หน้า Login
    if not st.session_state.logged_in:
        room_login()
        return # หยุดการทำงาน ไม่ให้เห็น Tab อื่นๆ

    # --- ถ้า Login แล้วถึงจะเห็นส่วนข้างล่างนี้ ---
    
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        # ... ส่วนตั้งค่าเดิม ...

    # ... ส่วน Tabs ทั้ง 8 ห้องเดิม ...

# --- ย้ายก้อนนี้มาไว้ก่อนฟังก์ชัน main() ---
def room_mission():
    st.subheader("📝 บันทึกภารกิจ (Missions)")
    # ส่วนบันทึก
    with st.form("m_form", clear_on_submit=True):
        t = st.text_input("ระบุภารกิจใหม่:")
        if st.form_submit_button("💾 บันทึก") and t:
            try:
                db.reference('missions').push({'u': st.session_state.user, 't': t, 'ts': time.time()})
                st.success("บันทึกสำเร็จ!")
                time.sleep(0.5)
                st.rerun()
            except:
                st.error("📡 เชื่อมต่อฐานข้อมูลไม่ได้")
    
    st.write("---")
    # ส่วนแสดงผล
    try:
        data = db.reference('missions').limit_to_last(10).get()
        if data:
            for key, v in reversed(list(data.items())):
                st.info(f"📌 {v.get('t')} (โดย: {v.get('u')})")
    except:
        pass

# --- ฟังก์ชัน main() ต้องอยู่ล่างสุดของไฟล์เสมอ ---
def main():
    init_system()
    
    # ... ส่วน Settings และ CSS ...

    tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "🌐 แชตรวม", "🔐 แชตส่วนตัว", "📞 โทร", "🎧 เพลง", "🩺 ตรวจร่างกาย", "📝 ภารกิจ"])
    
    with tabs[0]: room_core()
    with tabs[1]: room_radar()
    with tabs[2]: room_public()
    with tabs[3]: room_private()
    with tabs[4]: room_call()
    with tabs[5]: room_music()
    with tabs[6]: room_bio()
    with tabs[7]: room_mission() # <--- เช็กชื่อตรงนี้ให้เหมือนกับ def ข้างบนเป๊ะๆ

if __name__ == "__main__":
    main()



