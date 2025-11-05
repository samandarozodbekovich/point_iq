import requests

SERVICE_KEY = "AK4DOJYEMRTUKGH2WB4NTGLAUTUU5INNIMLHZQYQJ1I4PKUS"
url = "https://places-api.foursquare.com/places/search"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {SERVICE_KEY}",
    "X-Places-Api-Version": "2025-06-17",  # versiya sarlavhasini berish kerak
}

# params = {
#     "near": "Tashkent",
#     "categories": "13065,12000,17000"  # Example: Restaurant, Education, Market category IDs
# }

params = {
    "near": "Tashkent",          # shahar nomi          # qidiruv so‘zi

      # 13032 = Coffee Shop category ID

                 # nechta natija chiqsin
}

response = requests.get(url, headers=headers, params=params)
print("Status code:", response.status_code)
print("Response JSON:", response.json())
