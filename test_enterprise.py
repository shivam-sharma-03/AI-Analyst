import requests

url = "http://localhost:8000/v1/chat/completions"
payload = {
    "model": "llama-3.3-70b",
    "messages": [{"role": "user", "content": "Analyze credit risk for client 1"}],
    "user": "E102938" # Authorized User
}

print("🚀 Testing Enterprise OpenAI Endpoint...")
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("✅ Success!")
    print("Agent Response:", response.json()['choices'][0]['message']['content'])
else:
    print(f"❌ Failed! Status: {response.status_code}")
    print("Error Detail:", response.json())