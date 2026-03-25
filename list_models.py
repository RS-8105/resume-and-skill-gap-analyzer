import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyB-vTw6sX9Ms_mqejS8tuyUEC69ghCWdrI")

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
