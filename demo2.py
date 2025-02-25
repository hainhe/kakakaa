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

        # Giả sử alert có dạng gồm 2 dòng:
        # Dòng 1: "LONG" hoặc "SHORT" (có thể là toàn văn bản chứa các từ này)
        # Dòng 2: "Chart URL: https://www.tradingview.com/chart/?symbol=EURUSD"
        # Nếu có URL chart thì chúng ta tiến hành chụp hình, ngược lại chỉ gửi tin nhắn alert
        photo_url = None
        if "Chart URL:" in alert_message:
            # Tách URL chart
            parts = alert_message.split("\n")
            for part in parts:
                if part.startswith("Chart URL:"):
                    original_chart_url = part.split("Chart URL:")[1].strip()
                    break
            else:
                original_chart_url = ""
            
            parsed_url = urlparse(original_chart_url)
            qs = parse_qs(parsed_url.query)
            symbol = qs.get('symbol', [''])[0]
            if not symbol:
                print("⚠️ Symbol not found in the URL!")
                symbol = "Unknown"
            
            # Tạo URL chụp ảnh chart với Chart-Img (giả sử interval cố định là 15m và theme là dark)
            chart_img_url = (f"https://api.chart-img.com/v1/tradingview/advanced-chart?"
                             f"key={CHART_IMG_API_KEY}&symbol={symbol}&interval=15m&theme=dark")
            
            response = requests.get(chart_img_url)
            if response.status_code == 200:
                photo_url = response.url  # URL ảnh chụp từ Chart-Img
                print(f"✅ Screenshot captured: {photo_url}")
            else:
                print(f"❌ Error capturing screenshot: {response.status_code} - {response.text}")
        
        # Tạo caption cho alert
        # Giả sử nếu alert chứa từ LONG hoặc SHORT thì đó là tín hiệu tương ứng.
        if "LONG" in alert_message.upper():
            alert_caption = "🚀 LONG Signal"
            bot_token = BOT1_TOKEN
        elif "SHORT" in alert_message.upper():
            alert_caption = "📉 SHORT Signal"
            bot_token = BOT2_TOKEN
        else:
            alert_caption = "Alert Signal"
            bot_token = BOT1_TOKEN  # Mặc định BOT1
        
        # Nếu có hình thì gửi ảnh kèm caption, ngược lại chỉ gửi tin nhắn văn bản
        if photo_url:
            send_telegram_photo(bot_token, CHAT_ID, photo_url, alert_caption + "\n" + alert_message)
        else:
            send_telegram_message(bot_token, CHAT_ID, alert_caption + "\n" + alert_message)

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
