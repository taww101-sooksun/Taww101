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
            st.error(f"🛰️ Firebase Error: {e}")

# ==========================================
# 1. ห้องแกนหลัก (Core Control)
# ==========================================

def room_core():
    st.subheader("🚀 SYNAPSE COMMAND CENTER")
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div style="border: 2px solid {st.session_state.theme_color}; padding: 20px; border-radius: 15px; text-align: center;">
            <h1 style="color: {st.session_state.theme_color}; font-size: 3.5em; margin:0;">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 5px; opacity:0.7;">SYSTEM ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"👤 AGENT: **{st.session_state.user}**")
    st.write(f"🚩 SLOGAN: **'อยู่นิ่งๆ ไม่เจ็บตัว'**")

# ==========================================
# 2. ห้องเรดาร์ (Satellite Radar)
# ==========================================

def room_radar():
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัด")
    loc = get_geolocation()
    my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7, 100.5)
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="CartoDB dark_matter")
    folium.Marker([my_lat, my_lon], tooltip="YOU", icon=folium.Icon(color='red')).add_to(m)
    
    # ดึงพิกัดเพื่อน
    users = db.reference('users').get()
    if users:
        for uid, data in users.items():
            if uid != st.session_state.user:
                u_lat, u_lon = data.get('lat'), data.get('lon')
                if u_lat:
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    folium.Marker([u_lat, u_lon], tooltip=f"{uid} ({dist:.2f}km)", icon=folium.Icon(color='green')).add_to(m)
    
    st_folium(m, width="100%", height=400)
    if st.button("📡 กระจายสัญญาณพิกัดปัจจุบัน", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("อัปเดตตำแหน่งลงดาวเทียมแล้ว!")

# ==========================================
# 3. ห้องแชตรวม (Public Lobby)
# ==========================================

def room_public():
    st.subheader("🌐 แชตรวม (Public Lobby)")
    with st.form("pub_chat", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความสาธารณะ...")
        if st.form_submit_button("📢 ส่งสัญญาณ") and msg:
            db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
            st.rerun()
    
    data = db.reference('public_chat').order_by_key().limit_to_last(15).get()
    if data:
        for v in reversed(list(data.values())):
            st.write(f"**{v.get('u')}**: {v.get('m')}")

# ==========================================
# 4. ห้องแชตส่วนตัว (Private Room)
# ==========================================

def room_private():
    st.subheader("🔐 แชตส่วนตัว (Private Line)")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    
    target = st.selectbox("เลือกคู่สาย:", ["-- เลือก AGENT --"] + friends)
    if target != "-- เลือก AGENT --":
        rid = "_".join(sorted([st.session_state.user, target]))
        with st.form("priv_chat", clear_on_submit=True):
            msg = st.text_input(f"ข้อความถึง {target}")
            if st.form_submit_button("🔒 ส่งข้อความลับ") and msg:
                db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                st.rerun()
        
        msgs = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(10).get()
        if msgs:
            for v in reversed(list(msgs.values())):
                align = "right" if v['u'] == st.session_state.user else "left"
                color = st.session_state.theme_color if v['u'] == st.session_state.user else "#444"
                st.markdown(f"<div style='text-align:{align};'><span style='background:{color}; padding:8px; border-radius:10px;'>{v['m']}</span></div><br>", unsafe_allow_html=True)

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
            <button id="callBtn" style="padding:10px 20px; background:{st.session_state.theme_color}; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">📞 เริ่มการโทร</button>
            <audio id="remoteAudio" autoplay></audio>
        </div>
        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <script>
            const peer = new Peer('SYNAPSE_{st.session_state.user}');
            document.getElementById('callBtn').onclick = async () => {{
                const stream = await navigator.mediaDevices.getUserMedia({{audio: true}});
                const call = peer.call('SYNAPSE_{target}', stream);
                document.getElementById('status').innerText = "🟡 กำลังเรียก...";
                call.on('stream', (s) => {{ 
                    document.getElementById('remoteAudio').srcObject = s;
                    document.getElementById('status').innerText = "🟢 ในสาย";
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
        components.html(call_html, height=250)

# ==========================================
# 6. ห้องเพลง (Music Player)
# ==========================================

def room_music():
    st.subheader("🎧 ห้องฟังเพลง (Music Player)")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not files:
        st.warning("⚠️ ไม่พบไฟล์ .mp3")
        return
    
    current = files[st.session_state.song_index]
    st.info(f"🎵 กำลังเล่น: {current}")
    st.audio(current)
    
    for i, f in enumerate(files):
        if st.button(f"▶️ {f}", key=f"m_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()

# ==========================================
# 7. ห้องตรวจร่างกาย (Bio Sensor)
# ==========================================

def room_bio():
    st.subheader("🩺 ตรวจร่างกาย (Bio Sensor)")
    # (โค้ด Bio Sensor เดิมของคุณ)
    st.write("ฟีเจอร์นี้เปิดใช้งานกล้องเพื่อวัดชีพจร...")
    # ... ใส่โค้ด components.html ของ Bio Sensor ตรงนี้ ...

# ==========================================
# 8. ห้องภารกิจ (Missions)
# ==========================================

def room_mission():
    st.subheader("📝 บันทึกภารกิจ (Tasks)")
    with st.form("m_form", clear_on_submit=True):
        t = st.text_input("ภารกิจใหม่:")
        if st.form_submit_button("บันทึก") and t:
            db.reference('missions').push({'u': st.session_state.user, 't': t, 'ts': time.time()})
    
    data = db.reference('missions').limit_to_last(10).get()
    if data:
        for v in reversed(list(data.values())):
            st.info(f"📌 {v['t']} (โดย: {v['u']})")

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
        st.caption("SYNAPSE v2.5 PRO")

    # ปรับแต่ง CSS
    st.markdown(f"<style>.stApp {{ background-color: {st.session_state.bg_color}; }}</style>", unsafe_allow_html=True)

    # แยกห้องตามสั่ง
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
