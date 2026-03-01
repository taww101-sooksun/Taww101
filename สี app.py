import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import time
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
from geopy.distance import geodesic

# ==========================================
# 1. INITIAL SETTINGS & REFRESH
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=10000, key="global_refresh")

# สไตล์ Neon (ห้ามเอาออก)
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 35px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
        border: 5px double #ff1744; padding: 15px; background: rgba(0,0,0,0.8);
        border-radius: 15px; margin-bottom: 20px;
    }
    .terminal-box { border: 1px solid #00f2fe; padding: 15px; border-radius: 10px; background: rgba(0, 10, 20, 0.9); margin-bottom: 10px; }
    .clock-box { background: rgba(0, 242, 254, 0.1); border: 1px solid #00f2fe; padding: 8px; border-radius: 10px; text-align: center; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE & MUSIC
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

# ==========================================
# 3. HEADER & CLOCKS (ยูนิต 1.1 - 1.2)
# ==========================================
st.markdown('<div class="neon-header">SYNAPSE COMMAND CENTER</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><b>{city}</b><br><span style='color:#ff1744;'>{now}</span></div>", unsafe_allow_html=True)

# ==========================================
# 4. DATA PROCESSING
# ==========================================
all_users = db.reference('users').get()
my_id = st.session_state.get('my_name', 'Ta101')

# ==========================================
# 5. MAIN TABS (ยูนิต 1.1 - 1.10)
# ==========================================
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "📊 10-UNITS", "💬 COMMS", "🧹 SYSTEM"])

with tabs[0]: # ยูนิต 1.1 - 1.2
    st.markdown('<div class="terminal-box"><h3>[ UNIT 1.1 - CORE ACCESS ]</h3></div>', unsafe_allow_html=True)
    my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value=my_id)
    st.session_state.my_name = my_id
    
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        st.success(f"📍 GPS LOCKED: {lat}, {lon}")
        if st.button("🛰️ UPDATE GLOBAL POSITION"):
            db.reference(f'users/{my_id}').update({'lat': lat, 'lon': lon, 'status': 'ACTIVE', 'ts': time.time()})
            st.toast("POSITION SYNCHRONIZED!")

with tabs[1]: # ยูนิต 1.4 - 1.5
    st.markdown('<div class="terminal-box"><h3>[ UNIT 1.4 - RADAR ]</h3></div>', unsafe_allow_html=True)
    v_lat, v_lon = 13.75, 100.5
    if all_users and my_id in all_users:
        v_lat, v_lon = all_users[my_id].get('lat', 13.75), all_users[my_id].get('lon', 100.5)

    m = folium.Map(location=[v_lat, v_lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    if all_users:
        for name, info in all_users.items():
            if 'lat' in info and 'lon' in info:
                color = 'blue' if name == my_id else 'red'
                folium.Marker([info['lat'], info['lon']], tooltip=name, icon=folium.Icon(color=color, icon='star')).add_to(m)
    st_folium(m, width="100%", height=450)

with tabs[2]: # ยูนิต 1.3, 1.6, 1.7, 1.8, 1.9
    st.markdown('<div class="terminal-box"><h3>[ UNIT 1.3 - 1.9 STRATEGIC DATA ]</h3></div>', unsafe_allow_html=True)
    if all_users:
        df = pd.DataFrame.from_dict(all_users, orient='index')
        st.write("📊 **1.1 Nodes Status:**", df)
        
        # 1.3 Tactical Ruler
        if my_id in all_users and len(all_users) > 1:
            me_pos = (all_users[my_id]['lat'], all_users[my_id]['lon'])
            st.write("📏 **ระยะห่างจากเป้าหมาย (KM):**")
            for name, info in all_users.items():
                if name != my_id:
                    dist = geodesic(me_pos, (info['lat'], info['lon'])).km
                    st.write(f"- {name}: {dist:.2f} KM")

with tabs[3]: # ยูนิต 1.10
    st.markdown('<div class="terminal-box"><h3>[ UNIT 1.10 - COMMS ]</h3></div>', unsafe_allow_html=True)
    msg = st.chat_input("ส่งข้อความ...")
    if msg: db.reference('global_chat').push({'name': my_id, 'msg': msg, 'ts': time.time()})
    chats = db.reference('global_chat').get()
    if chats:
        for c in sorted(chats.values(), key=lambda x: x.get('ts', 0))[-5:]:
            st.write(f"**{c.get('name')}**: {c.get('msg')}")

with tabs[4]:
    if st.button("🧹 WIPE ALL DATABASE"):
        db.reference('/').delete()
        st.rerun()
