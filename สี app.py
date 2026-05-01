import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os

# --- 1. แปลงไฟล์เสียงในเครื่องเป็น Base64 (เพื่อให้เสียงดังชัวร์) ---
def get_audio_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# --- 2. ฟังก์ชันจัดการรูปภาพ (แปลงรูปส่งเข้า Firebase) ---
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

# --- 3. ตั้งค่าระบบ ---
st.set_page_config(page_title="SYNAPSE OS", layout="wide")

if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
theme = "#39FF14" # สีเขียวนีออนหลักของคุณ

# --- 4. UI หน้า LOGIN / REGISTER ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 20px {theme};'>SYNAPSE CONNECT</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    with tab1:
        with st.form("l_form"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("CONNECT ⚡", use_container_width=True):
                data = db.reference(f'users/{u}').get()
                if data and data.get('password') == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
    with tab2:
        with st.form("r_form"):
            nu = st.text_input("NEW ID")
            np = st.text_input("NEW PASS", type="password")
            if st.form_submit_button("CREATE"):
                db.reference(f'users/{nu}').set({'password': np, 'friends': []})
                st.success("สร้างสำเร็จ")
    st.stop()

# --- 5. ระบบแชต & แจ้งเตือน (ชุดรวม) ---
audio_data = get_audio_base64("notification.mp3")

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown(f"<h4 style='color:{theme}'>👤 {st.session_state.user}</h4>", unsafe_allow_html=True)
    f_id = st.text_input("ADD FRIEND ID")
    if st.button("➕ ADD"):
        my_ref = db.reference(f'users/{st.session_state.user}/friends')
        fs = my_ref.get() or []
        if f_id not in fs:
            fs.append(f_id); my_ref.set(fs); st.rerun()

<script>
    const conf = { databaseURL: "https://sooksun1-default-rtdb.firebaseio.com/" };
    if(!firebase.apps.length) firebase.initializeApp(conf);
    const db = firebase.database();
    let lastC = -1;
    const beep = document.getElementById('beep');

    // --- ระบบปลดล็อกเสียง (สำคัญมากสำหรับมือถือ) ---
    function unlockAudio() {
        beep.play().then(() => {
            beep.pause();
            beep.currentTime = 0;
            console.log("🔊 ระบบเสียงพร้อมใช้งาน");
            document.removeEventListener('click', unlockAudio);
            document.removeEventListener('touchstart', unlockAudio);
        }).catch(e => console.log("รอการสัมผัสหน้าจอเพื่อเปิดเสียง..."));
    }
    document.addEventListener('click', unlockAudio);
    document.addEventListener('touchstart', unlockAudio);

    // --- ระบบแจ้งเตือนสีแดงและเสียง ---
    db.ref('chat_notifications/unread_count').on('value', (s) => {
        const c = s.val() || 0;
        const n = document.getElementById('notif');
        n.innerText = c + " NEW SIGNAL";
        
        if(c > 0) {
            n.style.background = "#FF0000";
            n.style.boxShadow = "0 0 15px #FF0000, 0 0 30px #FF0000"; // ไฟแดงนีออน
            n.style.color = "#fff";
            
            if(lastC !== -1 && c > lastC) {
                beep.currentTime = 0;
                beep.play().catch(e => console.log("Browser บล็อกเสียง: กรุณาแตะหน้าจอ 1 ครั้ง"));
            }
        } else {
            n.style.background = "#444";
            n.style.boxShadow = "none";
        }
        lastC = c;
    });

    // --- ดีไซน์ตัวหนังสือแชทแบบใหม่ (Modern & Clean) ---
    db.ref('global_chat').limitToLast(20).on('child_added', (s) => {
        const d = s.val();
        const isMe = d.user === "{st.session_state.user}";
        const div = document.createElement('div');
        div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
        div.style.maxWidth = '80%';
        div.style.margin = '5px 0';
        
        // รูปแบบกล่องข้อความใหม่
        let bubbleStyle = `
            background: ${isMe ? 'rgba(57, 255, 20, 0.15)' : 'rgba(255, 255, 255, 0.05)'};
            color: #fff;
            padding: 10px 14px;
            border-radius: ${isMe ? '15px 15px 2px 15px' : '15px 15px 15px 2px'};
            border: 1px solid ${isMe ? '#39FF14' : '#444'};
            font-size: 14px;
            line-height: 1.4;
            box-shadow: ${isMe ? '0 0 10px rgba(57, 255, 20, 0.1)' : 'none'};
        `;
        
        let content = d.text ? `<div style="${bubbleStyle}">${d.text}</div>` : "";
        if(d.img) content += `<img src="data:image/png;base64,${d.img}" style="max-width:100%; border-radius:10px; margin-top:8px; border:1px solid #333;">`;
        
        div.innerHTML = `<div style="font-size:10px; color:#888; margin-bottom:3px; text-align:${isMe?'right':'left'};">[ ${d.user} ]</div>` + content;
        document.getElementById('msgs').appendChild(div);
        document.getElementById('chat-box').scrollTop = 999999;
    });
</script>
