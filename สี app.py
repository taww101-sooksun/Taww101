import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="centered")

# โค้ด HTML/JS/CSS ที่ปรับตามสั่งเป๊ะๆ
ui_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
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
            background-color: rgba(#f0f0f0);
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
