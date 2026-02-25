import os
import subprocess
import time
from datetime import datetime
from flask import Flask
from threading import Thread
import pytz 

app = Flask(__name__)

# ================= কনফিগারেশন এরিয়া =================

# ১. এখানে আপনার ভিডিওগুলোর লিস্ট দিন (কমা দিয়ে যত খুশি লিংক অ্যাড করতে পারেন)
VIDEO_PLAYLIST = [
    "https://youtu.be/gUqq0ugYXKE?si=tUHO6PL51PZ0U72P",  # প্রথম দিনের ভিডিও
    "https://youtu.be/DnxaA_N3fJQ?si=iXnRwa6txpoZKWEE",  # দ্বিতীয় দিনের ভিডিও
    "https://youtu.be/gHw0OLsixfQ?si=MX1w01DibmscCq1H",  # তৃতীয় দিনের ভিডিও
    "https://youtu.be/yY_OwjyKO8w?si=cmnQtosyFLYYvp_e",  # চতুর্থ দিনের ভিডিও
    "https://youtu.be/7-6tWzBTIFk?si=dnOFd_B7YATNO9do",  # এভাবে ৩০-৪০টা লিংক দিয়ে রাখতে পারেন
]

# ২. ফেসবুক স্ট্রিম কি
STREAM_KEY = "FB-1696468164019091-0-Ab6zGsOzLGn5MZwzyYOEPc08"

# ৩. লাইভ শুরুর সময় (24-hour format)
START_TIME = "14:30" 

# ৪. টাইমজোন
TIMEZONE = "Asia/Dhaka"

# ৫. লাইভ ডিউরেশন (সেকেন্ডে) -> ৯০ মিনিট = ৫৪০০
DURATION_SECONDS = 5711 

# ৬. যেদিন থেকে এই সিস্টেম চালু করছেন সেই তারিখ (গুরুত্বপূর্ণ)
# ফরম্যাট: YYYY, M, D (যেমন: ২০২৪ সালের অক্টোবর ২৫ হলে: 2024, 10, 25)
START_DATE_REF = datetime(2026, 2, 25) 

# ===================================================

def get_todays_video():
    """
    আজকের জন্য সঠিক ভিডিওটি নির্বাচন করার ফাংশন
    """
    if not VIDEO_PLAYLIST:
        return None
        
    tz = pytz.timezone(TIMEZONE)
    current_date = datetime.now(tz).replace(tzinfo=None) # টাইমজোন ইনফো সরিয়ে প্লেইন ডেট নেওয়া
    
    # শুরুর তারিখ থেকে আজ পর্যন্ত কত দিন পার হয়েছে
    days_passed = (current_date - START_DATE_REF).days
    
    # ভাগশেষ (Modulus) ব্যবহার করে ইনডেক্স বের করা। 
    # এতে লিস্ট শেষ হলে অটোমেটিক আবার শুরু থেকে আসবে।
    video_index = days_passed % len(VIDEO_PLAYLIST)
    
    selected_video = VIDEO_PLAYLIST[video_index]
    print(f"Day {days_passed + 1}: Playing Video #{video_index + 1} -> {selected_video}")
    return selected_video

@app.route('/')
def home():
    video = get_todays_video()
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz).strftime("%I:%M %p")
    return f"Status: Running | Time: {now} | Next Video: {video} | Waiting for {START_TIME}..."

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def stream_process():
    video_url = get_todays_video()
    
    if not video_url:
        print("No video found in playlist!")
        return

    rtmp_url = f"rtmps://live-api-s.facebook.com:443/rtmp/{STREAM_KEY}"
    
    print(f"Starting Stream with: {video_url}")
    
    command = (
        f"yt-dlp -o - {video_url} | "
        f"ffmpeg -re -i pipe:0 -t {DURATION_SECONDS} -c:v libx264 -preset veryfast -b:v 3000k "
        f"-maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 60 "
        f"-c:a aac -b:a 128k -ar 44100 -f flv \"{rtmp_url}\""
    )
    
    subprocess.call(command, shell=True)
    print("Stream Finished.")

def scheduler():
    while True:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")
        
        if current_time == START_TIME:
            stream_process()
            time.sleep(60) 
        
        time.sleep(30)

if __name__ == "__main__":
    t1 = Thread(target=run_flask)
    t1.start()
    scheduler()
