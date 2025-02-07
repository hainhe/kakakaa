# from flask import Flask, request
# import requests

# app = Flask(__name__)

# TELEGRAM_BOT_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'
# CHAT_ID = '-4708928215'

# # Route chính "/" để xử lý yêu cầu từ UptimeRobot
# @app.route('/')
# def index():
#     return "App is running!", 200  # Trả về thông báo xác nhận app hoạt động

# # Route "/webhook" để xử lý yêu cầu từ TradingView hoặc các nguồn khác
# @app.route('/webhook', methods=['POST', 'GET', 'HEAD'])
# def webhook():
#     # Xử lý yêu cầu POST (dành cho webhook từ TradingView)
#     if request.method == 'POST':
#         try:
#             if request.is_json:
#                 data = request.get_json(force=True)
#             else:
#                 data = {"message": request.data.decode('utf-8')}  # Giải mã text raw
#             print("Received data:", data)
#             message = data.get('message', 'No message received')
#         except Exception as e:
#             print("Error parsing JSON:", str(e))
#             return "Invalid JSON", 400

#         send_message_to_telegram(message)
#         return "Webhook received", 200

#     # Xử lý yêu cầu GET và HEAD (dành cho UptimeRobot)
#     return "Webhook is running!", 200

# # Hàm gửi tin nhắn đến Telegram
# def send_message_to_telegram(message):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     payload = {
#         'chat_id': CHAT_ID,
#         'text': message
#     }
#     response = requests.post(url, json=payload)
#     if response.status_code == 200:
#         print("Message sent successfully!")
#     else:
#         print(f"Failed to send message: {response.text}")

# if __name__ == '__main__':
#     app.run(port=5000)


# from flask import Flask, request
# import requests
# import threading
# import time

# app = Flask(__name__)

# # Token bot chính và bot phụ
# MAIN_BOT_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'
# SECONDARY_BOT_TOKEN = '7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA'
# CHAT_ID = '-4708928215'

from flask import Flask, request
import requests
import threading
import time

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI"
CHAT_ID = "-4708928215"

# Danh sách lưu trữ các tín hiệu đến trong khoảng thời gian ngắn
signal_buffer = []
lock = threading.Lock()

def send_telegram_message():
    global signal_buffer
    while True:
        time.sleep(5)  # Gửi tin nhắn mỗi 5 giây nếu có tín hiệu mới

        with lock:
            if signal_buffer:
                # Gộp tất cả các tín hiệu thành một tin nhắn duy nhất
                symbols = " - ".join(signal_buffer)
                message = f"🚨 LONG 🚨: {symbols}"
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                requests.post(url, json={"chat_id": CHAT_ID, "text": message})

                # Xóa buffer sau khi gửi
                signal_buffer = []

# Route kiểm tra bot hoạt động
@app.route("/")
def index():
    return "App is running!", 200

# Route nhận tín hiệu từ TradingView
@app.route("/webhook", methods=["POST"])
def webhook():
    global signal_buffer
    try:
        data = request.json
        symbol = data.get("symbol", "").upper()
        
        if symbol:
            with lock:
                if symbol not in signal_buffer:  # Tránh trùng lặp
                    signal_buffer.append(f"🌜{symbol}🌛")

        return "Webhook received", 200
    except Exception as e:
        return f"Error: {str(e)}", 400

# Chạy luồng riêng để gửi tin nhắn Telegram định kỳ
threading.Thread(target=send_telegram_message, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

