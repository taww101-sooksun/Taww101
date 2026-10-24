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

def number_outputs(target_date, positions):
    """Deterministic experimental transformations; no claim of predictive power."""
    d = digital_root(digit_sum(target_date.strftime("%Y%m%d")))
    w = target_date.weekday() + 1
    weighted = sum((i + 1) * positions[p] for i, p in enumerate(PLANETS))
    pval = round(weighted * 100) % 100
    separations = [angular_sep(positions[a], positions[b]) for a, b in combinations(PLANETS, 2)]
    aval = round(sum(separations) * 100) % 100
    mval = round(positions["Moon"] * 100) % 100
    base = (3*d + 2*w + pval + aval + mval) % 100
    candidates = [base, (base + w) % 100, (base + d) % 100, (base + pval) % 100, (base + aval) % 100, (base + mval) % 100,
                  (base + 11*w) % 100, (base + 7*d + w) % 100, (base + pval + mval) % 100]
    # Keep each formula's result but remove duplicate numbers; add reverse of each result for two-way viewing.
    formula_rows = []
    labels = ["สูตรหลัก", "บวกเลขวัน", "บวกค่ารากวันที่", "บวกค่าดาว", "บวกค่ามุมดาว", "บวกค่าดวงจันทร์", "สูตรวัน×11", "สูตรวันและวันที่", "สูตรดาว+จันทร์"]
    for label, value in zip(labels, candidates):
        formula_rows.append({"สูตร":label, "เลข 2 หลัก":f"{value:02d}", "เลขกลับ":f"{int(f'{value:02d}'[::-1]):02d}"})
    outputs = []
    for row in formula_rows:
        outputs.extend([row["เลข 2 หลัก"], row["เลขกลับ"]])
    outputs = list(dict.fromkeys(outputs))
    return formula_rows, outputs, {"date_value":d,"weekday_value":w,"planet_value":pval,"angle_value":aval,"moon_value":mval,"base":f"{base:02d}"}

# ---------------- Results import / analysis ----------------
def clean_num(v):
    s = str(v).strip()
    if s.endswith(".0"): s = s[:-2]
    return s if s.isdigit() else None

def parse_results_csv(uploaded):
    df = pd.read_csv(uploaded, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip().lower() for c in df.columns]
    required = {"date", "country", "lottery", "category", "number"}
    missing = required - set(df.columns)
    if missing:
        return None, "CSV ต้องมีคอลัมน์ date,country,lottery,category,number (ขาด: " + ", ".join(sorted(missing)) + ")"
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["number"] = df["number"].map(clean_num)
    df = df.dropna(subset=["date", "number"]).copy()
    for col in ["country", "lottery", "category"]: df[col] = df[col].astype(str).str.strip()
    df = df[(df["country"]!="") & (df["lottery"]!="") & (df["category"]!="") & (df["number"]!="")]
    if df.empty: return None, "ไม่พบข้อมูลที่ใช้งานได้"
    df["number"] = df["number"].map(lambda x: x.zfill(2) if len(x) <= 2 else x)
    if "source" not in df.columns: df["source"] = "นำเข้าโดยผู้ใช้"
    return df[["date","country","lottery","category","number","source"]], None

def import_results(df):
    with db_connect() as con:
        for row in df.itertuples(index=False):
            con.execute("INSERT INTO lottery_results(draw_date,country,lottery,category,number,source) VALUES(?,?,?,?,?,?)", (row.date,row.country,row.lottery,row.category,row.number,row.source))

# ---------------- UI ----------------
st.sidebar.markdown("# 🌌 SYNAPSE")
st.sidebar.markdown("### MYSTIC NUMBER")
page = st.sidebar.radio("เมนู", ["หน้าหลักและคำนวณ", "วิเคราะห์วันทั้ง 7", "มุมดาว", "ผลย้อนหลังและสถิติ", "ประวัติการคำนวณ", "เครื่องเล่นเพลง", "เกี่ยวกับระบบ"])
st.sidebar.caption("ข้อมูลดาราศาสตร์ • สูตรตรวจสอบได้ • ไม่รับประกันผลรางวัล")

logo_candidates = [APP_DIR / "logo1.png", APP_DIR / "logo.png", APP_DIR / "synapse_logo.png"]
for logo in logo_candidates:
    if logo.exists():
        c1,c2 = st.columns([1,5])
        with c1: st.image(str(logo), width=110)
        with c2: st.markdown("<h1 style='padding-top:12px'>SYNAPSE MYSTIC NUMBER</h1><p>SPACE • ASTRONOMY • NUMBER ANALYSIS</p>", unsafe_allow_html=True)
        break
else:
    st.markdown("<div class='cosmic-card'><h1>🌌 SYNAPSE MYSTIC NUMBER</h1><p>SPACE • ASTRONOMY • NUMBER ANALYSIS</p></div>", unsafe_allow_html=True)

if page == "หน้าหลักและคำนวณ":
    st.subheader("📅 วิเคราะห์วันที่และสร้างชุดตัวเลข")
    left, right = st.columns([1,1])
    with left:
        chosen = st.date_input("วันที่ต้องการคำนวณ", value=date.today(), min_value=date(1900,1,1), max_value=date(2100,12,31))
        country = st.selectbox("ประเทศ / ตลาด", ["ไทย", "ลาว", "เวียดนาม", "อื่น ๆ"])
        lottery = st.text_input("ชื่อหวย / ประเภทการออกรางวัล", value="หวยที่ต้องการวิเคราะห์")
        category = st.selectbox("หมวดเลขที่ต้องการเทียบ", ["เลข 2 ตัว", "เลขท้าย 2 ตัว", "เลข 3 ตัว", "เลข 4 ตัว", "อื่น ๆ"])
        run = st.button("🪐 คำนวณและบันทึก", use_container_width=True)
    age, illumination, phase = approximate_moon(chosen)
    with right:
        st.markdown("<div class='cosmic-card'>", unsafe_allow_html=True)
        st.metric("วันในสัปดาห์", WEEKDAYS[chosen.weekday()])
        st.write(f"**วันที่:** {chosen.day} {MONTHS_TH[chosen.month-1]} {chosen.year}")
        st.write(f"**ข้างขึ้น/ข้างแรม:** {phase}")
        st.write(f"**อายุจันทร์โดยประมาณ:** {age:.1f} วัน • สว่างประมาณ {illumination:.0f}%")
        st.write(f"**ราศีสุริยคติ:** คำนวณได้หลังโหลดตำแหน่งดวงอาทิตย์")
        st.write(f"**ปีนักษัตรโดยรอบปี:** {thai_zodiac_year(chosen)}")
        st.caption("หมายเหตุ: ข้างขึ้น/ข้างแรมและปีนักษัตรตรงนี้เป็นค่าประมาณ ไม่ใช่ปฏิทินจันทรคติไทยทางการ")
        st.markdown("</div>", unsafe_allow_html=True)
    if run:
        try:
            with st.spinner("กำลังโหลด ephemeris และคำนวณตำแหน่งดาว..."):
                positions = calculate_positions(chosen)
                rows, outputs, values = number_outputs(chosen, positions)
            save_calculation(chosen, country, lottery.strip() or "ไม่ระบุ", category, outputs, json.dumps(values, ensure_ascii=False), "ตำแหน่งดาวคำนวณจาก Skyfield DE421 เวลา 12:00 UTC")
            st.session_state["latest_date"] = chosen.isoformat()
            st.session_state["latest_positions"] = positions
            st.session_state["latest_rows"] = rows
            st.session_state["latest_outputs"] = outputs
            st.success("คำนวณและบันทึกประวัติแล้ว")
        except Exception as exc:
            st.error("คำนวณตำแหน่งดาวไม่สำเร็จ โปรดตรวจสอบ requirements.txt และการเชื่อมต่ออินเทอร์เน็ตครั้งแรก")
            st.code(f"{type(exc).__name__}: {exc}")
    if st.session_state.get("latest_date") == chosen.isoformat():
        st.markdown("### ผลลัพธ์จากสูตรทดลอง")
        st.markdown(f"<div class='cosmic-card'><div class='muted'>เลขหลักของสูตร</div><div class='big-number'>{st.session_state['latest_rows'][0]['เลข 2 หลัก']}</div></div>", unsafe_allow_html=True)
        st.caption("ตัวเลขเป็นผลจากสูตรที่กำหนดไว้เพื่อการทดลอง/ศึกษา ไม่ใช่คำทำนายที่ผ่านการพิสูจน์ และไม่รับประกันผลรางวัล")
        st.dataframe(pd.DataFrame(st.session_state["latest_rows"]), use_container_width=True, hide_index=True)
        st.markdown("**ชุดเลขจากสูตรและเลขกลับ (ไม่ซ้ำ):**")
        st.write(" · ".join(st.session_state["latest_outputs"]))
        with st.expander("แสดงเลขครบ 00–99 และเลขกลับทั้งหมด"):
            all_numbers = pd.DataFrame({"เลข 00–99": [f"{i:02d}" for i in range(100)], "เลขกลับ": [f"{i:02d}"[::-1] for i in range(100)]})
            st.dataframe(all_numbers, use_container_width=True, hide_index=True, height=360)
            st.download_button("ดาวน์โหลดเลข 00–99 CSV", all_numbers.to_csv(index=False).encode("utf-8-sig"), file_name="numbers_00_99.csv", mime="text/csv")
        if st.session_state.get("latest_positions"):
            p = st.session_state["latest_positions"]
            st.markdown("### ตำแหน่งดาว (องศาสุริยวิถีโดยประมาณ ณ 12:00 UTC)")
            st.dataframe(pd.DataFrame([{"ดาว":PLANET_TH[k],"ลองจิจูด (°)":round(v,4),"ราศีสุริยคติ":zodiac_from_longitude(v)} for k,v in p.items()]), use_container_width=True, hide_index=True)
            st.download_button("ดาวน์โหลดตำแหน่งดาว CSV", pd.DataFrame([{"planet":k,"longitude_degrees":v,"zodiac":zodiac_from_longitude(v)} for k,v in p.items()]).to_csv(index=False).encode("utf-8-sig"), file_name=f"planet_positions_{chosen.isoformat()}.csv", mime="text/csv")

elif page == "วิเคราะห์วันทั้ง 7":
    st.subheader("📆 เปรียบเทียบวันทั้ง 7 วัน")
    chosen = st.date_input("เลือกสัปดาห์อ้างอิงจากวันที่นี้", value=date.today(), key="week_date")
    st.info("คำนวณตำแหน่งดาวสำหรับแต่ละวันจริงจาก ephemeris เมื่อมีการกดปุ่ม อาจใช้เวลาสักครู่ในครั้งแรก")
    if st.button("คำนวณครบทั้ง 7 วัน", use_container_width=True):
        monday = date.fromordinal(chosen.toordinal() - chosen.weekday())
        rows=[]
        try:
            with st.spinner("กำลังคำนวณ 7 วัน..."):
                for i in range(7):
                    d = date.fromordinal(monday.toordinal()+i)
                    pos = calculate_positions(d)
                    formula_rows, outs, vals = number_outputs(d,pos)
                    rows.append({"วันที่":d.isoformat(),"วัน":WEEKDAYS[d.weekday()],"เลขหลัก":formula_rows[0]["เลข 2 หลัก"],"เลขกลับ":formula_rows[0]["เลขกลับ"],"ชุดเลขไม่ซ้ำ":", ".join(outs),"ราศีอาทิตย์":zodiac_from_longitude(pos["Sun"]),"ข้างขึ้น/แรมโดยประมาณ":approximate_moon(d)[2]})
            st.session_state["weekday_comparison"] = rows
        except Exception as exc:
            st.error(f"คำนวณไม่สำเร็จ: {type(exc).__name__}: {exc}")
    if st.session_state.get("weekday_comparison"):
        df = pd.DataFrame(st.session_state["weekday_comparison"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("ดาวน์โหลดตาราง 7 วัน CSV", df.to_csv(index=False).encode("utf-8-sig"), file_name="synapse_weekdays.csv", mime="text/csv")

elif page == "มุมดาว":
    st.subheader("🪐 ตำแหน่งและมุมสัมพันธ์ของดาว")
    chosen = st.date_input("วันที่อ้างอิง", value=date.today(), key="angles_date")
    if st.button("คำนวณมุมดาว", use_container_width=True):
        try:
            with st.spinner("กำลังคำนวณ..."):
                pos = calculate_positions(chosen)
                angle_df = make_angle_table(pos)
            st.session_state["angle_df"] = angle_df
            st.session_state["angle_pos"] = pos
        except Exception as exc:
            st.error(f"คำนวณไม่สำเร็จ: {type(exc).__name__}: {exc}")
    if st.session_state.get("angle_df") is not None:
        st.dataframe(st.session_state["angle_df"], use_container_width=True, hide_index=True)
        st.download_button("ดาวน์โหลดมุมดาว CSV", st.session_state["angle_df"].to_csv(index=False).encode("utf-8-sig"), file_name="planet_angles.csv", mime="text/csv")
        st.caption("มุมดาวเป็นเรขาคณิตเชิงดาราศาสตร์ ไม่ได้ยืนยันว่ามีผลต่อผลสลากหรือเลขรางวัล")

elif page == "ผลย้อนหลังและสถิติ":
    st.subheader("📊 นำเข้าผลจริงและตรวจสอบย้อนหลัง")
    st.warning("ระบบนี้ไม่ดึงผลรางวัลจากเว็บไซต์อัตโนมัติ และไม่สร้างผลรางวัลขึ้นเอง โปรดนำเข้า CSV จากแหล่งที่คุณตรวจสอบแล้ว")
    st.markdown("CSV ต้องมีหัวคอลัมน์ `date,country,lottery,category,number` และอาจมี `source` เพิ่มได้")
    sample = pd.DataFrame([{"date":"2026-10-01","country":"ไทย","lottery":"ตัวอย่างชื่อหวย","category":"เลขท้าย 2 ตัว","number":"42","source":"ใส่ URL/ชื่อแหล่งข้อมูลที่ตรวจสอบแล้ว"}])
    st.download_button("ดาวน์โหลดแม่แบบ CSV", sample.to_csv(index=False).encode("utf-8-sig"), file_name="lottery_results_template.csv", mime="text/csv")
    upload = st.file_uploader("นำเข้า CSV ผลย้อนหลัง", type=["csv"])
    if upload is not None and st.button("ตรวจสอบและนำเข้าผล", use_container_width=True):
        try:
            df, err = parse_results_csv(upload)
            if err: st.error(err)
            else:
                import_results(df)
                st.success(f"นำเข้าข้อมูล {len(df)} แถวแล้ว")
                st.dataframe(df.head(100), use_container_width=True, hide_index=True)
        except Exception as exc: st.error(f"อ่าน CSV ไม่สำเร็จ: {type(exc).__name__}: {exc}")
    results = read_sql("SELECT draw_date AS date,country,lottery,category,number,source FROM lottery_results ORDER BY draw_date DESC")
    if not results.empty:
        st.markdown("### ผลที่บันทึกไว้")
        countries = sorted(results["country"].dropna().unique().tolist())
        c = st.selectbox("กรองประเทศ", ["ทั้งหมด"]+countries)
        view = results if c == "ทั้งหมด" else results[results["country"] == c]
        st.dataframe(view, use_container_width=True, hide_index=True)
        st.download_button("ส่งออกผลย้อนหลัง CSV", view.to_csv(index=False).encode("utf-8-sig"), file_name="saved_lottery_results.csv", mime="text/csv")
        st.markdown("### เปรียบเทียบกับการคำนวณที่บันทึกไว้")
        hist = read_sql("SELECT id,target_date,country,lottery,category,main_number,number_set,created_at FROM calculations ORDER BY id DESC")
        if not hist.empty:
            idx = st.selectbox("เลือกรายการคำนวณ", hist.index, format_func=lambda i: f"{hist.loc[i,'target_date']} | {hist.loc[i,'country']} | {hist.loc[i,'lottery']} | {hist.loc[i,'category']} | สูตรหลัก {hist.loc[i,'main_number']}")
            h = hist.loc[idx]
            matching = results[(results["date"] == h["target_date"]) & (results["country"] == h["country"]) & (results["lottery"] == h["lottery"]) & (results["category"] == h["category"])]
            try: output_set = set(json.loads(h["number_set"]))
            except Exception: output_set = {str(h["main_number"]).zfill(2)}
            if matching.empty:
                st.info("ยังไม่มีผลจริงที่ตรงกันครบทั้งวันที่ ประเทศ ชื่อหวย และหมวดเลข")
            else:
                matching = matching.copy()
                matching["match"] = matching["number"].astype(str).isin(output_set)
                st.write(f"ตรวจสอบ {len(matching)} รายการผลจริง • ตรงกับชุดสูตร {int(matching['match'].sum())} รายการ")
                st.dataframe(matching, use_container_width=True, hide_index=True)
                st.caption("การตรงกันในข้อมูลย้อนหลังไม่ได้พิสูจน์ว่าสูตรทำนายได้ และการเปรียบเทียบนี้ไม่ใช่การทดสอบเชิงสถิติที่ควบคุมปัจจัยครบถ้วน")

elif page == "ประวัติการคำนวณ":
    st.subheader("🗂️ ประวัติการคำนวณ")
    hist = read_sql("SELECT * FROM calculations ORDER BY id DESC")
    if hist.empty: st.info("ยังไม่มีประวัติ ให้คำนวณจากหน้าหลักก่อน")
    else:
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
