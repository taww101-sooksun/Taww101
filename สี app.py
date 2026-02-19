<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Room Color Simulator</title>
    <style>
        /* CSS: ส่วนการตกแต่ง */
        :root {
            --room-bg: #e0e0e0;
            --frame-color: #4a4a4a;
            --btn-bg: #007bff;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            width: 100%;
            max-width: 600px;
        }

        .control-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        /* ส่วนแสดงผลห้องจำลอง */
        .room-preview {
            width: 100%;
            max-width: 500px;
            height: 350px;
            background-color: var(--room-bg);
            border: 15px solid #333;
            border-bottom: 30px solid #222; /* จำลองพื้น */
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            transition: background-color 0.3s;
        }

        /* กรอบหน้าต่าง/กรอบรูปในห้อง */
        .frame {
            width: 180px;
            height: 120px;
            border: 10px solid var(--frame-color);
            background: white;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
            transition: border-color 0.3s;
        }

        /* ปุ่มกดที่ต้องการทดสอบ */
        .test-button {
            background-color: var(--btn-bg);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px rgba(0,0,0,0.2);
            transition: all 0.2s;
        }

        .test-button:active {
            transform: translateY(2px);
            box-shadow: 0 2px rgba(0,0,0,0.2);
        }

        label { font-weight: bold; font-size: 14px; }
        input[type="color"] { width: 100%; height: 40px; cursor: pointer; border: none; }
    </style>
</head>
<body>

    <h2>🎨 ระบบทดลองสีห้องและอุปกรณ์</h2>

    <!-- ส่วนควบคุม -->
    <div class="controls">
        <div class="control-group">
            <label>สีผนังห้อง</label>
            <input type="color" id="roomInput" value="#e0e0e0">
        </div>
        <div class="control-group">
            <label>สีกรอบหน้าต่าง</label>
            <input type="color" id="frameInput" value="#4a4a4a">
        </div>
        <div class="control-group">
            <label>สีปุ่มกด</label>
            <input type="color" id="btnInput" value="#007bff">
        </div>
    </div>

    <!-- ส่วนแสดงผล -->
    <div class="room-preview">
        <div class="frame">
            <button class="test-button">กดปุ่มทดสอบ</button>
        </div>
    </div>

    <script>
        // JavaScript: ส่วนควบคุมการเปลี่ยนสีแบบ Real-time
        const root = document.documentElement;

        // ฟังก์ชันรับค่าจาก Input แล้วไปเปลี่ยนค่าใน CSS Variables
        document.getElementById('roomInput').addEventListener('input', (e) => {
            root.style.setProperty('--room-bg', e.target.value);
        });

        document.getElementById('frameInput').addEventListener('input', (e) => {
            root.style.setProperty('--frame-color', e.target.value);
        });

        document.getElementById('btnInput').addEventListener('input', (e) => {
            root.style.setProperty('--btn-bg', e.target.value);
        });
    </script>

</body>
</html>

