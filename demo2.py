import re
from flask import Flask, request, jsonify
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI"
BOT2_TOKEN = "7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA"
CHAT_ID = "-4708928215"

# API Key của Chart-Img
CHART_IMG_API_KEY = "8RLLVdMVMl7MQ9SuxhU0O5cONpyTGPba1BLbaiYG"

# Hàm gửi ảnh qua Telegram
def send_telegram_photo(bot_token, chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"❌ Error sending photo: {response.text}")

# Hàm gửi tin nhắn văn bản qua Telegram
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    print("🟢 UptimeRobot ping received! Keeping Render alive...")
    return "", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    print(f"📥 Headers: {request.headers}")
    print(f"📥 Raw data: {request.data}")

    try:
        alert_message = request.data.decode("utf-8").strip()
        if not alert_message:
            print("⚠️ No message received!")
            return jsonify({"error": "No message received"}), 400

        print(f"📥 Processed Message: {alert_message}")

        # Trích xuất symbol để chụp ảnh biểu đồ
        match = re.search(r'🌜(.*?)🌛', alert_message)
        symbol = match.group(1) if match else "Unknown"

        # Tạo URL chụp ảnh chart với Chart-Img
        chart_img_url = (f"https://api.chart-img.com/v1/tradingview/advanced-chart?"
                        f"key={CHART_IMG_API_KEY}&symbol={symbol}&interval=15m&theme=dark")

        response = requests.get(chart_img_url)
        if response.status_code == 200:
            photo_url = response.url
            print(f"✅ Screenshot captured: {photo_url}")
        else:
            photo_url = None
            print(f"❌ Error capturing screenshot: {response.status_code} - {response.text}")

        # Xác định bot dựa trên tín hiệu
        if "LONG" in alert_message:
            print("🚀 Sending LONG signal via BOT1")
            if photo_url:
                send_telegram_photo(BOT1_TOKEN, CHAT_ID, photo_url, alert_message)
            else:
                send_telegram_message(BOT1_TOKEN, CHAT_ID, f"{alert_message}\n(Ảnh không chụp được)")
        elif "SHORT" in alert_message:
            print("📉 Sending SHORT signal via BOT2")
            if photo_url:
                send_telegram_photo(BOT2_TOKEN, CHAT_ID, photo_url, alert_message)
            else:
                send_telegram_message(BOT2_TOKEN, CHAT_ID, f"{alert_message}\n(Ảnh không chụp được)")

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
