<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💖 Happy Valentine and Happy Anniversary!💖</title>
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
            background-color: #ffebf0;
            padding: 5%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: auto;
            margin: 0;
        }

        h1 {
            color: #d63384;
            font-size: 2.75em;
        }
        p {
            font-size: 1.3em;
            color: #d63384;
        }
       
        p1 {
            font-size: 1.7em;
            color: #555;
        }

        /* ซ่อนรูปตอนแรก */
        #loveImage {
            display: none;
            width: 350px;
            height: auto;
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            margin: 20px;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
            margin-top: 10px;
            margin-bottom: 30px;
        }

        #additionalImage {
            width: 350px;
            height: auto;
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            margin: 20px;
        }

        button {
            background-color: #ff66a3;
            color: white;
            border: none;
            padding: 1.5em 3em;
            font-size: 1.2em;
            cursor: pointer;
            border-radius: 10px;
            margin: 15px;
        }

        button:hover {
            background-color: #ff3385;
        }

        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 15px;
            position: relative;
        }

        #songTitle {
            font-size: 1.3em;
            color: black;
            margin-bottom: 20px;
        }

        /* ปรับขนาดปุ่ม */
        #toggleButton {
            background-color: #ff3385;
            color: white;
            border: none;
            padding: 1em 2em;
            font-size: 1em;
            cursor: pointer;
            border-radius: 10px;
        }

        #toggleButton:hover {
            background-color: #ff66a3;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>💕 hello darling 💕</h1>
        <p>💖Happy Valentine's Day & Happy Anniversary!💖</p>
        <p1>Do you know what I want to say?</p1>

        <!-- ชื่อเพลง -->
        <div id="songTitle">🎧 สิ่งที่ฉันเฝ้ารอไม่ใช่หิมะ 🎧</div>

        <!-- เครื่องเล่นเพลง MP3 ที่เล่นอัตโนมัติและวนลูป -->
        <audio controls autoplay loop>
            <source src="ที่เฝ้ารอไม่ใช่หิมะ.mp3" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>

        <!-- แสดงรูปภาพ -->
        <img id="additionalImage" src="ภาพประกอบเพลง.jpg" alt="Another Love Memory">

        <!-- ปุ่มเปิด/ปิด -->
        <button id="toggleButton" onclick="toggleLove()">💖Try clicking on it💖</button>

        <p id="message" style="font-size: 22px; color: #ff3385; font-weight: bold;"></p>

        <!-- รูปที่ซ่อนอยู่ -->
        <img id="loveImage" src="18BB3C2A-EC8C-4CE6-8F7F-66E8379153CD.jpg" alt="Our Love Memory">
    </div>

    <script>
        // ฟังก์ชันเปิด/ปิดข้อความและรูป
        function toggleLove() {
            var loveImage = document.getElementById("loveImage");
            var message = document.getElementById("message");
            var toggleButton = document.getElementById("toggleButton");

            if (loveImage.style.display === "none") {
                // แสดงข้อความและรูป
                loveImage.style.display = "block"; 
                setTimeout(() => {
                    loveImage.style.opacity = "1";
                }, 100);

                message.innerText = 
                    "🥰 You have replaced my nightmares with dreams, my worries with happiness, and my fears with love. ❤️\n\n"+ 
                    "คุณได้แทนที่ฝันร้ายของฉันด้วยความฝัน แทนที่ความกังวลด้วยความสุข และแทนที่ความกลัวด้วยความรัก\n\n"+ 
                    "💙&💚\n\n"+ 
                    "ขอบคุณนะ ที่เข้ามาเป็นคนรักของหนู ถึงแม้ว่าหนูจะแสดงความรักไม่ค่อยเก่ง แต่หนูได้เรียนรู้ความรักในอีกรูปแบบนึง\n\n"+ 
                    "ซึ่ง ณ ตอนนี้ความสัมพันธ์ก็เป็นไปได้ด้วยดี หวังว่าเราจะปรับตัวเข้าหากัน และคบกันไปนานๆ\n\n"+ 
                    "หนูอาจจะขี้หงุดหงิด แต่จริงๆ ในใจหนูไม่ได้มีอะไร และสุดท้ายนี้ลดน้ำหนักบ้างนะ 555 \n\n"+ 
                    "🐷 LOVE U GREEN MONKEY 🐵\n\n ";

                toggleButton.innerText = "🐱 Close 🐱"; // เปลี่ยนข้อความเป็นปิด
            } else {
                // ซ่อนข้อความและรูป
                loveImage.style.display = "none";
                message.innerText = "";
                toggleButton.innerText = "💖Try clicking on it💖"; // เปลี่ยนข้อความเป็นเปิด
            }
        }
    </script>

</body>
</html>
