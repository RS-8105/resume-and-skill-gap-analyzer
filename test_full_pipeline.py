import urllib.request
import urllib.parse
import sys
import json
import base64

# A simple Python script using standard library to test the endpoint
import json

try:
    import requests
except ImportError:
    print("Requests library not found, please run: pip install requests")
    sys.exit(1)

url = "http://localhost:8080/upload"
pdf_path = "TestResume.pdf"

payload = {
    'company': 'NextGen Tech',
    'jobDescription': 'We are hiring a Software Engineer expert in Java, Spring Boot, MySQL, Docker, and RESTful APIs.'
}
with open(pdf_path, 'rb') as f:
    files = {'file': ('TestResume.pdf', f, 'application/pdf')}
    
    print("\n🚀 Firing Pipeline: Sending Resume + JD to Spring Boot -> FastAPI -> OpenAI...")
    try:
        response = requests.post(url, data=payload, files=files)
        print("\n✅ AI Response Received:\n")
        parsed = response.json()
        print(json.dumps(parsed, indent=4))
    except Exception as e:
        print(f"Error: {e}")
