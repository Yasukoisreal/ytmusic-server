from flask import Flask, request, redirect
import yt_dlp
import traceback

app = Flask(__name__)

# Tạo một trang chủ nhỏ để Render không báo lỗi 404 khi quét thử
@app.route('/')
def home():
    return "🚀 Máy chủ YouTube Music API dành cho Lumia đang hoạt động mượt mà!"

# Cửa ngách xử lý việc bóc link nhạc
@app.route('/api/play')
def play_audio():
    # Lấy ID bài hát từ đường link (ví dụ: ?v=60ItHLz5WEA)
    video_id = request.args.get('v')
    if not video_id:
        return "Lỗi: Thiếu ID bài hát (tham số 'v')", 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    # CÔNG THỨC VƯỢT RÀO YOUTUBE TỐI ƯU NHẤT
    ydl_opts = {
        'format': 'bestaudio/best', # Lấy âm thanh tốt nhất có thể
        'cookiefile': 'cookies.txt', # Dùng "Thẻ căn cước" từ két sắt Render
        'extractor_args': {'youtube': {'client': ['web', 'tv']}}, # Vỏ bọc Smart TV/Web để tránh bị ép trả về ảnh
        'noplaylist': True,
        'quiet': False # Bật hiển thị log để theo dõi trên Render
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Tiến hành bóc tách thông tin (Không tải file về máy chủ Render)
            info_dict = ydl.extract_info(youtube_url, download=False)
            audio_url = info_dict.get('url')

            if not audio_url:
                return "Không thể trích xuất được đường dẫn âm thanh từ video này.", 500

            # Vượt rào thành công -> Chuyển hướng thẳng điện thoại đến file nhạc của Google
            return redirect(audio_url)

    except Exception as e:
        # Nếu bị lỗi, in thẳng lỗi ra màn hình trình duyệt để dễ bắt bệnh
        error_msg = str(e)
        traceback.print_exc() 
        return f"🚨 Lỗi từ yt-dlp: {error_msg}", 500

if __name__ == '__main__':
    # Chạy máy chủ ở cổng 5000
    app.run(host='0.0.0.0', port=5000)
