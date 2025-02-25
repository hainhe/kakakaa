
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI"
BOT2_TOKEN = "7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA"
CHAT_ID = "-4708928215"

# API Key của Chart-Img
CHART_IMG_API_KEY = "8RLLVdMVMl7MQ9SuxhU0O5cONpyTGPba1BLbaiYG"

# Hàm gửi tin nhắn văn bản qua Telegram
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# Hàm gửi ảnh qua Telegram
def send_telegram_photo(bot_token, chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"❌ Error sending photo: {response.text}")

@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    print("🟢 UptimeRobot ping received! Keeping Render alive...")
    return "", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        alert_message = request.data.decode("utf-8").strip()
        if not alert_message:
            print("⚠️ No message received!")
            return jsonify({"error": "No message received"}), 400

        print(f"📥 Processed Message: {alert_message}")

        # Chọn BOT token dựa trên tín hiệu trong alert (LONG hay SHORT)
        if "🚀 LONG 🚀:" in alert_message:
            bot_token = BOT1_TOKEN
        elif "🚨 SHORT 🚨:" in alert_message:
            bot_token = BOT2_TOKEN
        else:
            bot_token = BOT1_TOKEN  # Mặc định nếu không xác định

        # Gửi alert nguyên văn đến Telegram
        send_telegram_message(bot_token, CHAT_ID, alert_message)

        # Trích xuất symbol từ giữa "🌜" và "🌛"
        start = alert_message.find("🌜")
        end = alert_message.find("🌛", start)
        if start != -1 and end != -1:
            symbol = alert_message[start + len("🌜"):end].strip()
            print(f"✅ Extracted symbol: {symbol}")
        else:
            print("⚠️ Symbol not found in alert message; skipping screenshot.")
            return jsonify({"status": "ok"})

        # Tạo URL chụp ảnh chart với Chart-Img (ở đây interval cố định là 15m, theme là dark)
        chart_img_url = (
            f"https://api.chart-img.com/v1/tradingview/advanced-chart?"
            f"key={CHART_IMG_API_KEY}&symbol={symbol}&interval=15m&theme=dark"
        )

        response = requests.get(chart_img_url)
        if response.status_code == 200:
            photo_url = response.url  # Lấy URL ảnh được trả về từ Chart‑Img
            print(f"✅ Screenshot captured: {photo_url}")
            # Gửi ảnh kèm với tin nhắn (caption có thể để trống hoặc bổ sung thông tin nếu cần)
            send_telegram_photo(bot_token, CHAT_ID, photo_url, "")
        else:
            print(f"❌ Error capturing screenshot: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
