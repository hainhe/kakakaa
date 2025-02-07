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
import threading
import time

app = Flask(__name__)

# Token bot chính và bot phụ
MAIN_BOT_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'
SECONDARY_BOT_TOKEN = '7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA'
CHAT_ID = '-4708928215'

# Lưu trạng thái tín hiệu theo cặp giao dịch
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
            data = {"message": request.data.decode('utf-8')}
        
        print("📩 Nhận dữ liệu:", data)
        message = data.get('message', 'No message received')

        send_message_to_telegram(MAIN_BOT_TOKEN, message)  # Gửi tín hiệu ngay

        # Lấy cặp giao dịch từ tin nhắn
        symbol = message.split(":")[1].strip()

        # Reset đếm nếu nhận tín hiệu mới
        signals[symbol] = {"count": 0}
        print(f"✅ Nhận tín hiệu mới: {symbol} (Reset bộ đếm nến)")

    except Exception as e:
        print("❌ Lỗi JSON:", str(e))
        return "Invalid JSON", 400

    return "Webhook received", 200

def send_message_to_telegram(bot_token, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"📤 Gửi tin nhắn thành công: {message}")
    else:
        print(f"❌ Lỗi gửi tin ({bot_token}): {response.status_code}, {response.text}")

def update_candles():
    print("✅ Bot phụ đã khởi động và bắt đầu theo dõi nến...")
    while True:
        if signals:
            print("⏳ Kiểm tra trạng thái các cặp tiền...", signals)

        for symbol in list(signals.keys()):
            signals[symbol]["count"] += 1
            print(f"🔄 {symbol}: {signals[symbol]['count']} nến đã qua")

            # Kiểm tra từng nến sau tín hiệu
            if signals[symbol]["count"] == 1:
                send_message_to_telegram(SECONDARY_BOT_TOKEN, f"🥇 Huy chương 1 cho {symbol}")
                print(f"📤 Gửi huy chương 1 cho {symbol}")

            elif signals[symbol]["count"] == 2:
                send_message_to_telegram(SECONDARY_BOT_TOKEN, f"🥈 Huy chương 2 cho {symbol}")
                print(f"📤 Gửi huy chương 2 cho {symbol}")
                # Reset lại để kiểm tra các nến tiếp theo
                signals[symbol]["count"] = 0

        time.sleep(60)  # Chờ 1 phút (1 nến M1)

# Chạy cập nhật nến song song
threading.Thread(target=update_candles, daemon=True).start()
print("✅ Bot chính đã khởi động!")

if __name__ == '__main__':
    app.run(port=5000)
