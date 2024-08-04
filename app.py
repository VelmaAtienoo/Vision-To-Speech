import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from gtts import gTTS
from TTS.api import TTS
import os
import requests

# Initialize the BLIP model and processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Initialize the TTS model for Twi
tts_model = TTS(model_name="tts_models/tw_asante/openbible/vits")

# Define the function to generate English captions
def generate_english_caption(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

# Define the function to translate text to Twi
def translate(text, target_language):
    ngrok_url = "https://9482-41-79-97-5.ngrok-free.app"  # Use the URL provided by ngrok
    url = f"{ngrok_url}/translate"
    headers = {"Content-Type": "application/json"}
    data = {
        "text": text,
        "to": target_language
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        try:
            response_json = response.json()
            return response_json["translatedText"]
        except KeyError:
            raise Exception(f"Key 'translatedText' not found in response: {response_json}")
    else:
        raise Exception(f"Translation failed: {response.status_code} {response.text}")

# Streamlit code for uploading and processing the image
st.title("Image Captioning and Translation")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

    # Generate English caption
    english_caption = generate_english_caption(uploaded_file)
    st.write("English Caption:", english_caption)

    # Translate English caption to Twi
    twi_caption = translate(english_caption, target_language="tw")
    st.write("Twi Caption:", twi_caption)

    # Generate Twi audio
    audio_path = f"{os.path.splitext(uploaded_file.name)[0]}_twi.wav"
    tts_model.tts_to_file(text=twi_caption, file_path=audio_path)
    st.write(f"Audio saved at {audio_path}")

    # Display the audio player
    st.audio(audio_path)
