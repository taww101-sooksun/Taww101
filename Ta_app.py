from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import math
import time
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    # สูตรคำนวณระยะทางจริง (หน่วยกิโลเมตร)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * math.asin(math.sqrt(a)) * 6371

def scrape_flightradar_nearby(my_lat, my_lon, radius_km=2.0):
    # ตั้งค่า Chrome แบบซ่อนหน้าต่าง (Headless) จะได้รันเงียบๆ ไม่รบกวนสายตา
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    print("🌐 กำลังเปิดหน้าเว็บ FlightRadar24 ผ่านบราวเซอร์จำลอง (ไม่ใช้ API)...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # ดึงข้อมูลโซนประเทศไทยและพื้นที่ใกล้เคียงจากหน้าเว็บโดยตรง
    # ปรับค่า bounds ให้ครอบคลุมจุดที่นายอยู่ได้
    url = f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds={my_lat+0.5},{my_lat-0.5},{my_lon-0.5},{my_lon+0.5}"
    
    try:
        driver.get(url)
        time.sleep(2) # รอให้หน้าเว็บโหลดข้อมูลดิบเสร็จ
        
        # ดึงข้อความทั้งหมดจากหน้าเว็บมาแกะ
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        raw_data = soup.find('body').text
        
        # แปลงข้อมูล text จากหน้าเว็บให้กลายเป็น Dictionary ของ Python
        import json
        data = json.loads(raw_data)
        
        aircraft_list = []
        for key, value in data.items():
            # คัดกรองเอาเฉพาะข้อมูลตัวเลขที่เป็นเครื่องบินจริงๆ (โค้ดของเว็บจะเป็น Array ข้อมูล)
            if isinstance(value, list) and len(value) > 1:
                flight_lat = value[1]
                flight_lon = value[2]
                callsign = value[16] if value[16] else "UNKNOWN"
                altitude = value[4] # ความสูง (ฟุต)
                speed = value[5]    # ความเร็ว (น็อต)
                
                # คำนวณระยะห่าง
                distance = haversine(my_lat, my_lon, flight_lat, flight_lon)
                
                if distance <= radius_km:
                    aircraft_list.append([callsign, flight_lat, flight_lon, altitude, speed, distance])
        
        driver.quit()
        
        # สร้างเป็นตารางออกมาดู
        df = pd.DataFrame(aircraft_list, columns=['Callsign', 'Latitude', 'Longitude', 'Altitude(ft)', 'Speed(kts)', 'Distance(km)'])
        return df

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหน้าเว็บ: {e}")
        driver.quit()
        return None

# --- พิกัดของคุณ ---
MY_LAT = 13.6900
MY_LON = 100.7500
RADIUS = 2.0

result = scrape_flightradar_nearby(MY_LAT, MY_LON, radius_km=RADIUS)

if result is not None:
    if not result.empty:
        print(f"\n🎉 [เจอของจริงจากหน้าเว็บ] พบอากาศยานในรัศมี {RADIUS} กม. :")
        print(result.to_string(index=False))
    else:
        print(f"\nสแกนหน้าเว็บเสร็จสิ้น: ไม่มีเครื่องบิน/โดรนลำไหนอยู่ในระยะ {RADIUS} กม. รอบตัวคุณ ณ วินาทีนี้")
