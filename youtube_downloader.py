import os
import threading
from tkinter import *
from tkinter import ttk, filedialog
from pytube import YouTube

def progress_tracker(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    progress_var.set(f"Downloading: {percentage:.2f}% complete")
    window.update_idletasks()

def load_options_threaded():
    global available_streams
    url_button.config(state=DISABLED)
    download_button.config(state=DISABLED)
    options_combobox.config(state=DISABLED)
    status_var.set("Loading available streams...")
    window.update_idletasks()

    video_url = url_entry.get()
    yt = YouTube(video_url)
    available_streams = yt.streams

    if audio_only_var.get():
        available_streams = available_streams.filter(only_audio=True)
    else:
        available_streams = available_streams.filter(file_extension='mp4')

    options = [f"{stream.resolution} - {stream.mime_type}" for stream in available_streams]
    options_combobox["values"] = options
    options_combobox.current(0)

    status_var.set("")
    url_button.config(state=NORMAL)
    options_combobox.config(state="readonly")


def load_options():
    threading.Thread(target=load_options_threaded).start()


def on_option_selected(event):
    if options_combobox.current() > -1:
        download_button.config(state=NORMAL)
    else:
        download_button.config(state=DISABLED)

def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, END)
    folder_entry.insert(0, folder_path)

def download_video():
    destination_folder = folder_entry.get()
    stream = available_streams[options_combobox.current()]

    # Create a new YouTube object with the same URL and the progress_callback
    yt = YouTube(url_entry.get(), on_progress_callback=progress_tracker)
    stream = yt.streams.get_by_itag(stream.itag)

    stream.download(output_path=destination_folder)
    progress_var.set("Download complete!")
    window.update_idletasks()

window = Tk()
window.title("YouTube Video Downloader")

url_label = Label(window, text="YouTube video URL:")
url_label.grid(row=0, column=0, sticky=W, pady=(10, 5))
url_entry = Entry(window, width=50)
url_entry.grid(row=1, column=0, padx=(10, 10), pady=5)
url_button = Button(window, text="Select the quality", command=load_options_threaded)
url_button.grid(row=1, column=1, padx=(0, 10), pady=5)

options_label = Label(window, text="Quality options:")
options_label.grid(row=2, column=0, sticky=W, padx=(10, 10), pady=(10, 5))
options_combobox = ttk.Combobox(window, width=48, state="readonly")
options_combobox.grid(row=3, column=0, padx=(10, 10), pady=5)
options_combobox.bind("<<ComboboxSelected>>", on_option_selected)

folder_label = Label(window, text="Destination folder:")
folder_label.grid(row=4, column=0, sticky=W, padx=(10, 10), pady=(10, 5))
folder_entry = Entry(window, width=50)
folder_entry.grid(row=5, column=0, padx=(10, 10), pady=5)
folder_button = Button(window, text="Browse", command=browse_folder)
folder_button.grid(row=5, column=1, padx=(0, 10), pady=5)

audio_only_var = BooleanVar()
audio_only_check = Checkbutton(window, text="Download audio only", variable=audio_only_var, command=load_options_threaded)
audio_only_check.grid(row=6, column=0, padx=(10, 10), pady=(10, 5))

download_button = Button(window, text="Download", command=download_video, state=DISABLED)
download_button.grid(row=7, column=0, padx=(10, 10), pady=(10, 5))

progress_var = StringVar()
progress_label = Label(window, textvariable=progress_var)
progress_label.grid(row=8, column=0, padx=(10, 10), pady=(10, 5))

status_var = StringVar()
status_label = Label(window, textvariable=status_var)
status_label.grid(row=9, column=0, padx=(10, 10), pady=(10, 5))

window.mainloop()

