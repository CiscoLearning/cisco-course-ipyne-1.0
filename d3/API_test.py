import requests
import json

response = requests.get("https://api.github.com")

if response.status_code == 200:
    print("Your request was successful.")
    print("Response JSON:", json.dumps(response.json(), indent=3))
else:
    print(f"Unable to connect: {response.status_code}")
