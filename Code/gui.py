import subprocess
from customtkinter import *
from tkinter import filedialog, Label
from PIL import Image, ImageTk
import os
import glob
import time
import threading

app = CTk()
app.title("PII Detection and Masking Tool")
app.geometry("1280x720")
app.minsize(1280, 720)

doc_path = ""
latest_masked_doc_path = ""

frame = CTkFrame(master=app, height=300, width=450, border_width=2, corner_radius=20)
frame.pack(expand=True, fill='both')

alert_label = CTkLabel(
    master=app,
    text="Analyzing your document...",
    font=("Arial", 16),
    text_color="red"
)
alert_label.place_forget()

loading_canvas = CTkCanvas(master=app, width=100, height=100, bg="#2B2B2B", highlightthickness=0)
loading_canvas.place(relx=0.5, rely=0.35, anchor="center")
loading_arc = None
angle = 0
loading_canvas.place_forget()

def rotate_loader():
    global angle
    loading_canvas.delete("all")
    start_angle = angle
    extent_angle = 90
    loading_arc = loading_canvas.create_arc(
        10, 10, 90, 90,
        start=start_angle, extent=extent_angle, style='arc', outline="#FFCC70", width=5
    )
    angle = (angle + 50) % 360
    loading_canvas.after(50, rotate_loader)

def find_latest_masked_image(directory="temp", prefix="masked_doc"):
    search_pattern = os.path.join(directory, f"{prefix}*.jpg")
    list_of_files = glob.glob(search_pattern)
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def clear_previous_images():
    for widget in frame.winfo_children():
        widget.destroy()

def display_images(original_image_path, masked_image_path):
    clear_previous_images()

    original_image = Image.open(original_image_path)
    original_image.thumbnail((500, 500))  
    original_image_tk = ImageTk.PhotoImage(original_image)
    
    original_image_label = CTkLabel(
        master=frame,
        text="Original Image",
        font=("Arial", 16),
        text_color="#FFCC70"
    )
    original_image_label.place(relx=0.25, rely=0.9, anchor="center")
    
    original_image_widget = Label(frame, image=original_image_tk)
    original_image_widget.image = original_image_tk
    original_image_widget.place(relx=0.25, rely=0.55, anchor="center")

    masked_image = Image.open(masked_image_path)
    masked_image.thumbnail((500, 500))  
    masked_image_tk = ImageTk.PhotoImage(masked_image)
    
    masked_image_label = CTkLabel(
        master=frame,
        text="Masked Image",
        font=("Arial", 16),
        text_color="#FFCC70"
    )
    masked_image_label.place(relx=0.75, rely=0.9, anchor="center")
    
    masked_image_widget = Label(frame, image=masked_image_tk)
    masked_image_widget.image = masked_image_tk
    masked_image_widget.place(relx=0.75, rely=0.55, anchor="center")

def process_document():
    global doc_path
    global latest_masked_doc_path
    
    doc_path = filedialog.askopenfilename(
        initialdir="",
        title="Select a document",
        filetypes=(("jpg files", ".jpg"), ("png files", ".png"), ("pdf files", ".pdf"), ("all files", ".*"))
    )
    
    if not doc_path:
        alert_label.place_forget()
        loading_canvas.place_forget()
        return

    Python = r'C:\Users\mdana\OneDrive\Desktop\SIH\enviroment_venv\Scripts\python.exe'
    script_path = r'C:\Users\mdana\OneDrive\Desktop\SIH\code\pii_check.py'
    
    if not os.path.isfile(script_path):
        print(f"Error: The file {script_path} does not exist.")
        alert_label.place_forget()
        loading_canvas.place_forget()
        return
    
    alert_label.place(relx=0.5, rely=0.35, anchor="center")
    loading_canvas.place(relx=0.5, rely=0.5, anchor="center")
    rotate_loader()

    subprocess.run([Python, script_path, doc_path])

    while True:
        latest_masked_doc_path = find_latest_masked_image()
        if latest_masked_doc_path:
            break

    if latest_masked_doc_path:
        alert_label.place_forget()  
        loading_canvas.place_forget()  
        display_images(doc_path, latest_masked_doc_path)
    else:
        print("Error: No masked image found.")
        loading_canvas.place_forget()  

def click_handler():
    threading.Thread(target=process_document).start()

title_label = CTkLabel(
    master=app,
    text="PII DETECTION AND MASKING TOOL",
    font=("Arial", 20),
    text_color="#FFCC70"
)
title_label.place(relx=0.5, rely=0.1, anchor="center")

btn = CTkButton(
    master=app,
    text="Select a Document",
    command=click_handler,
    corner_radius=50,
    height=50,
    hover_color="white",
    text_color="black",
    font=("Arial Rounded MT Bold", 20),
    hover=True,
    fg_color="#FFCC70"
)
btn.place(relx=0.5, rely=0.25, anchor="center")

app.mainloop()
