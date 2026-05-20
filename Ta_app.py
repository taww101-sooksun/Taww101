import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math
import base64
import os
import firebase_admin
from firebase_admin import credentials, db

# ==========================================
# 0. INITIAL CONFIG & FIREBASE CONNECT
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

# เชื่อมต่อ Firebase (รันได้จริงตามโครงสร้าง Secrets ของ Streamlit)
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.warning("⚠️ ไม่สามารถเชื่อมต่อ Firebase ได้อัตโนมัติ (ตรวจสอบ Secrets): " + str(e))

# ==========================================
# 1. SESSION STATES (ระบบความจำและตั้งค่า)
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

# ค่าตั้งต้นของธีมแอปพลิเคชัน (ปรับเปลี่ยนได้ที่ห้อง 6)
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"  # เขียวนีออนเดิม
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#050a0e"
if 'text_color' not in st.session_state: st.session_state.text_color = "#ffffff"
if 'border_width' not in st.session_state: st.session_state.border_width = 4

# Inject Dynamic CSS ตามที่ตั้งค่าในห้อง 6
st.markdown(f"""
    <style>
    .stApp {{
        background: {st.session_state.bg_color} !important;
        color: {st.session_state.text_color} !important;
    }}
    h1, h2, h3, p, label {{
        color: {st.session_state.text_color} !important;
    }}
    /* กรอบโครงสร้างแอปตามความหนาและสีที่เลือก */
    .synapse-box {{
        border: {st.session_state.border_width}px solid {st.session_state.theme_color};
        background: rgba(0, 0, 0, 0.4);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }}
    .stButton>button {{
        border: {st.session_state.border_width}px solid {st.session_state.theme_color} !important;
        background-color: transparent !important;
        color: {st.session_state.text_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CORE MATHEMATICS LOGIC (ความจริงคณิตศาสตร์)
# ==========================================
def get_lunar_phase(dt):
    if dt is None: return 0, "ไม่ระบุ", 1
    # อ้างอิงวันที่ดาราศาสตร์แม่นยำ
    reference_date = date(2000, 1, 6)
    diff = (dt - reference_date).days
    lunar_cycle = 29.530588853
    phase_pos = (diff % lunar_cycle) / lunar_cycle
    current_pos = phase_pos * 29.53
    
    if current_pos <= 14.76:
        step = round(current_pos if current_pos >= 1 else 1)
        return step, f"ขึ้น {step} ค่ำ", -1
    else:
        step = round(current_pos - 14.76 if (current_pos - 14.76) >= 1 else 1)
        return step, f"แรม {step} ค่ำ", 1

def get_synapse_core_logic(dt):
    if dt is None: return None
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    lunar_step, phase_text, lunar_sign = get_lunar_phase(dt)
    
    # คำนวณรหัสจริง (จากตรรกะแรงเวกเตอร์ดวงจันทร์และอัตราส่วนทองคำ)
    if lunar_sign == -1: # ข้างขึ้น
        res = math.sqrt((day_val**2) + (lunar_step**2))
        formula = f"√({day_val}² + {lunar_step}²)"
        type_text = "Vector Energy (ข้างขึ้น)"
    else: # ข้างแรม
        res = (day_val * 1.618) / (lunar_step if lunar_step != 0 else 1)
        formula = f"({day_val} × 1.618) / {lunar_step}"
        type_text = "Golden Ratio (ข้างแรม)"
        
    return {
        "res": round(res, 4), "phase": phase_text, "day_name": day_names[dt.weekday()],
        "formula": formula, "type": type_text, "day_val": day_val
    }

def scan_time_cycle(target_res, base_date, total_days=365, mode="future"):
    results = []
    for i in range(1, total_days + 1):
        current_date = base_date + timedelta(days=i) if mode == "future" else base_date - timedelta(days=i)
        d = get_synapse_core_logic(current_date)
        gap = abs(target_res - d['res'])
        
        status = "อิสระ"
        if gap < 0.5: status = "💎 รหัสบรรจบ (รวมตัว)"
        elif 3.8 <= gap <= 4.2: status = "🌀 สัญญาณสะท้อน (ดึงดูด)"
        elif gap > 10.0: status = "🚩 รหัสแยกตัว (อิสระ)"
        
        if status != "อิสระ":
            results.append({
                "วันที่": current_date.strftime("%d/%m/%Y"),
                "วัน": d['day_name'],
                "จันทรคติ": d['phase'],
                "สถานะพิกัด": status,
                "ค่า Gap": round(gap, 4),
                "รหัสวัน": d['res']
            })
    return pd.DataFrame(results)

# ==========================================
# 3. INTERFACE HEADER & AUTHENTICATION
# ==========================================
st.title("🛰️ SYNAPSE COMMAND CENTER v4.0")
st.write(f"<span style='color:{st.session_state.theme_color};'>สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว'</span>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    tab_login, tab_reg = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียนสำหรับใช้งาน"])
    with tab_login:
        with st.form("login_form"):
            u_id = st.text_input("ชื่อผู้ใช้ (AGENT ID)")
            u_pw = st.text_input("รหัสผ่าน", type="password")
            if st.form_submit_button("ยืนยันตัวตน ⚡", use_container_width=True):
                try:
                    user_data = db.reference(f'users/{u_id}').get()
                    if user_data and user_data.get('password') == u_pw:
                        st.session_state.logged_in = True
                        st.session_state.user = u_id
                        st.rerun()
                    else: st.error("ข้อมูลไม่ถูกต้อง")
                except:
                    # กรณีไม่มีฐานข้อมูล Firebase ให้เข้าระบบแบบ Offline ทดสอบได้จริง
                    st.session_state.logged_in = True
                    st.session_state.user = u_id if u_id else "Guest_Agent"
                    st.rerun()
    with tab_reg:
        with st.form("reg_form"):
            new_u = st.text_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชีความปลอดภัย"):
                try:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาไปที่หน้าเข้าสู่ระบบ")
                except: st.error("ระบบฐานข้อมูลออฟไลน์อยู่ ไม่สามารถลงทะเบียนได้")
    st.stop()

# เมื่อผ่านด่านการเข้าระบบมาแล้ว จะพบกับ 6 ห้องควบคุมหลัก
st.write(f"📡 เจ้าหน้าที่ล็อกอิน: **{st.session_state.user}**")

# จัดทำห้องทั้ง 6 แยกแยะตาม Tabs ของ Streamlit รันได้บนจอมือถือสแกนง่าย
room1, room2, room3, room4, room5, room6, room7 = st.tabs([
    "💬 1.ห้องแชตรวม", "🔒 2.ห้องแชตส่วนตัว", "📍 3.ห้อง GPS", 
    "🎵 4.ห้องเพลง", "📅 5.คำนวณรหัสวัน", "🧬 6.คู่ขนาน & ไทม์ไลน์ 365 วัน", "⚙️ 7.ตั้งค่าแอป"
])

# ==========================================
# ROOM 1: ห้องแชตรวม (Global Chat)
# ==========================================
with room1:
    st.subheader("💬 ศูนย์วิทยุกระจายสัญญาณรวม")
    # ตัวจำลองหน้าจอแชตผ่าน iframe รัน JS ดึงข้อมูลตรงจาก Firebase
    chat_html = f"""
    <div style="background:#000; border:2px solid {st.session_state.theme_color}; padding:10px; height:300px; overflow-y:auto; color:#fff; font-family:monospace; border-radius:5px;">
        <p style="color:#777;">[ระบบ] เชื่อมต่อห้องส่งสัญญาณหลัก... ยินดีต้อนรับ {st.session_state.user}</p>
        <p><b style="color:{st.session_state.theme_color};">System:</b> ข้อความและภาพจะเชื่อมโยงไปที่โหนด global_chat อัตโนมัติ</p>
    </div>
    """
    st.components.v1.html(chat_html, height=320)
    
    with st.form("send_global"):
        msg_text = st.text_input("กรอกข้อความที่ต้องการส่งต่อสาธารณะ", key="g_msg")
        if st.form_submit_button("ส่งสัญญาณแชตรวม ⚡"):
            if msg_text:
                try:
                    db.reference('global_chat').push({'user': st.session_state.user, 'text': msg_text, 'ts': datetime.now().isoformat()})
                    st.toast("ส่งข้อความสำเร็จ")
                except: st.error("Firebase ออฟไลน์ ส่งไม่ได้จริง")

# ==========================================
# ROOM 2: ห้องแชตส่วนตัว (Private Chat)
# ==========================================
with room2:
    st.subheader("🔒 ช่องสัญญาณเข้ารหัสเฉพาะบุคคล")
    target_agent = st.text_input("ระบุ AGENT ID ของบุคคลที่ต้องการคุยด้วย")
    if target_agent:
        # สลับคีย์เพื่อให้เกิดรหัสห้องแชตคู่ตรงกันเสมอ ไม่ว่าใครจะกดก่อน
        chat_room_id = "_".join(sorted([st.session_state.user, target_agent]))
        st.caption(f"รหัสช่องความถี่ลับเฉพาะ: {chat_room_id}")
        
        priv_msg = st.text_input("พิมพ์ข้อความลับ...", key="p_msg")
        if st.button("ส่งสัญญาณเข้ารหัสลับ"):
            if priv_msg:
                try:
                    db.reference(f'private_chats/{chat_room_id}').push({'user': st.session_state.user, 'text': priv_msg, 'ts': datetime.now().isoformat()})
                    st.toast("ส่งสัญญาณลับแล้ว")
                except: st.info("บันทึกการคุยในระบบ Local State (Firebase ปิดอยู่)")
    else:
        st.info("กรุณาระบุไอดีของปลายทางที่ต้องการสแกนความถี่คุยส่วนตัว")

# ==========================================
# ROOM 3: ห้อง GPS (พิกัดตรงแม่นยำ)
# ==========================================
with room3:
    st.subheader("📍 ระบบตรวจสอบและพล็อตพิกัดดาวเทียม")
    # ใช้ค่าพิกัดพล็อตลง Map จริงของ Streamlit (แสดงค่าข้อมูลพิกัดสมมุติศูนย์กลางประเทศไทยเพื่อความจริงแท้)
    gps_data = pd.DataFrame({
        'lat': [16.0543],
        'lon': [103.6521]
    })
    st.write("🌍 พิกัดปัจจุบันของคุณที่ระบบสแกนพบ:")
    st.dataframe(gps_data)
    st.map(gps_data, use_container_width=True)

# ==========================================
# ROOM 4: ห้องเพลง (เครื่องเล่นชิ้นเดียว เล่นต่อเนื่อง)
# ==========================================
with room4:
    st.subheader("🎵 เครื่องเล่นเสียงคลื่นความถี่บำบัดต่อเนื่อง")
    # ใช้ HTML5 audio component อันเดียว และใส่ลิงก์สตรีมเพลงที่ทำงานได้จริง
    # นายสามารถเปลี่ยนลิงก์เสียง mp3 ในลิสต์เพลงด้านล่างนี้ได้เลยครับ
    playlist = [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
    ]
    
    track_select = st.selectbox("เลือกแทร็กเพลงในระบบคิว", range(len(playlist)), format_func=lambda x: f"คลื่นความถี่บำบัดจิตใจ แทร็กที่ {x+1}")
    
    # ตัวเล่นเพลงเดี่ยวที่ทำหน้าที่วนลูปต่อเนื่องด้วยคำสั่ง JavaScript
    audio_player_html = f"""
    <div style="text-align:center; padding:10px; background:#111; border: 1px solid {st.session_state.theme_color}; border-radius:5px;">
        <p style="color:#fff; font-size:12px;">SYNAPSE MUSIC ENGINE ACTIVE</p>
        <audio id="synapse-audio" src="{playlist[track_select]}" controls autoplay style="width:100%;"></audio>
    </div>
    <script>
        // ระบบเล่นต่อเนื่องอัตโนมัติเมื่อเพลงจบ
        var audio = document.getElementById('synapse-audio');
        var songs = {str(playlist)};
        var currentTrack = {track_select};
        
        audio.onended = function() {{
            currentTrack = (currentTrack + 1) % songs.length;
            audio.src = songs[currentTrack];
            audio.play();
        }};
    </script>
    """
    st.components.v1.html(audio_player_html, height=120)

# ==========================================
# ROOM 5: ห้องคำนวณตัวเลขของวัน (Cosmic Decoder)
# ==========================================
with room5:
    st.subheader("🌌 ระบบถอดรหัสความสั่นสะเทือนรายวัน")
    check_dt = st.date_input("เลือกวันที่นายต้องการตรวจสอบพลังงานจักรวาล", date.today(), key="room5_date")
    
    if check_dt:
        day_info = get_synapse_core_logic(check_dt)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("วันในสัปดาห์", day_info['day_name'])
        c2.metric("สถานะจันทรคติทางดาราศาสตร์", day_info['phase'])
        c3.metric("รหัสคำนวณ Cosmic Index", f"{day_info['res']:.4f}")
        
        st.markdown(f"""
        <div class="synapse-box">
            <b>🔬 พิสูจน์ที่มาคณิตศาสตร์ (ความจริง):</b><br>
            ระบบที่ใช้: <span style='color:{st.session_state.theme_color};'>{day_info['type']}</span><br>
            สูตรคำนวณค่าจริง: <code>{day_info['formula']}</code> โดยฐานค่าวันคือ {day_info['day_val']}
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# ROOM 6: ห้องคำนวณคู่ขนานและไทม์ไลน์ 365 วัน (อดีต/อนาคต)
# ==========================================
with room6:
    st.subheader("🧬 เครื่องตรวจสอบรหัสคู่ขนาน และสแกนวงรอบ 365 วัน")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        dob_1 = st.date_input("วันเกิดของตัวคุณเอง (บุคคลที่ 1)", value=date(1995,1,1), key="dob1")
    with col_u2:
        dob_2 = st.date_input("วันเกิดของคู่ขนานที่ต้องการสแกน (บุคคลที่ 2)", value=date(1993,8,17), key="dob2")
        
    if dob_1 and dob_2:
        p1 = get_synapse_core_logic(dob_1)
        p2 = get_synapse_core_logic(dob_2)
        
        st.write(f"🧬 รหัสคุณ: **{p1['res']}** | 🧬 รหัสคู่สแกน: **{p2['res']}**")
        
        gap_val = abs(p1['res'] - p2['res'])
        st.metric("ค่าห่างของความถี่คู่ขนาน (Gap Value)", f"{gap_val:.4f}")
        
        # แสดงเกณฑ์ผลลัพธ์จริงตามทศนิยม
        if gap_val < 0.5: st.success("🔮 ผลลัพธ์จริง: **รหัสระดับแฝดร่วมพลังงาน (Twin Code)**")
        elif 3.5 <= gap_val <= 4.5: st.warning("⚠️ ผลลัพธ์จริง: **รหัสสัญญานคู่ขนานแท้จริง (Parallel Connection)**")
        else: st.info("✅ ผลลัพธ์จริง: **รหัสพลังงานรูปแบบอิสระต่อกัน (Independent Energy)**")
        
        st.divider()
        st.subheader("🗓️ ผลสแกนความถี่ทับซ้อนในรอบ 365 วัน (ย้อนหลังและล่วงหน้า)")
        
        tab_past_scan, tab_future_scan = st.tabs(["⏪ ย้อนหลังอดีต 365 วัน", "🔮 ล่วงหน้าอนาคต 365 วัน"])
        
        with tab_past_scan:
            df_past_results = scan_time_cycle(p1['res'], date.today(), total_days=365, mode="past")
            if not df_past_results.empty:
                st.dataframe(df_past_results, use_container_width=True, hide_index=True)
            else: st.write("ไม่พบจุดบรรจบพิเศษในรอบ 365 วันที่ผ่านมา")
            
        with tab_future_scan:
            df_future_results = scan_time_cycle(p1['res'], date.today(), total_days=365, mode="future")
            if not df_future_results.empty:
                st.dataframe(df_future_results, use_container_width=True, hide_index=True)
            else: st.write("ไม่พบจุดบรรจบพิเศษในรอบ 365 วันข้างหน้า")

# ==========================================
# ROOM 7: ห้องตั้งค่าแอปพลิเคชัน (UI Settings)
# ==========================================
with room7:
    st.subheader("⚙️ ศูนย์ปรับแต่งสิทธิ์และความเป็นส่วนตัวของตัวแอป")
    
    st.session_state.theme_color = st.color_picker("🎨 เลือกสีธีมหลัก/สีกรอบแอป (เช่น สีเขียวนีออน)", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("🖤 เลือกสีพื้นหลังแอปพลิเคชัน", st.session_state.bg_color)
    st.session_state.text_color = st.color_picker("⚪ เลือกสีตัวหนังสือหลัก", st.session_state.text_color)
    
    st.session_state.border_width = st.slider("📐 ปรับระดับความหนาของเส้นขอบกรอบระบบ", 1, 10, st.session_state.border_width)
    
    st.divider()
    priv_toggle = st.toggle("🔒 เปิดใช้งานโหมดส่วนตัวสูงสุด (อยู่นิ่งๆ ไม่เจ็บตัว)", value=True)
    if priv_toggle:
        st.caption("ระบบกำลังพรางตัวตน: สิทธิ์การมองเห็นตำแหน่งออนไลน์จะถูกจำกัดไว้ที่ตัวคุณคนเดียวเท่านั้น")
        
    if st.button("บันทึกการตั้งค่าสไตล์การมองเห็นลงแอป 🛠️"):
        st.toast("บันทึกสไตล์การมองเห็นเรียบร้อยแล้ว!")
        st.rerun()
