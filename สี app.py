import streamlit as st
import os 
import time
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib

# ==========================================
# 1. ระบบพื้นฐาน & ธีม (Matrix, Ocean, Ember, Rainbow)
# ==========================================
def init_system():
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None
    if 'active_target' not in st.session_state: st.session_state.active_target = None 

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Connection Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def apply_theme():
    themes = {
        "Matrix":  {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF", "chat_user": "#39FF14", "chat_friend": "#333"},
        "Ocean":   {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC", "chat_user": "#00A8E8", "chat_friend": "#005F73"},
        "Ember":   {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF", "chat_user": "#FF4D4D", "chat_friend": "#990000"},
        "Rainbow": {"bg": "#FFFFFF", "main": "#FF69B4", "text": "#000000", "chat_user": "#FFB6C1", "chat_friend": "#E0FFFF"}
    }
    t = themes[st.session_state.theme_set]
    bg_style = f"background-color: {t['bg']} !important;"
    if st.session_state.theme_set == "Rainbow":
        bg_style = "background: linear-gradient(135deg, #FF99CC, #99CCFF, #99FFCC) !important;"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} color: {t['text']} !important; }}
        .stButton>button {{ border: 2px solid {t['main']} !important; color: {t['text']} !important; background: {t['main']} !important; border-radius: 12px; font-weight: bold; }}
        h1, h2, h3, p, span, label, .stMarkdown {{ color: {t['text']} !important; }}
        .stTabs [aria-selected="true"] {{ color: {t['main']} !important; border-bottom: 3px solid {t['main']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 2. ฟังก์ชันหลัก (GPS, Comms, Music)
# ==========================================
def room_gps(theme):
    st.subheader("🛰️ เรดาร์ระบุตำแหน่ง")
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        db.reference(f'locations/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup="คุณ", icon=folium.Icon(color='red')).add_to(m)
        st_folium(m, width=700, height=400)
    else: st.info("⌛ รอพิกัด (กรุณากด Allow)...")

def room_comms(theme):
    st.subheader("💬 ศูนย์สื่อสาร (Video Enabled)")
    tab_pub, tab_priv, tab_call = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว", "📹 วิดีโอคอล"])
    
    all_users = db.reference('accounts').get()
    friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []

    with tab_pub:
        with st.form("pub_chat", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความ...")
            if st.form_submit_button("SEND") and msg:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': msg, 'ts': time.time()})
        msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())): st.write(f"🟢 **{m.get('u')}**: {m.get('msg')}")

    with tab_priv:
        all_rooms = db.reference('private_rooms').get()
        if all_rooms:
            for rid in all_rooms.keys():
                if st.session_state.user in rid:
                    f_name = rid.replace(st.session_state.user, "").replace("_", "")
                    last_m = list(all_rooms[rid].values())[-1]
                    if st.button(f"💬 {f_name}: {last_m['msg'][:15]}...", key=f"btn_{rid}"):
                        st.session_state.active_target = f_name
        st.divider()
        target_p = st.selectbox("เลือกเพื่อน:", ["-- เลือกชื่อ --"] + friends, 
                                index=friends.index(st.session_state.active_target) + 1 if st.session_state.active_target in friends else 0)
        if target_p != "-- เลือกชื่อ --":
            st.session_state.active_target = target_p
            room_id = "_".join(sorted([st.session_state.user, target_p]))
            with st.form("p_chat", clear_on_submit=True):
                pm = st.text_input(f"คุยกับ {target_p}...")
                if st.form_submit_button("SEND"):
                    db.reference(f'private_rooms/{room_id}').push({'u': st.session_state.user, 'msg': pm, 'ts': time.time()})
            p_msgs = db.reference(f'private_rooms/{room_id}').order_by_key().limit_to_last(15).get()
            if p_msgs:
                for pi in reversed(list(p_msgs.values())):
                    align = "right" if pi.get('u') == st.session_state.user else "left"
                    bg = theme['chat_user'] if pi.get('u') == st.session_state.user else theme['chat_friend']
                    st.markdown(f'<div style="text-align:{align};"><div style="display:inline-block; background:{bg}; padding:8px 12px; border-radius:10px; margin:2px; color:#000;"><b>{pi.get("u")}</b>: {pi.get("msg")}</div></div>', unsafe_allow_html=True)

    with tab_call:
        target_c = st.selectbox("เลือกเพื่อนที่จะคอล:", ["-- เลือกชื่อ --"] + friends, key="vc_sel")
        if target_c != "-- เลือกชื่อ --":
            # --- อัปเกรดเป็น Video Call ---
            video_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#111; padding:15px; border-radius:15px; border:2px solid %s; text-align:center;">
                <div style="position:relative; width:100%%; height:250px; background:#000; border-radius:10px; overflow:hidden; margin-bottom:10px;">
                    <video id="remoteVideo" autoplay style="width:100%%; height:100%%; object-fit:cover;"></video>
                    <video id="localVideo" autoplay muted style="position:absolute; bottom:10px; right:10px; width:80px; height:60px; border:2px solid white; border-radius:5px; object-fit:cover;"></video>
                </div>
                <div style="display:flex; gap:10px;">
                    <button id="startVideo" style="flex:1; padding:12px; background:%s; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📹 เริ่มคอล</button>
                    <button id="endVideo" style="flex:1; padding:12px; background:#FF4D4D; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer; display:none;">🔴 วางสาย</button>
                </div>
                <p id="vStatus" style="color:#888; font-size:12px; margin-top:8px;">สถานะ: พร้อมวิดีโอคอล</p>
            </div>
            <script>
                const peer = new Peer('%s', {config: {'iceServers': [{ 'urls': 'stun:stun.l.google.com:19302' }]}});
                let myStream = null;
                let activeCall = null;

                peer.on('call', call => {
                    if(confirm('สายเข้าจาก ' + call.peer + ' รับวิดีโอคอลหรือไม่?')) {
                        navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
                            myStream = stream;
                            document.getElementById('localVideo').srcObject = stream;
                            call.answer(stream);
                            handleCall(call);
                        });
                    }
                });

                function handleCall(call) {
                    activeCall = call;
                    document.getElementById('startVideo').style.display = 'none';
                    document.getElementById('endVideo').style.display = 'inline-block';
                    document.getElementById('vStatus').innerText = 'สถานะ: กำลังคุย...';
                    call.on('stream', remoteStream => {
                        document.getElementById('remoteVideo').srcObject = remoteStream;
                    });
                }

                document.getElementById('startVideo').onclick = () => {
                    navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
                        myStream = stream;
                        document.getElementById('localVideo').srcObject = stream;
                        const call = peer.call('%s', stream);
                        handleCall(call);
                    }).catch(err => alert('ไม่สามารถเข้าถึงกล้องได้: ' + err));
                };

                document.getElementById('endVideo').onclick = () => {
                    if(activeCall) activeCall.close();
                    if(myStream) myStream.getTracks().forEach(t => t.stop());
                    location.reload();
                };
            </script>
            """ % (theme['main'], theme['main'], st.session_state.user, target_c)
            components.html(video_html, height=400)

def room_music():
    st.subheader("🎧 เพลง")
    files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if files:
        st.audio(files[st.session_state.song_index], autoplay=True)
        for idx, f in enumerate(files):
            if st.button(f"🎵 {f}", key=f"m_{idx}"):
                st.session_state.song_index = idx
                st.rerun()

# ==========================================
# 3. ส่วนประกอบหลัก (Main Application)
# ==========================================
def main():
    init_system()
    if not st.session_state.auth_status:
        st.title("🛡️ SYNAPSE GATE")
        t1, t2 = st.tabs(["🔐 Login", "📝 Register"])
        with t1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("ENTER"):
                data = db.reference(f'accounts/{u}').get()
                if data and data.get('pw') == hash_pw(p):
                    st.session_state.auth_status, st.session_state.user = True, u
                    st.rerun()
        with t2:
            ru = st.text_input("New User")
            rp = st.text_input("New PW", type="password")
            if st.button("REGISTER"):
                if ru and rp: db.reference(f'accounts/{ru}').set({'pw': hash_pw(rp)}); st.success("OK!")
        return

    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 ชุดสี:", ["Matrix", "Ocean", "Ember", "Rainbow"])
        if st.button("🚪 LOGOUT"): st.session_state.auth_status = False; st.rerun()
    
    t = apply_theme()
    menu = {"🛰️ เรดาร์": lambda: room_gps(t), "💬 สื่อสาร": lambda: room_comms(t), "🎧 เพลง": room_music}
    tabs = st.tabs(list(menu.keys()))
    for i, func in enumerate(menu.values()):
        with tabs[i]: func()

if __name__ == "__main__": main()
