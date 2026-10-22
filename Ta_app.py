ฃ
import base64
import calendar
import itertools
import json
import mimetypes
import random
import math
from datetime import date, datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


# ==========================================================
# SYNAPSE MYSTIC NUMBER
# ==========================================================

APP_DIR = Path(__file__).resolve().parent
MUSIC_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"}

THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
    "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

# ตามกติกาที่กำหนด: วันจันทร์ = 1
DAY_NUMBERS = {
    0: 1,  # Monday
    1: 2,  # Tuesday
    2: 3,  # Wednesday
    3: 4,  # Thursday
    4: 5,  # Friday
    5: 6,  # Saturday
    6: 7,  # Sunday
}

THAI_WEEKDAYS = [
    "วันจันทร์", "วันอังคาร", "วันพุธ",
    "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"
]

st.set_page_config(
    page_title="SYNAPSE MYSTIC NUMBER",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# NEON STYLE
# ==========================================================

st.markdown("""
<style>
:root {
    --syn-bg: #050814;
    --syn-panel: #0b1428;
    --syn-blue: #63f4ff;
    --syn-gold: #ffe66d;
    --syn-red: #d94a5a;
    --syn-silver: #e8edf5;
    --syn-muted: #a8b7d9;
}
.stApp {
    background:
      radial-gradient(ellipse at 10% 0%, #102c45 0%, transparent 36%),
      radial-gradient(ellipse at 90% 15%, #351522 0%, transparent 32%),
      linear-gradient(145deg, #050814, #080d1b 55%, #120b16);
    color: var(--syn-silver);
}
header[data-testid="stHeader"] { background: rgba(0,0,0,0); }
h1, h2, h3 {
    color: var(--syn-blue) !important;
    text-shadow: 0 0 10px #63f4ff55;
}
p, label, .stMarkdown { color: #e1eaff; }
.hero {
    text-align: center;
    padding: 24px 10px;
    border-radius: 22px;
    border: 1px solid var(--syn-gold);
    background: linear-gradient(130deg, #091629, #21121c, #0a1728);
    box-shadow: 0 0 18px #63f4ff20, inset 0 0 20px #ffe66d10;
    margin-bottom: 18px;
}
.hero-title {
    font-size: clamp(24px, 5vw, 40px);
    font-weight: 900;
    letter-spacing: 2px;
    color: var(--syn-gold);
    text-shadow: 0 0 8px #ffe66d66, 0 0 22px #63f4ff55;
}
.hero-sub {
    font-size: 12px;
    letter-spacing: 2px;
    color: var(--syn-blue);
    margin-top: 8px;
}
.neon-card {
    background: linear-gradient(135deg, #0a1426, #17131d);
    border: 1px solid #63f4ff80;
    border-radius: 16px;
    padding: 14px;
    margin: 8px 0;
    box-shadow: 0 0 10px #63f4ff18;
}
.neon-number {
    font-size: 27px;
    font-weight: 900;
    color: var(--syn-gold);
    text-shadow: 0 0 10px #ffe66d66;
    text-align: center;
}
.neon-label { color: var(--syn-blue); font-size: 13px; text-align: center; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0b1830, #20151e);
    border: 1px solid #ffe66d70;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 0 12px #63f4ff15;
}
[data-testid="stMetricValue"] { color: var(--syn-gold) !important; }
[data-testid="stMetricLabel"] { color: var(--syn-blue) !important; }
div.stButton > button, div.stDownloadButton > button {
    color: #f5f7ff;
    background: linear-gradient(110deg, #102d43, #38202a);
    border: 1px solid var(--syn-blue);
    border-radius: 12px;
    box-shadow: 0 0 8px #63f4ff25;
    transition: all .2s ease;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    border-color: var(--syn-gold);
    color: #ffffff;
    box-shadow: 0 0 14px #ffe66d40;
}
input, textarea, [data-baseweb="select"] > div {
    border-color: #63f4ff70 !important;
}
hr { border-color: #34465b; }
.small-note { color: var(--syn-muted); font-size: 12px; }
</style>
<div class="hero">
  <div class="hero-title">✦ SYNAPSE MYSTIC NUMBER ✦</div>
  <div class="hero-sub">DATE • LUNAR PHASE • NUMBER MATRIX • NEON MUSIC</div>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# CALCULATION FUNCTIONS
# ==========================================================

def last_digit(n):
    """ใช้ค่าสัมบูรณ์ แล้วเก็บเฉพาะหลักหน่วย"""
    return abs(int(n)) % 10


def lunar_estimate(d):
    """
    ประมาณอายุจันทร์จากรอบดวงจันทร์
    ไม่ใช่ปฏิทินจันทรคติไทยอย่างเป็นทางการ
    """
    reference = datetime(2000, 1, 6, 18, 14)
    target = datetime(d.year, d.month, d.day, 12, 0)
    cycle = 29.530588853
    age = ((target - reference).total_seconds() / 86400) % cycle

    # อายุจันทร์ 0-14.999 = ช่วงข้างขึ้นโดยประมาณ
    if age < cycle / 2:
        side = "ข้างขึ้น"
        lunar_day = min(15, max(1, int(age) + 1))
    else:
        side = "ข้างแรม"
        waning_age = age - cycle / 2
        lunar_day = min(15, max(1, int(waning_age) + 1))

    illumination = (1 - math.cos(2 * math.pi * age / cycle)) / 2 * 100

    if age < 1.85 or age >= 27.68:
        phase = "ใกล้เดือนดับ"
    elif age < 7.38:
        phase = "จันทร์เสี้ยวข้างขึ้น"
    elif age < 11.07:
        phase = "ใกล้ครึ่งดวงข้างขึ้น"
    elif age < 14.77:
        phase = "ใกล้วันเพ็ญ"
    elif age < 18.46:
        phase = "จันทร์เกือบเต็มดวงข้างแรม"
    elif age < 22.15:
        phase = "ใกล้ครึ่งดวงข้างแรม"
    else:
        phase = "จันทร์เสี้ยวข้างแรม"

    return {
        "age": round(age, 2),
        "side": side,
        "day": lunar_day,
        "phase": phase,
        "illumination": round(illumination, 1),
    }


def create_four_numbers(day_number, lunar_number):
    """
    เลขตั้งต้น 4 ตัว:
    1. เลขประจำวัน
    2. เลขประจำข้างขึ้น/ข้างแรม
    3. ผลบวกหลักหน่วย
    4. ผลต่างหลักหน่วย โดยใช้ค่าสัมบูรณ์
    """
    addition = last_digit(day_number + lunar_number)
    subtraction = last_digit(lunar_number - day_number)

    return [
        day_number,
        lunar_number,
        addition,
        subtraction,
    ]


def create_48_doors(numbers):
    """
    3 ตัว: permutation ของเลข 4 ตัว เลือก 3 ตำแหน่ง = 24 ชุด
    2 ตัว: เลือกคู่แบบไม่ซ้ำ แล้วสร้างเลขตรงและเลขกลับ
    """
    three_digit = [
        "".join(map(str, p))
        for p in itertools.permutations(numbers, 3)
    ]

    pairs = list(itertools.combinations(numbers, 2))
    two_digit_top = [
        "".join(map(str, pair))
        for pair in pairs
    ]
    two_digit_bottom = [
        value[::-1] for value in two_digit_top
    ]

    return three_digit, two_digit_top, two_digit_bottom


def find_music_files():
    if not APP_DIR.exists():
        return []
    return sorted(
        [
            p for p in APP_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in MUSIC_EXTENSIONS
        ],
        key=lambda p: p.name.lower()
    )


# ==========================================================
# DATE INPUT
# ==========================================================

st.header("📅 เลือกวันเพื่อคำนวณ")

today = date.today()
current_be = today.year + 543

c1, c2, c3 = st.columns(3)

with c1:
    day_value = st.selectbox(
        "วันที่",
        range(1, 32),
        index=today.day - 1
    )

with c2:
    month_value = st.selectbox(
        "เดือน",
        range(1, 13),
        index=today.month - 1,
        format_func=lambda x: THAI_MONTHS[x - 1]
    )

with c3:
    year_options = list(range(current_be - 100, current_be + 11))
    year_be = st.selectbox(
        "ปี พ.ศ.",
        year_options,
        index=year_options.index(current_be)
    )

year_ad = year_be - 543
max_day = calendar.monthrange(year_ad, month_value)[1]

if day_value > max_day:
    st.error(f"เดือนนี้มีเพียง {max_day} วัน กรุณาเลือกวันที่ใหม่")
    chosen_date = None
else:
    chosen_date = date(year_ad, month_value, day_value)


# ==========================================================
# LUNAR NUMBER INPUT
# ==========================================================

if chosen_date:
    d = chosen_date
    weekday_name = THAI_WEEKDAYS[d.weekday()]
    day_number = DAY_NUMBERS[d.weekday()]
    lunar = lunar_estimate(d)

    st.divider()
    st.header("🌙 กำหนดเลขข้างขึ้น–ข้างแรม")

    st.caption(
        "ระบบเสนอค่าเริ่มต้นจากการประมาณดวงจันทร์ "
        "คุณสามารถเลือกช่วงและเลขค่ำเองเพื่อให้ตรงกับกติกาที่ใช้"
    )

    l1, l2 = st.columns(2)

    with l1:
        lunar_side = st.selectbox(
            "ช่วงจันทรคติ",
            ["ข้างขึ้น", "ข้างแรม"],
            index=0 if lunar["side"] == "ข้างขึ้น" else 1
        )

    with l2:
        lunar_number = st.selectbox(
            "เลขค่ำที่ใช้คำนวณ (1–15)",
            range(1, 16),
            index=lunar["day"] - 1
        )

    st.markdown(
        f"""
        <div class="neon-card">
          <div class="neon-label">วันที่เลือก</div>
          <div class="neon-number">{weekday_name}</div>
          <div class="neon-label">
            {d.day} {THAI_MONTHS[d.month - 1]} พ.ศ. {d.year + 543}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)
    a.metric("เลขประจำวัน", day_number)
    b.metric("เลขข้างขึ้น/ข้างแรม", lunar_number)
    c.metric("ความสว่างจันทร์โดยประมาณ", f'{lunar["illumination"]}%')

    st.caption(
        f"อายุจันทร์โดยประมาณ {lunar['age']} วัน · {lunar['phase']}. "
        "การประมาณนี้ไม่ใช่การยืนยันวันค่ำตามปฏิทินไทยอย่างเป็นทางการ"
    )

    # ------------------------------------------------------
    # FOUR SEED NUMBERS
    # ------------------------------------------------------

    st.divider()
    st.header("🔢 สูตรคำนวณเลขตั้งต้น 4 ตัว")

    four_numbers = create_four_numbers(day_number, lunar_number)

    plus_result = day_number + lunar_number
    minus_result = lunar_number - day_number

    st.markdown(
        f"""
        <div class="neon-card">
          <div class="neon-label">เลขประจำวัน</div>
          <div class="neon-number">{day_number}</div>
          <div class="neon-label">เลข {lunar_side}</div>
          <div class="neon-number">{lunar_number}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    f1, f2 = st.columns(2)

    with f1:
        st.markdown("### ➕ สูตรบวก")
        st.write(f"{day_number} + {lunar_number} = {plus_result}")
        st.write(f"เก็บหลักหน่วย: **{last_digit(plus_result)}**")

    with f2:
        st.markdown("### ➖ สูตรลบ")
        st.write(f"{lunar_number} − {day_number} = {minus_result}")
        st.write(f"ค่าสัมบูรณ์หลักหน่วย: **{last_digit(minus_result)}**")

    st.markdown("### ✨ เลขตั้งต้น 4 ตัว")

    seed_cols = st.columns(4)
    for col, number, label in zip(
        seed_cols,
        four_numbers,
        ["เลขวัน", "เลขค่ำ", "เลขบวก", "เลขลบ"]
    ):
        with col:
            st.markdown(
                f"""
                <div class="neon-card">
                  <div class="neon-label">{label}</div>
                  <div class="neon-number">{number}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    if len(set(four_numbers)) != 4:
        st.warning(
            "เลขตั้งต้นมีเลขซ้ำกัน ระบบจะแสดงชุดที่เกิดจากตำแหน่งทั้งหมด "
            "แต่บางชุดอาจมีตัวเลขซ้ำกัน"
        )

    # ------------------------------------------------------
    # 48 DOORS
    # ------------------------------------------------------

    three_numbers, two_top, two_bottom = create_48_doors(four_numbers)

    st.divider()
    st.header("🚪 ผลลัพธ์ชุดตัวเลข")

    st.markdown(
        "### 🔷 3 ตัวบน — 24 ชุด"
    )
    st.caption("เรียงสลับตำแหน่งเลขตั้งต้น 4 ตัว เลือกครั้งละ 3 ตำแหน่ง")

    for start in range(0, len(three_numbers), 6):
        cols = st.columns(6)
        for col, value in zip(cols, three_numbers[start:start + 6]):
            with col:
                st.markdown(
                    f"""
                    <div class="neon-card">
                      <div class="neon-number">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("### 🟣 2 ตัวบน–ล่าง — 12 รายการ")

    pair_rows = list(zip(two_top, two_bottom))
    for start in range(0, len(pair_rows), 3):
        cols = st.columns(3)
        for col, (top, bottom) in zip(cols, pair_rows[start:start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="neon-card">
                      <div class="neon-label">บน ↔ ล่าง</div>
                      <div class="neon-number">{top} ↔ {bottom}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.divider()
    st.header("💠 สรุปจำนวนประตู")

    s1, s2, s3 = st.columns(3)
    s1.metric("3 ตัวบน", f"{len(three_numbers)} ชุด")
    s2.metric("2 ตัวบน", f"{len(two_top)} ชุด")
    s3.metric("2 ตัวล่าง", f"{len(two_bottom)} ชุด")

    total_doors = len(three_numbers) + len(two_top) + len(two_bottom)
    st.metric("รวมทั้งหมด", f"{total_doors} รายการ")

    st.caption(
        "หากคิดรายการละ 1 บาท จะเป็นยอดสมมติ "
        f"{total_doors} บาท ไม่ใช่การรับประกันผลรางวัล"
    )

    # ------------------------------------------------------
    # EXPORT CSV
    # ------------------------------------------------------

    export_rows = [
        ["ประเภท", "เลข"],
    ]
    export_rows += [["3 ตัวบน", n] for n in three_numbers]
    export_rows += [["2 ตัวบน", n] for n in two_top]
    export_rows += [["2 ตัวล่าง", n] for n in two_bottom]

    csv_text = "\ufeff" + "\n".join(
        f'"{row[0]}","{row[1]}"' for row in export_rows
    )

    st.download_button(
        "⬇️ ดาวน์โหลดชุดตัวเลข CSV",
        data=csv_text.encode("utf-8"),
        file_name=f"numbers_{d.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )


# ==========================================================
# NEON MUSIC PLAYER
# ==========================================================

st.divider()
st.header("🎧 SYNAPSE NEON MUSIC PLAYER")

music_files = find_music_files()

st.caption(
    "ใส่ไฟล์เพลงไว้ในโฟลเดอร์เดียวกับ Ta_app.py "
    "รองรับ MP3, WAV, OGG, M4A, AAC และ FLAC"
)

if not music_files:
    st.warning(
        "ยังไม่พบไฟล์เพลง กรุณาเพิ่มไฟล์เพลงใน GitHub "
        "ไว้ในโฟลเดอร์เดียวกับ Ta_app.py"
    )
else:
    st.success(f"พบไฟล์เพลง {len(music_files)} ไฟล์")

    with st.expander("📜 รายชื่อเพลงทั้งหมด", expanded=True):
        for index, music_file in enumerate(music_files, start=1):
            st.write(f"{index}. 🎵 {music_file.name}")

    # Embed tracks in one iframe. This avoids replacing DOM nodes
    # in the parent Streamlit page.
    tracks = []

    for music_file in music_files:
        try:
            mime, _ = mimetypes.guess_type(music_file.name)
            if not mime or not mime.startswith("audio/"):
                mime = "audio/mpeg"

            encoded = base64.b64encode(
                music_file.read_bytes()
            ).decode("ascii")

            tracks.append({
                "name": music_file.name,
                "mime": mime,
                "data": encoded,
            })
        except OSError:
            st.warning(f"อ่านไฟล์ไม่สำเร็จ: {music_file.name}")

    if tracks:
        tracks_json = json.dumps(tracks, ensure_ascii=True)

        player_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
  margin: 0;
  padding: 8px;
  color: #e8edf5;
  background: transparent;
  font-family: Arial, sans-serif;
}
.player {
  border: 1px solid #ffe66d;
  border-radius: 18px;
  padding: 16px;
  background: linear-gradient(135deg,#091629,#21121c,#101b2b);
  box-shadow: 0 0 16px #63f4ff22;
}
.title {
  color: #63f4ff;
  font-size: 18px;
  font-weight: 900;
  text-shadow: 0 0 10px #63f4ff;
}
.track {
  color: #ffe66d;
  margin: 10px 0;
  overflow-wrap: anywhere;
}
.status {
  color: #a8b7d9;
  font-size: 12px;
  margin: 8px 0;
}
audio { width: 100%; margin: 8px 0; }
button {
  color: #fff;
  background: #102d43;
  border: 1px solid #63f4ff;
  border-radius: 10px;
  padding: 10px 12px;
  margin: 3px;
}
button:hover { background: #38202a; }
.list {
  margin-top: 12px;
  max-height: 155px;
  overflow-y: auto;
  border-top: 1px solid #34465b;
  padding-top: 8px;
}
.item {
  font-size: 12px;
  padding: 7px;
  color: #e8edf5;
  border-radius: 7px;
  overflow-wrap: anywhere;
}
.item.active {
  color: #ffe66d;
  background: #20151e;
  border: 1px solid #ffe66d;
}
.note {
  color: #a8b7d9;
  font-size: 11px;
  line-height: 1.5;
}
</style>
</head>
<body>
<div class="player">
  <div class="title">✦ NEON MUSIC ✦</div>
  <div id="track" class="track">กำลังเตรียมเพลง...</div>
  <audio id="audio" controls playsinline></audio>
  <div>
    <button id="play">▶ เล่น</button>
    <button id="pause">⏸ หยุด</button>
    <button id="next">⏭ เพลงถัดไป</button>
    <button id="shuffle">🔀 สุ่มใหม่</button>
  </div>
  <div id="status" class="status"></div>
  <div id="list" class="list"></div>
  <p class="note">
    เพลงจะสุ่มลำดับและเล่นเพลงถัดไปเมื่อเพลงจบ
    หากเบราว์เซอร์บล็อกการเล่นอัตโนมัติ ให้แตะปุ่ม ▶ เล่นก่อนหนึ่งครั้ง
  </p>
</div>
<script>
const tracks = TRACKS_PLACEHOLDER;
const audio = document.getElementById("audio");
const trackLabel = document.getElementById("track");
const statusLabel = document.getElementById("status");
const list = document.getElementById("list");

let order = [];
let position = 0;
let current = -1;
let userStarted = false;

function shuffleArray(array) {
  const result = array.slice();
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function makeOrder() {
  order = shuffleArray(tracks.map((_, i) => i));
  if (order.length > 1 && order[0] === current) {
    [order[0], order[1]] = [order[1], order[0]];
  }
  position = 0;
}

function renderList() {
  list.replaceChildren();
  tracks.forEach((item, i) => {
    const row = document.createElement("div");
    row.className = "item" + (i === current ? " active" : "");
    row.textContent = (i + 1) + ". " + item.name;
    row.addEventListener("click", () => {
      userStarted = true;
      playIndex(i, true);
    });
    list.appendChild(row);
  });
}

async function playIndex(index, attemptPlay) {
  if (!tracks.length) return;
  current = index;
  const item = tracks[index];

  trackLabel.textContent =
    "กำลังเลือก: " + item.name + " (" + (index + 1) + "/" + tracks.length + ")";

  audio.src = "data:" + item.mime + ";base64," + item.data;
  audio.load();
  renderList();

  if (attemptPlay) {
    try {
      await audio.play();
      statusLabel.textContent = "กำลังเล่นเพลง";
    } catch (error) {
      statusLabel.textContent =
        "เบราว์เซอร์ไม่อนุญาตให้เล่นอัตโนมัติ แตะปุ่มเล่น";
    }
  }
}

function nextTrack() {
  if (!tracks.length) return;
  if (position >= order.length) makeOrder();

  const index = order[position];
  position += 1;
  playIndex(index, userStarted);
}

document.getElementById("play").addEventListener("click", async () => {
  userStarted = true;
  try {
    if (current < 0) {
      nextTrack();
    } else {
      await audio.play();
      statusLabel.textContent = "กำลังเล่นเพลง";
    }
  } catch (error) {
    statusLabel.textContent = "เล่นไม่ได้ โปรดลองเลือกเพลงจากรายชื่อ";
  }
});

document.getElementById("pause").addEventListener("click", () => {
  audio.pause();
  statusLabel.textContent = "หยุดชั่วคราว";
});

document.getElementById("next").addEventListener("click", () => {
  userStarted = true;
  nextTrack();
});

document.getElementById("shuffle").addEventListener("click", () => {
  makeOrder();
  userStarted = true;
  nextTrack();
});

audio.addEventListener("ended", () => {
  nextTrack();
});

audio.addEventListener("error", () => {
  statusLabel.textContent =
    "ไฟล์นี้เล่นไม่ได้ ลองใช้ MP3 หรือ WAV แล้วตรวจสอบไฟล์อีกครั้ง";
});

makeOrder();
renderList(
