import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def check_models():
    print("🔍 Consultando a API oficial do Google (v1)...")
    url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.text}")
            return

        modelos = response.json().get('models', [])
        
        print("\n🧠 Modelos de Geração de Texto (Chat):")
        for m in modelos:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"  ✅ {m['name']}")
                
        print("\n📊 Modelos de Embedding:")
        for m in modelos:
            if 'embedContent' in m.get('supportedGenerationMethods', []):
                print(f"  ✅ {m['name']}")
                
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ GOOGLE_API_KEY não encontrada no .env!")
    else:
        check_models()