import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

if not firebase_admin._apps:
    # ชี้ไปยังพาธของไฟล์โดยตรง
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://sooksun-101-default-rtdb.firebaseio.com'
    })

st.success("เชื่อมต่อผ่านไฟล์ JSON สำเร็จแล้ว!")
