from flask import Flask, request, redirect
import yt_dlp
import traceback
import os
import time

app = Flask(__name__)

# ===== BỘ NHỚ TẠM (CACHE) KHÔNG LƯU TRỮ TRÊN Ổ CỨNG =====
link_cache = {}
CACHE_EXPIRY = 3600 * 2  # Link sống 6 tiếng, nhưng mình chỉ lưu 2 tiếng (7200 giây) cho an toàn

cookie_data = os.environ.get('COOKIE_DATA')
if cookie_data:
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookie_data)

@app.route('/')
def home():
    return "🚀 API Railway (Có trang bị Cache siêu tốc) đang hoạt động!"

@app.route('/api/play')
def play_audio():
    video_id = request.args.get('v')
    if not video_id:
        return "Lỗi: Thiếu ID bài hát", 400

    current_time = time.time()

    # 1. KIỂM TRA SỔ TAY (CACHE) TRƯỚC
    if video_id in link_cache:
        cached_data = link_cache[video_id]
        # Nếu link trong sổ tay chưa quá 2 tiếng -> Dùng luôn! Tốc độ 0.01s
        if current_time - cached_data['time'] < CACHE_EXPIRY:
            return redirect(cached_data['url'])

    # 2. NẾU TRONG SỔ KHÔNG CÓ, MỚI ĐI HỎI YOUTUBE
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]/18/best[ext=mp4]',
        'cookiefile': 'cookies.txt',
        'extractor_args': {'youtube': {'client': ['android', 'ios', 'tv', 'web']}},
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            audio_url = info_dict.get('url')

            if not audio_url:
                return "Không tìm thấy định dạng âm thanh.", 500

            # 3. HỎI XONG THÌ GHI VÀO SỔ TAY ĐỂ DÀNH CHO NGƯỜI SAU
            link_cache[video_id] = {'url': audio_url, 'time': current_time}
            
            return redirect(audio_url)

    except Exception as e:
        traceback.print_exc()
        return f"🚨 Lỗi: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
