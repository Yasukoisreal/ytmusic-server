import os
import time
import traceback
from flask import Flask, request, redirect, jsonify
from cachetools import TTLCache
import yt_dlp

app = Flask(__name__)

# TỐI ƯU 1: CACHE CHỐNG TRÀN RAM
# Chỉ cho phép nhớ tối đa 1000 bài cùng lúc, quá 2 tiếng (7200s) tự động xóa sạch khỏi RAM
url_cache = TTLCache(maxsize=1000, ttl=7200)

# TỐI ƯU 2: KHÓA BẢO MẬT CHỐNG XÀI CHÙA
# Phải có chìa khóa này thì Server mới cho phép lấy link nhạc
SECRET_KEY = os.environ.get("APP_SECRET_KEY", "LumiaWP81-An")

# TỐI ƯU 3: NẠP COOKIE CHỐNG GIỚI HẠN ĐỘ TUỔI
cookie_data = os.environ.get('COOKIE_DATA')
if cookie_data:
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookie_data)

@app.route('/')
def home():
    return "🚀 API Railway (Bản Hợp Thể Tối Thượng) đang hoạt động!"

@app.route('/api/play')
def play_audio():
    # Kiểm tra chìa khóa bảo mật từ Ứng dụng gửi lên
    client_key = request.headers.get("App-Secret-Key")
    if client_key != SECRET_KEY:
        return jsonify({"error": "Unauthorized! Đi chỗ khác chơi!"}), 403

    video_id = request.args.get('v')
    if not video_id:
        return "Lỗi: Thiếu ID bài hát", 400

    # Kiểm tra trong RAM (Tốc độ ánh sáng 0.01s)
    if video_id in url_cache:
        print(f"⚡ [CACHE HIT] Lấy link bài {video_id} cực nhanh từ RAM!")
        return redirect(url_cache[video_id])

    # TỐI ƯU 4: CÔNG CỤ YT-DLP VƯỢT RÀO BÓP BĂNG THÔNG
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]/18/best[ext=mp4]',
        'extractor_args': {'youtube': {'client': ['android', 'ios', 'tv', 'web']}},
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True
    }
    
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            audio_url = info_dict.get('url')

            if not audio_url:
                return "Không tìm thấy định dạng âm thanh.", 500

            # Xử lý xong thì nhét link gốc vào RAM cho lần sau
            url_cache[video_id] = audio_url
            
            return redirect(audio_url)

    except Exception as e:
        traceback.print_exc()
        return f"🚨 Lỗi: {str(e)}", 500

if __name__ == '__main__':
    # TỐI ƯU 5: Bắt Port động của Railway để không bị lỗi Deploy
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
