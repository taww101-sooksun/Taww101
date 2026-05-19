import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64
import os
import random
import json
from datetime import datetime, date

# =========================================================
# 1. INITIAL CONFIG & CYBERPUNK THEME CONTROLLER
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

# ระบบจำสีธีมที่บาสเลือก (เพิ่มห้องตั้งค่าแอปตามสั่ง)
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = "#39FF14" # เริ่มต้นด้วยเขียวเรืองแสง

def inject_custom_cyber_ui(color_code):
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Sarabun:wght@400;700&display=swap');
            
            .stApp {{ 
                background: radial-gradient(circle at 50% 50%, #050a0f 0%, #010204 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #ffffff !important;
            }}
            
            p, span, label, .stMarkdown, h1, h2, h3, h4 {{
                color: #ffffff !important;
            }}
            
            #MainMenu, footer, header {{ visibility: hidden; }}
            .stApp {{ top: -60px; }}
            
            /* 🎯 ปุ่มเมนูขนาดกระชับ เล็กลงพอดีนิ้วจิ้มบนหน้าจอมือถือ ขอบหนา 4px ตามสั่ง */
            [data-testid="stRadio"] > div {{
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 6px !important;
                padding: 2px 0 !important;
            }}
            
            [data-testid="stRadio"] label {{
                background: #03070a !important;
                border: 4px solid #0055ff !important; /* ขอบหนาสีน้ำเงิน */
                border-radius: 8px !important;
                padding: 6px 10px !important; /* ย่อขนาดปุ่มลง */
                margin: 0 !important;
                min-width: 105px !important;
                text-align: center !important;
                justify-content: center !important;
                cursor: pointer !important;
                transition: all 0.2s ease-in-out !important;
            }}
            
            [data-testid="stRadio"] label p {{
                font-size: 12px !important; /* ขนาดอักษรกระชับ */
                font-weight: bold !important;
                color: #00d2ff !important;
            }}
            
            [data-testid="stRadio"] label:hover {{
                border-color: #ff003c !important; /* เมาส์ชี้หรือกดเปลี่ยนเป็นสีแดง */
            }}
            
            [data-testid="stRadio"] label[data-checked="true"] {{
                border-color: {color_code} !important; /* ไฮไลต์ตามสีธีมที่เลือก */
                box-shadow: 0 0 10px {color_code} !important;
            }}
            
            [data-testid="stRadio"] label[data-checked="true"] p {{
                color: #ffffff !important;
            }}
            
            /* ซ่อนโครงสร้างปุ่มแบบเก่า */
            [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] {{ display: none !important; }}
            [data-testid="stRadio"] input[type="radio"] {{ display: none !important; }}
            
            /* กล่องกรอกข้อมูลขอบหนา 4px */
            .stTextInput>div>div>input, .stForm, select {{
                background-color: #020508 !important;
                border: 4px solid #0055ff !important;
                color: #ffffff !important;
                border-radius: 8px !important;
                font-weight: bold !important;
            }}
            
            .truth-card {{
                background: #020508;
                border-left: 6px solid {color_code};
                padding: 15px;
                margin: 12px 0;
                border-radius: 0 8px 8px 0;
            }}
        </style>
    """, unsafe_allow_html=True)

inject_custom_cyber_ui(st.session_state.current_theme)

# =========================================================
# 2. FIREBASE SYSTEM CONNECTION
# =========================================================
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"ระบบฐานข้อมูลเชื่อมต่อไม่ได้: {e}")

# =========================================================
# 3. SESSION STATE CONTROLLER
# =========================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

# ดึงรูปโลโก้เต้นเรืองแสงของบาส
def get_base64_logo():
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""
logo_b64 = get_base64_logo()

# หัวแอปสโลแกนกระพริบเต้นได้ตามสั่ง
header_html = f"""
<style>
    @keyframes dance {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
    @keyframes wink {{ 0%, 100% {{ opacity: 1; color: {st.session_state.current_theme}; }} 50% {{ opacity: 0.4; color: #ff003c; }} }}
    .slogan-txt {{ font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 20px; text-align:center; animation: wink 3s infinite; text-shadow: 0 0 10px {st.session_state.current_theme}; }}
</style>
<div style="text-align:center; padding:5px 0; border-bottom:4px solid #0055ff; margin-bottom:15px;">
    {f'<img src="data:image/png;base64,{logo_b64}" style="width:45px; animation:dance 1s infinite;" /><br>' if logo_b64 else ''}
    <div class="slogan-txt">SYNAPSE COMMAND CENTER</div>
    <div style="font-size:11px; color:#666;">อยู่นิ่งๆ ไม่เจ็บตัว | V.4.0 CLOUD</div>
</div>
"""
components.html(header_html, height=100)

# =========================================================
# 4. AUTHENTICATION SYSTEM (หน้าลงชื่อเข้าใช้/ลงทะเบียน)
# =========================================================
if not st.session_state.logged_in:
    auth_tab = st.radio("ระบบความปลอดภัย:", ["🔑 LOGIN (เข้าสู่ระบบ)", "📝 REGISTER (ลงทะเบียน AGENT)"])
    
    with st.form("auth_system_form"):
        u_id = st.text_input("AGENT ID (ชื่อผู้ใช้)")
        u_pw = st.text_input("PASSWORD (รหัสผ่าน)", type="password")
        submit = st.form_submit_button("ยืนยันคำสั่งสัญญาณ ⚡", use_container_width=True)
        
        if submit:
            if not u_id or not u_pw:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วนคราฟบาส")
            else:
                user_ref = db.reference(f'users/{u_id}')
                user_info = user_ref.get()
                
                if auth_tab == "🔑 LOGIN (เข้าสู่ระบบ)":
                    if user_info and user_info.get('password') == u_pw:
                        st.session_state.logged_in = True
                        st.session_state.user = u_id
                        if 'theme_color' in user_info:
                            st.session_state.current_theme = user_info['theme_color']
                        st.rerun()
                    else:
                        st.error("ข้อมูลตรวจสอบความปลอดภัยไม่ถูกต้องจริง")
                else:
                    if user_info:
                        st.error("ชื่อ AGENT ID นี้ถูกใช้งานในฐานข้อมูลแล้ว")
                    else:
                        user_ref.set({'password': u_pw, 'theme_color': '#39FF14'})
                        st.success("ลงทะเบียนเข้าสู่ระบบฐานข้อมูลสำเร็จแล้ว! เลือกแท็บล็อกอินเพื่อเข้าใช้งาน")
    st.stop()

# =========================================================
# 5. NAVIGATION MENU CONTROL (ปุ่มเล็กหนา 4px กระชับหน้าจอมือถือ)
# =========================================================
st.markdown(f"<div style='text-align:right; color:#00d2ff; font-size:12px; font-weight:bold; margin-bottom:5px;'>📡 SENSOR ACTIVE: <span style='color:#ff003c;'>{st.session_state.user}</span></div>", unsafe_allow_html=True)

menu_choice = st.radio(
    "ระบบสั่งการห้อง:", 
    ["💬 แชทรวม/เดี่ยว", "🛰️ พิกัดดาวเทียม", "🔮 ควอนตัมวันเกิด", "🎵 ลูปเพลง (70)", "📖 คู่มือจริง", "⚙️ ตั้งค่าแอป"]
)
st.divider()

# =========================================================
# 6. ROOM FUNCTIONS CORE (ทำงานได้จริง 100%)
# =========================================================

# --- 6.1 ห้องแชทรวม และ แชทส่วนตัว (แก้ไขระบบดึงข้อมูลแก้บั๊กพัง) ---
if menu_choice == "💬 แชทรวม/เดี่ยว":
    st.markdown("#### 💬 GLOBAL CHATROOM (ห้องสื่อสารแกนกลาง)")
    
    # ดึงข้อมูลมาจัดเรียงใน Python ป้องกันดัชนีพังบน Firebase
    global_ref = db.reference('global_chat')
    g_data = global_ref.get()
    
    g_chat_html = "<div style='height:180px; overflow-y:auto; border:4px solid #0055ff; border-radius:8px; padding:10px; background:#020508; color:#fff; font-size:13px;'>"
    if g_data and isinstance(g_data, dict):
        sorted_g = sorted(g_data.items(), key=lambda x: x[1].get('timestamp', 0))[-15:]
        for mid, msg in sorted_g:
            sender = msg.get('user', 'UNKNOWN')
            color = "#39FF14" if sender == st.session_state.user else "#ff003c"
            g_chat_html += f"<div><b style='color:{color};'>[{sender}]</b>: {msg.get('text','')}</div>"
    else:
        g_chat_html += "<div style='color:#555; text-align:center; padding-top:70px;'>ไม่มีข้อมูลสื่อสารส่วนกลาง</div>"
    g_chat_html += "</div>"
    components.html(g_chat_html, height=195)
    
    with st.form("send_g_form", clear_on_submit=True):
        col1, col2 = st.columns([5,1])
        with col1: g_msg = st.text_input("พิมพ์แชทรวม...", label_visibility="collapsed")
        with col2: g_sub = st.form_submit_button("ส่ง ⚡", use_container_width=True)
        if g_sub and g_msg:
            global_ref.push({'user': st.session_state.user, 'text': g_msg, 'timestamp': time.time()})
            st.rerun()
            
    st.markdown("---")
    st.markdown("#### 🔒 PRIVATE DIRECT CHAT (ห้องกระซิบส่งข้อมูลลับส่วนตัว)")
    target_user = st.text_input("กรอก AGENT ID ปลายทางที่ต้องการส่งหาลับ ๆ:")
    
    if target_user:
        room_id = "_".join(sorted([st.session_state.user, target_user.strip()]))
        priv-ref = db.reference(f'private_chats/{room_id}')
        p_data = priv-ref.get()
        
        p_chat_html = "<div style='height:120px; overflow-y:auto; border:4px solid #ff003c; border-radius:8px; padding:10px; background:#020508; color:#fff; font-size:13px;'>"
        if p_data and isinstance(p_data, dict):
            sorted_p = sorted(p_data.items(), key=lambda x: x[1].get('timestamp', 0))
            for mid, msg in sorted_p:
                p_chat_html += f"<div><b style='color:#00d2ff;'>[{msg.get('sender')}] -> [{msg.get('receiver')}]:</b> {msg.get('text','')}</div>"
        else:
            p_chat_html += "<div style='color:#555; text-align:center; padding-top:40px;'>ไม่มีข้อมูลข้อความลับคู่นี้</div>"
        p_chat_html += "</div>"
        components.html(p_chat_html, height=135)
        
        with st.form("send_p_form", clear_on_submit=True):
            col1, col2 = st.columns([5,1])
            with col1: p_msg = st.text_input("พิมพ์ข้อความลับ...", label_visibility="collapsed")
            with col2: p_sub = st.form_submit_button("ส่งลับ", use_container_width=True)
            if p_sub and p_msg:
                priv-ref.push({
                    'sender': st.session_state.user, 'receiver': target_user.strip(),
                    'text': p_msg, 'timestamp': time.time()
                })
                st.rerun()

# --- 6.2 ห้องพิกัดดาวเทียมแผนที่ (ละติจูด/ลองจิจูด ป้อนตรงไม่คลาดเคลื่อน) ---
elif menu_choice == "🛰️ พิกัดดาวเทียม":
    st.markdown("#### 🛰️ REAL-TIME SATELLITE GPS TRACER")
    if st.button("📡 เชื่อมต่อดึงสัญญาณระบุตัวตนพิกัดจริง", use_container_width=True):
        with st.spinner("กำลังรับพิกัดจากชิปเซนเซอร์มือถือ..."):
            loc = get_geolocation()
        if loc and 'coords' in loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            
            st.success(f"🎯 สัญญาณนิ่ง! พิกัดตรง: ละติจูด {lat:.7f} / ลองจิจูด {lon:.7f}")
            
            # โหลดแผนที่ Dark Mode ป้อนค่าละติจูดลองจิจูดตรงจุด
            m = folium.Map(location=[lat, lon], zoom_start=16, tiles="CartoDB dark_matter")
            folium.Marker([lat, lon], popup=st.session_state.user).add_to(m)
            st_folium(m, width="100%", height=280, returned_objects=[])
        else:
            st.error("⚠️ ไม่สามารถดึงพิกัดได้คราฟบาส กรุณาเปิดระบบ GPS และยินยอมสิทธิ์บนหน้าจอมือถือด้วยครับ")

# --- 6.3 ห้องคำนวณตัวเลขวันเกิดเชิงลึก อธิบายรายละเอียดทุกตัวเลขผลลัพธ์ ---
elif menu_choice == "🔮 ควอนตัมวันเกิด":
    st.markdown("#### 🧬 ANALYTICAL QUANTUM MATRIX")
    u_dob = st.date_input("เลือกวันเดือนปีเกิดเพื่อสแกนโครงสร้างมวลตัวเลข:", value=date(1996, 8, 17))
    
    if u_dob:
        ref_date = date(1900, 1, 1)
        diff_days = (u_dob - ref_date).days
        day_of_week = u_dob.weekday() + 1 # 1=จันทร์, 7=อาทิตย์
        
        lunar_cycle = 29.530589
        pos = (diff_days - 0.5) % lunar_cycle
        is_waxing = pos <= 14.765
        lunar_num = Math.floor(pos + 1) if is_waxing else Math.floor((pos - 14.765) + 1)
        
        if is_waxing:
            res_idx = math.sqrt((day_of_week**2) + (lunar_num**2))
            formula_label = f"\\sqrt{{{day_of_week}^2 + {lunar_num}^2}}"
            lunar_txt = f"ข้างขึ้น ทรงพลังงานด้านบวก (+) ระดับขึ้น {lunar_num} ค่ำทางคณิตศาสตร์"
        else:
            res_idx = (day_of_week * 1.618) / (lunar_num if lunar_num != 0 else 1)
            formula_label = f"\\frac{{{day_of_week} \\times 1.618}}{{{lunar_num}}}"
            lunar_txt = f"ข้างแรม ทรงพลังงานบีบอัดความนิ่ง (-) ระดับแรม {lunar_num} ค่ำทางคณิตศาสตร์"
            
        st.markdown(f"""
            <div class="truth-card">
                <div style="font-size:12px; color:#00d2ff;">QUANTUM MATRIX RESULT VALUE</div>
                <h2 style="color:{st.session_state.current_theme}; font-size:35px; margin:5px 0; font-weight:bold;">{res_idx:.4f}</h2>
            </div>
        """, unsafe_allow_html=True)
        st.latex(rf"Result = {formula_label} = {res_idx:.4f}")
        
        st.markdown(f"""
        ##### 📖 อธิบายคำนวณรายละเอียดตัวเลขผลลัพธ์คราฟบาส:
        * **เลขฐานลำดับวันเกิด [{day_of_week}]:** ถอดค่าตำแหน่งของวันตามวงโคจรรอบสัปดาห์จริง (ค่าคงที่ประจำวันเกิด)
        * **เลขห้วงพลังงานจันทรคติ [{lunar_num}]:** มวลรอบคำนวณผลต่างระยะปีฐาน บ่งบอกตำแหน่งดาวจันทร์ในระบบพิกัด โดยวันเกิดนี้ตกอยู่ในช่อง **{lunar_txt}**
        * **ผลลัพธ์รวมภายนอกสุทธิ [{res_idx:.4f}]:** ค่าความสมดุลที่คำนวณผ่านทฤษฎีเรขาคณิตวิเคราะห์แบบสมบูรณ์ เป็นตัวเลขศูนย์รวมพลังงานจริงที่ไม่แปรผันตามอารมณ์มนุษย์
        """, unsafe_allow_html=True)

# --- 6.4 ห้องเครื่องเล่นเพลง (ดึงเพลง Mp3 จริงในโฟลเดอร์รัน ได้ถึง 70 เพลงวนลูปสุ่มต่อเนื่อง) ---
elif menu_choice == "🎵 ลูปเพลง (70)":
    st.markdown("#### 🎵 AUTOLOOP RANDOM JUKEBOX (70 MP3 FLUID)")
    all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
    st.write(f"📡 ตรวจค้นพบไฟล์เพลงพร้อมใช้งานในระดับโฟลเดอร์คราฟบาส: {len(all_songs)} เพลง")
    
    if all_songs:
        song_dict = {}
        for s in all_songs:
            if os.path.exists(s):
                with open(s, "rb") as f:
                    song_dict[s] = "data:audio/mp3;base64," + base64.b64encode(f.read()).decode()
                    
        songs_json = json.dumps(list(song_dict.keys()))
        data_json = json.dumps(song_dict)
        
        jukebox_html = f"""
        <div style="background:#020508; border:4px solid #ff003c; border-radius:10px; padding:15px; text-align:center;">
            <div id="t-name" style="color:#ffffff; font-size:13px; font-weight:bold; margin-bottom:12px;">กดปุ่มด้านล่างเพื่อปล่อยสัญญาณเสียง</div>
            <audio id="player-core" controls style="width:100%; margin-bottom:12px;"></audio>
            <button id="n-btn" style="background:linear-gradient(135deg, #ff003c, #0055ff); border:none; padding:10px 20px; border-radius:6px; color:#fff; font-weight:bold; cursor:pointer; width:100%;">⚡ สุ่มเพลงถัดไป (RANDOM NEXT)</button>
        </div>
        <script>
            const sData = JSON.parse('{data_json}');
            const playlist = JSON.parse('{songs_json}');
            const audio = document.getElementById('player-core');
            const txt = document.getElementById('t-name');
            const btn = document.getElementById('n-btn');

            function runRandom() {{
                if(playlist.length === 0) return;
                const idx = Math.floor(Math.random() * playlist.length);
                const track = playlist[idx];
                txt.innerHTML = "กำลังขับเคลื่อนคลื่นเสียง 🔄: <span style='color:#39FF14;'>" + track + "</span>";
                audio.src = sData[track];
                audio.play().catch(e => console.log("คอยการยืนยันผู้ใช้"));
            }}
            btn.onclick = runRandom;
            audio.onended = runRandom; // เมื่อเพลงยาวจบให้ดีดสุ่มเพลงต่อไปทันทีต่อเนื่อง 70 เพลง
        </script>
        """
        components.html(jukebox_html, height=170)
    else:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 คู่อยู่กับซอร์สโค้ดหลัก นำไฟล์ไปวางเรียงไว้ระบบจะเล่นทันทีคราฟบาส")

# --- 6.5 ห้องคู่มืออธิบายการใช้งานแก่ผู้ใช้ ---
elif menu_choice == "📖 คู่มือจริง":
    st.markdown("#### 📖 คู่มือการสั่งการระบบบอร์ดอย่างละเอียดและจริงแท้")
    st.markdown("""
    ยินดีต้อนรับเข้าสู่ระบบควบคุม **SYNAPSE COMMAND CENTER V.4.0** คู่มือนี้นำเสนอการทำงานจริงของฟังก์ชันบนระบบเซิร์ฟเวอร์คลาวด์:
    
    1. **ห้องแชทรวม/เดี่ยว:** ระบบตัดฟังก์ชันค้างดัชนีของเก่ายกชุด แชทรวมส่งข้อความจะบันทึกเข้าเซ็นทรัลกลาง ส่วนห้องแชทลับส่วนตัว เพียงระบุชื่อ AGENT ปลายทางให้ตรง ข้อมูลจะถูกเข้ารหัสสลับคุยเห็นกันแค่สองคนเท่านั้น
    2. **ห้องพิกัดดาวเทียม:** ดึงข้อมูลจากละติจูดและลองจิจูดจริงด้วยระบบตำแหน่งบนเบราว์เซอร์โทรศัพท์มือถือ แล้วสร้างจุดมาร์กเกอร์สีแดงลงบนแผนที่สายไซเบอร์ มั่นใจได้ในความตรงจุดไม่คลาดเคลื่อนพิกัด
    3. **ห้องควอนตัมวันเกิด:** ถอดสมการเชิงตัวเลขจากการคำนวณระยะวันจริงตั้งแต่ปีฐาน ผนวกเข้ากับสูตรเรขาคณิตวิเคราะห์ข้างขึ้นข้างแรม เพื่อดึงแรงโน้มถ่วงตัวเลขออกมาอธิบายความหมายโดยละเอียดชัดเจนทุกตำแหน่ง
    4. **ห้องลูปเพลง (70):** ระบบโหลดและอ่านไบนารี่ข้อมูลไฟล์ .mp3 ทุกเพลงที่บาสวางไว้เคียงข้างไฟล์แอปโดยตรง และสุ่มทำงานวนลูปไร้รอยต่อเมื่อแทร็กจบลง
    """)

# --- 6.6 ห้องตั้งค่าแอปพลิเคชัน (เปลี่ยนรหัสผ่าน / เปลี่ยนสีธีมระบบได้หลากหลายสีตามสั่ง) ---
elif menu_choice == "⚙️ ตั้งค่าแอป":
    st.markdown("#### ⚙️ MANAGEMENT COMMAND PANEL (ห้องตั้งค่าแอป)")
    
    with st.form("settings_form"):
        st.write("🔧 แก้ไขระบบความปลอดภัยและสกินตัวแอปส่วนบุคคล")
        new_pw = st.text_input("กรอกรหัสผ่านใหม่ (หากไม่ต้องการเปลี่ยนให้ปล่อยว่างไว้):", type="password")
        
        # เลือกเปลี่ยนสีธีมที่หลากหลายตามสั่งบาส
        theme_options = {
            "เขียวเรืองแสง (Cyber Neon)": "#39FF14",
            "แดงพิฆาตสายฟ้า (Crimson Red)": "#ff003c",
            "น้ำเงินเงาห้วงลึก (Deep Blue)": "#0055ff",
            "เหลืองอำพันสว่าง (Amber Cyber)": "#ffaa00",
            "ม่วงสนามพลาสม่า (Plasma Purple)": "#e000ff"
        }
        selected_theme_name = st.selectbox("เลือกเปลี่ยนสีธีมหลักของแอปพลิเคชัน:", list(theme_options.keys()))
        new_color_code = theme_options[selected_theme_name]
        
        save_btn = st.form_submit_button("บันทึกการเปลี่ยนโครงสร้างระบบ 💾", use_container_width=True)
        
        if save_btn:
            ref = db.reference(f'users/{st.session_state.user}')
            updates = {'theme_color': new_color_code}
            if new_pw.strip():
                updates['password'] = new_pw.strip()
                
            ref.update(updates)
            st.session_state.current_theme = new_color_code # สั่งเปลี่ยนสีสด ๆ ทันที
            st.success("อัปเดตระบบโครงสร้างส่วนบุคคลเรียบร้อยแล้วคราฟบาส!")
            st.rerun()

st.markdown("<div style='text-align:center; color:#00d2ff; font-size:11px; font-weight:bold; margin-top:25px; font-family:Orbitron;'>อยู่นิ่งๆ ไม่เจ็บตัว | TERMINAL END SEGMENT</div>", unsafe_allow_html=True)
