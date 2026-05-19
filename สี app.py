import os
import time
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SYNAPSE_CORE_KEY_999'
socketio = SocketIO(app, cors_allowed_origins="*")

# =========================================================
# 🔐 FIREBASE INITIALIZATION
# =========================================================
if not firebase_admin._apps:
    try:
        # ดึงค่าจากสภาพแวดล้อมระบบเพื่อความปลอดภัยและความจริงแท้
        fb_creds = dict(os.environ.get("FIREBASE_CREDENTIALS"))
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': os.environ.get("FIREBASE_DB_URL")})
    except Exception:
        # กรณีรันเครื่อง Local หรือแบบทดสอบไฟล์พิกัดตรง
        try:
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred, {'databaseURL': "https://your-db-default.firebaseio.com/"})
        except Exception as e:
            print(f"🚨 LOG ERROR: Firebase ทำงานไม่ได้เนื่องจากขาดคีย์จริง -> {e}")

# =========================================================
# ⚙️ SYSTEM CORE ROUTING
# =========================================================
@app.route('/')
def index():
    if 'user' not in session:
        return render_template('index.html', page='auth')
    return render_template('index.html', page='main', username=session['user'])

@app.route('/api/auth', methods=['POST'])
def handle_auth():
    data = request.json
    action = data.get('action')
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'status': 'error', 'msg': 'กรุณากรอกข้อมูลให้ครบถ้วน'})
        
    ref = db.reference(f'users/{username}')
    user_info = ref.get()

    if action == 'register':
        if user_info:
            return jsonify({'status': 'error', 'msg': 'AGENT ID นี้ถูกลงทะเบียนในระบบแล้ว'})
        ref.set({
            'password': password,
            'display_name': username,
            'theme_color': '#39FF14',
            'created_at': datetime.now().isoformat()
        })
        return jsonify({'status': 'success', 'msg': 'ลงทะเบียน AGENT สำเร็จแล้ว!'})
        
    elif action == 'login':
        if user_info and user_info.get('password') == password:
            session['user'] = username
            return jsonify({'status': 'success', 'msg': 'ผ่านการตรวจสอบความปลอดภัย'})
        return jsonify({'status': 'error', 'msg': 'ข้อมูล AGENT หรือรหัสผ่านไม่ตรงกับฐานข้อมูลจริง'})

@app.route('/api/logout')
def handle_logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/api/get_songs')
def get_songs():
    """ดึงข้อมูลไฟล์เพลงจริงจากโฟลเดอร์ที่รันไฟล์ .py รองรับได้ถึง 70 เพลงหรือมากกว่า"""
    try:
        songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
        return jsonify({'status': 'success', 'songs': sorted(songs)})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})

@app.route('/api/get_profile')
def get_profile():
    if 'user' not in session: return jsonify({'status': 'error'})
    info = db.reference(f'users/{session["user"]}').get()
    return jsonify({'status': 'success', 'data': info})

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session: return jsonify({'status': 'error'})
    data = request.json
    new_password = data.get('password', '').strip()
    new_theme = data.get('theme', '#39FF14')
    
    ref = db.reference(f'users/{session["user"]}')
    current_data = ref.get() or {}
    
    updates = {'theme_color': new_theme}
    if new_password:
        updates['password'] = new_password
        
    ref.update(updates)
    return jsonify({'status': 'success', 'msg': 'อัปเดตระบบโครงสร้างส่วนบุคคลสำเร็จ'})

# =========================================================
# 📡 SOCKET.IO REAL-TIME COMMUNICATION (แชทรวม และ แชทส่วนตัว)
# =========================================================
@socketio.on('send_global_chat')
def handle_global_message(data):
    if 'user' not in session: return
    msg_payload = {
        'user': session['user'],
        'text': data['text'],
        'time_display': datetime.now().strftime("%H:%M:%S"),
        'timestamp': time.time()
    }
    db.reference('global_chat').push(msg_payload)
    emit('receive_global_chat', msg_payload, broadcast=True)

@socketio.on('send_private_chat')
def handle_private_message(data):
    if 'user' not in session: return
    target = data['target'].strip()
    text = data['text']
    
    if not db.reference(f'users/{target}').get():
        emit('private_error', {'msg': f'ไม่พบสัญญาณ AGENT: {target} ในระบบ'})
        return
        
    msg_payload = {
        'sender': session['user'],
        'receiver': target,
        'text': text,
        'time_display': datetime.now().strftime("%H:%M:%S"),
        'timestamp': time.time()
    }
    # บันทึกห้องแชทแยกตามคีย์คู่สนทนาที่ไม่ซ้ำกัน
    room_id = "_".join(sorted([session['user'], target]))
    db.reference(f'private_chats/{room_id}').push(msg_payload)
    emit('receive_private_chat', msg_payload, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
