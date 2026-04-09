import streamlit as st
import pandas as pd
from datetime import datetime, date
from datetime import date

def calculate_life_info(birth_date):
    today = date.today()
    
    # 1. คำนวณ อายุ: ปี เดือน วัน
    years = today.year - birth_date.year
    months = today.month - birth_date.month
    days = today.day - birth_date.day
    
    if days < 0:
        months -= 1
        days += 30 # ประมาณการณ์จำนวนวันในเดือน
    if months < 0:
        years -= 1
        months += 12

    # 2. วันในสัปดาห์
    days_of_week = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = days_of_week[birth_date.weekday()]

    # 3. การหาปีนักษัตร (แบบไทยจะเปลี่ยนปีช่วงสงกรานต์ หรือ วันเถลิงศก แต่ในที่นี้ใช้เกณฑ์ปีปฏิทิน)
    zodiac_animals = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    zodiac_year = zodiac_animals[birth_date.year % 12]

    # 4. การหาราศี และ ธาตุ (เกณฑ์ไทย - สุริยยาตร์)
    day, month = birth_date.day, birth_date.month
    if (month == 4 and day >= 13) or (month == 5 and day <= 13):
        sign, element = "เมษ", "ไฟ"
    elif (month == 5 and day >= 14) or (month == 6 and day <= 14):
        sign, element = "พฤษภ", "ดิน"
    elif (month == 6 and day >= 15) or (month == 7 and day <= 15):
        sign, element = "เมถุน", "ลม"
    elif (month == 7 and day >= 16) or (month == 8 and day <= 16):
        sign, element = "กรกฎ", "น้ำ"
    elif (month == 8 and day >= 17) or (month == 9 and day <= 16):
        sign, element = "สิงห์", "ไฟ"
    elif (month == 9 and day >= 17) or (month == 10 and day <= 16):
        sign, element = "กันย์", "ดิน"
    elif (month == 10 and day >= 17) or (month == 11 and day <= 15):
        sign, element = "ตุลย์", "ลม"
    elif (month == 11 and day >= 16) or (month == 12 and day <= 15):
        sign, element = "พิจิก", "น้ำ"
    elif (month == 12 and day >= 16) or (month == 1 and day <= 14):
        sign, element = "ธนู", "ไฟ"
    elif (month == 1 and day >= 15) or (month == 2 and day <= 12):
        sign, element = "มังกร", "ดิน"
    elif (month == 2 and day >= 13) or (month == 3 and day <= 13):
        sign, element = "กุมภ์", "ลม"
    else:
        sign, element = "มีน", "น้ำ"

    return {
        "age": f"{years} ปี {months} เดือน {days} วัน",
        "day_name": day_name,
        "zodiac_year": zodiac_year,
        "sign": sign,
        "element": element
    }

# --- การใช้งาน ---
# ใส่ปี ค.ศ. / เดือน / วัน
my_birthday = date(1995, 5, 20) 
result = calculate_life_info(my_birthday)

print(f"วันเกิด: {result['day_name']}")
print(f"อายุปัจจุบัน: {result['age']}")
print(f"ปีนักษัตร: {result['zodiac_year']}")
print(f"ราศี: {result['sign']} (ธาตุ{result['element']})")
