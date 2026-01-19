
import os
from dotenv import load_dotenv
print("Loading dotenv...")
load_dotenv()
print(f"Environment Loaded. Checking keys...")
print(f"PERPLEXITY: {os.getenv('PERPLEXITY_API_KEY')}")

print("\nImporting ai_assistant...")
try:
    import ai_assistant
    print("Import successful.")
    
    print("\nCalling get_perplexity_client()...")
    client = ai_assistant.get_perplexity_client()
    print(f"Client: {client}")
    
    if client:
        print("\nTesting generate_recipe_from_name...")
        result = ai_assistant.generate_recipe_from_name("Fried Rice")
        print(f"Result: {result}")
    else:
        print("Client is None!")

except Exception as e:
    print(f"Exception: {e}")
