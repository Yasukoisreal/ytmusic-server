import os
import traceback
from flask import Flask, request, redirect, jsonify
from cachetools import TTLCache
import yt_dlp

app = Flask(__name__)

# TỐI ƯU 1: BỘ NHỚ ĐỆM (CACHE) BẢO VỆ RAM RAILWAY
# Lưu tối đa 1000 bài hát, tự động xóa link sau 2 tiếng (7200s)
url_cache = TTLCache(maxsize=1000, ttl=7200)

# TỐI ƯU 2: KHÓA BẢO MẬT CHỐNG XÀI CHÙA API
SECRET_KEY = os.environ.get("APP_SECRET_KEY", "LumiaWP81-An")

# TỐI ƯU 3: TỰ ĐỘNG NẠP COOKIE ĐỂ VƯỢT TƯỜNG LỬA YOUTUBE
cookie_data = os.environ.get('COOKIE_DATA')
if cookie_data:
    # Nếu Railway có biến COOKIE_DATA, ghi nó ra file cookies.txt
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookie_data)

@app.route('/')
def home():
    return "🚀 API Railway (Bản Tối Thượng - Đã nạp Cookie) đang hoạt động!"

@app.route('/api/play')
def play_audio():
    # 1. Kiểm tra chìa khóa bảo mật trên URL
    client_key = request.args.get("key")
    if client_key != SECRET_KEY:
        return jsonify({"error": "Unauthorized! Đi chỗ khác chơi!"}), 403

    # 2. Lấy ID bài hát
    video_id = request.args.get('v')
    if not video_id:
        return "Lỗi: Thiếu ID bài hát", 400

    # 3. Kiểm tra trong RAM (Tốc độ phản hồi cực nhanh)
    if video_id in url_cache:
        print(f"⚡ [CACHE HIT] Lấy link bài {video_id} cực nhanh từ RAM!")
        return redirect(url_cache[video_id])

    # 4. Yêu cầu lấy link từ YouTube bằng yt-dlp
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Cấu hình giả lập thiết bị để không bị bóp băng thông
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]/18/best[ext=mp4]',
        'extractor_args': {'youtube': {'client': ['android', 'ios', 'tv', 'web']}},
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True
    }
    
    # Nếu file cookies.txt tồn tại, nạp nó vào yt-dlp để chứng minh "không phải là bot"
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Lấy thông tin (chỉ lấy link, không tải file về Server)
            info_dict = ydl.extract_info(youtube_url, download=False)
            audio_url = info_dict.get('url')

            if not audio_url:
                return "Không tìm thấy định dạng âm thanh.", 500

            # Xử lý xong thì lưu link vào RAM cho lần sau
            url_cache[video_id] = audio_url
            
            # Trực tiếp đá (Redirect) điện thoại sang thẳng máy chủ nhạc của YouTube
            return redirect(audio_url)

    except Exception as e:
        traceback.print_exc()
        return f"🚨 Lỗi: {str(e)}", 500

if __name__ == '__main__':
    # TỐI ƯU 4: Bắt Port động của Railway để tránh lỗi Crash
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
