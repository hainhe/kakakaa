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


# from flask import Flask, request
# import requests

# app = Flask(__name__)

# # Token của 2 bot Telegram
# BOT1_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'  # Bot 1 nhận tín hiệu LONG/SHORT
# BOT2_TOKEN = '7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA'  # Bot 2 nhận tín hiệu 🥇🥈

# CHAT_ID = '-4708928215'  # ID nhóm Telegram nhận tin nhắn

# @app.route('/')
# def index():
#     return "App is running!", 200

# @app.route('/webhook', methods=['POST', 'GET', 'HEAD'])
# def webhook():
#     if request.method == 'POST':
#         try:
#             if request.is_json:
#                 data = request.get_json(force=True)
#             else:
#                 data = {"message": request.data.decode('utf-8')}
#             print("Received data:", data)
#             message = data.get('message', 'No message received')
#         except Exception as e:
#             print("Error parsing JSON:", str(e))
#             return "Invalid JSON", 400

#         # Phân loại tin nhắn để gửi đến bot phù hợp
#         if "🚀 LONG 🚀" in message or "🚨 SHORT 🚨" in message:
#             send_message_to_telegram(BOT1_TOKEN, message)  # Gửi Bot 1
#         elif "🥇" in message or "🥈" in message:
#             send_message_to_telegram(BOT2_TOKEN, message)  # Gửi Bot 2

#         return "Webhook received", 200

#     return "Webhook is running!", 200

# def send_message_to_telegram(bot_token, message):
#     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
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

app = Flask(__name__)

BOT1_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'  # Bot 1 nhận tín hiệu LONG/SHORT
BOT2_TOKEN = '7466054301:AAGexBfB5pNbwmnHP1ocC9jICxR__GSNgOA'  # Bot 2 nhận tín hiệu 🥇🥈
CHAT_ID = '-4708928215'  # ID nhóm Telegram nhận tin nhắn

message_buffer = []  # Danh sách lưu tin nhắn tạm thời
last_sent_time = 0  # Lưu thời gian gửi tin cuối cùng
TIME_THRESHOLD = 5  # Số giây tối thiểu giữa 2 lần gửi tin

@app.route('/')
def index():
    return "App is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    global last_sent_time

    try:
        if request.is_json:
            data = request.get_json(force=True)
        else:
            data = {"message": request.data.decode('utf-8')}
        print("Received data:", data)
        message = data.get('message', 'No message received')
    except Exception as e:
        print("Error parsing JSON:", str(e))
        return "Invalid JSON", 400

    # Thêm tin nhắn vào danh sách tạm
    message_buffer.append(message)

    # Nếu đã đủ 5 giây từ lần gửi trước → Gửi tin gộp
    current_time = time.time()
    if current_time - last_sent_time >= TIME_THRESHOLD:
        send_combined_messages()
        last_sent_time = current_time  # Cập nhật thời gian gửi

    return "Webhook received", 200

def send_combined_messages():
    global message_buffer

    if not message_buffer:
        return  # Không có tin nhắn thì không gửi gì cả

    combined_message = "\n".join(message_buffer)
    
    # Xác định bot phù hợp để gửi
    if any("🚀 LONG 🚀" in msg or "🚨 SHORT 🚨" in msg for msg in message_buffer):
        send_message_to_telegram(BOT1_TOKEN, combined_message)
    elif any("🥇" in msg or "🥈" in msg for msg in message_buffer):
        send_message_to_telegram(BOT2_TOKEN, combined_message)

    message_buffer.clear()  # Xóa danh sách sau khi gửi

def send_message_to_telegram(bot_token, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
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

