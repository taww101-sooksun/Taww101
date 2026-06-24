import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

st.set_page_config(page_title="Synapse AI")

st.title("🎨 Synapse AI Photo")

uploaded = st.file_uploader(
    "อัปโหลดรูป",
    type=["jpg", "png", "jpeg"]
)

if uploaded:

    image = Image.open(uploaded)

    st.image(image, caption="รูปต้นฉบับ")

    brightness = st.slider(
        "Brightness",
        0.5,
        2.0,
        1.0
    )

    blur = st.slider(
        "Blur",
        0,
        10,
        0
    )

    enhancer = ImageEnhance.Brightness(image)
    edited = enhancer.enhance(brightness)

    if blur > 0:
        edited = edited.filter(
            ImageFilter.GaussianBlur(blur)
        )

    st.image(
        edited,
        
