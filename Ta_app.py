_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชี"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาไปที่หน้าเข้าสู่ระบบ")
    st.stop()

# --- 5. MAIN CORE MODULE TABS ---
st.markdown(f"<div style='text-align:right; color:{theme_color}; font-size:12px; padding-right:10px; font-weight:bold;'>AGENT: {st.session_state.user}</div>", unsafe_allow_html=True)

# สร้างเมนูแยกแท็บการใช้งานหลักระหว่างห้องแชตและห้องถอดรหัสคณิตศาสตร์ควอนตัม
main_tabs = st.tabs(["💬 SYNAPSE CHAT LIVE", "🧬 TRUTH DECODER"])

with main_tabs[0]:
    chat_display_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        #chat-screen {{
            background: rgba(0,0,0,0.95); border: 2px solid {theme_color}; border-radius: 12px;
            height: 480px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
            box-shadow: inset 0 0 15px {theme_color}33;
        }}
        .bubble {{ padding: 10px 15px; border-radius: 10px; margin: 8px 0; max-width: 85%; color: #fff; font-family: 'Orbitron', sans-serif; font-size: 14px; line-height: 1.4; }}
        .me {{ background: {theme_color}22; border-right: 4px solid {theme_color}; align-self: flex-end; }}
        .others {{ background: #222; border-left: 4px solid #777; align-self: flex-start; }}
        .notif-box {{ background: #333; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; transition: 0.3s; }}
        .alert-red {{ background: #F00 !important; box-shadow: 0 0 15px #F00; font-weight: bold; }}
    </style>

    <div id="chat-screen">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid #333; padding-bottom: 5px;">
            <span style="color:{theme_color}; font-size:10px; letter-spacing: 2px;">📡 SYSTEM_ACTIVE</span>
            <span id="notif-box" class="notif-box">0 NEW SIGNAL</span>
        </div>
        <div id="msg-area" style="display:flex; flex-direction:column;"></div>
    </div>

    <audio id="notif-sound" preload="auto">
        <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
    </audio>

    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const fb_conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
        if(!firebase.apps.length) firebase.initializeApp(fb_conf);
        const database = firebase.database();
        let lastCount = -1;
        const beep = document.getElementById('notif-sound');

        function unlock() {{
            beep.play().then(() => {{ beep.pause(); beep.currentTime = 0; }});
            window.removeEventListener('click', unlock);
            window.removeEventListener('touchstart', unlock);
        }}
        window.addEventListener('click', unlock);
        window.addEventListener('touchstart', unlock);

        database.ref('global_chat').limitToLast(25).on('child_added', (snap) => {{
            const msg = snap.val();
            const area = document.getElementById('msg-area');
            const div = document.createElement('div');
            const isMe = msg.user === "{st.session_state.user}";
            div.className = "bubble " + (isMe ? "me" : "others");
            div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
            
            let html = `<div style="font-size:10px; color:#777; margin-bottom:5px;">${{msg.user}}</div>`;
            if(msg.text) html += `<div>${{msg.text}}</div>`;
            if(msg.img) html += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:8px; margin-top:8px; border: 1px solid #444;">`;
            
            div.innerHTML = html;
            area.appendChild(div);
            document.getElementById('chat-screen').scrollTop = 999999;
        }});

        database.ref('chat_notifications/unread_count').on('value', (snap) => {{
            const val = snap.val() || 0;
            const box = document.getElementById('notif-box');
            box.innerText = val + " NEW SIGNAL";
            if(val > 0) {{
                box.classList.add('alert-red');
                if(lastCount !== -1 && val > lastCount) {{
                    beep.currentTime = 0;
                    beep.play().catch(() => {{}});
                }}
            }} else {{
                box.classList.remove('alert-red');
            }}
            lastCount = val;
        }});
    </script>
    """
    components.html(chat_display_html, height=520)

    # --- CONTROLS CHAT INTERFACE ---
    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            m_txt = st.text_input("MESSAGE", placeholder="พิมพ์ข้อความตอบกลับโครงข่าย...", label_visibility="collapsed")
        with c2:
            m_img = st.file_uploader("IMAGE", type=['png','jpg','jpeg'], label_visibility="collapsed")
        with c3:
            if st.button("ส่งสัญญาณ ⚡", use_container_width=True):
                if m_txt or m_img:
                    p_load = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                    if m_txt: p_load['text'] = m_txt
                    if m_img: p_load['img'] = base64.b64encode(m_img.read()).decode()
                    db.reference('global_chat').push(p_load)
                    
                    cur = db.reference('chat_notifications/unread_count').get() or 0
                    db.reference('chat_notifications').set({'unread_count': cur + 1})
                    st.rerun()

with main_tabs[1]:
    # --- 6. LOGIC ROOM MODULE ---
    def room_logic():
        st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
        
        def decode_truth(dt):
            ref_date = date(1900, 1, 1)
            diff = (dt - ref_date).days
            lunar_cycle = 29.530589
            pos = (diff - 0.5) % lunar_cycle
            day_val = dt.weekday() + 1
            
            thai_year = dt.year + 543
            zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
            zodiac = zodiacs[thai_year % 12]
            
            elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
            element = elements.get(day_val)

            if pos <= 14.765:
                m_num = int(pos) + 1
                phase = f"ขึ้น {m_num} ค่ำ"
                res = math.sqrt((day_val**2) + (m_num**2))
                formula = f"√({day_val}² + {m_num}²)"
                p_type = "แรงผลักดัน (Vector)"
            else:
                m_num = int(pos - 14.765) + 1
                phase = f"แรม {m_num} ค่ำ"
                res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
                formula = f"({day_val} × 1.618) / {m_num}"
                p_type = "สมดุลสัดส่วนทองคำ (Phi)"
                
            return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "type": p_type, "day_num": day_val, "lunar_num": m_num, "diff": diff}

        st.subheader("🔍 วิเคราะห์พิกัดความจริง (อดีต-อนาคต)")
        target_date = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today(), min_value=date(1950,1,1), max_value=date(2026,12,31))
        
        if target_date:
            d = decode_truth(target_date)
            st.markdown(f"""
                <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:20px; background:rgba(0,0,0,0.3); box-shadow: 0 0 15px {st.session_state.theme_color}55;">
                    <small style="color:#aaa; letter-spacing: 2px;">รหัสพิกัดจักรวาล</small>
                    <h1 style="color:{st.session_state.theme_color}; font-size:60px; margin:0; text-shadow: 0 0 15px {st.session_state.theme_color};">{d['res']}</h1>
                    <p style="color:#888; margin-top:5px; font-weight:bold;">{d['type']}</p>
                </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📅 **ฐานวัน ({d['day_num']}):** แรงดึงดูดโลก")
                st.info(f"🌙 **จันทรคติ ({d['phase']}):** แรงดึงดูดดวงจันทร์")
            with col2:
                st.success(f"🐎 **ปีนักษัตร:** ปี{d['zodiac']}")
                st.success(f"💎 **ธาตุประจำวัน:** ธาตุ{d['element']}")

            st.markdown(f"""
                <div style="background:#111; padding:15px; border-left:5px solid {st.session_state.theme_color}; border-radius:10px; margin-top:10px;">
                    <p style="font-size:14px; color:#aaa; margin:0; font-family: monospace;">
                        <b>สูตรการคำนวณรหัสลับ:</b> {d['formula']}<br>
                        คำนวณจากวันที่สะสมตั้งแต่ปี 1900 รวมทั้งสิ้น {d['diff']:,} วัน
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if target_date < date.today(): st.warning("⏪ ตรวจสอบรอยเท้าพลังงานใน **'อดีต'**")
            elif target_date > date.today(): st.error("🔮 ตรวจสอบพิกัดเป้าหมายใน **'อนาคต'**")
            else: st.success("🟢 พิกัดพลังงานใน **'ปัจจุบัน'**")

    # เรียกใช้งานฟังก์ชันห้องคำนวณความจริงด้านในแท็บ
    room_logic()

# --- 7. GLOBAL TERMINAL CONTROLS ---
st.markdown("<br>", unsafe_allow_html=True)
st.divider()
col_act1, col_act2 = st.columns(2)
with col_act1:
    if st.button("ล้างการแจ้งเตือน (RESET)", use_container_width=True):
        db.reference('chat_notifications').set({'unread_count': 0})
        st.rerun()
with col_act2:
    if st.button("ออกจากระบบ (LOGOUT)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
