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
   # CÔNG THỨC ÉP YOUTUBE "NHẢ" LINK SIÊU TỐC
    ydl_opts = {
        'format': '140/18/best[ext=mp4]', # Chỉ lấy đích danh mã 140 (M4A) hoặc 18 (MP4) để không phải suy nghĩ tính toán
        'cookiefile': 'cookies.txt',
        # Thử Android trước -> nếu tạch thì thử iOS -> tạch tiếp thử TV -> đường cùng mới xài Web
        'extractor_args': {'youtube': {'client': ['android', 'ios', 'tv', 'web']}},
        'youtube_include_dash_manifest': False, # BỎ QUA TẢI DỮ LIỆU PHÂN MẢNH (Tiết kiệm 2-3 giây)
        'youtube_include_hls_manifest': False,  # BỎ QUA TẢI DỮ LIỆU LIVE STREAM (Tiết kiệm 1-2 giây)
        'noplaylist': True,
        'quiet': True,       # Tắt in log ra màn hình để server tập trung xử lý
        'no_warnings': True  # Tắt các cảnh báo thừa
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


