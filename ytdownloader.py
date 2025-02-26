import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import threading
import yt_dlp
import requests
from urllib.parse import urlparse, parse_qs

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
       
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.download_progress = tk.DoubleVar(value=0.0)
        self.status_text = tk.StringVar(value="Ready")
        self.video_info = None
        self.thumbnail_image = None
        
      
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", troughcolor='white', background='green')
        
        
        ttk.Label(self.main_frame, text="YouTube URL:", font=("Helvetica", 12)).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        url_entry = ttk.Entry(self.main_frame, textvariable=self.url_var, width=40, font=("Helvetica", 12))
        url_entry.grid(row=0, column=1, sticky=tk.EW, padx=(5, 5), pady=(0, 5))
        ttk.Button(self.main_frame, text="Load Info", command=self.load_video_info).grid(row=0, column=2, padx=5, pady=(0, 5))
        
        
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Video Information", padding=10)
        self.info_frame.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW, pady=10)
        
        
        self.thumbnail_label = ttk.Label(self.info_frame, text="Enter URL and click Load Info")
        self.thumbnail_label.grid(row=0, column=0, padx=10, pady=10)
        
        
        self.info_text = tk.Text(self.info_frame, height=10, width=40, wrap=tk.WORD, font=("Helvetica", 10))
        self.info_text.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.info_text.config(state=tk.DISABLED)
        
        
        options_frame = ttk.LabelFrame(self.main_frame, text="Download Options", padding=10)
        options_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
       
        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.format_combobox = ttk.Combobox(options_frame, width=40, state="readonly")
        self.format_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        
        self.audio_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Audio Only (MP3)", variable=self.audio_only_var, 
                        command=self.toggle_audio_only).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        
        ttk.Label(options_frame, text="Save to:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.output_dir_var, width=40).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=self.browse_output_dir).grid(row=2, column=2, padx=5, pady=5)
        
        
        self.download_button = ttk.Button(self.main_frame, text="Download", command=self.download_video, state=tk.DISABLED)
        self.download_button.grid(row=3, column=0, columnspan=3, pady=10)
        
        
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.download_progress, maximum=100, style="green.Horizontal.TProgressbar")
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
       
        status_label = ttk.Label(self.main_frame, textvariable=self.status_text, font=("Helvetica", 10))
        status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
       
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.info_frame.columnconfigure(1, weight=1)
        self.info_frame.rowconfigure(0, weight=1)
        
        
        url_entry.bind("<Return>", lambda event: self.load_video_info())
        
    def extract_video_id(self, url):
        """Extract the video ID from a YouTube URL."""
        parsed_url = urlparse(url)
        if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.netloc == 'youtu.be':
            return parsed_url.path[1:]
        return None
        
    def load_video_info(self):
        """Load video information and thumbnail."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
            return
            
        self.status_text.set("Loading video information...")
        self.download_button.config(state=tk.DISABLED)
        
       
        threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True).start()
    
    def _fetch_video_info(self, url):
        """Fetch video information in a separate thread."""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
            self.video_info = info
            
            
            formats = []
            if 'formats' in info:
                for fmt in info['formats']:
                    
                    if fmt.get('resolution') != 'audio only' and fmt.get('vcodec') != 'none':
                        format_note = fmt.get('format_note', '')
                        resolution = fmt.get('resolution', 'unknown')
                        ext = fmt.get('ext', '')
                        format_id = fmt.get('format_id', '')
                        formats.append(f"{resolution} - {format_note} ({ext}) [ID: {format_id}]")
            
            
            audio_formats = []
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                    format_note = fmt.get('format_note', '')
                    ext = fmt.get('ext', '')
                    format_id = fmt.get('format_id', '')
                    audio_formats.append(f"Audio: {format_note} ({ext}) [ID: {format_id}]")
            
            
            def sort_key(fmt):
                res = fmt.split(' - ')[0]
                try:
                    return int(res.split('x')[1]) if 'x' in res else int(res.split('p')[0]) if 'p' in res else 0
                except:
                    return 0
            
            formats.sort(key=sort_key, reverse=True)
            
            
            best_format = "Best quality"
            
           
            thumbnail_url = info.get('thumbnail')
            thumbnail_image = None
            if thumbnail_url:
                try:
                    response = requests.get(thumbnail_url)
                    img = Image.open(BytesIO(response.content))
                    
                    
                    img.thumbnail((300, 200))
                    thumbnail_image = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error loading thumbnail: {e}")
            
           
            self.root.after(0, lambda: self._update_ui_with_info(info, formats, audio_formats, best_format, thumbnail_image))
            
        except Exception as e:
            self.root.after(0, lambda msg=str(e): self.status_text.set(f"Error: {msg}"))
    
    def _update_ui_with_info(self, info, formats, audio_formats, best_format, thumbnail_image):
        """Update the UI with video information (called in main thread)."""
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info_text = f"Title: {info.get('title', 'Unknown')}\n"
        info_text += f"Channel: {info.get('uploader', 'Unknown')}\n"
        duration = info.get('duration')
        if duration:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                info_text += f"Duration: {hours}:{minutes:02d}:{seconds:02d}\n"
            else:
                info_text += f"Duration: {minutes}:{seconds:02d}\n"
        
        info_text += f"Views: {info.get('view_count', 'Unknown'):,}\n"
        
        upload_date = info.get('upload_date')
        if upload_date and len(upload_date) == 8:
            year, month, day = upload_date[:4], upload_date[4:6], upload_date[6:8]
            info_text += f"Upload Date: {year}-{month}-{day}\n"
        
        description = info.get('description', '')
        if description:
            info_text += f"\nDescription: {description[:200]}..."
        
        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state=tk.DISABLED)
        
        
        if thumbnail_image:
            self.thumbnail_image = thumbnail_image 
            self.thumbnail_label.config(image=thumbnail_image, text="")
        else:
            self.thumbnail_label.config(text="No thumbnail available", image="")
        
        
        all_formats = ["Best quality"] + formats
        if self.audio_only_var.get():
            all_formats = ["Best audio quality"] + audio_formats
            
        self.format_combobox['values'] = all_formats
        self.format_combobox.current(0)
        
       
        self.download_button.config(state=tk.NORMAL)
        self.status_text.set("Ready to download")
    
    def toggle_audio_only(self):
        """Toggle between audio and video formats."""
        if not self.video_info:
            return
            
        
        self._fetch_video_info(self.url_var.get().strip())
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def download_video(self):
        """Start video download."""
        if not self.video_info:
            messagebox.showwarning("Error", "No video information loaded.")
            return
            
        selected_format = self.format_combobox.get()
        output_dir = self.output_dir_var.get()
        
        if not os.path.isdir(output_dir):
            messagebox.showwarning("Error", "Invalid output directory.")
            return
        
        
        format_id = None
        if selected_format != "Best quality" and selected_format != "Best audio quality":
            
            format_id = selected_format.split("ID: ")[1].rstrip("]")
        
        
        self.download_button.config(state=tk.DISABLED)
        self.status_text.set("Preparing download...")
        self.progress_bar['value'] = 0
        
        
        threading.Thread(
            target=self._download_thread, 
            args=(self.url_var.get(), output_dir, self.audio_only_var.get(), format_id),
            daemon=True
        ).start()
    
    def _download_thread(self, url, output_dir, audio_only, format_id):
        """Download video in a separate thread."""
        try:
           
            ydl_opts = {
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [self._progress_hook],
                'retries': 10,
                'fragment_retries': 10,
                'socket_timeout': 30,
            }
            
           
            if audio_only:
                ydl_opts.update({
                    'format': format_id if format_id else 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                if format_id:
                    ydl_opts['format'] = format_id
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
            
           
            self.root.after(0, lambda: self.status_text.set("Downloading..."))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            
            self.root.after(0, lambda: [
                self.status_text.set("Download completed!"),
                self.download_button.config(state=tk.NORMAL),
                self.progress_bar.config(value=100)
            ])
            
        except yt_dlp.DownloadError as e:
            if "timed out" in str(e).lower():
                self.root.after(0, lambda: [
                    self.status_text.set("Error: Connection timed out. Please check your internet connection and try again."),
                    self.download_button.config(state=tk.NORMAL)
                ])
            else:
                self.root.after(0, lambda msg=str(e): [
                    self.status_text.set(f"Error: {msg}"),
                    self.download_button.config(state=tk.NORMAL)
                ])
        except Exception as e:
            self.root.after(0, lambda msg=str(e): [
                self.status_text.set(f"Error: {msg}"),
                self.download_button.config(state=tk.NORMAL)
            ])
    
    def _progress_hook(self, d):
        """Update progress bar from yt-dlp progress hook."""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes and total_bytes > 0:
                percentage = d['downloaded_bytes'] / total_bytes * 100
                self.root.after(0, lambda: self.progress_bar.config(value=percentage))
            if 'speed' in d and d['speed'] is not None:
                speed_mb = d['speed'] / 1024 / 1024
                eta = d.get('eta', 'unknown')
                status = f"Downloading: {speed_mb:.2f} MB/s, ETA: {eta} seconds"
                self.root.after(0, lambda: self.status_text.set(status))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: [
                self.status_text.set("Processing downloaded file..."),
                self.progress_bar.config(value=95)
            ])

if __name__ == "__main__":
    
    missing_libs = []
    try:
        import yt_dlp
    except ImportError:
        missing_libs.append("yt-dlp")
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_libs.append("pillow")
    
    if missing_libs:
        print(f"Missing required libraries: {', '.join(missing_libs)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_libs)}")
        sys.exit(1)
    
    
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()
