"""
Script para capturar JSESSIONID do browser e enviar para Railway
Execute este script localmente para enviar seu JSESSIONID para o Railway
"""

import requests
import json
import os
from datetime import datetime

def send_jsessionid_to_railway():
    """
    Envia JSESSIONID local para o Railway
    """
    # Configurações
    railway_url = "https://baze-double-web-production.up.railway.app"
    webhook_secret = "railway_secret_2024"  # Secret definido no app.py
    
    # JSESSIONID que você tem funcionando localmente
    print("🔑 COMO OBTER SEU JSESSIONID:")
    print("1. Abra DevTools (F12) no browser")
    print("2. Vá em Application > Cookies") 
    print("3. Procure site da Pragmatic Play")
    print("4. Copie o valor do JSESSIONID")
    print("=" * 50)
    
    jsessionid = input("Cole seu JSESSIONID funcionando: ").strip()
    
    if not jsessionid:
        print("❌ JSESSIONID não fornecido")
        return
    
    # Dados para enviar
    data = {
        'jsessionid': jsessionid,
        'source': 'local_script',
        'timestamp': datetime.now().isoformat()
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {webhook_secret}'
    }
    
    try:
        # Enviar para Railway
        response = requests.post(
            f"{railway_url}/api/jsessionid/update",
            json=data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ JSESSIONID enviado com sucesso para Railway!")
            print(f"Resposta: {response.json()}")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")

def test_railway_with_jsessionid():
    """
    Testa se o Railway está usando o JSESSIONID enviado
    """
    railway_url = "https://baze-double-web-production.up.railway.app"
    
    try:
        # Verificar status
        response = requests.get(f"{railway_url}/api/jsessionid/status")
        print(f"📊 Status JSESSIONID: {response.json()}")
        
        # Testar estatísticas
        response = requests.get(f"{railway_url}/api/roulette/statistics/enhanced")
        data = response.json()
        
        print(f"📊 Teste estatísticas:")
        print(f"   Sucesso: {data.get('success')}")
        print(f"   Total resultados: {data.get('total_results')}")
        print(f"   Dados simulados: {data.get('simulated', 'N/A')}")
        
        if not data.get('simulated'):
            print("🎉 DADOS REAIS FUNCIONANDO NO RAILWAY!")
        else:
            print("⚠️ Ainda usando dados simulados")
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")

if __name__ == "__main__":
    print("🚂 RAILWAY JSESSIONID SENDER")
    print("=" * 50)
    
    choice = input("1) Enviar JSESSIONID\n2) Testar Railway\nEscolha (1 ou 2): ")
    
    if choice == "1":
        send_jsessionid_to_railway()
    elif choice == "2":
        test_railway_with_jsessionid()
    else:
        print("Opção inválida")