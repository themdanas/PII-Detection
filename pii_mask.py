import pytesseract as pyt
from PIL import Image, ImageDraw, ImageFont
import cv2
import re
import sys
import os
from datetime import datetime

def import_doc_path():
    global doc_path
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]

if __name__ == "__main__":
    import_doc_path()

# Generate a unique filename with a timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
masked_doc_path = f"temp/masked_doc_{timestamp}.jpg"

pyt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def edit_text_in_image(image_path, output_path, patterns_and_replacements, confidence_threshold):
    image = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    data = pyt.image_to_data(img_rgb, output_type=pyt.Output.DICT)

    img_pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img_pil)

    text_boxes = []
    accumulated_text = ""

    for i, text in enumerate(data['text']):
        if text.strip() != "":
            confidence = int(data['conf'][i])
            if confidence >= confidence_threshold:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                text_boxes.append((text, x, y, w, h))
                accumulated_text += text + " "

    for pattern, replacement in patterns_and_replacements:
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        if compiled_pattern.search(accumulated_text):
            for text, x, y, w, h in text_boxes:
                if compiled_pattern.search(text):
                    draw.rectangle([x, y, x+w, y+h], fill='black')
                    if replacement:
                        font = ImageFont.load_default()
                        draw.text((x, y), replacement, font=font, fill='red')
                    
    img_pil.save(output_path)

patterns_and_replacements = [
    ("[A-Z]{5}[0-9]{4}[A-Z]{1}", '<PAN_NUMBER>'),
    (r'\b(?:\d{2}[\/\-\.\s]\d{2}[\/\-\.\s]\d{4}|\d{4}[\/\-\.\s]\d{2}[\/\-\.\s]\d{2})\b', '<DOB>'),
    (r'\b\d{4} \d{4} \d{4}\b', '<AADHAAR_NUMBER>'),
    ("[0-9]{11}", '<DRIVING_LICENSE_NUMBER>'),
    ("[A-Z]{2}[0-9]{2}", '<DRIVING>'),
    ("[0-9]{4}", '<HIDDEN>')
]

edit_text_in_image(doc_path, masked_doc_path, patterns_and_replacements, 10)

print(masked_doc_path) 
