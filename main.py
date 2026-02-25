import os
import subprocess
import time
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Quran Live Stream is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# স্ট্রিম করার ফাংশন
def start_stream():
    # এখানে আপনার ইউটিউব ভিডিওর লিংক দিন
    youtube_url = "https://youtu.be/VIDEO_LINK_HERE"
    
    # ফেসবুক স্ট্রিম কি (Environment variable থেকে নেওয়াই নিরাপদ, তবে এখানে সরাসরিও দিতে পারেন)
    # সতর্কতা: গিটহাবে পাবলিকলি কি (Key) দেখা যাবে।
    stream_key = "YOUR_FACEBOOK_STREAM_KEY_HERE"
    
    rtmp_url = f"rtmps://live-api-s.facebook.com:443/rtmp/{stream_key}"

    while True:
        try:
            print("Starting Stream...")
            # yt-dlp দিয়ে লিংক থেকে ভিডিও নিয়ে FFmpeg দিয়ে ফেসবুকে পাঠানো
            command = (
                f"yt-dlp -o - {youtube_url} | "
                f"ffmpeg -re -i pipe:0 -c:v libx264 -preset veryfast -b:v 3000k "
                f"-maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 60 "
                f"-c:a aac -b:a 128k -ar 44100 -f flv \"{rtmp_url}\""
            )
            
            subprocess.call(command, shell=True)
            print("Stream ended, restarting in 10 seconds...")
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # ওয়েব সার্ভার চালু রাখা (যাতে সার্ভার বন্ধ না হয়)
    t = Thread(target=run_flask)
    t.start()
    
    # স্ট্রিম শুরু করা
    start_stream()
