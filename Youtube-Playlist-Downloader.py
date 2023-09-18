import customtkinter
from CTkMessagebox import CTkMessagebox
import os
from pytube import YouTube
import requests
import re
import threading
import webbrowser
import time
import datetime
from tkinter import *
from tkinter import PhotoImage
from PIL import Image
from tkinter import ttk



current_mode = "dark"

def switches_mode():
    global current_mode
    if current_mode == "dark":
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")
        current_mode = "light"
    else:
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        current_mode = "dark"
        
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}


SAVEPATH = ""



root = customtkinter.CTk()
root.geometry("1000x500")
root.resizable(False,False)
root.title("YouTube Playlist Downloader - By SaNd4StOrM")
root.iconbitmap('img/icon-youtube1.ico')

fontlabel1 = customtkinter.CTkFont(family="Cascadia Mono ExtraLight", size=16)
fontlabel2 = customtkinter.CTkFont(family="Cascadia Mono ExtraLight", size=12)

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=35, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Put URL for the playlist you would like to download\n I only support 360p & 720p", font=fontlabel1)
label.pack(pady=10, padx=10)

Enrty_GetUrl = customtkinter.CTkEntry(master=frame, width=550, placeholder_text="Playlist URL", font=fontlabel1)
Enrty_GetUrl.pack(pady=10)

res_comobox1 = customtkinter.CTkComboBox(master=frame, values=["360p", "720p"], font=fontlabel1)
res_comobox1.pack(pady=10)


def link_snatcher(url):
    our_links = []

    try:
        res = requests.get(url, headers=headers)
    except:
        CTkMessagebox(title="Info", message="No internet connection")
        
        return False

    plain_text = res.text

    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]
    else:
        CTkMessagebox(title="Info", message="Incorrect Playlist URL")
        return False

    tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
    mat = re.findall(tmp_mat, plain_text)

    for m in mat:
        new_m = m.replace('&amp;', '&')
        work_m = 'https://youtube.com/' + new_m

        if work_m not in our_links:
            our_links.append(work_m)

    return our_links

def foldertitle(url):
    try:
        res = requests.get(url, headers=headers)
    except:
        CTkMessagebox(title="Info", message="No internet connection")
        return False

    plain_text = res.text

    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]
    else:
        CTkMessagebox(title="Info", message="Incorrect Playlist URL")
        return False

    playlist_title_match = re.search(r'<title>(.*?) - YouTube</title>', plain_text)
    if playlist_title_match:
        playlist_title = playlist_title_match.group(1)
    else:
        CTkMessagebox(title="Info", message="Playlist title not found")

    return playlist_title

def open_url(url):
    webbrowser.open(url)

new_folder_checkbox = customtkinter.CTkCheckBox(master=frame, text="Create new folder for playlist", font=fontlabel1)
new_folder_checkbox.select()
new_folder_checkbox.pack(pady=10)

def download_video():
    url = Enrty_GetUrl.get()
    user_resolution = res_comobox1.get()
    def download_in_thread():

        BASE_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')
        our_links = link_snatcher(url)

        if new_folder_checkbox.get():
            unique_folder_name = foldertitle(url)[:7] + "_" + str(time.time()).replace(".", "")
        else:
            unique_folder_name = foldertitle(url)[:7]

        new_folder_dir = os.path.join(BASE_DIR, unique_folder_name)
        
        try:
            os.mkdir(new_folder_dir)
        except:
            CTkMessagebox(title="Info", message="Folder already exists")

        os.chdir(new_folder_dir)

        SAVEPATH = os.getcwd()
        CTkMessagebox(title="Info", message=f'Files will be saved to {SAVEPATH}')

        x = []
        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                pathh = os.path.join(root, name)
                if os.path.getsize(pathh) < 1:
                    os.remove(pathh)
                else:
                    x.append(str(name))
        download_status_label.configure(text='Connecting...')

        for link in our_links:
            try:
                yt = YouTube(link)
                main_title = yt.title
                main_title = main_title + '.mp4'
                main_title = main_title.replace('|', '')
            except:
                download_status_label.configure(text='Connection problem..unable to fetch video info')
                break
            if main_title not in x:
                vid = yt.streams.filter(progressive=True, file_extension='mp4', res=user_resolution).first()
                if vid is None and user_resolution == '720p':
                    vid = yt.streams.filter(progressive=True, file_extension='mp4', res='360p').first()
                if vid is not None:
                    download_status_label.configure(text=f'Downloading {vid.default_filename} and its file size -> {round(vid.filesize / (1024 * 1024), 2)} MB.')
                    vid.download(SAVEPATH)
                    download_status_label.configure(text=f'Download of {vid.default_filename} completed.')
                else:
                    download_status_label.configure(text='No video stream found that matches the selected resolution')
                    
            else:
                download_status_label.configure(text=f'Skipping "{main_title}" video')
        download_status_label.configure(text='Downloading finished')
        CTkMessagebox(title="Info", message=f'All your videos are saved at --> {SAVEPATH}')


    download_thread = threading.Thread(target=download_in_thread)
    download_thread.start()

button_frame = customtkinter.CTkFrame(master=frame)
button_frame.pack(pady=10)

download_button = customtkinter.CTkButton(master=button_frame, text="Download", font=fontlabel1, command=download_video)
download_button.grid(row=0, column=0, pady=10, padx=(0, 50))

download_status_label = customtkinter.CTkLabel(master=frame, text="", font=fontlabel2)
download_status_label.pack()

def open_folder():
    global SAVEPATH
    os.startfile(SAVEPATH)

open_folder_button = customtkinter.CTkButton(master=button_frame, text="Open Folder", font=fontlabel1, command=open_folder)
open_folder_button.grid(row=0, column=10, pady=4)


framebuttons = customtkinter.CTkFrame(master=frame)
framebuttons.pack(pady=30)

IMAGE_WIDTH = 20
IMAGE_HEIGHT = 20


facebook_ico = customtkinter.CTkImage(light_image=Image.open(os.path.join("img/4202110_facebook_logo_social_social media_icon.png")), size=(IMAGE_WIDTH , IMAGE_HEIGHT))
whatsapp_ico = customtkinter.CTkImage(light_image=Image.open(os.path.join("img/5296520_bubble_chat_mobile_whatsapp_whatsapp logo_icon.png")), size=(IMAGE_WIDTH , IMAGE_HEIGHT))
telegram_ico = customtkinter.CTkImage(light_image=Image.open(os.path.join("img/4102591_applications_media_social_telegram_icon.png")), size=(IMAGE_WIDTH , IMAGE_HEIGHT))



facebook_ico_button = customtkinter.CTkButton(master=framebuttons, text="Facebook", image=facebook_ico, cursor="hand2")
whatsapp_ico_button = customtkinter.CTkButton(master=framebuttons, text="WhatsApp", image=whatsapp_ico, cursor="hand2")
telegram_ico_button = customtkinter.CTkButton(master=framebuttons, text="Telegram", image=telegram_ico, cursor="hand2")

facebook_ico_button.pack(side=LEFT, padx=5, pady=5)
whatsapp_ico_button.pack(side=LEFT, padx=5, pady=5)
telegram_ico_button.pack(side=LEFT, padx=5, pady=5)

facebook_ico_button.bind("<Button-1>", lambda e:open_url("https://www.facebook.com/hossam.omar.3192"))
whatsapp_ico_button.bind("<Button-1>", lambda e:open_url("https://wa.me/201095280572"))
telegram_ico_button.bind("<Button-1>", lambda e:open_url("https://t.me/+gAQ0s6FH0o05NWM8"))



mode_button = customtkinter.CTkSwitch(master=frame, text="Light / Dark", command=switches_mode)
mode_button.pack(side=LEFT, padx=5, pady=5)


root.mainloop()