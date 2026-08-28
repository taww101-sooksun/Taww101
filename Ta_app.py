import math 
import os 

นำเข้า folium 
นำเข้า streamlit as st 
จาก folium.plugins import LocateControl 
จาก streamlit_folium import st_folium 


st.set_page_config( 
    page_title="Ta App - เฆี่ยนฑ์” เธียเธ‰เธ™เธ— เธียเธ™เธฒ", page_icon 
    ="๐ŸŒพ", 
    layout="wide", 
    Initial_sidebar_state="collapsed", 
) 

PLOW_RATE = 250.0 
MILL_RATE = 350.0 
RAI_M2 = 1600.0 
NGAN_M2 = 400.0 
WA_M2 = 4.0 
LOGO_PATH = "logo1.png" 


def thai_area(m2): 
    m2 = max(0.0, float(m2)) 
    rai = int(m2 // RAI_M2) 
    ยังคงอยู่ = m2 - rai * RAI_M2 
    งาน = int (ยังคงอยู่ // NGAN_M2) 
    remain -= ngan * NGAN_M2 
    wa = int(remain // WA_M2) 
    remain -= wa * WA_M2 
    return rai, ngan, wa, remain 


def polygon_area_m2(points): 
    if len(points) < 3: 
        return 0.0 

    average_lat = sum(p[0] for p in points) / len(points) 
    lat_radians = math.radians(average_lat) 
    earth_radius = 6378137.0 

    xy = [] 
    for lat, lon in points: 
        x = math.radians(lon) * earth_radius * math.cos(lat_radians) 
        y = math.radians(lat) * earth_radius 
        xy.append((x, y)) 

    area = 0.0 
    for i in range(len(xy)): 
        x1, y1 = xy[i] 
        x2, y2 = xy[(i + 1) % len(xy)] 
        area += x1 * y2 - x2 * y1 

    return abs(area) / 2.0 


def money(value): 
    return f"{value:,.2f}" 


if "points" not in st.session_state: 
    st.session_state.points = [] 

if "saved_plots" not in st.session_state: 
    st.session_state.saved_plots = [] 

if "lat" not in st.session_state: 
    st.session_state.lat = 13.7563 

if "lon" not in st.session_state: 
    st.session_state.lon = 100.5018 


st.markdown( 
    """ 
    <style> 
    html, body, [class*="css"], .stApp, 
    button, input, textarea, select { 
        font-family: Tahoma, Arial, sans-serif !important; 
    } 

    .total-box { 
        padding: 24px; 
        border-radius: 18px; 
        background: rgba(46, 125, 50, 0.12); 
        border: 2px solid rgba(46, 125, 50, 0.35); 
        text-align: center; 
        margin-top: 10px; 
    } 

    .total-title { 
        font-size:20px; 
    } 

    .total-money {
        ขนาดตัวอักษร: 42 พิกเซล; 
        น้ำหนักตัวอักษร: 800; 
    } 
    </style> 
    """, 
    unsafe_allow_html=True, 
) 


left, right = st.columns([1, 5], Vertical_alignment="center") 

with left: 
    if os.path.exists(LOGO_PATH): 
        st.image(LOGO_PATH, width=115) 
    else: 
        st.markdown("## ๐ŸŒพ") 

with right: 
    st.title("๐ŸŒพ Ta App") 
    st.caption(" เฉลิมฑ์” ชัทเน‰ เธ™เธ— ัฒเนˆเธ™เธฒ โ€ข เธ› ฑ์เธซเธชเธ” โ€ข “เธีย™เธงเธ” ัน “เนˆ เธฒเธซเธียเธฒเธน” เธ – / เธ> เธียเธ™”) 

st.divider() 

c1, c2 = st.columns(2) 

ด้วย c1: 
    owner = st.text_input( 
        "๐Ÿ'คเฮิร์ชเธเนˆเธ€เธˆเน‰พลัสฑ์เธียเธ™เธฒ", 
        placeholder="เน€เธสเนˆเธ™เธ™เธฒเธขเธกเธฒเธข เนเอฟเธียเธ” เธต", 
        key="owner", 
    ) 

ด้วย c2: 
    note = st.text_input( 
        "๐Ÿ“ เธซเธียฒเธขเน€เธซเธ•เธ", 
        placeholder="เน€เธˆเธ™เธ™เธฒเนเธh› เธียเธซเธฅเธฑเธียเธ‰เธฒเธ™ / เธ™เธฑ”เน “เธ–เธงเธฑเธ™เธียเธฑเธ™เธ—เธเน”, 
        key="note", 
    ) 

st.subheader("๐Ÿ—บ........ธันเธซเธ€เธ€เธ•เนเธีย›เธฅเธ™เธฒ") st.info( " 
เน
    เธ•เธธเธ™เน | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |ใน
    ระยะ อังกฤษ
    3 ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿” ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿ ” ) map_center = 
[st.session_state.lat, st.session_state.lon] 
m 
= folium.Map( 
    location=map_center, 
    Zoom_start=17, 
    control_scale=True, 
    tiles="OpenStreetMap", 
) 
LocateControl( 
    auto_start=False, 
    flyTo=True, 
    keepCurrentZoomLevel=False, 
    showCompass=True, 
).add_to(m) 
for i, (lat, lon) ในการแจกแจง (st.session_state.points): 
    folium.Marker( 
        [lat, lon], 
        tooltip=f"เฉลิม" {i + 1}", 
        icon=folium.Icon(color="green", icon="map-marker"), 
    ).add_to(m) 
if len(st.session_state.points) >= 2: 
    line_points = list(st.session_state.points) 
    if len(line_points) >= 3: 
        line_points.append(line_points[0]) 
    folium.PolyLine( 
        line_points,
        color="green", 
        weight=4, 
        opacity=0.85, 
    ).add_to(m)







ถ้า len(st.session_state.points) >= 3: 
    folium.Polygon( 
        st.session_state.points, 
        color="green", 
        weight=2, 
        fill=True, 
        fill_opacity=0.20, 
    ).add_to(m) 

map_data = st_folium( 
    m, 
    width=None, 
    height=520, 
    returned_objects=["last_clicked", "center"], 
    key="farm_map", 
) 

clicked = map_data.get("last_clicked") 

if clicked: 
    clicked_lat = float(clicked["lat"]) 
    clicked_lon = float(clicked["lng"]) 

    last_point = st.session_state.points[-1] if st.session_state.points else None 

    different = ( 
        last_point is None 
        or abs(last_point[0] - clicked_lat) > 0.000001 
        or abs(last_point[1] - clicked_lon) > 0.000001 
    ) 

    ถ้าต่างกัน: 
        st.session_state.points.append((clicked_lat, clicked_lon)) 
        st.rerun() 

st.write("### ๐Ÿ“ ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿ b1 

, b2, b3, b4 = st.columns(4) 

ด้วย b1: 
    if st.button("โ†ฉ๏ธ ฅฅนเธซเธีย” ฅเนˆ ฑฒธชธ”", use_container_width=True): 
        if st.session_state.points: 
            st.session_state.points.pop( ) 
            st.rerun() 

with b2: 
    if st.button("๐Ÿ—'๏ธ ” ﻿— ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿””, use_container_width=True): st.session_state.points = [] st.rerun() with b3: if st.button("๐Ÿ“ ฑˆธธัน” • 
        เธ
• 
        เธี
    ยเธ่เธขเนเธฒเธ", use_container_width=True): 
        st.session_state.points = [ 
            (13.75630, 100.50180), 
            (13.75630, 100.50300), 
            (13.75530, 100.50300), 
            (13.75530, 100.50180), 
        ] 
        st.rerun() 
ด้วย b4: 
    ถ้า st.button("๐Ÿ”„ ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿”, use_container_width=True): 
        st.rerun() 
area_m2 = polygon_area_m2(st.session_state.points) 
rai, ngan, wa, still_m2 = thai_area(area_m2) 
plow_cost = (area_m2 / RAI_M2) * PLOW_RATE 
mill_cost = (area_m2 / RAI_M2) * MILL_RATE 
Total_cost = plow_cost + mill_cost 
st.divider() 
st.subheader("๐Ÿ“ เธฅเธ เธฒเธ‰เธ™ เธ— เธอร์เนˆ") 
ถ้า len(st.session_state.points) < 3: 
    st.คำเตือน(" เธชเธช“ เธฒเธ› ฑ์เธซเธียเธ” เธียขเนˆ ฑฒเธ™เธ‰เธช 3 ᆆ เธีย” เน€ชเธเนˆ เธ่เธ่ “เธ่เน‰ เธ™เธ— เธเนˆ”) 
else: 
    a1, a2, a3, a4 = st.คอลัมน์(4)







    ด้วย
    a1: 
        st.metric(" | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | , ; ; ; ; ; ; ; ; ; f ; {area_m2:,.2f} เธ•เธ‰ เธ™เธ— เธ เธ ˆ เธ เธ เธ เธ เธ เธ เธ ่
        เธ เธ เธ เธ เธ เธ เธ เธ เธ เธ เธ เธ เธ เธ ท เธ เธ เธ เธ เธ เธ เธ เธ เธ เธ
        เธ เธ เธ เธ เธ เธ’ ง งงเธ
    ง
    เธงเธ ? 
        st.metric(" | | | | | | | | | | | | | | | | | | | | | | | | | | | | | ) ; 
    st.metric( 
        " | | | | | | | | | | | | | | | | | | | | | | | | | | | | | ) ; st.metric(" | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | ) ; st.metric(" | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | 
        ) st.success( f" | | | | | | | | | | | | | | | | | | | | | | | | | ) เธ•เธียเธ่เธ่เธงเธฒ {remain_m2:.2f} ื•เอชเอช.เอช." 
    ) 
    st.divider() 
    st.subheader("๐Ÿ'ฐ
    s1, s2 = st.columns(2) 
    ด้วย s1: 
        st.markdown("### ŸšOE st.markdown( f"** 
        {money(PLOW_RATE)} ﻿เธฒเธ— / เน “เธนˆ**”) 
        st.metric(" ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿”, f"{money(plow_cost)} ﻿เธฒเธ—") 
    กับ s2: 
        st.markdown("### โš™๏ธ ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿ ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿ ﻿﻿﻿﻿﻿﻿﻿﻿﻿ st.markdown(f"**{money(MILL_RATE )} ﻿﻿﻿﻿﻿— 
        / 
        เน﻿﻿﻿﻿﻿**”) st.metric 
    ( 
        " ﻿﻿﻿﻿﻿﻿﻿﻿﻿ st.metric( 
        " class="total-box"> 
            <div class="total-title">๐Ÿ'ฐ ประเทศไทย—</div> <div>เนน
            ธี– {money(plow_cost)} 
            + เธียฑัณฑ์เธ™ {money(mill_cost)}</div> 
        </div> 
        """, 
        unsafe_allow_html=True, 
    ) 
    st.divider() 
    if st.button( 
        "๐Ÿ'พเธฑ™เธ— เธียเนเธีย › เธฅเธ™เธ‰", 
        type="primary", 
        use_container_width=True, 
    ): 
        record = { 
            "เน€เธ‰เธฑเธ‚เธ่เธ™เธฒ": เจ้าของ หรือ "-", 
            "เฮิร์ทเน‰เธ™เธ— เธˆ เอช•เธซ.ก..": รอบ(area_m2, 2), 
            "เฮิร์ทเน‰เธ™เธ— เธˆ": ( 
                f"{rai} เนนชเนˆ {ngan} เธฒเธ™ {wa} เธ•เธียเธ่เธฒเธนเธงเธฒ " 
                f"{remain_m2:.2f} เธ•เอชเอชก." 
            ), 
            "เฒ่าเนˆเธฒเน„เธ–": รอบ(plow_cost, 2), 
            "คลัทธ์เธียเธดีเธน™": รอบ(mill_cost, 2), 
            "มืีน” เธรงเฮก": รอบ(total_cost, 2),
            " เชียงเฒ่าขเน€เธซเธ•เธ": note หรือ "-", 
            "เฉลิมไทย”": list(st.session_state.points), 
        } 
        st.session_state.saved_plots.append(record) 
        st.success(" เธซเธ™เธ—เธียเธ่เธ่เน‰เธ อังกฤษ













ถ้า st.session_state.saved_plots: 
    st.divider() 
    st.subheader("๐Ÿ“‹ เน ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿— ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿ ﻿﻿﻿﻿﻿﻿﻿﻿ st.subheader("๐Ÿ“‹ เน

    for “ดัชนี”, รายการในรูปแบบ enumerate( 
        Reversed(st.session_state.saved_plots), 
        1, 
    ): 
        number = len(st.session_state.saved_plots) - index + 1 

        with st.expander( 
            f"เน ﻿﻿﻿﻿﻿﻿﻿— ﻿﻿ {number} โ€ข {item['เน€เธˆเน‰เธ่﻿﻿﻿﻿﻿﻿﻿﻿']} โ€ข " 
            f"{money(item['เธอร์คชึ” เธรงเฮก'])} เธฒเธ—" 
        ): 
            st.write(f"**เน€เธˆเน‰ัฒเธ‚เธ‰เธ™เธ™เธฒเธ:** {item['เน€เธˆเน‰พลัสฑ์เธลเธ™เธฒ']}") st.write 
            (f"** เธเน‰เธ™เธ— ชันเนˆ:** {item['฿เธเน‰เธ™เธ— เธˆ']}") 
            st.write(f"** ﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿–:** {money(item['﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿)} ﻿เธฒเธ—") st.write(f"**
            ** {money(item[' ﻿﻿﻿﻿﻿﻿﻿﻿﻿)} ﻿﻿﻿﻿﻿ st.write(f"** เธฒเธ—") 
            st.write(f"** ประเทศไทย” ประเทศไทย:** {money(item['ธกสธัน” เชียงเฮง'])} ชัฒธัน—") 
            st.write(f"** ประเทศไทย ประเทศไทย:** {item['ไทยเฒ่าไทยขเน€เธ•เธ']}") 

st.divider() 
st.caption( 
    "Ta App โ€ขเธซเธียเธ่ย์” GPS เน€เธียเนเธ™เธียเนเธ‰เธ™h› เธียเธ่เธฒเธ“ " 
    " เนียรชช•สโลว์เนียืัน™เนีย€เธ€เธ€เธ•เธียเธเธเธเนเธˆเธ่™เนเอฟเฟียสเน‰เธฒเธ™" 
)
