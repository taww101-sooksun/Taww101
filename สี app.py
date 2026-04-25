import streamlit as st
import os
import base64
import random
from datetime import date, timedelta

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V.8", layout="wide")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_b64 = get_base64("logo1.png")

# --- 2. DECODER FUNCTIONS (สูตรคำนวณคุณต๊ะ) ---
def get_step_by_step_data(dt):
    if dt is None: return None
    day_val = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}[dt.weekday()]
    day_name = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][dt.weekday()]
    date_val = dt.day
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        l_logic, l_type = -7.5, f"ขึ้น {int(lunar_pos)+1} ค่ำ"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        l_logic, l_type = 7.5, f"แรม {int(lunar_pos-14.765)+1} ค่ำ"
    month_val = dt.month
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {i: v for i, v in zip(range(12), [9,10,11,12,1,2,3,4,5,6,7,8])}
    zv, z_name = z_map[dt.year % 12], z_names[dt.year % 12]
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): ev, en = 1, "ดิน"
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): ev, en = 2, "น้ำ"
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): ev, en = 4, "ไฟ"
    else: ev, en = 3, "ลม"
    return {"day": day_val, "day_n": day_name, "date": date_val, "moon": moon_num, "l_logic": l_logic, "l_type": l_type, "month": month_val, "zv": zv, "zn": z_name, "ev": ev, "en": en, "year": dt.year}

def get_grade_info(val):
    s_val = str(abs(val)).replace('.', '').lstrip('0')
    digit = int(s_val[0]) if s_val else 0
    if digit in [0, 5]: return digit, "⚖️ สมดุลคงที่ (ค่ากลาง)", "#00f3ff"
    elif 1 <= digit <= 4: return digit, "⚠️ ไม่สู้ดี (ไม่ดีพอ)", "#ff4b4b"
    else: return digit, "🔥 ดีถึงดีมาก (พัฒนาได้)", "#00ff00"

# --- 3. GLOBAL STATE ---
if 'global_song_idx' not in st.session_state: st.session_state.global_song_idx = 0

room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"},
    {"name": "🔢 DECODER", "color1": "#FFFFFF", "color2": "#444444"}
]

all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 4. UI RENDER ---
tabs = st.tabs([r["name"] for r in room_info])

for index, tab in enumerate(tabs):
    with tab:
        info = room_info[index]
        c1, c2 = info["color1"], info["color2"]
        
        # แสดง Logo และหัวข้อ
        st.markdown(f"""<div style="text-align:center;"><div style="width:70px;height:70px;margin:0 auto;background-image:url('data:image/png;base64,{logo_b64}');background-size:contain;filter:drop-shadow(0 0 15px {c1});animation:pulse 2s infinite alternate;"></div><h1 style="font-family:'Orbitron';color:#fff;text-shadow:0 0 10px {c1};text-align:center;">{info["name"]}</h1></div>""", unsafe_allow_html=True)

        if info["name"] == "🔢 DECODER":
            # --- ระบบคำนวณ (ห้ามเอาเลขออก) ---
            sub_tab1, sub_tab2 = st.tabs(["👤 บุคคล", "👥 คู่ขนาน"])
            with sub_tab1:
                u_birth = st.date_input("เลือกวันเกิด", value=None, min_value=date(1960,1,1), key="u_in")
                if u_birth:
                    d = get_step_by_step_data(u_birth)
                    st.write(f"**พิกัดฐาน:** วัน{d['day_n']}({d['day']}), วันที่({d['date']}), {d['l_type']}, เดือน({d['month']}), ปี{d['zn']}({d['zv']}), ธาตุ{d['en']}({d['ev']})")
                    base_sum = d['day'] + d['date'] + d['moon'] + d['month'] + d['zv'] + d['ev']
                    raw_code = (base_sum + d['l_logic']) * 1.618
                    days_alive = (date.today() - u_birth).days
                    final_val = (raw_code + days_alive) / 1.618
                    digit, grade, color = get_grade_info(final_val)
                    st.write(f"**Step 1-2 (Raw):** ({base_sum} + {d['l_logic']}) * 1.618 = {round(raw_code, 2)}")
                    st.write(f"**Step 3 (Life Flow):** ({round(raw_code, 2)} + {days_alive} วัน) / 1.618 = {round(final_val, 4)}")
                    st.markdown(f"<div style='border:4px solid {color};padding:20px;text-align:center;border-radius:15px;'><h1 style='color:{color};font-size:50px;'>{round(final_val, 4)}</h1><h2 style='color:{color};'>เลขหน้า {digit} : {grade}</h2></div>", unsafe_allow_html=True)
                    
                    # สแกนไทม์ไลน์
                    st.write("---")
                    col_p, col_f = st.columns(2)
                    with col_p:
                        st.write("🗓️ อดีต 365 วัน (Sync)")
                        p_list = []
                        for i in range(-365, 0):
                            sd = get_step_by_step_data(date.today() + timedelta(days=i))
                            s_c = ((sd['day']+sd['date']+sd['moon']+sd['month']+sd['zv']+sd['ev']) + sd['l_logic']) * 1.618
                            if get_grade_info(s_c)[0] == digit: p_list.append({"วันที่": (date.today()+timedelta(days=i)).strftime("%d/%m/%Y"), "รหัส": round(s_c, 2)})
                        st.table(p_list[:5])
                    with col_f:
                        st.write("🗓️ อนาคต 365 วัน (Sync)")
                        f_list = []
                        for i in range(1, 366):
                            sd = get_step_by_step_data(date.today() + timedelta(days=i))
                            s_c = ((sd['day']+sd['date']+sd['moon']+sd['month']+sd['zv']+sd['ev']) + sd['l_logic']) * 1.618
                            if get_grade_info(s_c)[0] == digit: f_list.append({"วันที่": (date.today()+timedelta(days=i)).strftime("%d/%m/%Y"), "รหัส": round(s_c, 2)})
                        st.table(f_list[:5])

            with sub_tab2:
                c1a, c2a = st.columns(2)
                with c1a: b1 = st.date_input("คนแรก", value=None, key="b1")
                with c2a: b2 = st.date_input("คนที่สอง", value=None, key="b2")
                if b1 and b2:
                    d1, d2 = get_step_by_step_data(b1), get_step_by_step_data(b2)
                    r1 = ((d1['day']+d1['date']+d1['moon']+d1['month']+d1['zv']+d1['ev']) + d1['l_logic']) * 1.618
                    r2 = ((d2['day']+d2['date']+d2['moon']+d2['month']+d2['zv']+d2['ev']) + d2['l_logic']) * 1.618
                    reso = (r1 + r2) / 1.618
                    dp, gp, cp = get_grade_info(reso)
                    st.write(f"**Fusion:** ({round(r1, 2)} + {round(r2, 2)}) / 1.618 = {round(reso, 4)}")
                    st.markdown(f"<div style='border:4px solid gold;padding:20px;text-align:center;border-radius:15px;'><h1 style='color:white;font-size:50px;'>{round(reso, 4)}</h1><h2 style='color:{cp};'>เลขหน้า {dp} : {gp}</h2></div>", unsafe_allow_html=True)

        elif all_music:
            # --- ระบบเพลงเดิม ---
            current_song = all_music[st.session_state.global_song_idx % len(all_music)]
            song_b64 = get_base64(current_song)
            if song_b64:
                st.components.v1.html(f"""
                <canvas id="c-{index}" style="width:100%;height:100px;background:#000;border:1px solid {c1}44;border-radius:15px;"></canvas>
                <button id="b-{index}" style="width:100%;padding:15px;margin-top:10px;background:transparent;color:{c1};border:2px solid {c1};font-family:'Orbitron';border-radius:10px;font-weight:bold;">ACTIVATE {info["name"]}</button>
                <audio id="a-{index}" src="data:audio/mp3;base64,{song_b64}"></audio>
                <script>
                    const a=document.getElementById('a-{index}'), b=document.getElementById('b-{index}'), cv=document.getElementById('c-{index}'), ctx=cv.getContext('2d');
                    let ac, an, src, da;
                    b.onclick=()=>{{
                        if(!ac){{ ac=new AudioContext(); an=ac.createAnalyser(); src=ac.createMediaElementSource(a); src.connect(an); an.connect(ac.destination); da=new Uint8Array(an.frequencyBinCount); render(); }}
                        if(a.paused){{ a.play(); b.innerText="ONLINE 🟢"; }} else {{ a.pause(); b.innerText="PAUSED 🔴"; }}
                    }};
                    function render() {{ requestAnimationFrame(render); an.getByteFrequencyData(da); ctx.clearRect(0,0,cv.width,cv.height); let x=0, bw=(cv.width/da.length)*2; for(let i=0;i<da.length;i++){{ let h=(da[i]/255)*cv.height; ctx.fillStyle="{c1}"; ctx.fillRect(x,cv.height-h,bw-1,h); x+=bw; }} }}
                </script>
                """, height=200)

# --- 5. คลังเพลง & คอนโทรล ---
st.write("---")
col_next, col_shuf = st.columns(2)
if col_next.button("⏭️ NEXT TRACK"): st.session_state.global_song_idx += 1; st.rerun()
if col_shuf.button("🎲 SHUFFLE"): st.session_state.global_song_idx = random.randint(0, len(all_music)-1); st.rerun()
with st.expander("📂 GLOBAL PLAYLIST (52 TRACKS)"):
    for i, s in enumerate(all_music):
        if st.button(f"{'▶️' if i==st.session_state.global_song_idx % len(all_music) else '▪️'} {i+1}. {s}", key=f"s_{i}", use_container_width=True):
            st.session_state.global_song_idx = i; st.rerun()
