import requests
import json
import os

# --- ตั้งค่าระบบ (ดึงคีย์และเซ็ต URL ให้ถูกต้อง) ---
API_KEY = "AIzaSyBAtABvP9snIQ9bWmkunHgvB0wQPeAIGXc"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# --- ส่วนของการทำงานฟังก์ชันคุยกับ AI ---
def chat_with_ai(prompt):
    # เตรียมข้อมูล (Payload) โครงสร้างตามที่ Google API กำหนดไว้จริง
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {'Content-Type': 'application/json'}

    try:
        # ซ่อมจุดตาย: จัดระเบียบการยิง Post Request ใหม่ ไม่ให้มีคำสั่ง import มาแซกกลาง
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        
        # เช็คสถานะการส่ง (200 = ผ่านสำเร็จ)
        if response.status_code == 200:
            data = response.json()
            # เจาะดึงข้อความจาก Object JSON ชั้นในสุดของ Gemini 
            if 'candidates' in data and len(data['candidates']) > 0:
                 return data['candidates'][0]['content']['parts'][0]['text']
            else:
                 return "🤔 AI ไม่ตอบกลับ (อาจจะไม่มีคำตอบ)"
        else:
            return f"❌ เกิดข้อผิดพลาด (Code {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"❌ เชื่อมต่อไม่ได้: {str(e)}"

# --- เริ่มรันโปรแกรมระบบ Command Line (CLI) ---
# บล็อกตรวจจับระบบปฏิบัติการ: ล้างหน้าจอให้รองรับทั้ง Termux บนมือถือ และคอมพิวเตอร์ทั่วไป
if os.name == 'nt':
    os.system('cls')
else:
    os.system('clear')

print("🤖 ระบบ AI พร้อมทำงาน! (พิมพ์ 'exit' เพื่อออก)")
print("---------------------------------------------")

# ลูปอินพุตรับส่งข้อความต่อเนื่อง
while True:
    user_input = input("\nคุณ: ")
    
    if user_input.lower() in ['exit', 'ออก']:
        print("👋 บ๊ายบายครับเพื่อนบาส!")
        break
        
    if not user_input.strip():
        continue

    print("⚡ กำลังคิด...")
    ai_reply = chat_with_ai(user_input)
    print(f"🤖 AI: {ai_reply}")
