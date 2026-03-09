from flask import Flask, request, redirect
import yt_dlp
import traceback

app = Flask(__name__)

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
    # 140 (M4A) -> bestaudio đuôi m4a -> 18 (MP4) -> best đuôi mp4
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]/18/best[ext=mp4]', 
        'cookiefile': 'cookies.txt', # Giữ nguyên thẻ căn cước
        'extractor_args': {'youtube': {'client': ['web', 'tv']}}, # Giữ nguyên vỏ bọc
        'noplaylist': True,
        'quiet': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Chỉ bóc link, không tải file về server
            info_dict = ydl.extract_info(youtube_url, download=False)
            audio_url = info_dict.get('url')

            if not audio_url:
                return "Không tìm thấy định dạng m4a/mp4 tương thích cho điện thoại.", 500

            # Chuyển hướng thẳng điện thoại đến file nhạc
            return redirect(audio_url)

    except Exception as e:
        traceback.print_exc()
        return f"🚨 Lỗi từ yt-dlp: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
