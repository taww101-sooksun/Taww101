import streamlit as st
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าจอ Streamlit (Python Part)
st.set_page_config(layout="wide", page_title="SYNAPSE CORE")

# 2. รวมร่างโค้ด HTML + CSS + JS (Firebase & Math Engine) ไว้ในตัวแปรเดียว
# ใช้เครื่องหมาย ''' คร่อมหัวท้าย เพื่อบอก Python ว่านี่คือ "ข้อความยาว" ไม่ใช่คำสั่ง Python
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { background: #050505; color: #0f0; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; }
        
        /* CSS ส่วนที่เคย Error จะอยู่ในนี้ ซึ่งปลอดภัยแล้ว */
        .top-section { 
            height: 150px; 
            border-bottom: 2px solid #0f0; 
            position: relative; 
            background: #000; 
            padding: 10px;
        }
        
        .grid { 
            display: grid; 
            grid-template-columns: repeat(12, 1fr); 
            gap: 2px; 
            padding: 10px; 
            height: calc(100vh - 170px);
            overflow-y: auto;
        }
        
        .cell { 
            height: 40px; 
            background: #111; 
            border: 1px solid #222; 
            font-size: 10px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: #333;
        }
        
        .cell.active { 
            background: #0f0 !important; 
            box-shadow: 0 0 15px #0f0; 
            color: #000; 
            font-weight: bold;
        }

        button { 
            background: #000; 
            color: #0f0; 
            border: 1px solid #0f0; 
            padding: 8px 15px; 
            cursor: pointer; 
            font-family: inherit;
        }
        
        button:hover { background: #0f0; color: #000; }
    </style>
</head>
<body>

<div class="top-section">
    <h3 style="margin:0">🛰️ SYNAPSE REAL-TIME NODE</h3>
    <p id="status" style="font-size: 12px; color: #888;">ระบบพร้อม... กรุณากดปุ่มเพื่อเริ่มดักฟัง Firebase</p>
    <button onclick="startSync()">START ENGINE</button>
</div>

<div class="grid" id="grid"></div>

<script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/9.17.1/firebase-app.js";
    import { getDatabase, ref, onValue } from "https://www.gstatic.com/firebasejs/9.17.1/firebase-database.js";

    // --- CONFIG จริงของคุณต๊ะ ---
    const firebaseConfig = {
        databaseURL: "https://sooksun1-default-rtdb.firebaseio.com/"
    };

    const app = initializeApp(firebaseConfig);
    const db = getDatabase(app);
    const syncRef = ref(db, 'live/sync_node');

    // สร้างตาราง 144
    const gridEl = document.getElementById('grid');
    for(let i=0; i<144; i++) {
        const div = document.createElement('div');
        div.className = 'cell'; div.id = 'c-'+i;
        div.innerText = i;
        gridEl.appendChild(div);
    }

    // ฟังก์ชันดักฟังค่าจริงจาก Cloud
    window.startSync = () => {
        document.getElementById('status').innerText = "กำลังเชื่อมต่อกับความจริง (Cloud Data)...";
        
        onValue(syncRef, (snapshot) => {
            const data = snapshot.val();
            if (data && data.idx !== undefined) {
                updateUI(data.idx);
                document.getElementById('status').innerText = "📡 Receiving Note: " + data.idx;
            }
        });
    };

    function updateUI(idx) {
        const cell = document.getElementById('c-'+idx);
        if(cell) {
            cell.classList.add('active');
            setTimeout(() => cell.classList.remove('active'), 150);
        }
    }
</script>
</body>
</html>
"""

# 3. ใช้คำสั่งนี้เพื่อรัน HTML บนหน้า Streamlit
components.html(html_code, height=900, scrolling=True)
