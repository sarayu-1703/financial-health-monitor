from google import genai

client = genai.Client(
    api_key="AIzaSyD1Sjt1vjzN5GDuGEGo0_2ypr9q1W8HDT0"
)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello"
)

print(response.text)