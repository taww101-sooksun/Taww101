import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SYNAPSE - Music Therapy", layout="wide")

# 2. เชื่อมต่อ Firebase
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
    except Exception as e:
        st.error(f"Firebase Setup Error: {e}")

# ฟังก์ชันคำนวณเวลาจากพิกัด Longitude (ความจริงทางภูมิศาสตร์)
def get_time_by_coords(lon):
    if lon is None: return datetime.datetime.now().strftime("%H:%M") # ถ้าไม่มีพิกัดให้ใช้เวลาเครื่องแก้ขัด
    offset = round(float(lon) / 15)
    actual_time = datetime.datetime.utcnow() + datetime.timedelta(hours=offset)
    return actual_time.strftime("%H:%M")

# --- ส่วนหัวและโลโก้ (เช็คไฟล์ logo3.jpg ให้ละเอียด) ---
st.markdown("---")
col1, col2 = st.columns([1, 5])
with col1:
    # พยายามหาไฟล์โลโก้ทุดชื่อที่เป็นไปได้
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=120)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.write("### 🌐 SYNAPSE") # ถ้าหาไฟล์ไม่เจอจริงๆ ให้ขึ้นชื่อแทนแอปจะได้ไม่โล่ง
with col2:
    st.title("SYNAPSE - Music Therapy")
    st.write("ระบบติดตามเวลาจริงตามพิกัดโลก")
st.markdown("---")

location = get_geolocation()

# 3. สร้าง 3 Tab
tab1, tab2, tab3 = st.tabs(["🚀 เช็คอิน", "📊 แผนที่", "💬 ห้องสนทนา"])

with tab1:
    st.header("เริ่มการเดินทางของคุณ")
    user_id = st.text_input("ระบุชื่อของคุณ:", placeholder="เช่น Ta101", key="user_input")
    if st.button("Start Journey"):
        if user_id and location and 'coords' in location:
            try:
                lat = location['coords']['latitude']
                lon = location['coords']['longitude']
                # ดึงเวลาจริงจากตำแหน่งโลก
                true_time = get_time_by_coords(lon)
                
                if firebase_admin._apps:
                    db.reference(f'users/{user_id}').set({
                        'last_seen': true_time, 
                        'lat': lat, 
                        'lon': lon,
                        'status': "Online"
                    })
                    st.success(f"บันทึกสำเร็จ! เวลาจริงที่ตำแหน่งของคุณคือ: {true_time}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("กรุณาใส่ชื่อและรอสัญญาณ GPS สักครู่ครับ (ต้องกดยืนยันสิทธิ์เข้าถึงตำแหน่งในเบราว์เซอร์ด้วยนะ)")

with tab2:
    st.header("📊 แผนที่ติดตามตำแหน่ง (Google Maps)")
    if firebase_admin._apps:
        try:
            users_ref = db.reference('users').get()
            if users_ref:
                valid_users = []
                all_coords = []
                for k, v in users_ref.items():
                    # ตรวจสอบว่าข้อมูลมีพิกัดครบถ้วน
                    if isinstance(v, dict) and 'lat' in v and 'lon' in v:
                        u_data = {
                            'name': k, 
                            'lat': float(v['lat']), 
                            'lon': float(v['lon']), 
                            'time': v.get('last_seen', '--:--')
                        }
                        valid_users.append(u_data)
                        all_coords.append([u_data['lat'], u_data['lon']])
                
                if valid_users:
                    # สร้างแผนที่ Google Maps (ภาษาไทย)
                    m = folium.Map(location=[valid_users[0]['lat'], valid_users[0]['lon']], 
                                   zoom_start=18, 
                                   tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                                   attr="Google")
                    
                    for u in valid_users:
                        folium.Marker([u['lat'], u['lon']], 
                                      popup=f"ชื่อ: {u['name']} <br> เวลาท้องถิ่น: {u['time']}", 
                                      tooltip=u['name'],
                                      icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
                    
                    if len(all_coords) > 1:
                        m.fit_bounds(all_coords)
                    st_folium(m, width=None, height=550)
                else:
                    st.info("ยังไม่มีข้อมูลพิกัดในระบบ")
        except Exception as e:
            st.error(f"Map Error: {e}")

with tab3:
    st.header("💬 ห้องสนทนา (International Time)")
    if firebase_admin._apps:
        with st.form("chat_form", clear_on_submit=True):
            name_val = user_id if user_id else ""
            c_user = st.text_input("ผู้ส่ง:", value=name_val)
            c_msg = st.text_input("พิมพ์ข้อความของคุณที่นี่:")
            if st.form_submit_button("ส่งข้อความ") and c_user and c_msg:
                # คำนวณเวลาแชทจากพิกัดจริง ณ ตอนนั้น
                user_lon = location['coords']['longitude'] if location and 'coords' in location else None
                db.reference('chats').push({
                    'name': c_user, 
                    'msg': c_msg, 
                    'time': get_time_by_coords(user_lon)
                })
        
        try:
            chats = db.reference('chats').order_by_key().limit_to_last(20).get()
            if chats:
                for _, data in reversed(chats.items()):
                    st.write(f"🗨️ **{data.get('name','?')}** ({data.get('time','--:--')})")
                    st.info(data.get('msg',''))
                    st.divider()
        except Exception as e:
            st.error(f"Chat Load Error: {e}")
