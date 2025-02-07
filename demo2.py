from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'
CHAT_ID = '-4708928215'

# Route chính "/" để xử lý yêu cầu từ UptimeRobot
@app.route('/')
def index():
    return "App is running!", 200  # Trả về thông báo xác nhận app hoạt động

# Route "/webhook" để xử lý yêu cầu từ TradingView hoặc các nguồn khác
@app.route('/webhook', methods=['POST', 'GET', 'HEAD'])
def webhook():
    # Xử lý yêu cầu POST (dành cho webhook từ TradingView)
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json(force=True)
            else:
                data = {"message": request.data.decode('utf-8')}  # Giải mã text raw
            print("Received data:", data)
            message = data.get('message', 'No message received')
        except Exception as e:
            print("Error parsing JSON:", str(e))
            return "Invalid JSON", 400

        send_message_to_telegram(message)
        return "Webhook received", 200

    # Xử lý yêu cầu GET và HEAD (dành cho UptimeRobot)
    return "Webhook is running!", 200

# Hàm gửi tin nhắn đến Telegram
def send_message_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.text}")

if __name__ == '__main__':
    app.run(port=5000)


# from flask import Flask, request
# import requests
# import threading
# import time

# app = Flask(__name__)

# # Token bot chính và bot phụ
# MAIN_BOT_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'
# SECONDARY_BOT_TOKEN = '7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA'
# CHAT_ID = '-4708928215'

# from flask import Flask, request
# import requests
# import threading
# import time

# app = Flask(__name__)

# TELEGRAM_BOT_TOKEN = "7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI"
# CHAT_ID = "-4708928215"

# # Danh sách chứa các tín hiệu nhận được
# signals = set()
# lock = threading.Lock()

# # Hàm gửi tin nhắn Telegram
# def send_message_to_telegram():
#     while True:
#         time.sleep(5)  # Gửi tin nhắn mỗi 10 giây nếu có tín hiệu mới
#         with lock:
#             if signals:
#                 message = "🚨 LONG 🚨: " + " - ".join([f"🌜{s}🌛" for s in signals])
#                 signals.clear()
#                 url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#                 payload = {"chat_id": CHAT_ID, "text": message}
#                 requests.post(url, json=payload)

# # Chạy luồng gửi tin nhắn Telegram
# threading.Thread(target=send_message_to_telegram, daemon=True).start()

# # Webhook nhận tín hiệu từ TradingView
# @app.route("/webhook", methods=["POST"])
# def webhook():
#     try:
#         data = request.get_json()
#         symbol = data.get("symbol")
#         if symbol:
#             with lock:
#                 signals.add(symbol)
#         return "Received", 200
#     except Exception as e:
#         return f"Error: {str(e)}", 400

# if __name__ == "__main__":
#     app.run(port=5000)
