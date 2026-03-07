<!DOCTYPE html>
<html>
<head>
    <title>Firebase Chat Demo</title>
    <style>
        #messages {
            border: 1px solid #ccc;
            height: 300px;
            overflow-y: scroll;
            padding: 10px;
            margin-bottom: 10px;
            font-family: sans-serif;
        }
        .message-item { margin-bottom: 5px; }
    </style>
</head>
<body>
    <h1>Realtime Chat with Firebase Firestore</h1>

    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="พิมพ์ข้อความของคุณ...">
    <button id="sendButton">ส่ง</button>

    <script type="module">
        // ใช้ Import แบบ Modular จาก CDN โดยตรง (เวอร์ชัน 10+)
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getFirestore, collection, addDoc, serverTimestamp, query, orderBy, onSnapshot } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

        // 1. ใส่ค่าของจริงที่นี่
        const firebaseConfig = {
            apiKey: "YOUR_API_KEY",
            authDomain: "YOUR_AUTH_DOMAIN",
            projectId: "YOUR_PROJECT_ID",
            storageBucket: "YOUR_STORAGE_BUCKET",
            messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
            appId: "YOUR_APP_ID"
        };

        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);
        const messagesCollection = collection(db, 'messages');

        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        // 2. ส่งข้อความ
        sendButton.addEventListener('click', async () => {
            const text = messageInput.value.trim();
            if (text) {
                try {
                    await addDoc(messagesCollection, {
                        text: text,
                        sender: "Anonymous User",
                        timestamp: serverTimestamp()
                    });
                    messageInput.value = ''; 
                } catch (error) {
                    console.error("Error writing document: ", error);
                }
            }
        });

        // 3. รับข้อความ Realtime
        const q = query(messagesCollection, orderBy('timestamp'));
        onSnapshot(q, (snapshot) => {
            messagesDiv.innerHTML = ''; 
            snapshot.forEach((doc) => {
                const message = doc.data();
                const messageElement = document.createElement('div');
                messageElement.classList.add('message-item');
                
                // เปลี่ยนข้อความตอนรอเซิร์ฟเวอร์ให้ดูสมจริงขึ้น
                const timestamp = message.timestamp ? new Date(message.timestamp.toDate()).toLocaleTimeString() : 'กำลังส่ง...';
                messageElement.textContent = `[${timestamp}] ${message.sender}: ${message.text}`;
                messagesDiv.appendChild(messageElement);
            });
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });
    </script>
</body>
</html>
