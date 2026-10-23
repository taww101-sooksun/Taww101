# -*- coding: utf-8 -*-
"""SYNAPSE MYSTIC NUMBER - transparent experimental astronomy/number analysis app."""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import date, datetime
from itertools import combinations
from pathlib import Path

import pandas as pd
import streamlit as st

APP_TITLE = "SYNAPSE MYSTIC NUMBER"
APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "synapse_mystic.db"

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
PLANET_TH = {
    "Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
    "Venus": "ดาวศุกร์", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัสบดี",
    "Saturn": "ดาวเสาร์", "Uranus": "ดาวยูเรนัส", "Neptune": "ดาวเนปจูน",
}
WEEKDAYS = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
MONTHS_TH = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
ZODIAC = ["ราศีเมษ", "ราศีพฤษภ", "ราศีเมถุน", "ราศีกรกฎ", "ราศีสิงห์", "ราศีกันย์", "ราศีตุล", "ราศีพิจิก", "ราศีธนู", "ราศีมังกร", "ราศีกุมภ์", "ราศีมีน"]
THAI_ANIMALS = ["ชวด (หนู)", "ฉลู (วัว)", "ขาล (เสือ)", "เถาะ (กระต่าย)", "มะโรง (มังกร)", "มะเส็ง (งู)", "มะเมีย (ม้า)", "มะแม (แพะ)", "วอก (ลิง)", "ระกา (ไก่)", "จอ (สุนัข)", "กุน (หมู)"]

st.set_page_config(page_title=APP_TITLE, page_icon="🌌", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.stApp{background:radial-gradient(circle at top right,#18295b 0%,#090f26 48%,#030711 100%);color:#f5f0dc}
[data-testid="stSidebar"]{background:#080d20;border-right:1px solid #c9a85c}
h1,h2,h3{color:#f1cf78!important} p,label,span{color:#e9e8f5}
.cosmic-card{background:rgba(19,29,62,.88);border:1px solid #a88c4d;border-radius:16px;padding:18px;margin-bottom:12px}
.big-number{color:#f1cf78;font-size:54px;font-weight:800;text-align:center;letter-spacing:7px}
div.stButton>button{background:linear-gradient(90deg,#b08b3d,#e8cd7c);color:#11162b;border:0;border-radius:10px;font-weight:bold;min-height:42px}
div[data-testid="stMetric"]{background:rgba(22,33,69,.85);border:1px solid #75643e;padding:12px;border-radius:12px}
</style>""", unsafe_allow_html=True)

# ---------------- Database ----------------
def db_connect():
    return sqlite3.connect(DB_PATH, timeout=20)

def init_db():
    with db_connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS calculations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, target_date TEXT NOT NULL,
            weekday TEXT NOT NULL, country TEXT NOT NULL, lottery TEXT NOT NULL, category TEXT NOT NULL,
            main_number TEXT NOT NULL, number_set TEXT NOT NULL, formula_notes TEXT NOT NULL,
            astronomy_status TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS lottery_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT, draw_date TEXT NOT NULL, country TEXT NOT NULL,
            lottery TEXT NOT NULL, category TEXT NOT NULL, number TEXT NOT NULL, source TEXT DEFAULT '')""")
        # Migrate databases created by earlier app versions, without deleting user data.
        cols = {r[1] for r in con.execute("PRAGMA table_info(calculations)").fetchall()}
        for name, typ, default in [
            ("country", "TEXT", "''"), ("lottery", "TEXT", "''"),
            ("category", "TEXT", "''"), ("main_number", "TEXT", "''"), ("number_set", "TEXT", "'[]'"),
            ("formula_notes", "TEXT", "''"), ("result_number", "TEXT", "''"),
            ("date_value", "INTEGER", "0"), ("weekday_value", "INTEGER", "0"),
            ("planet_value", "INTEGER", "0"), ("angle_value", "INTEGER", "0"),
            ("moon_value", "INTEGER", "0")
        ]:
            if name not in cols:
                con.execute(f"ALTER TABLE calculations ADD COLUMN {name} {typ} NOT NULL DEFAULT {default}")
        cols = {r[1] for r in con.execute("PRAGMA table_info(calculations)").fetchall()}
        # Keep legacy fields if present; new inserts only use common columns.

def read_sql(query, params=()):
    with db_connect() as con:
        return pd.read_sql_query(query, con, params=params)

def save_calculation(target_date, country, lottery, category, outputs, notes, status):
    try:
        vals = json.loads(notes)
    except Exception:
        vals = {}
    with db_connect() as con:
        # Include legacy required columns too, so older SQLite databases remain usable.
        con.execute("""INSERT INTO calculations(
            created_at,target_date,weekday,country,lottery,category,main_number,number_set,
            formula_notes,astronomy_status,result_number,date_value,weekday_value,planet_value,angle_value,moon_value
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (datetime.now().isoformat(timespec="seconds"), target_date.isoformat(), WEEKDAYS[target_date.weekday()],
         country, lottery, category, outputs[0], json.dumps(outputs), notes, status, outputs[0],
         int(vals.get("date_value",0)), int(vals.get("weekday_value",0)), int(vals.get("planet_value",0)),
         int(vals.get("angle_value",0)), int(vals.get("moon_value",0))))

init_db()

# ---------------- Calendar helpers ----------------
def digit_sum(n):
    return sum(int(c) for c in str(n) if c.isdigit())

def digital_root(n):
    n = abs(int(n))
    return 0 if n == 0 else 1 + (n - 1) % 9

def approximate_moon(target_date):
    """Approximate phase using a standard synodic-month reference; not Thai lunar-calendar authority."""
    known_new_moon = date(2000, 1, 6)
    age = ((target_date - known_new_moon).days % 29.530588853)
    illumination = (1 - math.cos(2 * math.pi * age / 29.530588853)) / 2
    if age < 1.85 or age >= 27.68:
        phase = "ใกล้วันเดือนดับ (โดยประมาณ)"
    elif age < 7.38:
        phase = "ข้างขึ้น (เสี้ยว)"
    elif age < 9.23:
        phase = "ใกล้วันขึ้น 8 ค่ำ (โดยประมาณ)"
    elif age < 13.84:
        phase = "ข้างขึ้น (เกือบเต็มดวง)"
    elif age < 15.69:
        phase = "ใกล้วันเพ็ญ (โดยประมาณ)"
    elif age < 22.15:
        phase = "ข้างแรม"
    elif age < 23.99:
        phase = "ใกล้วันแรม 8 ค่ำ (โดยประมาณ)"
    else:
        phase = "ข้างแรม (เสี้ยว)"
    return age, illumination * 100, phase

def zodiac_from_longitude(longitude):
    return ZODIAC[int((longitude % 360) // 30)]

def thai_zodiac_year(target_date):
    # Approximate calendar-year cycle anchored to 2024 = Dragon; Thai/Chinese zodiac year boundaries vary.
    idx = (target_date.year - 2024 + 4) % 12
    return THAI_ANIMALS[idx]

# ---------------- Astronomy ----------------
@st.cache_resource(show_spinner=False)
def load_ephemeris():
    from skyfield.api import load
    return load("de421.bsp"), load.timescale()

def calculate_positions(target_date):
    eph, ts = load_ephemeris()
    t = ts.utc(target_date.year, target_date.month, target_date.day, 12, 0, 0)
    earth = eph["earth"]
    body_keys = {"Sun":"sun", "Moon":"moon", "Mercury":"mercury", "Venus":"venus", "Mars":"mars", "Jupiter":"jupiter barycenter", "Saturn":"saturn barycenter", "Uranus":"uranus barycenter", "Neptune":"neptune barycenter"}
    positions = {}
    for name, key in body_keys.items():
        apparent = earth.at(t).observe(eph[key]).apparent()
        _, lon, _ = apparent.ecliptic_latlon(epoch="date")
        positions[name] = float(lon.degrees) % 360
    return positions

def angular_sep(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)

def make_angle_table(pos):
    rows = []
    for a, b in combinations(pos, 2):
        sep = angular_sep(pos[a], pos[b])
        rows.append({"ดาวดวงที่ 1": PLANET_TH[a], "ดาวดวงที่ 2": PLANET_TH[b], "ระยะห่าง (องศา)": round(sep, 4), "มุมใกล้เคียง": min([("ร่วม 0°",abs(sep)),("60°",abs(sep-60)),("ฉาก 90°",abs(sep-90)),("ตรีโกณ 120°",abs(sep-120)),("ตรงข้าม 180°",abs(sep-180))], key=lambda x:x[1])[0]})
    return pd.DataFrame(rows)
         show_cols = [c for c in ["id","created_at","target_date","weekday","country","lottery","category","main_number","number_set","astronomy_status"] if c in hist.columns]
        st.dataframe(hist[show_cols], use_container_width=True, hide_index=True)
        st.download_button("ส่งออกประวัติ CSV", hist[show_cols].to_csv(index=False).encode("utf-8-sig"), file_name="synapse_calculation_history.csv", mime="text/csv")
        if st.button("ลบประวัติการคำนวณทั้งหมด", type="secondary"):
            with db_connect() as con: con.execute("DELETE FROM calculations")
            st.success("ลบประวัติการคำนวณแล้ว"); st.rerun()

elif page == "เครื่องเล่นเพลง":
    st.subheader("🎵 เครื่องเล่นเพลงจากโฟลเดอร์เดียวกับ Ta_app.py")
    audio_files = sorted([p for p in APP_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".mp3",".wav",".ogg",".m4a",".aac",".flac"}])
    if not audio_files:
        st.info("ยังไม่พบไฟล์เพลง กรุณาเพิ่มไฟล์ .mp3, .wav, .ogg, .m4a, .aac หรือ .flac ไว้ในโฟลเดอร์เดียวกับ Ta_app.py และ commit เข้า GitHub")
    else:
        chosen_audio = st.selectbox("เลือกเพลง", audio_files, format_func=lambda p:p.name)
        st.audio(chosen_audio.read_bytes(), format={".mp3":"audio/mpeg",".wav":"audio/wav",".ogg":"audio/ogg",".m4a":"audio/mp4",".aac":"audio/aac",".flac":"audio/flac"}.get(chosen_audio.suffix.lower(),"audio/mpeg"))
        st.caption("การเล่นต่อเนื่อง/เล่นสุ่มอัตโนมัติขึ้นกับข้อจำกัดของเบราว์เซอร์ Streamlit; กดเล่นเพลงด้วยตนเองได้")

else:
    st.subheader("ℹ️ เกี่ยวกับระบบ")
    st.markdown("""
**สิ่งที่ระบบทำได้**
- คำนวณตำแหน่งดวงอาทิตย์ ดวงจันทร์ และดาวเคราะห์ 7 ดวงจาก ephemeris DE421 ผ่าน Skyfield ณ เวลาอ้างอิง 12:00 UTC
- แสดงลองจิจูดสุริยวิถี ราศีสุริยคติ และมุมห่างระหว่างดาว
- สร้างชุดตัวเลขจากสูตรที่กำหนดชัดเจน รวมเลขกลับและเปรียบเทียบทั้ง 7 วัน
- บันทึกประวัติใน SQLite, นำเข้าผลย้อนหลัง CSV และเทียบตามวันที่/ประเทศ/ชื่อหวย/หมวดเลข
- เล่นไฟล์เสียงที่วางไว้ในโฟลเดอร์เดียวกับแอป

**ข้อจำกัดสำคัญ**
- สูตรตัวเลขเป็นสูตรทดลอง ไม่ได้รับการพิสูจน์ว่าทำนายผลสลากได้ และไม่ควรใช้เป็นหลักประกันทางการเงิน
- ข้างขึ้น/ข้างแรมเป็นค่าประมาณจากอายุจันทร์ ไม่ใช่ปฏิทินจันทรคติไทยที่รับรองอย่างเป็นทางการ
- ปีนักษัตรใช้รอบปีโดยประมาณที่ยึดปี 2024 เป็นปีมะโรง; เส้นแบ่งปีจริงอาจต่างกันตามธรรมเนียม
- ผลรางวัลต้องนำเข้าจากแหล่งข้อมูลที่ตรวจสอบเอง แอปไม่ได้สร้างผลจริงหรือดึงผลจากเว็บโดยอัตโนมัติ
- Streamlit Cloud อาจไม่เก็บไฟล์ SQLite ไว้ถาวรเมื่อมีการรีบูต/สร้างแอปใหม่ ควรใช้ฐานข้อมูลภายนอกหากต้องการความคงทน
- การคำนวณดาวครั้งแรกต้องดาวน์โหลดไฟล์ ephemeris; ถ้าดาวน์โหลดไม่ได้ ระบบจะแจ้งข้อผิดพลาด
""")

st.markdown("---")
st.caption("SYNAPSE MYSTIC NUMBER • โปร่งใส ตรวจสอบสูตรได้ • ผลลัพธ์เพื่อการศึกษาและทดลองเท่านั้น")                   
