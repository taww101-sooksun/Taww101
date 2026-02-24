import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pandas as pd
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SYNAPSE", layout="wide")

# 2. เชื่อมต่อ Firebase แบบปลอดภัย
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            # แก้ไขเรื่องเว้นวรรคใน Private Key
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        else:
            st.error("❌ ไม่พบหัวข้อ [firebase] ใน Secrets ของ Streamlit Cloud")
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Firebase พัง: {e}")

st.title("🌐 SYNAPSE - Music Therapy")

# 3. ดึงพิกัด GPS
location = get_geolocation()

tab1, tab2 = st.tabs(["🚀 สำหรับเพื่อน", "📊 Dashboard ของเรา"])

with tab1:
    st.header("เริ่มการเดินทางของคุณ")
    user_id = st.text_input("ระบุชื่อหรือรหัสของคุณ:", placeholder="เช่น Ta101", key="user_input")
    
    if st.button("Start Journey", key="main_start_btn"):
        if user_id:
            if location and 'coords' in location:
                try:
                    lat = location['coords']['latitude']
                    lon = location['coords']['longitude']
                    now = datetime.datetime.now()
                    
                    song_path = "test_morning.mp3" if 6 <= now.hour < 12 else "test_evening.mp3"
                    status = "เช้าอันสดใส" if 6 <= now.hour < 12 else "เย็นที่ผ่อนคลาย"

                    # บันทึกข้อมูล (เช็คว่าเชื่อมต่อแอปสำเร็จก่อน)
                    if firebase_admin._apps:
                        ref = db.reference(f'users/{user_id}')
                        ref.set({
                            'last_seen': str(now),
                            'lat': lat,
                            'lon': lon,
                            'status': status
                        })
                        st.success(f"เชื่อมต่อสำเร็จ! พิกัดปัจจุบัน: {lat}, {lon}")
                        if os.path.exists(song_path):
                            st.audio(song_path)
                    else:
                        st.error("ระบบฐานข้อมูลไม่พร้อมใช้งาน")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
            else:
                st.warning("⚠️ กรุณากด 'Allow' เพื่อเปิด GPS หรือรอสัญญาณสักครู่")
        else:
            st.warning("กรุณาใส่ชื่อก่อนนะครับ")

with tab2:
    st.header("📊 แผนที่ติดตามตำแหน่ง (เห็นชื่อถนน)")
    
    # เช็คก่อนว่าเชื่อมต่อ Firebase ติดไหม ไม่งั้นโปรแกรมจะค้างที่บรรทัดนี้
    if firebase_admin._apps:
        try:
            users_ref = db.reference('users').get()
            
            if users_ref:
                map_points = []
                for uid, info in users_ref.items():
                    if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                        map_points.append({
                            'lat': float(info['lat']),
                            'lon': float(info['lon']),
                            'name': uid
                        })
                
                if map_points:
                    center_lat = map_points[0]['lat']
                    center_lon = map_points[0]['lon']
                    # เปลี่ยนบรรทัดที่ 87 เป็นชุดนี้ครับ
m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=16, 
    tiles="CartoDB voyager", 
    attr="© CartoDB"
)

                    
                    for point in map_points:
                        folium.Marker(
                            [point['lat'], point['lon']], 
                            popup=point['name'],
                            tooltip=point['name'],
                            icon=folium.Icon(color='red', icon='info-sign')
                        ).add_to(m)
                    
                    st_folium(m, width=None, height=500)
                    st.dataframe(pd.DataFrame(map_points))
                else:
                    st.info("ยังไม่มีข้อมูลพิกัดในฐานข้อมูล")
            else:
                st.info("ยังไม่มีใครออนไลน์ในขณะนี้")
        except Exception as e:
            st.error(f"ไม่สามารถดึงข้อมูลจากฐานข้อมูลได้: {e}")
    else:
        st.error("ฐานข้อมูลไม่ทำงาน ตรวจสอบการตั้งค่า Secrets อีกครั้งนะเพื่อน")
with tab3:
    st.header("💬 ห้องสนทนากลุ่ม")
    
    if firebase_admin._apps:
        # 1. ส่วนการพิมพ์ข้อความ
        with st.form("chat_form", clear_on_submit=True):
            chat_user = st.text_input("ชื่อผู้ส่ง:", value=user_id if 'user_id' in locals() else "")
            chat_msg = st.text_input("ข้อความ:")
            submit = st.form_submit_button("ส่งข้อความ")
            
            if submit and chat_user and chat_msg:
                chat_ref = db.reference('chats')
                chat_ref.push({
                    'name': chat_user,
                    'msg': chat_msg,
                    'time': str(datetime.datetime.now().strftime("%H:%M"))
                })

        # 2. ส่วนการแสดงผลข้อความ
        st.divider()
        all_chats = db.reference('chats').order_by_key().limit_to_last(20).get()
        
        if all_chats:
            for cid, data in reversed(all_chats.items()):
                # ตกแต่งหน้าตาแชตให้น่าอ่าน
                st.markdown(f"**{data['name']}** ({data['time']}):  \n{data['msg']}")
                st.write("---")
        else:
            st.info("ยังไม่มีข้อความ คุยกันได้นะเพื่อน!")
    else:
        st.error("เชื่อมต่อฐานข้อมูลไม่ได้ ระบบแชตจึงไม่ทำงาน")
