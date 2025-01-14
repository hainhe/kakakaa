from flask import Flask, request
import requests
from datetime import datetime
import pytz  # Thư viện để xử lý múi giờ

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '7637391486:AAEYarDrhPKUkWzsoteS3yiVgB5QeiZdKoI'
CHAT_ID = '-4708928215'

# Hàm lấy thời gian hiện tại theo múi giờ UTC+7
def get_current_time():
    utc_plus_7 = pytz.timezone('Asia/Bangkok')  # UTC+7 tương ứng với Asia/Bangkok
    current_time = datetime.now(utc_plus_7)
    return current_time.strftime('%Y-%m-%d %H:%M:%S')  # Định dạng: Năm-Tháng-Ngày Giờ:Phút:Giây

@app.route('/webhook', methods=['POST'])
def webhook():
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

    # Lấy thời gian hiện tại
    current_time = get_current_time()

    # Thêm thời gian vào thông báo gửi đi
    message_with_time = f"{message}\n\nTime: {current_time} (UTC+7)"

    send_message_to_telegram(message_with_time)
    return "Webhook received", 200

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
