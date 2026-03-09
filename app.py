from flask import Flask, request, redirect
import yt_dlp
import traceback
import os

app = Flask(__name__)

# TỰ ĐỘNG TẠO FILE COOKIE TỪ BÍ MẬT CỦA RAILWAY
cookie_data = os.environ.get('COOKIE_DATA')
if cookie_data:
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookie_data)

@app.route('/')
def home():
    return "🚀 Máy chủ YouTube Music API trên Railway đang hoạt động siêu mượt!"

@app.route('/api/play')
def play_audio():
    video_id = request.args.get('v')
    if not video_id:
        return "Lỗi: Thiếu ID bài hát (tham số 'v')", 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    # CÔNG THỨC ÉP BUỘC ĐỊNH DẠNG CHO WINDOWS PHONE 8.1
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]/18/best[ext=mp4]', 
        'cookiefile': 'cookies.txt', # Đã có thẻ căn cước
        'extractor_args': {'youtube': {'client': ['web', 'tv']}},
        'noplaylist': True,
        'quiet': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            audio_url = info_dict.get('url')

            if not audio_url:
                return "Không tìm thấy định dạng m4a/mp4 tương thích cho điện thoại.", 500

            return redirect(audio_url)

    except Exception as e:
        traceback.print_exc()
        return f"🚨 Lỗi từ yt-dlp: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
