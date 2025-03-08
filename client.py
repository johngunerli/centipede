# send a request 
import requests
API_URL = "http://localhost:8000/add"

# Example arrays
data = {
    "array1": [1.0, 2.0, 3.0, 4.0],
    "array2": [5.0, 6.0, 7.0, 8.0]
}

# Send POST request
response = requests.post(API_URL, json=data)

# Print response
if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Error:", response.status_code, response.text)