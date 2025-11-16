import requests
from django.conf import settings


ESKIZ_EMAIL = settings.ESKIZ_EMAIL 
ESKIZ_PASSWORD = settings.ESKIZ_PASSWORD  

def get_token():
    url = "https://notify.eskiz.uz/api/auth/login"
    data = {
        "email": ESKIZ_EMAIL,
        "password": ESKIZ_PASSWORD
    }
    response = requests.post(url, json=data)
    response_data = response.json()
    return response_data.get("data", {}).get("token")

def send_sms(phone, message):
    token = get_token()

    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "mobile_phone": phone,
        "message": message,
        "from": "4546",
        "callback_url": "http://45.138.159.84/.com"
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()