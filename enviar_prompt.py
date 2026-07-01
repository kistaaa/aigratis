import os
import time
import yaml
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from openai import OpenAI

# Carrega variáveis do arquivo .env
load_dotenv()

# 1. Carrega tudo que precisa
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
MODELS_FILE = "models.yaml"
PROMPT_FILE = "prompt.yaml"

# Inicializa clientes
genai.configure(api_key=GEMINI_API_KEY)
gemini_client = genai

groq_client = Groq(api_key=GROQ_API_KEY)

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


def chamar_ia(prompt, sistema, provedor, modelo):
    try:
        if provedor == "gemini":
            # Configuração do Gemini
            generation_config = {
                "temperature": 1.2,
                "top_p": 0.95,
            }
            
            model = gemini_client.GenerativeModel(
                model_name=modelo,
                system_instruction=sistema,
                generation_config=generation_config,
            )
            
            response = model.generate_content(prompt)
            return response.text

        elif provedor == "groq":
            # A API da Groq usa o padrão OpenAI
            response = groq_client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.2,
                top_p=0.95,
            )
            return response.choices[0].message.content

        elif provedor == "openrouter":
            # A API do OpenRouter usa o padrão OpenAI
            response = openrouter_client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.2,
                top_p=0.95,
            )
            return response.choices[0].message.content
            
    except Exception as e:
        print(f"  ❌ Erro no {provedor}/{modelo}: {str(e)}")
        return None


def main():
    # Carrega lista de modelos
    with open(MODELS_FILE, "r", encoding="utf-8") as f:
        models_config = yaml.safe_load(f)
    
    # Carrega o prompt e a mensagem de sistema
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_config = yaml.safe_load(f)
    
    sistema = prompt_config["sistema"].strip()
    prompt = prompt_config["prompt"].strip()
    
    print("=" * 80)
    print("INSTRUÇÃO DE SISTEMA:")
    print(sistema)
    print("=" * 80)
    print("PROMPT:")
    print(prompt)
    print("=" * 80)
    print()
    
    # Cria uma lista plana de todos os modelos para tentar
    todos_modelos = []
    for item in models_config:
        provedor = item["provedor"]
        for modelo in item["modelos"]:
            todos_modelos.append({"provedor": provedor, "modelo": modelo})
    
    # Tenta cada modelo até conseguir uma resposta
    for idx, config in enumerate(todos_modelos):
        provedor = config["provedor"]
        modelo = config["modelo"]
        
        print(f"🔄 Tentando {idx + 1}/{len(todos_modelos)}: {provedor}/{modelo}...")
        
        resposta = chamar_ia(prompt, sistema, provedor, modelo)
        
        if resposta:
            print()
            print("=" * 80)
            print(f"✅ RESPOSTA RECEBIDA COM SUCESSO DE: {provedor}/{modelo}")
            print("=" * 80)
            print(resposta)
            print("=" * 80)
            return
        
        time.sleep(1)
    
    print("❌ Todos os modelos falharam!")


if __name__ == "__main__":
    main()
