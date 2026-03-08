def private_chat_logic(my_name, target_name, p_msg=None):
    # สร้างชื่อห้องจากชื่อคนสองคนเรียงกัน (กันชื่อสลับที่กันแล้วหาห้องไม่เจอ)
    pair = sorted([my_name, target_name])
    room_id = f"priv_{pair[0]}_{pair[1]}"
    
    if p_msg:
        db.reference(f'private_rooms/{room_id}').push({
            'name': my_name, 'msg': p_msg, 'ts': time.time()
        })
    
    raw_p_msgs = db.reference(f'private_rooms/{room_id}').get()
    if raw_p_msgs:
        return sorted(raw_p_msgs.values(), key=lambda x: x.get('ts', 0))[-10:]
    return []
