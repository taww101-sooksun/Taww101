import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# --- 1. INITIALIZE FIREBASE (เชื่อมต่อฐานข้อมูลอัตโนมัติ) ---
if not firebase_admin._apps:
    fb_config = {
        "type": "service_account",
        "project_id": "notty-101",
        "private_key_id": "e280e1fe09351106936545fc0d0175dfb45716b2",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDbOYSW+i8jyezE\nsnIUglx8/8yrclUh+DrWWVbgmPEcinECAeT9m3MrtlPSlX4HlRcgUAY2GOVNvx8+\n2bfQ4odpvsxiP3D0lX23Pex8fkDc0BHQplOjAgYBmQtyr+0IDXJZgGfKqdvbu82u\nmmEUuP7NGML4xGnd/pobmmFo3jG8e0Q33CQl2lLyAOlrXJ/7bxW/7mHPMngOj2In\njAw/38triq/a5DrAWTq0eQaBGq84BI+AkCoN1Pjn6se1JJBL7JkTnS4+zhQQNLEz\ng0cUV8LTAoWUm//4JeezW44K83Jof4SVyu8lUkjWBcGoEbnVh9PdFqEiipJrk8Bk\noNV5yVGXAgMBAAECggEAJMn0PDnj60eZmjCwAE0YJEnxGNxo+PhlN09qyuofnECH\nUmTq/rw1iaJhUrePnMoiRWPohu+Km491OODkfgNl4hMIzXwEAqeLn1Ke+w1c6TFp\nq/AdnP9b7qy2RRrM1ksbY3Wu9U2n/an4jFKP9CBPci+zmHetpHlzdypjKmwPQKfH\nUIkFm29JsFjQiV3mlFTxh8KWSofOKk2idkW6pSuf9Vg+U7G7PfcmY8zJ7R4xFHhU\n4SxGn/zEaclfvv4BGKA8VwVsXvtedSqgf3m153XI72eNcFLR05laoqCffj4ZFlL0\nOZcWAI9l9USjlwM6r3bx68zqzX+fRP9B+DEt1oYQcQKBgQD8hg45u10WJ70VMVJB\n8rIgPNdMIyUSodOjqgna0oOCb9jmOwLqSQy/DbF5nyG4bdoIMvA1MY/anPqZ9T4X\nJti/owndmMzuNXK10ltpctmy8fu8L0Py9E20GiqFkLi+CZFL2owZxK7xXQ6SW5N2\njK23wTd6xxp8+/0WC9DPQxCkKwKBgQDePhwrZQWFbDbd0Absb+mnbL3W8BymUYEF\nlIxd9VaUSOw4bJ93HOHF7e7ZI+Pe2HjNAYdhdu+uvJTN4vYRFQgwO8nv2noPupw8\nCl/WhwKvWFU13pB4f46v/awSg1Ec0/dVWXOimGxxS2AY6hsQPs4RDukBVk6X9Ws1\nRtDoeQQ2RQKBgQDyqdgNvnErkzBupyDG4vQtaonyTmuXxg7c3c/uihF6TQT/6YFZ\npq0rA3uixjrfQiEdc+XFGEWG7Qcc38C0+s2bCo+2dNmpp47+DpFtecKd5U/lfP4t\nAHuTMPnftDzz0bngTLoJISqEIsqX9ox0haeCR5iK0b4wkO6aOuyD34ykVQKBgA/o\nXDXS9lE1jLvVzxkPbacZRoFjEHnrLZQLrPxwujDFA3uKcuOgwpxbSpRqWD40Onla\nGamlTMSyJOiTzU8ttTdWoD614bTMg7Bcgb2mTk/kv7yqYKbvYnRAcRemJKEunu6S\nB4/k3yZA4fEGmMdR54gbDByXY+rGm1Tl68AoIWANAoGBAOdcPg/t6CXw7aXRzV9O\nxIzE6oQNn5djZBKvOqQi2C7b1/jNF3odFC0wXK8xDqAPvUNXfNwxz1FjHYkKSSH1\nxbjoa3WHPFqgkUvBuh5N77Ish3dsRMd47dnHSPPY0WKt2LP1IRQw7z3qCmLWSTpy\n+tvkS1k9uAU6qLcsKVrkxr4e\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-fbsvc@notty-101.iam.gserviceaccount.com",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    cred = credentials.Certificate(fb_config)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://notty-101-default-rtdb.firebaseio.com/'
    })

# --- 2. CONFIGURATION ---
st.set_page_config(page_title="SYNAPSE IDENTITY", layout="wide")

if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 3. LANGUAGE MATRIX (6 ภาษา) ---
TAB_LABELS = {
    "TH": ["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 สื่อสาร", "📊 ล็อก", "🔐 ปลอดภัย", "📺 มีเดีย", "🧹 ระบบ"],
    "EN": ["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOG", "🔐 SEC", "📺 MEDIA", "🧹 SYS"],
    "JP": ["🚀 コア", "🛰️ レーダー", "💬 通信", "📊 ログ", "🔐 セキュリティ", "📺 メディア", "🧹 システム"],
    "CN": ["🚀 核心", "🛰️ 雷达", "💬 通讯", "📊 日志", "🔐 安全", "📺 媒体", "🧹 系统"],
    "MM": ["🚀 အဓိက", "🛰️ ရေဒါ", "💬 ဆက်သွယ်ရေး", "📊 မှတ်တမ်း", "🔐 လုံခြုံရေး", "📺 မီဒီယာ", "🧹 စနစ်"],
    "LA": ["🚀 ແກນຫຼັກ", "🛰️ ເຣດາ", "💬 ສື່ສານ", "📊 ບັນທຶກ", "🔐 ປອດໄພ", "📺 ມີເດຍ", "🧹 ລະບົບ"]
}

# --- 4. ADVANCED CSS CUSTOMIZATION ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background: transparent !important; 
        border-radius: 10px;
    }}
    .chat-bubble {{
        border: 1px solid {st.session_state.theme_color}33;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
        border-left: 4px solid {st.session_state.theme_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR CONTROL ---
with st.sidebar:
    st.title("🌐 SYNAPSE IDENTITY")
    st.session_state.user_name = st.text_input("YOUR ID", st.session_state.user_name)
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.session_state.lang = st.selectbox("LANGUAGE", ["TH", "EN", "JP", "CN", "MM", "LA"])
    st.markdown("---")
    st.write(f'**Slogan:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 6. MAIN CONTENT (TABS) ---
tabs = st.tabs(TAB_LABELS[st.session_state.lang])

# --- TAB: RADAR (ตัวอย่างการล็อกพิกัด) ---
with tabs[1]:
    st.subheader("🛰️ GPS TARGET LOCK")
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("LATITUDE", value=13.75)
    with col2:
        lon = st.number_input("LONGITUDE", value=100.50)
    if st.button("LOCK COORDINATES"):
        db.reference('radar/target').set({'lat': lat, 'lon': lon, 'by': st.session_state.user_name, 'ts': time.time()})
        st.success("Target Locked in Database")

# --- TAB: COMMS (แชตลับ P2P Signaling) ---
with tabs[2]:
    st.subheader("💬 NEURAL PRIVATE LINK")
    target_id = st.text_input("TARGET ID (ID เพื่อนที่จะคุยด้วย)")
    
    if target_id:
        chat_msg = st.chat_input("Type your message...")
        
        # Room ID Logic (เรียงชื่อกันชื่อสลับ)
        room_id = f"priv_{'_'.join(sorted([st.session_state.user_name, target_id]))}"
        
        if chat_msg:
            db.reference(f'private_rooms/{room_id}').push({
                'name': st.session_state.user_name,
                'msg': chat_msg,
                'ts': time.time()
            })
        
        # Display Messages
        raw_data = db.reference(f'private_rooms/{room_id}').order_by_child('ts').limit_to_last(15).get()
        if raw_data:
            for key in sorted(raw_data.keys(), key=lambda k: raw_data[k]['ts']):
                m = raw_data[key]
                st.markdown(f"""
                    <div class="chat-bubble">
                        <small style="color:{st.session_state.theme_color}">{m['name']}</small><br>{m['msg']}
                    </div>
                """, unsafe_allow_html=True)

# --- TAB: SYSTEM (สถานะเซิร์ฟเวอร์) ---
with tabs[6]:
    st.subheader("🧹 SYSTEM DIAGNOSTICS")
    is_connected = db.reference('.info/connected').get()
    status_color = st.session_state.theme_color if is_connected else "#ff1744"
    st.markdown(f"""
        <div style="border: 2px solid {status_color}; padding: 20px; border-radius: 15px; text-align: center;">
            <h1 style="color:{status_color};">{ "CORE ONLINE" if is_connected else "CORE OFFLINE" }</h1>
            <p>Connection to Firebase RTDB: Active</p>
        </div>
    """, unsafe_allow_html=True)
