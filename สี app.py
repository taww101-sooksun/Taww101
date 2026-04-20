from firebase_admin import db

# ฟังก์ชันบันทึกความจริง
def save_synapse_log(user_name, result_code, status):
    ref = db.reference('/synapse_logs') # อ้างอิงโฟลเดอร์ใน Firebase
    ref.push({
        'name': user_name,
        'code': result_code,
        'status': status,
        'time': str(datetime.now())
    })

# ตัวอย่างการใช้: ถ้าเจอเพชร ให้บันทึกทันที
if gap < 0.5:
    save_synapse_log("Bas", user_data['res'], "💎 บรรจบ (เพชร)")
