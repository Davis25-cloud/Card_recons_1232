import requests

# Replace this with your actual API key
API_KEY = "ade5a1aef4a5431709501ab107be56a7"
city = input("Enter city name: ")

url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

response = requests.get(url)
data = response.json()
print(data)

# if response.status_code == 200:
#     print("\n✅ Weather Report")
#     print("---------------------------")
#     print("City:", data['name'])
#     print("Temperature:", data['main']['temp'], "°C")
#     print("Weather:", data['weather'][0]['description'])
#     print("Humidity:", data['main']['humidity'], "%")
#     print("Wind Speed:", data['wind']['speed'], "m/s")
# else:
#     print("❌ Error:", data['message'])
