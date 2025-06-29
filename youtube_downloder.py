import requests.exceptions
from yt_dlp import YoutubeDL
import os
import subprocess
import customtkinter as ctk
import time
from PIL import Image
import tkinter
import threading
import requests
import shutil
import ctypes


Video_Quality = {'指定なし(最高)':'',
                 '480p':'[height<=480]',
                 '720p':'[height<=720]',
                 '1080p':'[height<=1080]',
                 '2k(1440p)':'[height<=1440]',
                 '4k(2160p)':'[height<=2160]'}

Video_Codec = {'指定なし(最高)':'',
               'av01':'[vcodec*=av01]',
               'vp9':'[vcodec*=vp9]',
               'vp09':'[vcodec*=vp09]',
               'avc1':'[vcodec*=avc1]'}

class tube_sync(ctk.CTk):

    #current directory
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):

        #initialize application
        #file check
        #log
        self.log_path = os.path.join(self.CURRENT_PATH, 'log')
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log_path = os.path .join(self.log_path, time.strftime("%Y_%m_%d_%H%M%S", time.localtime())) + ".log"
        self.wlog("TubuSync started")

        self.wlog("checking files...")

        #source
        self.source_path = os.path.join(self.CURRENT_PATH, 'source')
        if not os.path.exists(self.source_path):
            self.wlog("make source directory")
            os.makedirs(self.source_path)
        else:
            self.wlog("source loaded successfully")

        #logo
        self.logo_path = os.path.join(self.source_path, 'logo.png')
        if not os.path.exists(self.logo_path):
            self.wlog("failed to load logo.png")

            self.wlog("download logo.png in source directory")
            self.download_image("https://raw.githubusercontent.com/Meron530/youtube/main/source/logo.png", self.logo_path)
            self.wlog("logo.png downloaded successfully")

        else:
            self.wlog("logo.png loaded successfully")

        #start image
        self.start_png_path = os.path.join(self.source_path, 'start.png')
        if not os.path.exists(self.start_png_path):
            self.wlog("failed to load start.png")
            
            self.wlog("download start.png in source directory")
            self.download_image("https://raw.githubusercontent.com/Meron530/youtube/main/source/start.png", self.start_png_path)
            self.wlog("start.png downloaded successfully")

        else:
            self.wlog("start.png loaded successfully")

        self.wlog("checking files completed successfully")

        #initialize customtkinter
        self.wlog("customtkinter initializing...")

        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.wlog("customtkinter initialized successfully")

        #load tkinter
        self.wlog("setting up tkinter...")

        self.title("TubuSync")
        self.icon_change(self.logo_path)
        
        self.grid_rowconfigure(0,weight=0)
        self.grid_columnconfigure(0,weight=0)

        self.start_frame = ctk.CTkFrame(self, width=500, height=500)
        self.start_canvas = ctk.CTkCanvas(self.start_frame, width=500, height=500)

        self.start_photo = ctk.CTkImage(Image.open(self.start_png_path),size=(500,500))
        self.start_label = ctk.CTkLabel(self.start_canvas, text="",image=self.start_photo,width=500,height=500)
        self.start_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.start_canvas.grid(row=0,column=0)

        self.start_progress = ctk.CTkProgressBar(self.start_canvas, width=400, mode='indeterminate', progress_color="cyan")
        self.start_progress.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)
        self.start_progress.start()

        self.start_frame.grid(row=0,column=0)

        self.update()

        self.wlog("tkinter initialized successfully")

        t = threading.Thread(target=self.wedget)
        t.start()

    def wedget(self):

        self.wlog("\n===========\nsetting up wedget...")

        #file check
        #ffmpeg
        self.ffmpeg_path = os.path.join(self.source_path, 'ffmpeg')
        if not os.path.exists(self.ffmpeg_path):
            self.wlog("failed to check ffmpeg")

            self.wlog("download ffmpeg in source directory")
            self.download_zip('https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip', self.ffmpeg_path + '.zip')
            os.rename(self.ffmpeg_path + '-master-latest-win64-gpl-shared', self.ffmpeg_path)
            self.wlog("ffmpeg downloaded successfully")

        else:
            self.wlog("ffmpeg check successfully")


        #set resize
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #Main Frame
        self.main_frame = ctk.CTkFrame(self, width=1080, height=720)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0,weight=1)
        self.main_frame.grid_columnconfigure(1,weight=1)

        #URL Frame
        self.url_frame = ctk.CTkFrame(self.main_frame)
        self.url_frame.grid(row=0,column=0,padx=20, pady=20, sticky=ctk.NSEW)
        self.url_frame.grid_columnconfigure(0, weight=1)
        self.url_frame.grid_rowconfigure(0, weight=1)

        self.url_ScrollFrame = ctk.CTkScrollableFrame(self.url_frame,width=600,height=320)
        self.url_ScrollFrame.grid(row=0, column=0, padx=10, pady=20, sticky=ctk.NSEW)
        self.url_ScrollFrame.grid_columnconfigure(0, weight=1)

        self.url_add_button = ctk.CTkButton(self.url_frame, text="+追加",command=self.add_box)
        self.url_add_button.grid(row=1,column=0,padx=20,pady=10, sticky=ctk.EW)
        self.url_boxes = []
        
        self.url_remove_button = ctk.CTkButton(self.url_frame, text="-削除",command=self.remove_box,fg_color="#b22222")
        self.url_remove_button.grid(row=2,column=0,padx=20,pady=10, sticky=ctk.EW)
        
        self.output_button = ctk.CTkButton(self.url_frame,text="ダウンロード",command=self.download_video)
        self.output_button.grid(row=3,column=0,padx=20,pady=10, sticky=ctk.EW)

        self.output_file_button = ctk.CTkButton(self.url_frame,text="ダウンロード先ファイル",command=self.explorer_open)
        self.output_file_button.grid(row=4,column=0,padx=20,pady=10, sticky=ctk.EW)

        #Video Frame
        self.video_frame = ctk.CTkFrame(self.main_frame)
        self.video_frame.grid(row=0,column=1,padx=20, pady=20, sticky=ctk.NSEW)
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)

        self.video_image_frame = ctk.CTkFrame(self.video_frame)
        self.video_image_frame.grid(row=0,column=0,padx=20,pady=20, sticky=ctk.NE+ctk.EW)
        
        self.video_image_label = ctk.CTkLabel(self.video_image_frame, text="", width=720 / 1.3, height=480 / 1.3)
        self.video_image_label.grid(row=0,column=0,sticky=ctk.NSEW)
        self.Video_Name_label = ctk.CTkLabel(self.video_image_frame, text="", font=ctk.CTkFont(size=15, weight="bold"), width=720 / 1.3)
        self.Video_Name_label.grid(row=1,column=0,sticky=ctk.EW)

        self.video_info_frame = ctk.CTkFrame(self.video_frame)
        self.video_info_frame.grid(row=1,column=0,padx=20,pady=20, sticky=ctk.NSEW)
        self.video_info_frame.grid_rowconfigure(0,weight=1)
        self.video_info_frame.grid_columnconfigure(0,weight=1)

        self.video_label = ctk.CTkLabel(self.video_info_frame,text='ビデオ画質', width=720 / 1.3)
        self.video_label.grid(row=0,column=0)

        self.video_option = ctk.CTkComboBox(self.video_info_frame, values=list(Video_Quality.keys()), width=500)
        self.video_option.grid(row=1,column=0)

        self.video_label = ctk.CTkLabel(self.video_info_frame,text='コーデック')
        self.video_label.grid(row=2,column=0)

        self.video_codec_option = ctk.CTkComboBox(self.video_info_frame, values=list(Video_Codec.keys()),width=500)
        self.video_codec_option.set("vp09")
        self.video_codec_option.grid(row=3,column=0)

        self.switch_label = ctk.CTkLabel(self.video_info_frame)
        self.switch_label.grid(row=4,column=0, sticky=ctk.EW, padx=10, pady=10)

        self.darkmode_switch_var = ctk.StringVar(value="on")
        self.darkmode_switch = ctk.CTkSwitch(self.switch_label,text='ダークモード', command=self.darkmode_switch_event,variable=self.darkmode_switch_var, onvalue="on", offvalue="off")
        self.darkmode_switch.grid(row=0,column=0)

        self.mp3_switch_var = ctk.StringVar(value="off")
        self.mp3_switch = ctk.CTkSwitch(self.switch_label,text='mp3形式にする(最高音質のみ)',variable=self.mp3_switch_var, onvalue="on", offvalue="off")
        self.mp3_switch.grid(row=0,column=1)

        time.sleep(2)
        self.main_frame.grid(row=0,column=0, sticky=ctk.NSEW)

        self.wlog("wedget initialized successfully")
        self.wlog("\n===========\n")

    #image download
    def download_image(self, url, path):

        try:

            r = requests.get(url, timeout=10)
            r.raise_for_status()

            if r.headers['Content-Type'] != 'image/png':
                self.wlog(f'failed to download {url}, content type is not image/png')
                exit()
            
            with open(path, 'wb') as f:
                    f.write(r.content)

        except requests.exceptions.HTTPError as e:
                self.wlog("HTTPError: " + str(e))
                self.quit()

    #zip download
    def download_zip(self, url, path):

        try:

            r = requests.get(url, timeout=10)
            r.raise_for_status()

            with open(path, 'wb') as f:
                f.write(r.content)

            #unzip
            shutil.unpack_archive(path, self.source_path, 'zip')
            os.remove(path)
        
        except requests.exceptions.HTTPError as e:
                self.wlog("HTTPError: " + str(e))
                self.quit()

    #ダークモードボタン
    def darkmode_switch_event(self):
        if self.darkmode_switch.get() == "on":
            ctk.set_appearance_mode("dark")
            self.update()
        else:
            ctk.set_appearance_mode("light")
            self.update()

    def add_box(self):
        box = ctk.CTkEntry(self.url_ScrollFrame)
        box.grid(row=len(self.url_boxes),column=0,pady=3,padx=10, sticky=ctk.EW)
        self.url_boxes.append(box)
        
    def remove_box(self):
        if(len(self.url_boxes) > 0):
            box = self.url_boxes.pop(-1)
            box.destroy()

    #start download thread
    def download_video(self):

        self.video_download_bar = ctk.CTkProgressBar(self.video_image_frame, width=720 / 1.3, mode='determinate', progress_color=("cyan", "gray"))
        self.video_download_bar.grid(row=2,column=0,sticky=ctk.EW)

        download_thread = threading.Thread(target=self.download_video_thread)
        download_thread.start()


    #ダウンロード
    def download_video_thread(self):

        self.video_download_bar.start()

        self.output_button.configure(text="ダウンロード中...")
        self.update()

        path = os.getcwd()
        download_path = os.getcwd()

        # 環境変数の設定
        path = os.path.join(path, r'source\ffmpeg\bin')
        os.environ['PATH'] = path

        # os.system('ffmpeg')
        subprocess.call('ffmpeg')

        video_option_text = Video_Quality[self.video_option.get()]
        video_ccodec_option_text = Video_Codec[self.video_codec_option.get()]

        Video_len = len(self.url_boxes)
        Video_Num = 0

        for url_box in self.url_boxes:

            Video_Num += 1
            URL_PATH = url_box.get()

            ydl_opts = {
                'writethumbnail': True,
                'outtmpl' : download_path + '/output/' + '%(title)s',
                'skip_download': True,
                'nooverwrites': True
            }

            title = ""
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(URL_PATH, download=False)
                title = info.get('title', None)
                ydl.download([URL_PATH])

            #display thumbnail
            #self.image_label = ctk.CTkLabel(self.video_image_frame, text="", image=ctk.CTkImage(Image.open(download_path + '/output/' + title + '.webp'), size=(720 / 1.3, 480 / 1.3)))
            self.video_image_label.configure(image=ctk.CTkImage(Image.open(download_path + '/output/' + title + '.webp'), size=(720 / 1.3, 480 / 1.3)))
            self.Video_Name_label.configure(text=title)

            #最高の画質と音質を動画をダウンロードする
            if self.mp3_switch.get() == "on":
                ydl_opts = {'format': 'bestaudio/best',
                            'postprocessors': [
                                {'key': 'FFmpegExtractAudio',
                                 'preferredcodec': 'mp3',
                                 'preferredquality': '192'},
                                {'key': 'FFmpegMetadata'},
                            ],
                            'outtmpl': download_path + '%(title)s'}
            else:
                ydl_opts = {'format': 'bestvideo[ext=mp4]' + video_option_text + video_ccodec_option_text + '+bestaudio[ext=mp4]' + video_option_text,
                            'outtmpl': download_path + '/output/' + '%(title)s'}

            self.output_button.configure(text="ダウンロード中..." + " (" + str(Video_Num) + "/" + str(Video_len) +")")
            self.update()

            self.output_button.configure(text="ダウンロード失敗")

            #動画のURLを指定
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([URL_PATH])

            self.video_image_label.configure(image=None)
            os.remove(download_path + '/output/' + title + '.webp')
            self.Video_Name_label.configure(text="")

        self.output_button.configure(text="ダウンロード終了")
        self.video_download_bar.destroy()

    #write for log
    def wlog(self, text):
        with open(self.log_path, 'a') as f:
            f.write(text + '\n')

    #subprocessのファイルオープン
    def explorer_open(self):
        file_path = os.getcwd()
        subprocess.Popen(['explorer', file_path + r'\output'])

    #CustomTkinter独自のアイコン変更
    def icon_change(self,path):
        myappid = u'meron.tubesync.youtube.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


        self.iconphoto(True, tkinter.PhotoImage(file=path))
        self.after(201, lambda :self.iconphoto(False, tkinter.PhotoImage(file=path)))

if __name__ == "__main__":
    app = tube_sync()
    app.mainloop()
    app.wlog("TubuSync closed")