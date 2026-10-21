
import base64
import calendar
import json
import mimetypes
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# SYNAPSE MYSTIC NUMBER
# Date Calculator + Lunar Phase + Random Music Player
# =========================================================

APP_DIR = Path(__file__).resolve().parent
LOGO_FILE = APP_DIR / "logo1.png"

MUSIC_EXTENSIONS = {
    ".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"
}

THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
    "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

THAI_WEEKDAYS = [
    "วันจันทร์", "วันอังคาร", "วันพุธ",
    "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"
]

THAI_DIGITS = str.maketrans("0123456789", "๐๑๒๓๔๕๖๗๘๙")


# ------------------------- PAGE ---------------------------

st.set_page_config(
    page_title="SYNAPSE MYSTIC NUMBER",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# -------------------------- STYLE -------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 5%, #152746 0%, transparent 32%),
            radial-gradient(circle at 90% 15%, #351c30 0%, transparent 30%),
            linear-gradient(150deg, #050811 0%, #0a1020 55%, #08070e 100%);
        color: #f4f6ff;
    }

    h1, h2, h3 {
        color: #e8c76a !important;
    }

    p, label, .stMarkdown, .stCaption {
        color: #e2e8f7;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #111b2e, #171326);
        border: 1px solid #334b70;
        padding: 16px;
        border-radius: 15px;
    }

    [data-testid="stMetricLabel"] {
        color: #b7c8e9 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f3d57c !important;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border: 1px solid #d7b65e;
        border-radius: 12px;
        background: linear-gradient(120deg, #172844, #29172c);
        color: #fff2bd;
        min-height: 42px;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        border-color: #fff0a3;
        color: white;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #10182a;
        color: white;
    }

    .hero {
        text-align: center;
        padding: 20px 8px 14px 8px;
        border: 1px solid #3c4163;
        border-radius: 20px;
        background: linear-gradient(
            120deg,
            rgba(12, 26, 48, .95),
            rgba(34, 16, 38, .95)
        );
        margin-bottom: 20px;
        box-shadow: 0 0 28px rgba(48, 120, 220, .10);
    }

    .hero-title {
        font-size: clamp(24px, 5vw, 38px);
        font-weight: 900;
        letter-spacing: 2px;
        color: #f1d17b;
        text-shadow: 0 0 15px rgba(80, 155, 255, .30);
    }

    .hero-subtitle {
        color: #b9c9e9;
        font-size: 14px;
    }

    .result-card {
        background: rgba(15, 24, 42, .92);
        border: 1px solid #35486a;
        border-radius: 16px;
        padding: 16px;
        margin: 8px 0;
    }

    .result-label {
        color: #aebfdf;
        font-size: 13px;
        margin-bottom: 6px;
    }

    .result-value {
        color: #f2d27a;
        font-size: 23px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .small-note {
        color: #a8b4cc;
        font-size: 12px;
    }

    hr {
        border-color: #303c58;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------- HELPERS ------------------------

def thai_digits(value):
    """Convert digits to Thai numerals."""
    return str(value).translate(THAI_DIGITS)


def digit_sum(value):
    """Sum all digits in a value."""
    digits = [int(ch) for ch in str(value) if ch.isdigit()]
    return sum(digits)


def reduce_to_one_digit(value):
    """Repeatedly add digits until the result is one digit."""
    n = abs(int(value))
    while n >= 10:
        n = sum(int(ch) for ch in str(n))
    return n


def thai_weekday(d):
    """Python weekday: Monday=0 through Sunday=6."""
    return THAI_WEEKDAYS[d.weekday()]


def western_zodiac(d):
    """Approximate Western zodiac sign by month and day."""
    m, day = d.month, d.day

    if (m == 3 and day >= 21) or (m == 4 and day <= 19):
        return "ราศีเมษ"
    if (m == 4 and day >= 20) or (m == 5 and day <= 20):
        return "ราศีพฤษภ"
    if (m == 5 and day >= 21) or (m == 6 and day <= 20):
        return "ราศีเมถุน"
    if (m == 6 and day >= 21) or (m == 7 and day <= 22):
        return "ราศีกรกฎ"
    if (m == 7 and day >= 23) or (m == 8 and day <= 22):
        return "ราศีสิงห์"
    if (m == 8 and day >= 23) or (m == 9 and day <= 22):
        return "ราศีกันย์"
    if (m == 9 and day >= 23) or (m == 10 and day <= 22):
        return "ราศีตุลย์"
    if (m == 10 and day >= 23) or (m == 11 and day <= 21):
        return "ราศีพิจิก"
    if (m == 11 and day >= 22) or (m == 12 and day <= 21):
        return "ราศีธนู"
    if (m == 12 and day >= 22) or (m == 1 and day <= 19):
        return "ราศีมังกร"
    if (m == 1 and day >= 20) or (m == 2 and day <= 18):
        return "ราศีกุมภ์"
    return "ราศีมีน"


def zodiac_year(d):
    """Approximate Thai/Chinese animal year based on Gregorian year."""
    animals = [
        "ปีชวด (หนู)",
        "ปีฉลู (วัว)",
        "ปีขาล (เสือ)",
        "ปีเถาะ (กระต่าย)",
        "ปีมะโรง (มังกร)",
        "ปีมะเส็ง (งู)",
        "ปีมะเมีย (ม้า)",
        "ปีมะแม (แพะ)",
        "ปีวอก (ลิง)",
        "ปีระกา (ไก่)",
        "ปีจอ (สุนัข)",
        "ปีกุน (หมู)"
    ]

    # This is a Gregorian-year approximation, not a traditional
    # Thai lunar new-year boundary calculation.
    return animals[(d.year - 2020) % 12]


def approximate_moon_phase(d):
    """
    Estimate lunar age using a known approximate new-moon reference.
    This is astronomical approximation, not an official Thai lunar calendar.
    """
    known_new_moon = datetime(2000, 1, 6, 18, 14)
    target = datetime(d.year, d.month, d.day, 12, 0)

    synodic_month = 29.530588853
    elapsed_days = (target - known_new_moon).total_seconds() / 86400
    age = elapsed_days % synodic_month
    phase_fraction = age / synodic_month

    illumination = (1 - __import__("math").cos(
        2 * __import__("math").pi * phase_fraction
    )) / 2 * 100

    if age < 1.85 or age >= 27.68:
        phase = "ใกล้วันเดือนดับ"
        lunar_side = "ใกล้เดือนดับ"
    elif age < 5.54:
        phase = "จันทร์เสี้ยวข้างขึ้น"
        lunar_side = "ช่วงข้างขึ้น"
    elif age < 9.22:
        phase = "ใกล้ครึ่งดวงข้างขึ้น"
        lunar_side = "ช่วงข้างขึ้น"
    elif age < 12.91:
        phase = "จันทร์เกือบเต็มดวงข้างขึ้น"
        lunar_side = "ช่วงข้างขึ้น"
    elif age < 16.61:
        phase = "ใกล้วันเพ็ญ"
        lunar_side = "ใกล้วันเพ็ญ"
    elif age < 20.30:
        phase = "จันทร์เกือบเต็มดวงข้างแรม"
        lunar_side = "ช่วงข้างแรม"
    elif age < 23.99:
        phase = "ใกล้ครึ่งดวงข้างแรม"
        lunar_side = "ช่วงข้างแรม"
    elif age < 27.68:
        phase = "จันทร์เสี้ยวข้างแรม"
        lunar_side = "ช่วงข้างแรม"
    else:
        phase = "ใกล้วันเดือนดับ"
        lunar_side = "ใกล้เดือนดับ"

    return {
        "age": age,
        "illumination": illumination,
        "phase": phase,
        "side": lunar_side,
    }


def list_music_files():
    """Find music files beside this Python file."""
    if not APP_DIR.exists():
        return []

    return sorted(
        [
            p for p in APP_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in MUSIC_EXTENSIONS
        ],
        key=lambda p: p.name.lower()
    )


def render_music_player():
    """
    Render a self-contained browser music player.
    Randomizes the starting track and shuffles subsequent tracks.
    Audio is embedded as data URLs, so no local filesystem URL is exposed.
    """
    music_files = list_music_files()

    st.subheader("🎵 เครื่องเล่นเพลงสุ่มอัตโนมัติ")
    st.caption(
        "วางไฟล์เพลงไว้ในโฟลเดอร์เดียวกับ Ta_app.py "
        "รองรับ MP3, WAV, OGG, M4A, AAC และ FLAC "
        "ทั้งนี้บางเบราว์เซอร์อาจไม่รองรับทุกชนิดไฟล์"
    )

    if not music_files:
        st.info(
            "ยังไม่พบไฟล์เพลงครับ ให้อัปโหลดไฟล์เพลง เช่น song1.mp3 "
            "ไว้ในโฟลเดอร์เดียวกับ Ta_app.py แล้วเปิดแอปใหม่"
        )
        return

    # Embed the files into the HTML component.
    # Large music files increase memory use and initial loading time.
    tracks = []

    for path in music_files:
        try:
            mime_type, _ = mimetypes.guess_type(path.name)
            if not mime_type:
                mime_type = "audio/mpeg"

            raw_bytes = path.read_bytes()
            encoded = base64.b64encode(raw_bytes).decode("ascii")

            tracks.append({
                "name": path.name,
                "mime": mime_type,
                "data": encoded,
            })
        except OSError:
            continue

    if not tracks:
        st.warning("อ่านไฟล์เพลงไม่สำเร็จ กรุณาตรวจสอบสิทธิ์การเข้าถึงไฟล์")
        return

    tracks_json = json.dumps(tracks, ensure_ascii=True)

    player_html = r"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body {
        margin: 0;
        padding: 8px;
        background: transparent;
        color: #f3d47d;
        font-family: Arial, sans-serif;
      }
      .player {
        padding: 16px;
        border: 1px solid #3d5077;
        border-radius: 16px;
        background: linear-gradient(135deg, #111b2e, #25172d);
      }
      .title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
        overflow-wrap: anywhere;
      }
      .status {
        font-size: 12px;
        color: #b8c8e5;
        margin-bottom: 12px;
      }
      audio {
        width: 100%;
        margin: 5px 0 12px 0;
      }
      button {
        background: #172b49;
        color: #ffedb0;
        border: 1px solid #d8ba68;
        border-radius: 9px;
        padding: 10px 14px;
        margin: 3px;
        cursor: pointer;
      }
      button:active {
        background: #30496d;
      }
      .note {
        color: #aebcda;
        font-size: 11px;
        line-height: 1.5;
        margin-top: 10px;
      }
    </style>
    </head>
    <body>
      <div class="player">
        <div class="title">🎧 SYNAPSE MUSIC PLAYER</div>
        <div id="trackName" class="status">กำลังเตรียมเพลง...</div>
        <audio id="audio" controls autoplay playsinline></audio>
        <div>
          <button id="playBtn">▶ เล่นเพลง</button>
          <button id="pauseBtn">⏸ หยุดชั่วคราว</button>
          <button id="nextBtn">⏭ สุ่มเพลงถัดไป</button>
        </div>
        <div id="status" class="status"></div>
        <div class="note">
          ระบบสุ่มเพลงเริ่มต้นและสุ่มเพลงถัดไปโดยอัตโนมัติ
          หากเพลงไม่เริ่มเอง ให้แตะปุ่มเล่นเพลงหนึ่งครั้ง
        </div>
      </div>

      <script>
      const tracks = TRACKS_PLACEHOLDER;
      const audio = document.getElementById("audio");
      const trackName = document.getElementById("trackName");
      const statusText = document.getElementById("status");
      const playBtn = document.getElementById("playBtn");
      const pauseBtn = document.getElementById("pauseBtn");
      const nextBtn = document.getElementById("nextBtn");

      let currentIndex = -1;
      let shuffledOrder = [];
      let orderPosition = 0;

      function shuffleArray(arr) {
        const result = arr.slice();
        for (let i = result.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [result[i], result[j]] = [result[j], result[i]];
        }
        return result;
      }

      function makeNewOrder() {
        shuffledOrder = shuffleArray(
          tracks.map((_, index) => index)
        );

        // Avoid repeating the last song immediately, when possible.
        if (shuffledOrder.length > 1 &&
            shuffledOrder[0] === currentIndex) {
          [shuffledOrder[0], shuffledOrder[1]] =
          [shuffledOrder[1], shuffledOrder[0]];
        }
        orderPosition = 0;
      }

      function nextIndex() {
        if (tracks.length === 1) return 0;

        if (orderPosition >= shuffledOrder.length) {
          makeNewOrder();
        }

        const result = shuffledOrder[orderPosition];
        orderPosition += 1;
        return result;
      }

      async function playTrack(index, tryAutoplay = true) {
        if (!tracks.length) return;

        currentIndex = index;
        const track = tracks[index];

        trackName.textContent =
          "เพลง: " + track.name +
          " (" + (index + 1) + "/" + tracks.length + ")";

        audio.src = "data:" + track.mime + ";base64," + track.data;
        audio.load();

        if (tryAutoplay) {
          try {
            await audio.play();
            statusText.textContent = "กำลังเล่นเพลง";
          } catch (err) {
            statusText.textContent =
              "เบราว์เซอร์บล็อกการเล่นอัตโนมัติ กรุณาแตะ ▶ เล่นเพลง";
          }
        }
      }

      function playNext() {
        if (!tracks.length) return;
        if (orderPosition >= shuffledOrder.length) {
          makeNewOrder();
        }
        const index = nextIndex();
        playTrack(index, true);
      }

      playBtn.addEventListener("click", async () => {
        try {
          if (audio.src && audio.paused) {
            await audio.play();
          } else if (!audio.src) {
            playTrack(nextIndex(), true);
          }
          statusText.textContent = "กำลังเล่นเพลง";
        } catch (err) {
          statusText.textContent = "ไม่สามารถเล่นได้ กรุณาตรวจสอบชนิดไฟล์เพลง";
        }
      });

      pauseBtn.addEventListener("click", () => {
        audio.pause();
        statusText.textContent = "หยุดเพลงชั่วคราว";
      });

      nextBtn.addEventListener("click", playNext);

      audio.addEventListener("ended", playNext);

      audio.addEventListener("error", () => {
        statusText.textContent =
          "ไฟล์นี้เล่นไม่ได้ในเบราว์เซอร์ ลองใช้ MP3 หรือ WAV";
      });

      if (tracks.length > 0) {
        makeNewOrder();
        playTrack(nextIndex(), true);
      }
      </script>
    </body>
    </html>
    """

    player_html = player_html.replace(
        "TRACKS_PLACEHOLDER",
        tracks_json
    )

    components.html(
        player_html,
        height=275,
        scrolling=False
    )


# ------------------------- HEADER -------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">✦ SYNAPSE MYSTIC NUMBER ✦</div>
        <div class="hero-subtitle">
            DATE CALCULATOR • LUNAR PHASE • NUMBER SYSTEM • MUSIC
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if LOGO_FILE.exists():
    try:
        st.image(str(LOGO_FILE), width=140)
    except Exception:
        pass


# --------------------- DATE INPUT -------------------------

st.header("📅 คำนวณวันที่และตัวเลข")

today = date.today()
current_be_year = today.year + 543

col1, col2, col3 = st.columns(3)

with col1:
    selected_day = st.selectbox(
        "วันที่",
        options=list(range(1, 32)),
        index=today.day - 1
    )

with col2:
    selected_month = st.selectbox(
        "เดือน",
        options=list(range(1, 13)),
        format_func=lambda m: THAI_MONTHS[m - 1],
        index=today.month - 1
    )

with col3:
    year_options = list(
        range(current_be_year - 120, current_be_year + 11)
    )
    selected_be_year = st.selectbox(
        "ปี พ.ศ.",
        options=year_options,
        index=year_options.index(current_be_year)
    )

selected_year = selected_be_year - 543

# Validate the chosen day for the selected month/year.
days_in_month = calendar.monthrange(
    selected_year,
    selected_month
)[1]

if selected_day > days_in_month:
    st.error(
        f"เดือน{THAI_MONTHS[selected_month - 1]} "
        f"ปี พ.ศ. {selected_be_year} มีเพียง {days_in_month} วัน "
        "กรุณาเลือกวันที่ใหม่"
    )
    selected_date = None
else:
    selected_date = date(
        selected_year,
        selected_month,
        selected_day
    )

if selected_date:
    d = selected_date
    date_string = d.strftime("%Y%m%d")
    date_digit_total = digit_sum(date_string)
    date_reduced = reduce_to_one_digit(date_digit_total)
    day_digit_total = digit_sum(d.day)
    year_digit_total = digit_sum(d.year)
    day_of_year = d.timetuple().tm_yday
    iso_week = d.isocalendar().week

    moon = approximate_moon_phase(d)

    st.divider()
    st.subheader("✨ ผลการคำนวณ")

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">วันที่ที่เลือก</div>
            <div class="result-value">
                {thai_weekday(d)} {d.day} {THAI_MONTHS[d.month - 1]}
                พ.ศ. {d.year + 543}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("ผลรวมตัวเลขวันที่", date_digit_total)
    with m2:
        st.metric("เลขสรุป 1 หลัก", date_reduced)
    with m3:
        st.metric("เลขวันที่", day_digit_total)

    m4, m5, m6 = st.columns(3)

    with m4:
        st.metric("วันที่ลำดับที่ของปี", day_of_year)
    with m5:
        st.metric("สัปดาห์ ISO", iso_week)
    with m6:
        st.metric("ผลรวมตัวเลขปี ค.ศ.", year_digit_total)

    st.divider()
    st.subheader("🌙 ข้างขึ้น–ข้างแรมโดยประมาณ")

    l1, l2, l3 = st.columns(3)

    with l1:
        st.metric("ช่วงดวงจันทร์", moon["side"])
    with l2:
        st.metric("อายุจันทร์โดยประมาณ", f'{moon["age"]:.1f} วัน')
    with l3:
        st.metric("พื้นที่สว่างโดยประมาณ", f'{moon["illumination"]:.0f}%')

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">ลักษณะดวงจันทร์โดยประมาณ</div>
            <div class="result-value">{moon["phase"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "หมายเหตุ: ระบบนี้ประมาณอายุและความสว่างของดวงจันทร์จากรอบดาราศาสตร์ "
        "ไม่ได้คำนวณวันขึ้น/แรมและเลขค่ำตามปฏิทินจันทรคติไทยอย่างเป็นทางการ"
    )

    st.divider()
    st.subheader("♈ ข้อมูลปีและราศี")

    z1, z2 = st.columns(2)

    with z1:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">ราศีตะวันตกโดยประมาณ</div>
                <div class="result-value">{western_zodiac(d)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with z2:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">ปีนักษัตรโดยประมาณ</div>
                <div class="result-value">{zodiac_year(d)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.caption(
        "หมายเหตุ: ปีนักษัตรในเวอร์ชันนี้อิงปี ค.ศ. แบบง่าย "
        "ไม่ได้ตรวจเส้นแบ่งปีใหม่ตามปฏิทินจันทรคติ"
    )

    st.divider()
    st.subheader("🔢 รายละเอียดตัวเลขทั้งหมด")

    digit_details = {
        "วันที่": d.day,
        "เดือน": d.month,
        "ปี ค.ศ.": d.year,
        "ปี พ.ศ.": d.year + 543,
        "วันที่แบบ YYYYMMDD": date_string,
        "ผลรวมเลขวันที่ทั้งหมด": date_digit_total,
        "เลขสรุป 1 หลัก": date_reduced,
        "ผลรวมเลขวัน": day_digit_total,
        "ผลรวมเลขปี ค.ศ.": year_digit_total,
        "ลำดับวันที่ของปี": day_of_year,
        "สัปดาห์ ISO": iso_week,
        "อายุจันทร์โดยประมาณ (วัน)": round(moon["age"], 2),
        "ความสว่างดวงจันทร์โดยประมาณ (%)": round(
            moon["illumination"], 1
        ),
        "ช่วงดวงจันทร์": moon["phase"],
        "ราศี": western_zodiac(d),
        "ปีนักษัตรโดยประมาณ": zodiac_year(d),
        "วันในสัปดาห์": thai_weekday(d),
    }
    for label, value in digit_details.items():
        st.write(f"**{label}:** {value}")

    # Prepare a simple CSV report.
    csv_lines = ["รายการ,ผลลัพธ์"]
    for label, value in digit_details.items():
        safe_label = str(label).replace('"', '""')
        safe_value = str(value).replace('"', '""')
        csv_lines.append(f'"{safe_label}","{safe_value}"')
    csv_content = "\ufeff" + "\n".join(csv_lines)

    st.download_button(
        label="⬇️ ดาวน์โหลดผลลัพธ์เป็น CSV",
        data=csv_content.encode("utf-8"),
        file_name=f"mystic_number_{d.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
# ----------------------- MUSIC PLAYER --------------------

st.divider()
render_music_player()


# -------------------------- FOOTER -------------------------

st.divider()
st.markdown(
    """
    <div style="text-align:center; color:#8998b8; font-size:12px;">
        SYNAPSE MYSTIC NUMBER<br>
        Date Calculator • Lunar Phase Estimate • Random Music Player
    </div>
    """,
    unsafe_allow_html=True
)
