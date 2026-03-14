import streamlit as st
import time
from firebase_admin import db # อย่าลืมตั้งค่า firebase_admin.initialize_app ก่อนรัน
import streamlit as st
import time
import firebase_admin
from firebase_admin import credentials, db

# --- 0. ยืนยันตัวตนกับ Firebase (เพิ่มส่วนนี้เข้าไป!) ---
if not firebase_admin._apps:
    # นำไฟล์ JSON ที่ได้จาก Firebase มาใส่ชื่อไฟล์ให้ตรง
    # หรือถ้าไม่อยากใช้ไฟล์ ให้ใส่ path ของไฟล์ที่คุณอัปโหลดขึ้น GitHub/Server
    cred = credentials.Certificate("ชื่อไฟล์-คีย์-ของคุณ.json") 
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ชื่อโปรเจกต์ของคุณ.firebaseio.com/' # ใส่ URL ฐานข้อมูลของคุณ
    })

# --- ต่อด้วยโค้ดเดิมของคุณ ---
# st.set_page_config ...

# --- 1. SET UP & THEME (ก๊อปจากที่คุณเลือก) ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 
if 'lang' not in st.session_state:
    st.session_state.lang = "TH"
if 'lang_open' not in st.session_state:
    st.session_state.lang_open = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = "USER_" + str(int(time.time()))[-4:]
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

# --- 2. คลังภาษา (6 ภาษาครอบคลุมทุกส่วน) ---
LANG_MAP = {
    "TH": {"back": "⬅️ ย้อนกลับ", "target": "เป้าหมาย", "status": "สถานะระบบ", "send": "ส่ง", "chat": "แชต"},
    "EN": {"back": "⬅️ BACK", "target": "TARGET", "status": "SYS STATUS", "send": "SEND", "chat": "CHAT"},
    "JP": {"back": "⬅️ 戻る", "target": "目標", "status": "システム状態", "send": "送信", "chat": "チャット"},
    "CN": {"back": "⬅️ 返回", "target": "目标", "status": "系统状态", "send": "发送", "chat": "聊天"},
    "MM": {"back": "⬅️ နောက်သို့", "target": "ပစ်မှတ်", "status": "စနစ်အခြေအနေ", "send": "ပို့ပါ", "chat": "စကားပြောခန်း"},
    "LA": {"back": "⬅️ ກັບຄືນ", "target": "ເປົ້າໝາຍ", "status": "ສະຖານະລະບົບ", "send": "ສົ່ງ", "chat": "ແຊັດ"}
}

TAB_LABELS = {
    "TH": ["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 สื่อสาร", "📊 ล็อก", "🔐 ปลอดภัย", "📺 มีเดีย", "🧹 ระบบ"],
    "EN": ["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOG", "🔐 SEC", "📺 MEDIA", "🧹 SYS"],
    "JP": ["🚀 コア", "🛰️ レーダー", "💬 通信", "📊 ログ", "🔐 セキュリティ", "📺 メディア", "🧹 システム"],
    "CN": ["🚀 核心", "🛰️ 雷达", "💬 通讯", "📊 日志", "🔐 安全", "📺 媒体", "🧹 系统"],
    "MM": ["🚀 အဓိက", "🛰️ ရေဒါ", "💬 ဆက်သွယ်ရေး", "📊 မှတ်တမ်း", "🔐 လုံခြုံရေး", "📺 မီဒီယာ", "🧹 စနစ်"],
    "LA": ["🚀 ແກນຫຼັກ", "🛰️ ເຣດາ", "💬 ສື່ສານ", "📊 ບັນທຶກ", "🔐 ປອດໄພ", "📺 ມີເດຍ", "🧹 ລະບົບ"]
}

# --- 3. UI STYLE (CSS นีออนตามสีที่เลือก) ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .ghost-glass {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid {st.session_state.theme_color}44;
        padding: 20px; border-radius: 15px; margin-bottom: 15px;
    }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background: transparent !important;
        width: 100%; transition: 0.3s;
    }}
    .stButton>button:hover {{ background: {st.session_state.theme_color}22 !important; box-shadow: 0 0 15px {st.session_state.theme_color}; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC FUNCTIONS (เช็คระบบ & แชต) ---
def check_server_logic():
    try: return "ONLINE" if db.reference('.info/connected').get() else "OFFLINE"
    except: return "OFFLINE"

def private_chat_logic(my_name, target_name, p_msg=None):
    pair = sorted([my_name, target_name])
    room_id = f"priv_{pair[0]}_{pair[1]}"
    if p_msg:
        db.reference(f'private_rooms/{room_id}').push({'name': my_name, 'msg': p_msg, 'ts': time.time()})
    raw = db.reference(f'private_rooms/{room_id}').order_by_child('ts').limit_to_last(10).get()
    return sorted(raw.values(), key=lambda x: x.get('ts', 0)) if raw else []

# --- 5. SIDEBAR & LANGUAGE SELECTOR ---
with st.sidebar:
    st.markdown(f"### 🌐 SYNAPSE IDENTITY")
    st.session_state.user_name = st.text_input("YOUR ID", st.session_state.user_name)
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    
    # ระบบเลือกภาษา 2 จังหวะ
    if st.button(f"LANGUAGE: {st.session_state.lang}"):
        st.session_state.lang_open = not st.session_state.lang_open
    
    if st.session_state.lang_open:
        c1, c2 = st.columns(2)
        l_opts = [("TH", "🇹🇭"), ("EN", "🇺🇸"), ("JP", "🇯🇵"), ("CN", "🇨🇳"), ("MM", "🇲🇲"), ("LA", "🇱🇦")]
        for code, flag in l_opts:
            if st.button(f"{flag} {code}"):
                st.session_state.lang = code
                st.session_state.lang_open = False
                st.rerun()
    st.write("---")
    st.info('"อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 6. MAIN NAVIGATION (Tabs & UI) ---
L = LANG_MAP[st.session_state.lang]
main_tabs = st.tabs(TAB_LABELS[st.session_state.lang])

# [Tab 💬 COMMS] - แชตลับ
with main_tabs[2]:
    st.markdown('<div class="ghost-glass">', unsafe_allow_html=True)
    target = st.text_input(L["target"], placeholder="Target ID...")
    if target:
        msg = st.chat_input(f"{L['chat']}...")
        p_history = private_chat_logic(st.session_state.user_name, target, msg)
        for m in p_history:
            color = st.session_state.theme_color if m['name'] == st.session_state.user_name else "#888"
            st.markdown(f"<p style='color:{color}'><b>{m['name']}:</b> {m['msg']}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# [Tab 🧹 SYS] - เช็คสถานะ
with main_tabs[6]:
    status = check_server_logic()
    color = "#00f2fe" if status == "ONLINE" else "#ff1744"
    st.markdown(f"""
        <div style='border: 2px solid {color}; padding: 20px; border-radius: 10px; text-align: center;'>
            <h2 style='color:{color};'>{L['status']}: {status}</h2>
        </div>
    """, unsafe_allow_html=True)

# ปุ่ม BACK (ที่ท้ายหน้า)
if st.session_state.nav_level != "HOME":
    if st.button(L["back"]):
        st.session_state.nav_level = "HOME"
        st.rerun()
