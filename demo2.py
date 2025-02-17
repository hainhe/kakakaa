from flask import Flask, request, jsonify
import requests
import traceback  # Thêm vào đầu file

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI"
BOT2_TOKEN = "7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA"
CHAT_ID = "-4708928215"

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
    try:
        alert_message = request.data.decode("utf-8").strip()
        print("Received alert:", alert_message)  # Log nội dung nhận được

        if not alert_message:
            return jsonify({"error": "No message received"}), 400

        signal = extract_signal(alert_message)
        chart_url = extract_chart_url(alert_message)

        print("Extracted signal:", signal)  # Log tín hiệu
        print("Extracted chart URL:", chart_url)  # Log URL

        image_path = None
        if chart_url:
            image_path = capture_chart_screenshot(chart_url)
            print("Captured image path:", image_path)  # Log ảnh chụp

        if signal == "LONG":
            send_telegram_message(BOT1_TOKEN, CHAT_ID, alert_message, image_path)
        elif signal == "SHORT":
            send_telegram_message(BOT2_TOKEN, CHAT_ID, alert_message, image_path)
        else:
            return jsonify({"error": "Unknown signal type"}), 400

    except Exception as e:
        error_message = traceback.format_exc()
        print("Error in webhook:", error_message)  # Log lỗi chi tiết
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
