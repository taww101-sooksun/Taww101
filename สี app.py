def global_chat_logic(my_name, msg_input=None):
    # ถ้ามีการส่งข้อความใหม่
    if msg_input:
        db.reference('global_chat').push({
            'name': my_name, 
            'msg': msg_input, 
            'ts': time.time()
        })
    
    # ดึงข้อความเก่ามาแสดง (กรองเฉพาะ 15 ข้อความล่าสุด)
    raw_msgs = db.reference('global_chat').get()
    if raw_msgs:
        return sorted(raw_msgs.values(), key=lambda x: x.get('ts', 0))[-15:]
    return []

