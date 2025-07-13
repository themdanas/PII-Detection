from tkinter import *
import os
from pytesseract import Output
import subprocess

import pytesseract as pyt
import sys
from presidio_analyzer import AnalyzerEngine
from customtkinter import *
from tkinter import *
from langchain.schema import Document
import re
from langchain_experimental.data_anonymizer import PresidioReversibleAnonymizer
from presidio_analyzer import Pattern,PatternRecognizer
from customtkinter import *
import fitz  
print("\nAnalyzing text in the uploaded Document...\n" )


def import_doc_path():
    global doc_path
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]

if __name__ == "__main__":
    import_doc_path()

ext = os.path.splitext(doc_path)[-1].lower()
pyt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if ext == ".pdf":
    pdf = fitz.open(doc_path)

    def pdf_to_image(pdf_path, image_path):
        pdf_document = fitz.open(pdf_path)
        first_page = pdf_document.load_page(0)
        pix = first_page.get_pixmap(dpi=120)
        pix.save(image_path)

    pdf_file_path = doc_path
    output_image_path = 'temp/imagefrompdf.jpg'
    pdf_to_image(pdf_file_path, output_image_path)
            
    data = pyt.image_to_data(output_image_path, output_type=Output.DICT, lang= "eng+hin")
    confidence_threshold = 30
    extracted_text = ""

    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > confidence_threshold:
            text = data['text'][i]
            extracted_text += text + " "

    doc_path = output_image_path

else:
    data = pyt.image_to_data(doc_path, output_type=Output.DICT, lang= "eng+hin")
    confidence_threshold = 30
    extracted_text = ""

    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > confidence_threshold:
            text = data['text'][i]
            extracted_text += text + " "
    
analyzer = AnalyzerEngine()

def contains_pii(text):
    results = analyzer.analyze(text=text, entities=[], language='en')

    if results:
        return True
    else:
        return False

if contains_pii(extracted_text):
    app = CTk()
    app.title("")

    frame = CTkFrame(master=app, height= 150, width= 350, border_width= 2, corner_radius=20)
    frame.pack(expand=True)

    def click_handler():
        app.quit()
        Python = r'C:\Users\mdana\OneDrive\Desktop\SIH\enviroment_venv\Scripts\python.exe'
        subprocess.run([(Python), "code/pii_mask.py", doc_path] )

    btn = CTkButton(
        master=app, 
        text="Mask PII data and save Document", 
        command=click_handler,
        corner_radius=20, 
        height=40, 
        hover_color="white", 
        text_color="black", 
        font=("Arial Rounded MT Bold", 15), 
        hover=True,
        fg_color="#FFCC70",
    )
    btn.place(relx=0.5, rely=0.55, anchor="center")

    path_label = CTkLabel(app, text = "PII data found in the document.", fg_color="transparent", text_color= "red", font =("arial",15))
    path_label.place(relx=0.5, rely=0.2, anchor="center")

    print(extracted_text)
    print("\nFinding and Anonymizing detected PII data...\n")

    Documents =[Document(page_content=extracted_text)]

    def colored_pii(string):
        colored_string = re.sub(
            r"(<[^>]*>)", lambda m: "\033[31m" + m.group(1) + "\033[0m",
        string        
        )
        return colored_string

    anonymizer = PresidioReversibleAnonymizer(
        add_default_faker_operators = False
    )

    time_pattern = Pattern(
        name="time_pattern",
        regex=r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?(?:\s?[APap][Mm])?\b',
        score=1
    )
    dob_pattern = Pattern(
        name="dob_pattern",
        regex=r'\b(?:\d{2}[\/\-\.\s]\d{2}[\/\-\.\s]\d{4}|\d{4}[\/\-\.\s]\d{2}[\/\-\.\s]\d{2})\b',
        score=1
    )
    pan_number_pattern = Pattern(
        name="pan_number_pattern",
        regex="[A-Z]{5}[0-9]{4}[A-Z]{1}",
        score=1  
    )
    aadhaar_number_pattern = Pattern(
        name="aadhaar_number_pattern",
        regex= r'\b\d{4} \d{4} \d{4}\b',
        score=1
    )
    gender_pattern = Pattern(
        name="gender_pattern",
        regex=r'\b(?:male|female)\b',
        score=1
    )

    time_recognizer = PatternRecognizer(
        supported_entity="TIME", patterns=[time_pattern]
    )
    dob_recognizer = PatternRecognizer(
        supported_entity="DOB", patterns=[dob_pattern]
    )
    pan_card_recognizer = PatternRecognizer(
        supported_entity="PAN_NUMBER", patterns=[pan_number_pattern]
    )
    aadhaar_card_recognizer =PatternRecognizer(
        supported_entity="AADHAAR_NUMBER", patterns=[aadhaar_number_pattern]
    )
    gender_recognizer =PatternRecognizer(
        supported_entity="GENDER", patterns=[gender_pattern]
    )

    anonymizer.add_recognizer(time_recognizer)
    anonymizer.add_recognizer(dob_recognizer)
    anonymizer.add_recognizer(pan_card_recognizer)
    anonymizer.add_recognizer(aadhaar_card_recognizer)
    anonymizer.add_recognizer(gender_recognizer)

    anonymizer.reset_deanonymizer_mapping()

    colored_text =colored_pii(anonymizer.anonymize(extracted_text))
    print(colored_text)

    app.quit()
    app.mainloop()

else:
    app = CTk()
    app.title("")

    frame = CTkFrame(master=app, height= 150, width= 350, border_width= 2, corner_radius=20)
    frame.pack(expand=True)

    path_label = CTkLabel(app, text = "No PII data found in the document.", fg_color="transparent", text_color= "green", font =("arial",15))
    path_label.place(relx=0.5, rely=0.5, anchor="center")

    app.quit()
    app.mainloop()