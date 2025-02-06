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



from flask import Flask, request
import requests
import time
import threading

app = Flask(__name__)

# Token bot chính và bot phụ
MAIN_BOT_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'
SECONDARY_BOT_TOKEN = '7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA'  # Bot phụ để gửi huy chương
CHAT_ID = '-4708928215'

# Thời gian của 1 nến 15 phút (tính bằng giây)
ONE_CANDLE = 60  # 15 phút = 900 giây
TWO_CANDLES = 2 * ONE_CANDLE  # 30 phút = 1800 giây

# Bộ nhớ lưu tín hiệu và trạng thái gửi huy chương
signals = {}

@app.route('/')
def index():
    return "App is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if request.is_json:
            data = request.get_json(force=True)
        else:
            data = {"message": request.data.decode('utf-8')}  # Giải mã text raw
        
        print("Received data:", data)
        message = data.get('message', 'No message received')
        send_message_to_telegram(MAIN_BOT_TOKEN, message)

        # Lấy cặp giao dịch từ tin nhắn (có thể chỉnh lại nếu format khác)
        symbol = message.split(":")[1].strip()  

        # Cập nhật trạng thái tín hiệu
        current_time = time.time()
        signals[symbol] = {
            "time": current_time,
            "sent_🥇": False,
            "sent_🥈": False
        }

    except Exception as e:
        print("Error parsing JSON:", str(e))
        return "Invalid JSON", 400

    return "Webhook received", 200

# Hàm gửi tin nhắn đến Telegram
def send_message_to_telegram(bot_token, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Message sent successfully via bot {bot_token}!")
    else:
        print(f"Failed to send message: {response.text}")

# Kiểm tra và gửi huy chương nếu đủ điều kiện
def check_signals():
    while True:
        current_time = time.time()
        
        for symbol in list(signals.keys()):
            elapsed_time = current_time - signals[symbol]["time"]
            
            # Nếu sau 15 phút không có tín hiệu mới -> Gửi huy chương 🥇
            if elapsed_time > ONE_CANDLE and not signals[symbol]["sent_🥇"]:
                send_message_to_telegram(SECONDARY_BOT_TOKEN, f"🥇 Huy chương 1 cho {symbol}")
                signals[symbol]["sent_🥇"] = True
            
            # Nếu sau 30 phút không có tín hiệu mới -> Gửi huy chương 🥈 và xóa tín hiệu
            if elapsed_time > TWO_CANDLES and not signals[symbol]["sent_🥈"]:
                send_message_to_telegram(SECONDARY_BOT_TOKEN, f"🥈 Huy chương 2 cho {symbol}")
                del signals[symbol]  # Xóa tín hiệu khỏi bộ nhớ
        
        time.sleep(10)  # Kiểm tra mỗi 10 giây

# Chạy kiểm tra tín hiệu song song
threading.Thread(target=check_signals, daemon=True).start()

if __name__ == '__main__':
    app.run(port=5000)

