import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import google.generativeai as genai
import time
import datetime
from streamlit_folium import st_folium
import folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. INITIALIZE SERVICES (ความเป็นจริง: ต้องต่อติดถึงจะไปต่อ)
# ==========================================

# เชื่อมต่อ Firebase (ใช้ข้อมูล Private Key ที่คุณให้มา)
if not firebase_admin._apps:
    fb_creds = {
        "type": "service_account",
        "project_id": "notty-101",
        "private_key_id": "24b42506b719388286d33ced19a26a49f8c48971",
        "private_key": st.secrets.get("private_key", "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCyt5pHunFmVNyc\nhjLiQN+5Xhst6X1rVA5vzOxSApCLXHwe0qgSYO87u8tk3CqP8TzAUw25YGEhGSr+\n1aSqgcoRUKhigFwNh01KoyC+KG7zd7hTwxm4d1FbRUke4oC6HkLPaaSCyJQaUNry\ngGqNCnYJH0paDq16yPGWYEuTm2S7kjGjvO8btzryuB94txduv/K7bHsgEx2NWYSz\n6Spz5mCeH/YMF76/2e7ozCdxmSNclUWsQ5YPR9vXkEnBR8fwmXYSwEoKCxNtV/Uf\ngT7gh9oNt89nK+2fGvTsxoFqkMG03D4N4oKxtYU6xlfOGwb//JRpWSTY7l6kFu6m\n533OQBN1AgMBAAECggEAEqdgVplKydQUvM+zEvOThn0gmB+1ZBT/dsLsbbjvzmQG\nXo89VMHCZrk4xxvF44VaAncIyS8apEJEvxmcmOF4Lmt9T962/QCA3Ef/nGmK/yWh\nWzjTf/IQT1cBhVQ9/G85KP4NWktGTiLfX41w0azkWhpmf9TlXZoIwVnmuY7wKjWx\nCKDGcDK6W0BSKsf2A39ntUaetEV2wCuvANZkpfRldrg0VGdcl2cbRoyuvanlAJzK\nBV/mSlO5pUXz9mfMglV08UqU+PbuaWj68PGHVG9UVLU6HoM7fWccoDoYsFBhxyKs\njLuVfcmt0HzH4xsPfbPlMnKzVJSKK0keeVcswqm+1wKBgQDaGrbTRNrgfN9Jisqg\nzzSqng6+9wiZ3XxTUl2hsGzuLALAIMktSI0d71uDPEasDx8uqJKnvh5ns+jwZgY+\ns3MXAhq0cCvF5wsfbWCfFeji0zEXLFgT/GVZFzAzzi/BA+ezjEMsf5d8HBziGD+m\nCkw5jtBQXkt0CCTRP/J6FTwpqwKBgQDRxPJ1ZXWVpb5JSRpVmRKeVU2RicuCjyhj\n5yJt0ukC9G/9tDrm6gj/Plbmxd4u1JbLKxB3+S1YyEKc8yahnaFy9yQuMkRfFR1i\n7/2fUzaUbWvDEubJY3CnVF8zAXCy3fWoJlcBkNmoaNVE/QVdc2HXvnOU1CjsTL7V\ngwnRj8rXXwKBgQChNoHQ4+JNcL+zIm3oM4CgZLhNm1e2M6rEA+vFqhy6Z7mYviM1\n35y/db9U3+b1IzBPUrckWjkrOiaCG0eebRIy/ZEzsn4IiGEGV9jFfnJnxudQU6y/\nCR74nVU51bwilXpckt7MM3uLd1Q6IuZZGt+A4/lCjpCDMcnVCcl3R97yhQKBgQCT\n9/4jq4cPIZQhs+xclxaYE4oc8HtaxEr0dbVGjPEKwYxCBSFLg6kHC11XehnpJNKd\ny+nZBy7iopjCh44nkL6zDvw5jgHGpGlPQgTAn30vpCPQvgOH6Zosnopsu0ZZFdLU\nYv8avqeacSCHgoeHTP2mptR3FlUrolM23zFM3sZxtwKBgQCJLw3lagE4P9mOW3Oa\nGKOBUWATRi4C4xt/rRfF8UviXnBRDPRzhp7k5DAlryLhbLEI7W4VdwHZnYyfuWlA\nJSSE/PWN3FoJAdgGzBDY5XONW85FOG7vK3TTjgS/uTNq1/+12f7HqPG73aNaQ3RH\nbHt/wUmZCOcf3t17GTaJbuLZnQ==\n-----END PRIVATE KEY-----\n"),
        "client_email": "firebase-adminsdk-fbsvc@notty-101.iam.gserviceaccount.com",
        "client_id": "117289448766434215709",
    }
    # หมายเหตุ: ในโปรดักชั่นควรแก้ \n ใน private_key ด้วย .replace('\\n', '\n')
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# เชื่อมต่อ Gemini AI
genai.configure(api_key="AIzaSyAsDG8TprQwkJ0r2SQhh4CipJtvyBgb6JU")
model = genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# 2. UI & APP LOGIC
# ==========================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000; color: #00FF00; font-family: 'Courier New'; }
    .neon-text { text-shadow: 0 0 10px #00FF00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ SYNAPSE COMMAND CENTER")

tabs = st.tabs(["🚀 RADAR & GPS", "🧠 GEMINI AI", "💬 DATABASE LOG"])

# --- TAB 1: RADAR ---
with tabs[0]:
    st.subheader("REAL-TIME TRACKING")
    user_id = st.text_input("ENTER CODENAME:", value="Agent_X")
    
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        st.write(f"CURRENT POS: {lat}, {lon}")
        
        if st.button("🛰️ BROADCAST LOCATION"):
            db.reference(f'users/{user_id}').update({
                'lat': lat, 'lon': lon, 'timestamp': time.time()
            })
            st.toast("พิกัดถูกส่งเข้าดาวเทียมแล้ว!")

    # แผนที่ Folium
    m = folium.Map(location=[13.75, 100.5], zoom_start=6, tiles="CartoDB dark_matter")
    try:
        users = db.reference('users').get()
        if users:
            for name, data in users.items():
                folium.Marker([data['lat'], data['lon']], popup=name).add_to(m)
    except: pass
    st_folium(m, width="100%", height=400)

# --- TAB 2: GEMINI AI ---
with tabs[1]:
    st.subheader("🧠 INTELLIGENCE UNIT")
    prompt = st.text_area("ส่งคำสั่งให้ AI วิเคราะห์:")
    if st.button("GENERATE"):
        if prompt:
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                st.markdown(f"> {response.text}")
                # เก็บประวัติลง Firebase
                db.reference('ai_logs').push({
                    'user': user_id, 'prompt': prompt, 'time': str(datetime.datetime.now())
                })
        else:
            st.error("กรุณาใส่ข้อมูลก่อน")

# --- TAB 3: LOGS ---
with tabs[2]:
    st.subheader("SYSTEM ACTIVITY")
    logs = db.reference('ai_logs').order_by_key().limit_to_last(10).get()
    if logs:
        for l_id in reversed(list(logs.keys())):
            log = logs[l_id]
            st.text(f"[{log['time']}] {log['user']}: {log['prompt'][:50]}...")

st.sidebar.markdown("---")
st.sidebar.write("🛡️ STATUS: **ENCRYPTED**")
st.sidebar.write(f"PROJECT: {fb_creds['project_id']}")
st.sidebar.button("WIPE SESSION", on_click=lambda: st.session_state.clear())
