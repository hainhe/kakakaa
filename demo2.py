from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI"
BOT2_TOKEN = "7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA"
CHAT_ID = "-4708928215"

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Headers:", request.headers)
    print("Raw data:", request.data)
    
    try:
        alert_message = request.data.decode("utf-8").strip()  # Đọc dữ liệu thô
        if not alert_message:
            return jsonify({"error": "No message received"}), 400
    except Exception as e:
        return jsonify({"error": "Failed to read data", "details": str(e)}), 400
    
    # Bot1 chỉ gửi tín hiệu LONG/SHORT
    if "🚀 LONG 🚀" in alert_message or "🚨 SHORT 🚨" in alert_message:
        send_telegram_message(BOT1_TOKEN, CHAT_ID, alert_message)
    
    # Bot2 chỉ gửi tín hiệu theo dõi nến
    if "👀" in alert_message:
        send_telegram_message(BOT2_TOKEN, CHAT_ID, alert_message)
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
