import streamlit as st
import os 
import base64
import time
import math
from datetime import datetime, timedelta, date
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. INITIAL SETUP & SECURITY CHECK
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide", initial_sidebar_state="expanded")

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = None
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    # ตัวแปรคอยจำเวลาการกดอ่านแชตเพื่อเช็กข้อความใหม่
    if 'last_read_global' not in st.session_state: st.session_state.last_read_global = datetime.utcnow().isoformat()
    if 'last_read_private' not in st.session_state: st.session_state.last_read_private = {}

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
    return True

init_system()

# CSS ตกแต่งหน้าจอ
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    div[data-testid="stDecoration"] {{display: none;}}
    
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {{ 
        background-color: {st.session_state.bg_color} !important; 
        color: #FFFFFF !important; 
        font-family: 'Orbitron', sans-serif; 
    }}
    
    .stButton>button {{ 
        border: 2px solid {st.session_state.theme_color} !important; 
        color: #FFFFFF !important; 
        background: linear-gradient(45deg, #FF0055, #0066FF) !important; 
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0 0 10px #0066FF, 0 0 5px #FF0055;
    }}
    
    .neon-box {{ 
        border: 2px solid #0066FF; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        box-shadow: inset 0 0 15px #FF0055, 0 0 15px {st.session_state.theme_color}; 
        background-color: rgba(0,0,0,0.8);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION SYSTEM
# ==========================================
def login_screen():
    st.markdown("<center><h1 style='color:#FF0055; text-shadow: 0 0 10px #FF0055;'>🔒 SYNAPSE GATEWAY</h1></center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="neon-box">', unsafe_allow_html=True)
        user_input = st.text_input("รหัสตัวแทน (AGENT ID)", value="").strip()
        pass_input = st.text_input("รหัสผ่านความปลอดภัย (PASSWORD)", type="password").strip()
        mode = st.radio("ปฏิบัติการ :", ["เข้าสู่ระบบ", "ลงทะเบียนตัวแทนใหม่"], horizontal=True)
        
        if st.button("EXECUTE PROTOCOL", use_container_width=True):
            if not user_input or not pass_input:
                st.warning("❌ กรุณากรอกรหัสข้อมูลให้ครบถ้วน")
            else:
                acc_ref = db.reference(f'users/{user_input}')
                account_data = acc_ref.get()
                
                if mode == "ลงทะเบียนตัวแทนใหม่":
                    if account_data:
                        st.error("❌ มีรหัสตัวแทนนี้อยู่ในระบบสารสนเทศแล้ว")
                    else:
                        acc_ref.set({
                            'password': pass_input, 
                            'created_at': datetime.now().isoformat()
                        })
                        st.success("🛰️ ลงทะเบียนตัวแทนใหม่สำเร็จ เข้าสู่ระบบได้ทันที")
                else:
                    if account_data and account_data.get('password') == pass_input:
                        st.session_state.user = user_input
                        st.session_state.authenticated = True
                        st.success("🔓 อนุมัติสิทธิ์เข้าถึงฐานข้อมูลกลาง!")
                        st.rerun()
                    else:
                        st.error("❌ รหัสตัวแทนหรือรหัสผ่านไม่ถูกต้อง")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. ROOM CORE
# ==========================================
def room_core():
    st.markdown(f"<h2 style='text-align:center; color:#0066FF;'>🚀 CORE COMMAND CENTER</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{st.session_state.theme_color};">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:5px 0 0 0; font-weight:bold;">ACTIVE AGENT: <span style="color:#FF0055;">{st.session_state.user}</span></p>
            <p style="margin:0; color:#CCCCCC; font-style: italic;">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. ROOM RADAR (แก้จุด GPS คลาดเคลื่อน 300 เมตร)
# ==========================================
def room_radar():
    st.markdown("<h2 style='color:#FF0055;'>🛰️ SATELLITE HIGH-ACCURACY GPS</h2>", unsafe_allow_html=True)
    
    loc = get_geolocation()
    col_lat, col_lon = st.columns(2)
    
    if loc and 'coords' in loc:
        default_lat = loc['coords']['latitude']
        default_lon = loc['coords']['longitude']
    else:
        default_lat, default_lon = 13.7367, 100.5231
        st.info("💡 หากพิกัดไม่ตรง ให้เปิดระบบระบุตำแหน่ง (GPS) บนมือถือ หรือพิมพ์กรอกตัวเลขโดยตรงได้เลย")

    with col_lat:
        real_lat = st.number_input("ปรับแต่งพิกัดละติจูด (Latitude) ตรงจุดจริง", value=default_lat, format="%.6f")
    with col_lon:
        real_lon = st.number_input("ปรับแต่งพิกัดลองจิจูด (Longitude) ตรงจุดจริง", value=default_lon, format="%.6f")

    if st.button("📡 ซิงค์ล็อกพิกัดแท้จริงเข้าฐานข้อมูลกลาง", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': real_lat,
            'lon': real_lon,
            'gps_ts': time.time()
        })
        st.success("🎯 ยิงพิกัดความแม่นยำสูงเข้าสู่ระบบกลางเรียบร้อย!")

    m = folium.Map(location=[real_lat, real_lon], zoom_start=17, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([real_lat, real_lon], tooltip="ตำแหน่งแท้จริงของคุณ", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    all_users = db.reference('users').get()
    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user and isinstance(data, dict) and data.get('lat'):
                folium.Marker([data['lat'], data['lon']], tooltip=f"Agent: {uid}", icon=folium.Icon(color='blue')).add_to(m)
                
    st_folium(m, width="100%", height=400, key="radar_map")

# ==========================================
# 5. ROOM COMMS (ระบบแชต + แจ้งเตือนสแกนความจริง)
# ==========================================
def room_comms():
    chat_mode = st.radio("เลือกช่องทางสื่อสาร :", ["💬 แชตรวมกลาง (Global Chat)", "🔒 แชตส่วนตัว (Direct Message)"], horizontal=True)
    
    if chat_mode == "💬 แชตรวมกลาง (Global Chat)":
        st.session_state.last_read_global = datetime.utcnow().isoformat()  # เคลียร์สถานะการอ่านแชตรวม
        st.subheader("ช่องสัญญาณแชตรวม")
        chat_ref = db.reference('global_chat')
        
        # FIXED: ใส่ .order_by_key() เรียงลำดับก่อนดึงข้อมูล ป้องกันแอปพัง
        messages_data = chat_ref.order_by_key().limit_to_last(15).get()
        
        chat_html = "<div style='background:#111; padding:10px; border-radius:10px; height:250px; overflow-y:auto; display:flex; flex-direction:column;'>"
        if messages_data:
            for msg_id, msg in messages_data.items():
                if isinstance(msg, dict):
                    user_name = msg.get('user', 'Unknown')
                    text_content = msg.get('text', '')
                    align = "align-self: flex-end; background:#1b4d3e;" if user_name == st.session_state.user else "align-self: flex-start; background:#222;"
                    chat_html += f"<div style='{align} padding:8px 12px; margin:4px; border-radius:8px; max-width:75%; color:#fff;'><b style='color:#39FF14;'>{user_name}:</b> {text_content}</div>"
        else:
            chat_html += "<center style='color:#444;'>[ ไม่มีข้อความ ]</center>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
        
        with st.form(key="global_chat_form", clear_on_submit=True):
            user_message = st.text_input("พิมพ์ข้อความส่งเข้าแชตรวม...", key="g_msg")
            if st.form_submit_button("ส่งข้อความรวม ⚡", use_container_width=True) and user_message.strip():
                chat_ref.push({
                    'user': st.session_state.user,
                    'text': user_message.strip(),
                    'ts': datetime.utcnow().isoformat()
                })
                st.rerun()

    else:
        st.subheader("ช่องสัญญาณแชตส่วนตัว")
        all_agents = db.reference('users').get()
        if all_agents:
            agent_list = [uid for uid in all_agents.keys() if uid != st.session_state.user]
            if not agent_list:
                st.info("ยังไม่มีตัวแทนคนอื่นออนไลน์ในระบบขณะนี้")
                return
            
            target_agent = st.selectbox("เลือกตัวแทนปลายทางที่ต้องการส่งรหัสลับ", agent_list)
            
            room_id = f"room_{min(st.session_state.user, target_agent)}_{max(st.session_state.user, target_agent)}"
            st.session_state.last_read_private[room_id] = datetime.utcnow().isoformat()  # เคลียร์สถานะการอ่านห้องลับนี้
            
            priv_ref = db.reference(f'private_chats/{room_id}')
            
            # FIXED: ใส่ .order_by_key() แชตส่วนตัวไม่ให้บอร์ดโปรแกรมพัง
            priv_data = priv_ref.order_by_key().limit_to_last(15).get()
            
            chat_html = "<div style='background:#111; padding:10px; border-radius:10px; height:250px; overflow-y:auto; display:flex; flex-direction:column;'>"
            if priv_data:
                for msg_id, msg in priv_data.items():
                    if isinstance(msg, dict):
                        user_name = msg.get('user', 'Unknown')
                        text_content = msg.get('text', '')
                        align = "align-self: flex-end; background:#4a1525;" if user_name == st.session_state.user else "align-self: flex-start; background:#333;"
                        chat_html += f"<div style='{align} padding:8px 12px; margin:4px; border-radius:8px; max-width:75%; color:#fff;'><b style='color:#FF0055;'>{user_name}:</b> {text_content}</div>"
            else:
                chat_html += "<center style='color:#444;'>[ ยังไม่มีการคุยส่วนตัวในห้องนี้ ]</center>"
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)
            
            with st.form(key="private_chat_form", clear_on_submit=True):
                priv_message = st.text_input("พิมพ์รหัสลับส่งส่วนตัว...", key="p_msg")
                if st.form_submit_button("ส่งข้อความลับคู่ขนาน 🔒", use_container_width=True) and priv_message.strip():
                    priv_ref.push({
                        'user': st.session_state.user,
                        'text': priv_message.strip(),
                        'ts': datetime.utcnow().isoformat()
                    })
                    st.rerun()
        else:
            st.warning("ไม่พบรายชื่อตัวแทนในระบบข้อมูล")

    if st.button("🔄 อัปเดตรีเฟรชหน้าต่างสนทนา", use_container_width=True):
        st.rerun()

# ==========================================
# 6. ROOM MUSIC (ระบบคิวเพลง เล่นต่อเนื่องวนลูป)
# ==========================================
def room_music():
    st.markdown("<h2 style='color:#39FF14; text-align:center;'>🎧 CONTINUOUS HOLOGRAPHIC STATION</h2>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not songs:
        st.warning("⚠️ ไม่พบไฟล์ .mp3 ใน Directory หลักของแอปโปรแกรม")
        return
        
    if st.session_state.song_index >= len(songs):
        st.session_state.song_index = 0
        
    current_song = songs[st.session_state.song_index]
    st.success(f"กำลังเปิดเครื่องขยายสัญญาณเพลงคิวที่ {st.session_state.song_index + 1}: {current_song}")
    
    with open(current_song, "rb") as f:
        song_b64 = base64.b64encode(f.read()).decode()
        
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("⏮️ เพลงก่อนหน้า", use_container_width=True):
            st.session_state.song_index = (st.session_state.song_index - 1) % len(songs)
            st.rerun()
    with col_p2:
        if st.button("⏭️ เพลงถัดไป", use_container_width=True):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(songs)
            st.rerun()

    audio_html = f"""
    <div style="background:#000; border:2px solid #39FF14; padding:15px; border-radius:10px; text-align:center;">
        <p style="color:#fff;">AUDIO STREAMING: {current_song}</p>
        <audio id="hologram-player" controls autoplay style="width:100%;">
            <source src="data:audio/mp3;base64,{song_b64}" type="audio/mp3">
        </audio>
    </div>
    """
    components.html(audio_html, height=130)

# ==========================================
# 7. ROOM MATH (แก้แกนปีนักษัตรให้ถูกต้องตรงความจริง)
# ==========================================
def room_math():
    st.markdown("<h2 style='text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        current_date = date(dt.year, dt.month, dt.day)
        ref_date = date(1900, 1, 1)
        diff = (current_date - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = current_date.weekday() + 1
        
        # FIXED: แก้ไขเรียงอาร์เรย์ปีสากลใหม่ทั้งหมดให้แกนโลกตรงจุดจริง พ.ศ. 2569 ต้องได้ ปีมะเมีย
        zodiacs = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
        zodiac = zodiacs[(current_date.year - 4) % 12]
        
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val, "ดิน")

        if pos <= 14.765:
            m_num = int(pos) + 1
            phase = f"ขึ้น {m_num} ค่ำ"
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            p_type = "แรงผลักดันวงเวียนเวกเตอร์ (Vector)"
        else:
            m_num = int(pos - 14.765) + 1
            phase = f"แรม {m_num} ค่ำ"
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            p_type = "สมดุลสัดส่วนทองคำศักดิ์สิทธิ์ (Phi)"
            
        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "type": p_type, "day_num": day_val, "lunar_num": m_num, "diff": diff, "day_name": ["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"][current_date.weekday()]}

    def run_scanner(base_res, start_dt, days_range, direction="future"):
        data_list = []
        start_date = date(start_dt.year, start_dt.month, start_dt.day)
        
        for i in range(1, days_range + 1):
            target_step = start_date + timedelta(days=i) if direction == "future" else start_date - timedelta(days=i)
            inf = decode_truth(target_step)
            gap = abs(base_res - inf['res'])
            
            status = ""
            if gap <= 1.0: status = "💎 เพชร (บรรจบสูงสุด)"
            elif 3.8 <= gap <= 4.2: status = "🌀 ธร (สะท้อนคู่ขนาน)"
            elif gap >= 10.0: status = "⚙️ กงจักร (แยกตัวอิสระ)"
            
            if status:
                data_list.append({
                    "วันที่สแกนพบ": target_step.strftime('%Y-%m-%d'),
                    "รหัสวัน": inf['res'],
                    "ค่า GAP": round(gap, 4),
                    "ระดับสัญญาณ": status,
                    "รายละเอียด": f"วัน{inf['day_name']} {inf['phase']} ปี{inf['zodiac']}"
                })
        return data_list

    st.subheader("1️⃣ ตรวจสอบพิกัดความจริงรายวัน")
    target_date = st.date_input("เลือกวันที่ตรวจสอบพิกัดสารสนเทศ", value=date.today(), min_value=date(1960,1,1), max_value=date(2026,12,31))
    
    if target_date:
        d = decode_truth(target_date)
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:20px; background:rgba(0,0,0,0.3);">
                <small>รหัสพิกัดคลื่นความถี่จักรวาล</small>
                <h1 style="color:{st.session_state.theme_color}; font-size:60px; margin:0;">{d['res']}</h1>
                <p style="color:#888;">{d['type']}</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 **ฐานวัน ({d['day_num']}):** วัน{d['day_name']}")
            st.info(f"🌙 **จันทรคติ ({d['phase']}):** พิกัด {d['lunar_num']}")
        with col2:
            st.success(f"🐎 **ปีนักษัตรประจำวัน:** ปี{d['zodiac']}")
            st.success(f"💎 **ธาตุสนามพลังงาน:** ธาตุ{d['element']}")

        st.divider()
        st.subheader("2️⃣ วิเคราะห์รหัสคู่ขนาน & สัญญาณ GAP")
        c1, c2 = st.columns(2)
        with c1:
            dob1 = st.date_input("👤 AGENT 1 (ตัวตั้งต้นความจริง)", value=date.today(), min_value=date(1960,1,1), key="u1_main")
        with c2:
            dob2 = st.date_input("👤 AGENT 2 (เป้าหมายร่วมสแกน)", value=date.today(), min_value=date(1960,1,1), key="u2_main")

        if dob1 and dob2:
            dat1 = decode_truth(dob1)
            dat2 = decode_truth(dob2)
            g_val = abs(dat1['res'] - dat2['res'])

            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>GAPผลลัพธ์ห่าง: {g_val:.4f}</h1>", unsafe_allow_html=True)
            
            if g_val <= 1.0: st.error("💎 **ระดับความเสถียร: เพชร (Diamond)**")
            elif 3.8 <= g_val <= 4.2: st.warning("🌀 **ระดับความเสถียร: ธร (Tor)**")
            elif g_val >= 10.0: st.success("⚙️ **ระดับความเสถียร: กงจักร (Chakra)**")

            st.divider()
            st.subheader("3️⃣ ตารางแผนที่พิกัดกาลเวลาจุดเปลี่ยน (แปรผันตามหลักดาราศาสตร์จริง)")
            st.write(f"คำนวณฐานรอบวันของรหัสตัวตั้งต้น: **{dat1['res']}**")
            t_back, t_next = st.tabs(["⏪ ตรวจสอบจุดพลังงานในอดีต", "🔮 พยากรณ์คลื่นความถี่ในอนาคต"])
            with t_back:
                past_data = run_scanner(dat1['res'], dob1, 365, "past")
                if past_data: st.dataframe(past_data, use_container_width=True)
                else: st.info("--- ไม่พบสัญญาณแทรกแซงพิเศษในรอบ 365 วันที่ผ่านมา ---")
            with t_next:
                future_data = run_scanner(dat1['res'], dob1, 365, "future")
                if future_data: st.dataframe(future_data, use_container_width=True)
                else: st.info("--- ไม่พบวันบรรจบพลังงานระดับวิกฤตล่วงหน้าใน 365 วันนี้ ---")

# ==========================================
# 8. MAIN ARCHITECTURE (ตัวสแกนแจ้งเตือนอัตโนมัติ)
# ==========================================
def main():
    if not st.session_state.authenticated:
        login_screen()
    else:
        # ฟังก์ชันสแกนหาข้อความแชตเข้าเพื่อแจ้งเตือน
        global_notif = False
        private_notif = False
        
        try:
            # 1. เช็กแจ้งเตือนแชตรวม
            last_msg = db.reference('global_chat').order_by_key().limit_to_last(1).get()
            if last_msg and isinstance(last_msg, dict):
                for k, m in last_msg.items():
                    if m.get('user') != st.session_state.user and m.get('ts', '') > st.session_state.last_read_global:
                        global_notif = True
            
            # 2. เช็กแจ้งเตือนแชตส่วนตัว (สแกนทุกห้องที่มีคุณอยู่)
            all_rooms = db.reference('private_chats').get()
            if all_rooms and isinstance(all_rooms, dict):
                for r_id, msgs in all_rooms.items():
                    if f"room_" in r_id and st.session_state.user in r_id:
                        if isinstance(msgs, dict):
                            # หาข้อความสุดท้ายของห้องนั้น
                            last_p_k = sorted(msgs.keys())[-1]
                            last_p_m = msgs[last_p_k]
                            last_read = st.session_state.last_read_private.get(r_id, "")
                            if last_p_m.get('user') != st.session_state.user and last_p_m.get('ts', '') > last_read:
                                private_notif = True
        except:
            pass # กันระบบหน่วงถ้าเน็ตช้า

        with st.sidebar:
            st.title("⚙️ SYNAPSE DASHBOARD")
            st.markdown(f"**ตัวแทนล็อกอิน:** <span style='color:{st.session_state.theme_color};'>{st.session_state.user}</span>", unsafe_allow_html=True)
            
            # แสดงไฟแจ้งเตือนที่แถบด้านข้าง (Sidebar) ให้เห็นตลอดเวลา
            if global_notif:
                st.markdown("<p style='background:#1b4d3e; color:#39FF14; padding:8px; border-radius:5px; font-size:12px; text-align:center; font-weight:bold;'>🟢 มีข้อความใหม่ในแชตรวมกลาง!</p>", unsafe_allow_html=True)
            if private_notif:
                st.markdown("<p style='background:#4a1525; color:#FF0055; padding:8px; border-radius:5px; font-size:12px; text-align:center; font-weight:bold;'>🚨 🔒 มีข้อความลับส่งถึงคุณ!</p>", unsafe_allow_html=True)
                
            st.session_state.theme_color = st.color_picker("ปรับแต่งหน้าสีธีม (THEME)", st.session_state.theme_color)
            st.session_state.bg_color = st.color_picker("สีพื้นหลังแกนกลาง (BG)", st.session_state.bg_color)
            if st.button("🔴 ออกจากระบบความปลอดภัย", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()

        # แทรกตัวบอกสถานะแจ้งเตือนในป้ายเมนูหลัก
        tab_comm_label = "💬 COMM SYSTEM 🔔" if (global_notif or private_notif) else "💬 COMM SYSTEM"
        
        tabs = st.tabs(["🚀 CORE COMMAND", "🛰️ HIGH-GPS RADAR", tab_comm_label, "🎧 LOOP MUSIC", "📟 QUANTUM MATRIX"])
        rooms = [room_core, room_radar, room_comms, room_music, room_math]
        for i, tab in enumerate(tabs):
            with tab: 
                rooms[i]()

if __name__ == "__main__":
    main()
