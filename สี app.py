import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="centered")

# โค้ด HTML/JS/CSS ที่ปรับตามสั่งเป๊ะๆ
ui_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
    /* 1. กรอบย่อยด้านใน (เช่น ช่องใส่กราฟ หรือช่องชื่อเพลง) */
    .inner-panel {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid #8b00ff; /* ขอบม่วงบางๆ */
        box-shadow: inset 0 0 10px #00f2fe; /* ไฟนีออนฟ้าสะท้อนด้านใน */
        padding: 10px;
        margin-bottom: 15px;
        color: #f0f0f0;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 1px;
    }

    /* 2. ปุ่มกดสไตล์ SYNAPSE */
    .synapse-btn {
        width: 100%;
        background: transparent;
        border: 2px solid #ff0000; /* ขอบแดง */
        color: #f0f0f0; /* ขาวมุก */
        padding: 12px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        margin-top: 10px;
        box-shadow: 0 0 5px #ff0000;
    }

    /* เอฟเฟกต์ตอนเอาเมาส์วางปุ่ม */
    .synapse-btn:hover {
        background: #00f2fe; /* เปลี่ยนพื้นหลังเป็นนีออนฟ้า */
        color: #000; /* ตัวหนังสือดำตัด */
        box-shadow: 0 0 20px #00f2fe; /* ไฟฟ้าสว่างวาบ */
        border-color: #00f2fe;
    }

    /* 3. แถบเลื่อน (Slider) ทุ้ม-กลาง-แหลม */
    input[type=range] {
        -webkit-appearance: none;
        width: 100%;
        background: transparent;
    }

    input[type=range]::-webkit-slider-runnable-track {
        height: 4px;
        background: #8b00ff; /* รางม่วง */
    }

    input[type=range]::-webkit-slider-thumb {
        -webkit-appearance: none;
        height: 15px;
        width: 15px;
        background: #00f2fe; /* หัวลากฟ้า */
        margin-top: -5px;
        box-shadow: 0 0 10px #00f2fe;
        cursor: pointer;
    }
</style>

<div class="synapse-frame">
    <div class="header">SYNAPSE COMMAND</div>
    
    <div class="inner-panel">
        NOW PLAYING: <span style="color:#00f2fe">SYSTEM_READY.MP3</span>
    </div>

    <div style="margin-bottom: 20px;">
        <div style="font-size: 10px; color: #ff0000;">BASS FREQUENCY</div>
        <input type="range">
    </div>

    <button class="synapse-btn">ACTIVATE SYSTEM</button>
    <button class="synapse-btn" style="border-color:#8b00ff; box-shadow:0 0 5px #8b00ff;">VOCAL CANCEL</button>

    <div class="slogan">อยู่นิ่งๆ ไม่เจ็บตัว</div>
</div>

        body { 
            background: transparent; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }
        
        .synapse-frame {
            width: 400px;
            height: 500px;
            background-color: rgba(0,0,0,0.5);
            border: 4px solid;
            /* เส้นขอบไล่สีม่วงไปแดง */
            border-image: linear-gradient(to bottom right, #8b00ff, #ff0000) 1;
            border-radius: 0px; /* ทรงเหลี่ยมตามสั่ง */
            box-shadow: 0 0 15px #00f2fe; /* นีออนฟ้า */
            padding: 10px;
            color: #f0f0f0; /* ขาวสว่างมุก */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-sizing: border-box;
            position: relative;
        }

        .header {
            text-align: center;
            font-weight: bold;
            font-size: 20px;
            margin-bottom: 20px;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
            border-bottom: 1px solid rgba(0, 242, 254, 0.3);
            padding-bottom: 10px;
        }

        .status-box {
            border: 1px solid #00f2fe;
            height: 100px;
            margin-bottom: 20px;
            background: rgba(0, 242, 254, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }

        .label { color: #f0f0f0; font-size: 14px; margin-bottom: 5px; }
        
        .slogan {
            position: absolute;
            bottom: 10px;
            width: calc(100% - 20px);
            text-align: center;
            font-size: 12px;
            color: rgba(255,255,255,0.4);
        }
    </style>
</head>
<body>
    <div class="synapse-frame">
        <div class="header">SYNAPSE COMMAND</div>
        
        <div class="label">VISUALIZER SYSTEM</div>
        <div class="status-box">READY TO SCAN...</div>
        
        <div class="label">SYSTEM STATUS</div>
        <div style="font-size: 13px; line-height: 1.6;">
            > Width: 400px<br>
            > Height: 500px<br>
            > Border: 4px (Purple-Red)<br>
            > Neon: 15px (#00f2fe)<br>
            > Mode: Stay Still, No Pain
        </div>

        <div class="slogan">อยู่นิ่งๆ ไม่เจ็บตัว</div>
    </div>
</body>
</html>
"""

# แสดงผลใน Streamlit (ความกว้าง 100% เพื่อให้คลุม iframe)
components.html(ui_code, width=500, height=600)
