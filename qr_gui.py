import os
import tkinter as tk
from tkinter import filedialog, messagebox
import qrcode
from PIL import Image, ImageTk
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Google Drive Authentication
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

def upload_to_drive(file_path):
    """ Uploads a file to Google Drive and returns the sharable link. """
    if not file_path:
        return None

    try:
        file_drive = drive.CreateFile({'title': os.path.basename(file_path)})
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
        file_drive.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
        return file_drive['alternateLink']
    except Exception as e:
        messagebox.showerror("Upload Failed", f"Error uploading file: {e}")
        return None

def generate_qr(file_path):
    """ Generates a QR code from the uploaded file's link. """
    if not file_path:
        messagebox.showerror("Error", "No file selected!")
        return

    output_folder = "qr_codes"
    os.makedirs(output_folder, exist_ok=True)

    # Upload file and get URL
    file_url = upload_to_drive(file_path)
    if not file_url:
        return

    # Generate QR Code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(file_url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    # Save QR Code
    qr_filename = os.path.join(output_folder, f"{os.path.basename(file_path)}_qr.png")
    img.save(qr_filename)

    # Display QR Code
    display_qr(qr_filename)

    messagebox.showinfo("Success", f"QR Code saved at:\n{qr_filename}\nScanning will open the file!")

def display_qr(qr_path):
    """ Displays the generated QR code in the GUI. """
    img = Image.open(qr_path)
    img = img.resize((200, 200))
    img = ImageTk.PhotoImage(img)
    qr_label.config(image=img)
    qr_label.image = img

def browse_file():
    """ Opens a file dialog for selecting a file. """
    file_path = filedialog.askopenfilename()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def generate_qr_from_gui():
    """ Triggers the QR code generation process. """
    file_path = file_entry.get()
    generate_qr(file_path)

# GUI Setup
root = tk.Tk()
root.title("Cloud File to QR Code Generator")
root.geometry("400x400")
root.resizable(False, False)

tk.Label(root, text="Select a file:", font=("Arial", 12)).pack(pady=10)
file_entry = tk.Entry(root, width=40)
file_entry.pack(pady=5)
tk.Button(root, text="Browse", command=browse_file).pack(pady=5)
tk.Button(root, text="Generate QR Code", command=generate_qr_from_gui, bg="blue", fg="white").pack(pady=15)

qr_label = tk.Label(root)
qr_label.pack()

root.mainloop()
