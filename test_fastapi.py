import requests
import json
import time

url = "http://127.0.0.1:8000/analyze"
payload = {
    "resume_text": "I am a Java developer with 5 years experience in Spring Boot, MySQL, and Docker.",
    "company": "Stripe",
    "job_description": "We need a Senior Backend Engineer strong in Java, Spring Boot, MySQL, Docker, and RESTful APIs."
}
print(f"Testing {url} ...")
start = time.time()
try:
    resp = requests.post(url, json=payload, timeout=30)
    print(f"STATUS: {resp.status_code} in {time.time()-start:.2f}s")
    print("RESPONSE:", resp.text)
except Exception as e:
    print(f"ERROR: {e} in {time.time()-start:.2f}s")
