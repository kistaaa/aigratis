import os
import time
import yaml
import requests
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# 1. Carrega as chaves
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
MODELS_FILE = "models.yaml"


# criar requests para cada modelo
def construir_requisicao(item):
    """Monta dinamicamente a URL, headers e payload com base no provedor."""
    provedor = item["provedor"]
    
    if provedor == "gemini":
        return {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/{item['modelo']}:generateContent?key={GEMINI_API_KEY}",
            "headers": {"Content-Type": "application/json"},
            "payload": {"contents": [{"parts": [{"text": "ping"}]}]}
        }
        
    elif provedor == "groq":
        return {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            "payload": {"model": item['modelo'], "messages": [{"role": "user", "content": "ping"}], "max_tokens": 5}
        }
        
    elif provedor == "openrouter":
        return {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            "payload": {"model": item['modelo'], "messages": [{"role": "user", "content": "ping"}]}
        }
    
    return None

# testar conexões
def testar_conexoes():
    # Verifica se as chaves de API estão definidas
    print("=" * 80)
    print("VERIFICAÇÃO DE CHAVES DE API:")
    print(f"GEMINI_API_KEY: {'DEFINIDA' if GEMINI_API_KEY else 'NÃO DEFINIDA'}")
    print(f"GROQ_API_KEY: {'DEFINIDA' if GROQ_API_KEY else 'NÃO DEFINIDA'}")
    print(f"OPENROUTER_API_KEY: {'DEFINIDA' if OPENROUTER_API_KEY else 'NÃO DEFINIDA'}")
    print("=" * 80)
    print()
    
    for item in models_list:
        provedor = item["provedor"]
        modelos = item.get("modelos", [])
        
        if not modelos:
            print(f"[{provedor}] Nenhum modelo configurado.")
            print()
            continue
        
        # Testa cada modelo individualmente
        for modelo in modelos:
            print(f"MODELO: {modelo}")
            print(f"PROVEDOR: {provedor}")
            
            item_copy = item.copy()
            item_copy["modelo"] = modelo
            
            config = construir_requisicao(item_copy)
            if not config:
                print("STATUS: ERRO")
                print("DETALHES: Provedor não suportado no script.")
                print("-" * 80)
                print()
                continue
                
            start_time = time.time()
            try:
                response = requests.post(
                    config["url"], 
                    headers=config["headers"], 
                    json=config["payload"], 
                    timeout=15
                )
                duration = time.time() - start_time
                
                print(f"TEMPO: {duration:.3f}s")
                
                if response.status_code == 200:
                    print("STATUS: OK")
                    print("DETALHES: Conexão bem-sucedida.")
                else:
                    print("STATUS: ERRO")
                    print(f"DETALHES: Status HTTP {response.status_code}")
                    print(f"RESPOSTA COMPLETA: {response.text}")
                    
            except requests.exceptions.Timeout:
                duration = time.time() - start_time
                print(f"TEMPO: {duration:.3f}s")
                print("STATUS: ERRO")
                print("DETALHES: Tempo limite esgotado (Timeout).")
            except requests.exceptions.RequestException as e:
                duration = time.time() - start_time
                print(f"TEMPO: {duration:.3f}s")
                print("STATUS: ERRO")
                print(f"DETALHES: Erro de rede: {str(e)}")
            
            print("-" * 80)
            print()

if __name__ == "__main__":

    try:
        models_list = yaml.safe_load(open(MODELS_FILE, encoding="utf-8"))
    except FileNotFoundError:
        print(f"Erro: O arquivo '{MODELS_FILE}' não foi encontrado na mesma pasta.")
        exit(1)

    testar_conexoes()
