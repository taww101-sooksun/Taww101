
import streamlit as st
import base64

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="NEON MOON FORMULA",
    layout="centered"
)

# ---------------------------------
# LOAD LOGO
# ---------------------------------
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64("logo1.png")

# ---------------------------------
# MUSIC URL FROM GITHUB
# ---------------------------------
music_url = "https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/song.mp3"

# ---------------------------------
# CUSTOM CSS
# ---------------------------------
st.markdown("""
<style>

body {
    background-color: #050505;
}

.stApp {
    background:
    radial-gradient(circle at top,
    #111111 0%,
    #050505 60%);
    color: white;
}

/* TITLE */

.main-title{
    text-align:center;
    font-size:55px;
    font-weight:bold;

    color:#ffffff;

    text-shadow:
    0 0 10px #00ccff,
    0 0 20px #00ccff,
    0 0 40px #cc00ff,
    0 0 80px #00ff99;
}

/* SUBTITLE */

.sub-title{
    text-align:center;
    color:#cccccc;
    font-size:18px;
    margin-bottom:30px;
}

/* BOX */

.neon-box{

    border:2px solid #00ccff;
    border-radius:20px;

    padding:25px;

    background:rgba(0,0,0,0.4);

    box-shadow:
    0 0 10px #00ccff,
    0 0 20px #cc00ff,
    0 0 40px #00ff99;
}

/* RESULT */

.result-text{

    text-align:center;
    font-size:60px;
    font-weight:bold;

    color:#00ff99;

    text-shadow:
    0 0 10px #00ff99,
    0 0 20px #00ff99,
    0 0 40px #00ff99;
}

/* LABEL */

label{
    color:#00ccff !important;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------
# AUTO PLAY MUSIC
# ---------------------------------
st.markdown(f"""
<audio autoplay loop controls>
    <source src="{music_url}" type="audio/mp3">
</audio>
""", unsafe_allow_html=True)

# ---------------------------------
# LOGO
# ---------------------------------
st.markdown(f"""
<div style="text-align:center;">

<img src="data:image/png;base64,{logo_base64}"
width="220"

style="

filter:
drop-shadow(0 0 10px #00ccff)
drop-shadow(0 0 20px #cc00ff)
drop-shadow(0 0 40px #00ff99);

animation:pulse 2s infinite;
">

</div>
""", unsafe_allow_html=True)

# ---------------------------------
# TITLE
# ---------------------------------
st.markdown("""
<div class="main-title">
NEON MOON FORMULA
</div>

<div class="sub-title">
Cosmic Lunar Energy System
</div>
""", unsafe_allow_html=True)

# ---------------------------------
# INPUT SECTION
# ---------------------------------
st.markdown('<div class="neon-box">', unsafe_allow_html=True)

# DAY
day = st.selectbox(
    "DAY / วัน",
    [
        ("Sunday / อาทิตย์",1),
        ("Monday / จันทร์",2),
        ("Tuesday / อังคาร",3),
        ("Wednesday / พุธ",4),
        ("Thursday / พฤหัส",5),
        ("Friday / ศุกร์",6),
        ("Saturday / เสาร์",7)
    ],
    format_func=lambda x: x[0]
)[1]

# MONTH
month = st.slider(
    "MONTH / เดือน",
    1,
    12,
    1
)

# MOON PHASE
moon = st.slider(
    "MOON PHASE / ข้างขึ้น-แรม",
    1,
    29,
    1
)

# ZODIAC
zodiac = st.slider(
    "ZODIAC / นักษัตร",
    1,
    12,
    1
)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------
# CONSTANTS
# ---------------------------------
MOON_CYCLE = 29.530588
GOLDEN_RATIO = 1.618033988

# ---------------------------------
# FORMULA
# ---------------------------------
day_energy = day / 7
month_energy = month / 12
moon_energy = moon / MOON_CYCLE
zodiac_energy = zodiac / 12

total_energy = (
    day_energy
    +
    month_energy
    +
    moon_energy
    +
    zodiac_energy
)

final_result = total_energy * GOLDEN_RATIO

# ---------------------------------
# RESULT
# ---------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"""
<div class="neon-box">

<h2 style="
text-align:center;
color:#cc00ff;

text-shadow:
0 0 10px #cc00ff,
0 0 20px #cc00ff;
">

COSMIC ENERGY

</h2>

<div class="result-text">

{final_result:.6f}

</div>

</div>
""", unsafe_allow_html=True)

# ---------------------------------
# EXPLAIN SYSTEM
# ---------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""

# ความหมายของตัวเลข

## 7
รอบวันของโลก

## 12
รอบเดือนของปี
และ 12 นักษัตร

## 29.530588
รอบดวงจันทร์จริง

## 1.618
Golden Ratio
สัดส่วนสมดุลธรรมชาติ

""")

# ---------------------------------
# FOOTER
# ---------------------------------
st.markdown("""
<br><br>

<div style="
text-align:center;
color:#777777;
">

NEON MOON SYSTEM • CYBER COSMIC ENERGY

</div>
""", unsafe_allow_html=True)
