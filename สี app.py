import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import datetime
import pytz
import time

# ==========================================
# 1. CORE SETUP & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide", page_icon="🛰️")

# อัปเดตหน้าจออัตโนมัติทุก 30 วินาที (ไม่ถี่ไปจนเครื่องค้าง ตามหลักอยู่นิ่งๆ ไม่เจ็บตัว)
st_autorefresh(interval=30000, key="datarefresh")

# --- FIREBASE INIT ---
if not firebase_admin._apps:
    fb_creds = {
        "type": "service_account",
        "project_id": "notty-101",
        "private_key_id": "24b42506b719388286d33ced19a26a49f8c48971",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCyt5pHunFmVNyc\nhjLiQN+5Xhst6X1rVA5vzOxSApCLXHwe0qgSYO87u8tk3CqP8TzAUw25YGEhGSr+\n1aSqgcoRUKhigFwNh01KoyC+KG7zd7hTwxm4d1FbRUke4oC6HkLPaaSCyJQaUNry\ngGqNCnYJH0paDq16yPGWYEuTm2S7kjGjvO8btzryuB94txduv/K7bHsgEx2NWYSz\n6Spz5mCeH/YMF76/2e7ozCdxmSNclUWsQ5YPR9vXkEnBR8fwmXYSwEoKCxNtV/Uf\ngT7gh9oNt89nK+2fGvTsxoFqkMG03D4N4oKxtYU6xlfOGwb//JRpWSTY7l6kFu6m\n533OQBN1AgMBAAECggEAEqdgVplKydQUvM+zEvOThn0gmB+1ZBT/dsLsbbjvzmQG\nXo89VMHCZrk4xxvF44VaAncIyS8apEJEvxmcmOF4Lmt9T962/QCA3Ef/nGmK/yWh\nWzjTf/IQT1cBhVQ9/G85KP4NWktGTiLfX41w0azkWhpmf9TlXZoIwVnmuY7wKjWx\nCKDGcDK6W0BSKsf2A39ntUaetEV2wCuvANZkpfRldrg0VGdcl2cbRoyuvanlAJzK\BV/mSlO5pUXz9mfMglV08UqU+PbuaWj68PGHVG9UVLU6HoM7fWccoDoYsFBhxyKs\njLuVfcmt0HzH4xsPfbPlMnKzVJSKK0keeVcswqm+1wKBgQDaGrbTRNrgfN9Jisqg\zzSqng6+9wiZ3XxTUl2hsGzuLALAIMktSI0d71uDPEasDx8uqJKnvh5ns+jwZgY+\ns3MXAhq0cCvF5wsfbWCfFeji0zEXLFgT/GVZFzAzzi/BA+ezjEMsf5d8HBziGD+m\nCkw5jtBQXkt0CCTRP/J6FTwpqwKBgQDRxPJ1ZXWVpb5JSRpVmRKeVU2RicuCjyhj\n5yJt0ukC9G/9tDrm6gj/Plbmxd4u1JbLKxB3+S1YyEKc8yahnaFy9yQuMkRfFR1i\n7/2fUzaUbWvDEubJY3CnVF8zAXCy3fWoJlcBkNmoaNVE/QVdc2HXvnOU1CjsTL7V\ngwnRj8rXXwKBgQChNoHQ4+JNcL+zIm3oM4CgZLhNm1e2M6rEA+vFqhy6Z7mYviM1\n35y/db9U3+b1IzBPUrckWjkrOiaCG0eebRIy/ZEzsn4IiGEGV9jFfnJnxudQU6y/\nCR74nVU51bwilXpckt7MM3uLd1Q6IuZZGt+A4/lCjpCDMcnVCcl3R97yhQKBgQCT\n9/4jq4cPIZQhs+xclxaYE4oc8HtaxEr0dbVGjPEKwYxCBSFLg6kHC11XehnpJNKd\ny+nZBy7iopjCh44nkL6zDvw5jgHGpGlPQgTAn30vpCPQvgOH6Zosnopsu0ZZFdLU\nYv8avqeacSCHgoeHTP2mptR3FlUrolM23zFM3sZxtwKBgQCJLw3lagE4P9mOW3Oa\nGKOBUWATRi4C4xt/rRfF8UviXnBRDPRzhp7k5DAlryLhbLEI7W4VdwHZnYyfuWlA\nJSSE/PWN3FoJAdgGzBDY5XONW85FOG7vK3TTjgS/uTNq1/+12f7HqPG73aNaQ3RH\nbHt/wUmZCOcf3t17GTaJbuLZnQ==\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-fbsvc@notty-101.iam.gserviceaccount.com",
    }
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# --- GEMINI INIT ---
genai.configure(api_key="AIzaSyAsDG8TprQwkJ0r2SQhh4CipJtvyBgb6JU")
model = genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# 2. UI STYLING (Cyberpunk Theme)
# ==========================================
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
    .neon-card {
        border: 1px solid #00f2fe; padding: 15px; border-radius: 10px;
        background: rgba(0, 242, 254, 0.05); box-shadow: 0 0 10px rgba(0,242,254,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MAIN DASHBOARD
# ==========================================
st.title("🛰️ SYNAPSE NETWORK SYSTEM")

# Sidebar - User Info
with st.sidebar:
    st.header("👤 USER PROFILE")
    my_id = st.text_input("CODENAME:", value="AGENT_NOTTY")
    st.markdown("---")
    st.write("🌐 **WORLD CLOCK**")
    for city, zone in {'BANGKOK': 'Asia/Bangkok', 'TOKYO': 'Asia/Tokyo'}.items():
        t = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M')
        st.write(f"{city}: `{t}`")

tabs = st.tabs(["📍 RADAR MAP", "🧠 GEN AI", "📻 COMMS", "🧹 SYSTEM"])

# --- TAB 1: RADAR & GPS ---
with tabs[0]:
    st.subheader("LIVE TRACKING")
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        if st.button("📡 BROADCAST POSITION"):
            db.reference(f'users/{my_id}').update({
                'lat': lat, 'lon': lon, 'last_seen': time.time()
            })
            st.toast("Position Synced!")
    else:
        lat, lon = 13.75, 100.5 # Default Bangkok
    
    m = folium.Map(location=[lat, lon], zoom_start=10, tiles="CartoDB dark_matter")
    # ดึงข้อมูลทุกคนจาก Firebase มาปักหมุด
    try:
        all_users = db.reference('users').get()
        if all_users:
            for uid, data in all_users.items():
                color = 'red' if uid == my_id else 'blue'
                folium.Marker([data['lat'], data['lon']], tooltip=uid, icon=folium.Icon(color=color)).add_to(m)
    except: pass
    st_folium(m, width="100%", height=450)

# --- TAB 2: GEMINI AI ---
with tabs[1]:
    st.subheader("🧠 SYMBOLIC INTELLIGENCE")
    prompt = st.chat_input("Ask Gemini anything...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.write(response.text)
            # Log การถามลง Firebase
            db.reference('logs/ai').push({'user': my_id, 'query': prompt, 'ts': time.time()})

# --- TAB 3: COMMS (Realtime Chat) ---
with tabs[2]:
    st.subheader("💬 SECURE CHANNEL")
    chat_ref = db.reference('global_chat')
    
    with st.form("chat_box", clear_on_submit=True):
        msg = st.text_input("Message:")
        if st.form_submit_button("SEND") and msg:
            chat_ref.push({'user': my_id, 'text': msg, 'ts': time.time()})
    
    # แสดงแชท 10 อันดับล่าสุด
    chats = chat_ref.order_by_child('ts').limit_to_last(10).get()
    if chats:
        for cid in reversed(list(chats.keys())):
            c = chats[cid]
            st.markdown(f"**{c['user']}**: {c['text']}")

# --- TAB 4: SYSTEM ---
with tabs[3]:
    st.subheader("🧹 DATA MANAGEMENT")
    if st.button("🔥 WIPE MY DATA"):
        db.reference(f'users/{my_id}').delete()
        st.warning("Data Erased.")
