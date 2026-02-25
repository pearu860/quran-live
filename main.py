import os
import subprocess
import time
from datetime import datetime
from flask import Flask
from threading import Thread
import pytz 

app = Flask(__name__)

# ================= কনফিগারেশন এরিয়া =================

# দাওয়াতে ইসলামীর বা যেকোনো ডাইরেক্ট ভিডিও লিংক
VIDEO_PLAYLIST = [
    "https://data2.dawateislami.net/download/tilawat-e-quran/ur/mp3/2021/90968.mp3",

    # লিংকগুলো এখানে দিন...
]

STREAM_KEY = "FB-1696468164019091-0-Ab6zGsOzLGn5MZwzyYOEPc08"

# লাইভ শুরুর সময় (24-hour format)
START_TIME = "18:17" 

# আপনার টাইমজোন
TIMEZONE = "Asia/Dhaka" 

# শুরুর তারিখ (Reference Date)
START_DATE_REF = datetime(2024, 1, 1) 

# ===================================================

def get_todays_video():
    if not VIDEO_PLAYLIST:
        return None
    tz = pytz.timezone(TIMEZONE)
    current_date = datetime.now(tz).replace(tzinfo=None)
    days_passed = (current_date - START_DATE_REF).days
    video_index = days_passed % len(VIDEO_PLAYLIST)
    return VIDEO_PLAYLIST[video_index]

@app.route('/')
def home():
    video = get_todays_video()
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz).strftime("%I:%M %p")
    return f"Status: Running | Time: {now} | Next Video: {video}"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def stream_process():
    video_url = get_todays_video()
    if not video_url:
        print("No video found!")
        return

    rtmp_url = f"rtmps://live-api-s.facebook.com:443/rtmp/{STREAM_KEY}"
    print(f"Starting Stream: {video_url}")
    
    # --- পরিবর্তন খেয়াল করুন ---
    # আগে এখানে -t {DURATION_SECONDS} ছিল, সেটা মুছে ফেলা হয়েছে।
    # এখন ভিডিও শেষ না হওয়া পর্যন্ত FFmpeg চলতেই থাকবে।
    
    command = (
        f"yt-dlp -o - \"{video_url}\" | "
        f"ffmpeg -re -i pipe:0 -c:v libx264 -preset veryfast -b:v 3000k "
        f"-maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 60 "
        f"-c:a aac -b:a 128k -ar 44100 -f flv \"{rtmp_url}\""
    )
    # -------------------------
    
    subprocess.call(command, shell=True)
    print("Video finished. Stream ended.")

def scheduler():
    while True:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")
        
        if current_time == START_TIME:
            stream_process()
            # লাইভ শেষ হওয়ার পর ১ মিনিট ব্রেক নেবে যাতে একই দিনে দুবার চালু না হয়
            time.sleep(60) 
        
        time.sleep(30)

if __name__ == "__main__":
    t1 = Thread(target=run_flask)
    t1.start()
    scheduler()
