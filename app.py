from flask import Flask, request, Response
import yt_dlp
import requests

app = Flask(__name__)

@app.route('/api/play')
def play_audio():
    video_id = request.args.get('v')
    if not video_id:
        return "Thiếu Video ID", 400

    # Cấu hình tối ưu lấy luồng nhạc nhẹ nhất từ InnerTube
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'quiet': True,
        'simulate': True,
        'extractor_args': {'youtube': {'player_client': ['android']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            audio_url = info['url']

        # Đóng vai trò làm trình duyệt để tải nhạc từ Google
        headers = {"User-Agent": "Mozilla/5.0"}
        req = requests.get(audio_url, stream=True, headers=headers)
        
        # Băm nhỏ file và phát sóng trực tiếp qua mạng LAN
        def generate():
            for chunk in req.iter_content(chunk_size=1024 * 64):
                yield chunk

        return Response(generate(), content_type=req.headers.get('content-type', 'audio/mp4'))
        
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)