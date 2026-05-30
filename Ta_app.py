import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time

# 1. ⚡ ล้างหน้าจอให้คมชัimport 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:geolocator/geolocator.dart';

class P2PHealingSystem {
  # --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบเลือกสี (Color/Theme Selector)
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    picked_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.session_state.theme_color = picked_color
    st.write(f"สีปัจจุบัน: {picked_color}")
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# ใช้ CSS ฉีดสีตามที่เลือก
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .chat-box {{ 
        border: 1px solid {st.session_state.theme_color}; 
        padding: 10px; border-radius: 10px; margin-bottom: 5px;
        background: rgba(255,255,255,0.05);
    }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบเลือกสี (Color/Theme Selector)
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    picked_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.session_state.theme_color = picked_color
    st.write(f"สีปัจจุบัน: {picked_color}")
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# ใช้ CSS ฉีดสีตามที่เลือก
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .chat-box {{ 
        border: 1px solid {st.session_state.theme_color}; 
        padding: 10px; border-radius: 10px; margin-bottom: 5px;
        background: rgba(255,255,255,0.05);
    }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background-color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)} !important; 
        background-color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)? _peerConnection;
  RTCDataChannel? _dataChannel; // ท่อสำหรับ แชต และ GPS
  MediaStream? _localStream;    // ท่อสำหรับ เสียงคอล

  // 1. เริ่มสร้าง "ท่อลับ" (Initialize Connection)
  Future<void> initP2P() async {
    Map<String, dynamic> configuration = {
      "iceServers": [
        {"url": "stun:stun.l.google.com:19302"}, // ใช้แค่หาทางออกเน็ต ไม่ได้เก็บข้อมูล
      ]
    };

    _peerConnection = await createPeerConnection(configuration);

    // สร้างท่อส่งข้อมูล (แชต + GPS)
    RTCDataChannelInit dataChannelDict = RTCDataChannelInit();
    _dataChannel = await _peerConnection!.createDataChannel("chat_gps_pipe", dataChannelDict);

    // ฟังข้อมูลที่ส่งกลับมา
    _dataChannel!.onMessage = (RTCDataChannelMessage message) {
      print("ได้รับข้อมูลลับ: ${message.text}");
      // ตรงนี้คือจุดที่แอปจะแยกข้อมูลว่า เป็นข้อความแชต หรือ พิกัด GPS
    };
  }

  // 2. ระบบส่งพิกัด GPS เรียลไทม์ (ส่งผ่านท่อ P2P ไม่ผ่านใคร)
  void shareLiveLocation() {
    Geolocator.getPositionStream().listen((Position position) {
      String gpsData = "GPS:${position.latitude},${position.longitude}";
      _dataChannel!.send(RTCDataChannelMessage(gpsData));
      print("ส่งพิกัดเรียลไทม์แล้ว...");
    });
  }

  // 3. ระบบคอลเสียง (Voice Call)
  Future<void> startVoiceCall() async {
    final Map<String, dynamic> mediaConstraints = {
      "audio": true, // เปิดไมค์
      "video": false, // ปิดกล้อง (เพื่อความเป็นส่วนตัวตามสไตล์พี่)
    };

    _localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints);
    _localStream!.getTracks().forEach((track) {
      _peerConnection!.addTrack(track, _localStream!);
    });
    print("เริ่มส่งสัญญาณเสียงผ่านท่อลับแล้ว...");
  }

  // 4. ระบบแชต (Send Message)
  void sendMessage(String text) {
    _dataChannel!.send(RTCDataChannelMessage("TEXT:$text"));
  }
}
ด
st.set_page_config(page_title="SYNAPSE CLEAR", layout="wide")

# 2. 🛰️ เชื่อมต่อ FIREBASE
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

st.title("🛰️ SYNAPSE COMMAND CENTER")

# 3. 🎵 บังคับเล่นเพลง (ยักษ์ในตัวฉัน)
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

# 4. 🚀 ระบบดึงพิกัดจริง (แก้จากอนุสาวรีย์ฯ เป็นตัวคุณ)
loc = get_geolocation()

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR"])

with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value="Ta101")
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 ตรวจพบตำแหน่งจริง: {lat}, {lon}")
        
        if st.button("🛰️ บันทึกพิกัดจริง"):
            db.reference(f'users/{my_id}').update({
                'lat': lat, 'lon': lon, 'last_update': time.time()
            })
            st.balloons()
    else:
        st.warning("🚨 กรุณากด 'อนุญาต' (Allow) การเข้าถึงตำแหน่งบนเบราว์เซอร์")

with tabs[1]:
    all_users = db.reference('users').get()
    
    # 💡 หัวใจสำคัญ: ถ้ามีพิกัดเรา ให้เปิดแผนที่ตรงที่เราอยู่เลย!
    view_lat, view_lon = 13.75, 100.5 # ค่าพื้นฐาน
    if all_users and my_id in all_users:
        view_lat = all_users[my_id].get('lat', 13.75)
        view_lon = all_users[my_id].get('lon', 100.5)

    m = folium.Map(location=[view_lat, view_lon], zoom_start=17, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for name, info in all_users.items():
            if 'lat' in info and 'lon' in info:
                # 🔵 ตัวคุณ | 🔴 คนอื่น
                color = 'blue' if name == my_id else 'red'
                folium.Marker([info['lat'], info['lon']], tooltip=name,
                              icon=folium.Icon(color=color, icon='star')).add_to(m)
        st_folium(m, width="100%", height=500)
