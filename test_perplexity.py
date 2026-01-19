
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key prefix: {api_key[:8]}...")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.perplexity.ai"
)


print(f"Testing Perplexity API with model: sonar-pro")
try:
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[{"role": "user", "content": "用一句话介绍一下中国早餐文化"}],
    )
    print("✅ API Connection Successful!")
    print("🤖 Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ Failed: {e}")


