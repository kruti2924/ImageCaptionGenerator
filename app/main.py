import os
os.environ['HF_HOME'] = 'D:/hf_cache'

from flask import Flask, render_template, request, jsonify
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
import torch

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()  # Load env vars

# Configure cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Make sure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image_url):
    raw_image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
    inputs = processor(raw_image, return_tensors="pt")

    with torch.no_grad():
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

    print("Generated caption:", caption)  # Debugging
    return caption

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    image = request.files['image']
    if image:
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(image)

        # Get URL of uploaded image
        image_url = upload_result.get("secure_url")

        # # Generate caption from image
        caption = generate_caption(image_url)

        # Dummy caption
        return jsonify({
            "caption": caption,
            "image_url": image_url
        })

    return jsonify({"error": "No image uploaded"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
