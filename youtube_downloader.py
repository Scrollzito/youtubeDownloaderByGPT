import os
import threading
import time
from tkinter import *
from tkinter import ttk, filedialog
from pytube import YouTube
import customtkinter as ctk
from tkinter import messagebox

def format_filesize(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1048576:
        return f"{size / 1024:.2f} KB"
    elif size < 1073741824:
        return f"{size / 1048576:.2f} MB"
    else:
        return f"{size / 1073741824:.2f} GB"

def progress_tracker(stream, chunk, bytes_remaining):
    global start_time
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    elapsed_time = time.time() - start_time
    download_speed = bytes_downloaded / elapsed_time

    if download_speed < 1048576:
        speed_str = f"{download_speed / 1024:.2f} KB/s"
    else:
        speed_str = f"{download_speed / 1048576:.2f} MB/s"

    percentage = (bytes_downloaded / total_size) * 100
    progress_var.set(f"Downloading: {bytes_downloaded / 1048576:.2f}MB / {total_size / 1048576:.2f}MB ({percentage:.2f}% complete) - Speed: {speed_str}")
    window.update_idletasks()

def size_readable(size):
    if size < 1048576:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / 1048576:.2f} MB"

def load_options_threaded():
    global available_streams
    load_button.configure(state=DISABLED)
    download_button.configure(state=DISABLED)
    options_combobox.configure(state=DISABLED)
    status_var.set("Loading available streams...")
    window.update_idletasks()

    video_url = url_entry.get()
    yt = YouTube(video_url)
    available_streams = yt.streams

    if audio_only_var.get():
        available_streams = available_streams.filter(only_audio=True)
    else:
        available_streams = available_streams.filter(file_extension='mp4')

    available_streams = sorted(available_streams, key=lambda x: x.filesize if x.filesize else 0, reverse=True)

    options = [f"{stream.resolution} - {stream.mime_type} - {stream.codecs} - {format_filesize(stream.filesize)}" for stream in available_streams]
    options_combobox["values"] = options
    options_combobox.current(0)

    status_var.set("")
    load_button.configure(state=NORMAL)
    options_combobox.configure(state="readonly")



def load_options():
    if not url_entry.get():
        messagebox.showerror("Error", "Please enter a valid YouTube video URL.")
    else:
        threading.Thread(target=load_options_threaded).start()


def on_option_selected(event):
    if options_combobox.current() > -1:
        download_button.configure(state=NORMAL)
    else:
        download_button.configure(state=DISABLED)

def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, END)
    folder_entry.insert(0, folder_path)

def download_video_threaded():
    threading.Thread(target=download_video).start()

def download_video():
    global start_time
    destination_folder = folder_entry.get()
    stream = available_streams[options_combobox.current()]

    yt = YouTube(url_entry.get(), on_progress_callback=progress_tracker)
    stream = yt.streams.get_by_itag(stream.itag)

    start_time = time.time()
    stream.download(output_path=destination_folder)
    progress_var.set("Download complete!")
    window.update_idletasks()

def refresh_options():
    load_options_threaded()

window = Tk()
window.title("YouTube Video Downloader")

url_label = Label(window, text="YouTube video URL:")
url_label.grid(row=0, column=0, sticky=W, pady=(10, 5))
url_entry = ctk.CTkEntry(window, width=50)
url_entry.grid(row=1, column=0, padx=(10, 10), pady=5, sticky=W+E)

# Set the weight of column 0 to 1 so that the URL input takes up the available width
window.columnconfigure(0, weight=1)

audio_only_var = BooleanVar()
audio_only_check = Checkbutton(window, text="Download audio only", variable=audio_only_var)
audio_only_check.grid(row=2, column=0, padx=(10, 10), pady=(10, 5))

load_button = ctk.CTkButton(window, text="Load options", command=load_options)
load_button.grid(row=3, column=0, padx=(10, 10), pady=(10, 5))

options_label = Label(window, text="Quality options:")
options_label.grid(row=4, column=0, sticky=W, padx=(10, 10), pady=(10, 5))
options_combobox = ttk.Combobox(window, width=48, state="readonly")
options_combobox.grid(row=5, column=0, padx=(10, 10), pady=5)
options_combobox.bind("<<ComboboxSelected>>", on_option_selected)

folder_label = Label(window, text="Destination folder:")
folder_label.grid(row=6, column=0, sticky=W, padx=(10, 10), pady=(10, 5))
folder_entry = ctk.CTkEntry(window, width=50)
folder_entry.grid(row=7, column=0, padx=(10, 10), pady=5, sticky=W+E)
folder_button = ctk.CTkButton(window, text="Browse", command=browse_folder)
folder_button.grid(row=7, column=1, padx=(0, 10), pady=5)

window.columnconfigure(0, weight=1)

download_button = ctk.CTkButton(window, text="Download", command=download_video_threaded, state=DISABLED)
download_button.grid(row=8, column=0, padx=(10, 10), pady=(10, 5))

progress_var = StringVar()
progress_label = Label(window, textvariable=progress_var)
progress_label.grid(row=9, column=0, padx=(10, 10), pady=(10, 5))

status_var = StringVar()
status_label = Label(window, textvariable=status_var)
status_label.grid(row=10, column=0, padx=(10, 10), pady=(10, 5))

window.mainloop()

