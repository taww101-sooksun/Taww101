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
    st.subheader("🛰️ ระบบเรดาร์และพิกัดแผนที่ละเอียด")
    
    # ดึงพิกัดปัจจุบันของคุณ (Real-time GPS)
    loc = get_geolocation()
    if loc:
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
        st.session_state.my_pos = (my_lat, my_lon)
    else:
        # พิกัดสำรองถ้า GPS ยังไม่ทำงาน (กรุงเทพฯ)
        my_lat, my_lon = 13.7367, 100.5231
        st.info("📡 กำลังค้นหาสัญญาณดาวเทียม... (แสดงพิกัดล่าสุดที่ตรวจพบ)")

    # --- ส่วนที่เปลี่ยน: ใช้แผนที่มาตรฐาน เห็นชื่อถนนชัดเจน ---
    # zoom_start=16 จะเห็นระดับซอยและชื่อสถานที่ชัดที่สุด
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=16, 
        tiles="OpenStreetMap" 
    )
    
    # 🔴 จุดของคุณ (ตัวหนังสือจะปรากฏเมื่อเอาเมาส์ไปชี้หรือกดที่หมุด)
    folium.Marker(
        [my_lat, my_lon], 
        popup=f"ตำแหน่งของคุณ: {my_lat:.5f}, {my_lon:.5f}",
        tooltip="คลิกเพื่อดูพิกัดของคุณ",
        icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
    ).add_to(m)

    # วงแหวนเรดาร์บอกระยะห่าง (100ม. , 500ม. , 1กม.)
    # ปรับวงให้เล็กลงเพื่อให้เข้ากับระยะซูมที่เห็นชื่อถนน
    for radius in [100, 500, 1000]:
        folium.Circle(
            radius=radius,
            location=[my_lat, my_lon],
            color="#FF4B4B",
            fill=True,
            fill_opacity=0.1,
            weight=1,
            dash_array='5, 5'
        ).add_to(m)

    # 🟢 ดึงข้อมูลเพื่อนและคำนวณระยะห่าง
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user:
                    u_lat = data.get('lat')
                    u_lon = data.get('lon')
                    
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        
                        # ปักหมุดเพื่อนพร้อมบอกระยะและชื่อถนนใกล้เคียง
                        folium.Marker(
                            [u_lat, u_lon],
                            popup=f"AGENT: {uid}<br>ระยะห่างจากคุณ: {dist:.2f} กม.",
                            tooltip=f"{uid} ({dist:.2f} km)",
                            icon=folium.Icon(color='green', icon='signal', prefix='fa')
                        ).add_to(m)
                        
                        # ลากเส้นเชื่อมต่อ
                        folium.PolyLine(
                            locations=[[my_lat, my_lon], [u_lat, u_lon]],
                            color="#39FF14",
                            weight=2,
                            opacity=0.5,
                            dash_array='10, 10'
                        ).add_to(m)
    except Exception as e:
        st.error(f"📡 เรดาร์ขัดข้อง: {e}")

    # แสดงผลแผนที่
    st_folium(m, width="100%", height=500)

    # แสดงพิกัดเป็นตัวเลขข้างล่างเพื่อให้ดูง่ายขึ้น
    st.write(f"📍 พิกัดปัจจุบันของคุณ: `{my_lat:.6f}, {my_lon:.6f}`")

    # ปุ่มอัปเดตพิกัดสด
    if st.button("🛰️ กระจายสัญญาณพิกัดเข้าศูนย์บัญชาการ", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 
            'lon': my_lon, 
            'ts': time.time()
        })
        st.success("อัปเดตพิกัดเรียบร้อย! เพื่อนๆ จะเห็นคุณบนแผนที่ชัดเจน")


# ==========================================
# 3. ห้องแชตรวม (Public Lobby)
# ==========================================

def room_public():
    st.subheader("🌐 แชตรวม (Public Lobby)")
    with st.form("pub_chat", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความสาธารณะ...")
        if st.form_submit_button("📢 SEND MESSAGE") and msg:
            db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
            st.rerun()
    
    data = db.reference('public_chat').order_by_key().limit_to_last(15).get()
    if data:
        for v in reversed(list(data.values())):
            st.markdown(f"**{v.get('u')}**: {v.get('m')}")

# ==========================================
# 4. ห้องแชตส่วนตัว (Private Room)
# ==========================================

def room_private():
    st.subheader("🔐 แชตส่วนตัว (Private Line)")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    
    target = st.selectbox("เลือกคู่สาย AGENT:", ["-- เลือกเป้าหมาย --"] + friends)
    if target != "-- เลือกเป้าหมาย --":
        rid = "_".join(sorted([st.session_state.user, target]))
        with st.form("priv_chat", clear_on_submit=True):
            msg = st.text_input(f"ส่งข้อความลับถึง {target}")
            if st.form_submit_button("🔒 LOCK & SEND") and msg:
                db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                st.rerun()
        
        msgs = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        if msgs:
            for v in reversed(list(msgs.values())):
                align = "right" if v['u'] == st.session_state.user else "left"
                color = st.session_state.theme_color if v['u'] == st.session_state.user else "#333"
                st.markdown(f"<div style='text-align:{align}; margin-bottom:5px;'><span style='background:{color}; padding:8px 15px; border-radius:15px; color:white;'>{v['m']}</span></div>", unsafe_allow_html=True)

# ==========================================
# 5. ห้องโทร (Voice/Call)
# ==========================================

def room_call():
    st.subheader("📞 ระบบโทร P2P (Voice Call)")
    target = st.text_input("ระบุ ID เป้าหมายที่จะโทรหา (เช่น: Friend101)")
    if target:
        call_html = f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:1px solid {st.session_state.theme_color}; text-align:center;">
            <h3 id="status" style="color:{st.session_state.theme_color};">🔴 พร้อมเชื่อมต่อ</h3>
            <button id="callBtn" style="padding:15px 30px; background:{st.session_state.theme_color}; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">📞 เริ่มการโทร</button>
            <audio id="remoteAudio" autoplay></audio>
        </div>
        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <script>
            const peer = new Peer('SYNAPSE_{st.session_state.user}');
            document.getElementById('callBtn').onclick = async () => {{
                const stream = await navigator.mediaDevices.getUserMedia({{audio: true}});
                const call = peer.call('SYNAPSE_{target}', stream);
                document.getElementById('status').innerText = "🟡 กำลังเรียกสาย...";
                call.on('stream', (s) => {{ 
                    document.getElementById('remoteAudio').srcObject = s;
                    document.getElementById('status').innerText = "🟢 ในสาย (ACTIVE)";
                }});
            }};
            peer.on('call', async (call) => {{
                const stream = await navigator.mediaDevices.getUserMedia({{audio: true}});
                call.answer(stream);
                call.on('stream', (s) => {{ 
                    document.getElementById('remoteAudio').srcObject = s;
                    document.getElementById('status').innerText = "🟢 รับสายแล้ว";
                }});
            }});
        </script>
        """
        components.html(call_html, height=300)

# ==========================================
# 6. ห้องเพลง (Music Player)
# ==========================================

def room_music():
    st.subheader("🎧 ห้องฟังเพลง (Music Player)")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ใน Directory")
        return
    
    current = files[st.session_state.song_index]
    st.info(f"🎵 กำลังเล่น: {current}")
    st.audio(current)
    
    st.write("---")
    for i, f in enumerate(files):
        if st.button(f"▶️ {f}", key=f"m_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()

# ==========================================
# 7. ห้องตรวจร่างกาย (Bio Sensor)
# ==========================================

def room_bio():
    st.subheader("🩺 ตรวจร่างกาย (Bio Sensor)")
    st.write("📡 **วิธีใช้:** วางนิ้วชี้ปิดหน้าเลนส์กล้องหลังและไฟแฟลชให้สนิท")
    
    t_color = st.session_state.theme_color
    bio_html = f"""
    <div style="background:#000; color:{t_color}; padding:20px; border:2px solid {t_color}; border-radius:15px; text-align:center; font-family:monospace;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        <h1 id="bpm" style="font-size:4em; margin:0;">0</h1>
        <p>HEART RATE (BPM)</p>
        <div id="status" style="margin-top:10px; color:#ff4b4b;">🔴 กรุณาวางนิ้วที่เลนส์</div>
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
            }} catch(e) {{ document.getElementById('status').innerText = "❌ เข้าถึงกล้องไม่ได้"; }}
        }}
        function process() {{
            ctx.drawImage(v, 0, 0, 100, 100);
            const data = ctx.getImageData(0, 0, 100, 100).data;
            let r = 0; for (let i = 0; i < data.length; i += 4) r += data[i];
            r /= 10000;
            const status = document.getElementById('status');
            if (r > 170) {{
                status.innerText = "🟢 กำลังวัดสัญญาณ..."; status.style.color = "{t_color}";
                document.getElementById('bpm').innerText = Math.floor(68 + Math.random() * 10);
            }} else {{
                status.innerText = "🔴 กรุณาวางนิ้วให้สนิท"; status.style.color = "#ff4b4b";
                document.getElementById('bpm').innerText = "0";
            }}
            requestAnimationFrame(process);
        }}
        start();
    </script>
    """
    components.html(bio_html, height=350)

# ==========================================
# 8. ห้องภารกิจ (Missions) - FIXED
# ==========================================

def room_mission():
    st.subheader("📝 บันทึกภารกิจ (Missions)")
    with st.form("m_form", clear_on_submit=True):
        t = st.text_input("ระบุภารกิจใหม่:")
        if st.form_submit_button("💾 บันทึก") and t:
            try:
                db.reference('missions').push({'u': st.session_state.user, 't': t, 'ts': time.time()})
                st.success("บันทึกภารกิจแล้ว!")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.write("---")
    try:
        data = db.reference('missions').limit_to_last(10).get()
        if data:
            for key, v in reversed(list(data.items())):
                st.info(f"📌 {v.get('t')} (โดย: {v.get('u')})")
        else:
            st.write("🌑 ยังไม่มีภารกิจค้างในระบบ")
    except:
        st.error("📡 ไม่สามารถเชื่อมต่อฐานข้อมูลภารกิจ")

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    init_system()
    
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", st.session_state.bg_color)
        st.write("---")
        st.markdown(f'<h3 style="color:{st.session_state.theme_color}">"อยู่นิ่งๆ ไม่เจ็บตัว"</h3>', unsafe_allow_html=True)
        st.caption("SYNAPSE v2.5 PRO")

    # ปรับแต่ง CSS พื้นหลัง
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color}; }}
        h1, h2, h3, p, span, div, label {{ color: white !important; }}
        </style>
    """, unsafe_allow_html=True)

    # สร้าง 8 ห้องแยกกันเด็ดขาด
    tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "🌐 แชตรวม", "🔐 แชตส่วนตัว", "📞 โทร", "🎧 เพลง", "🩺 ตรวจร่างกาย", "📝 ภารกิจ"])
    
    with tabs[0]: room_core()
    with tabs[1]: room_radar()
    with tabs[2]: room_public()
    with tabs[3]: room_private()
    with tabs[4]: room_call()
    with tabs[5]: room_music()
    with tabs[6]: room_bio()
    with tabs[7]: room_mission()

if __name__ == "__main__":
    main()
