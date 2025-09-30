#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar se as correções de conexão estão funcionando
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_connection():
    """Testa a conexão e reconexão do sistema."""
    base_url = "http://localhost:5000"
    
    print("🧪 Testando correções de conexão...")
    print("=" * 50)
    
    # Teste 1: Status inicial
    print("\n1️⃣  Testando status inicial...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status obtido: {status}")
            
            # Verificar se PlayNabets está conectado
            if status.get('playnabets_connected'):
                print("✅ PlayNabets conectado")
            else:
                print("⚠️  PlayNabets não conectado")
                
            # Verificar tentativas de reconexão
            reconnect_attempts = status.get('reconnect_attempts', 0)
            print(f"📊 Tentativas de reconexão: {reconnect_attempts}")
            
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # Teste 2: Obter resultados
    print("\n2️⃣  Testando obtenção de resultados...")
    try:
        response = requests.get(f"{base_url}/api/results", timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Resultados obtidos: {len(results.get('results', []))} resultados")
            
            if results.get('results'):
                last_result = results['results'][0]
                print(f"📊 Último resultado: {last_result}")
            else:
                print("⚠️  Nenhum resultado disponível")
        else:
            print(f"❌ Erro ao obter resultados: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: Forçar reconexão
    print("\n3️⃣  Testando reconexão forçada...")
    try:
        response = requests.post(f"{base_url}/api/playnabets/reconnect", timeout=15)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reconexão iniciada: {result.get('message')}")
            
            # Aguardar um pouco e verificar status novamente
            print("⏳ Aguardando 5 segundos...")
            time.sleep(5)
            
            # Verificar status após reconexão
            response = requests.get(f"{base_url}/api/status", timeout=10)
            if response.status_code == 200:
                status = response.json()
                print(f"📊 Status após reconexão: conectado={status.get('playnabets_connected')}")
                
        else:
            print(f"❌ Erro na reconexão: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na reconexão: {e}")
    
    # Teste 4: Monitorar por 30 segundos
    print("\n4️⃣  Monitorando conexão por 30 segundos...")
    start_time = time.time()
    last_result_count = 0
    
    while time.time() - start_time < 30:
        try:
            response = requests.get(f"{base_url}/api/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                current_results = status.get('total_results', 0)
                
                if current_results > last_result_count:
                    print(f"📊 Novos resultados recebidos! Total: {current_results}")
                    last_result_count = current_results
                
                # Verificar status da conexão
                connected = status.get('playnabets_connected', False)
                reconnect_attempts = status.get('reconnect_attempts', 0)
                
                print(f"🔌 Status: conectado={connected}, tentativas={reconnect_attempts}")
                
        except Exception as e:
            print(f"⚠️  Erro no monitoramento: {e}")
        
        time.sleep(5)
    
    print("\n✅ Teste de conexão concluído!")
    return True

def test_manual_result():
    """Testa adição de resultado manual."""
    base_url = "http://localhost:5000"
    
    print("\n5️⃣  Testando resultado manual...")
    try:
        # Adicionar resultado manual
        result_data = {
            'number': 7,
            'color': 'red'
        }
        
        response = requests.post(
            f"{base_url}/api/add_result", 
            json=result_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resultado manual adicionado: {result}")
        else:
            print(f"❌ Erro ao adicionar resultado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste manual: {e}")

def test_session_clear():
    """Testa limpeza de sessão."""
    base_url = "http://localhost:5000"
    
    print("\n6️⃣  Testando limpeza de sessão...")
    try:
        # Verificar status antes da limpeza
        response = requests.get(f"{base_url}/api/session/status", timeout=10)
        if response.status_code == 200:
            status_before = response.json()
            print(f"📊 Status antes da limpeza: {status_before['total_results']} resultados")
        
        # Limpar sessão
        response = requests.post(f"{base_url}/api/session/clear", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sessão limpa: {result['message']}")
            
            # Verificar status após limpeza
            response = requests.get(f"{base_url}/api/session/status", timeout=10)
            if response.status_code == 200:
                status_after = response.json()
                print(f"📊 Status após limpeza: {status_after['total_results']} resultados")
                
                if status_after['total_results'] == 0:
                    print("✅ Limpeza de sessão funcionando corretamente!")
                else:
                    print("⚠️  Ainda há resultados após limpeza")
        else:
            print(f"❌ Erro ao limpar sessão: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste de limpeza: {e}")

def test_no_historical_data():
    """Testa se não há dados históricos sendo carregados."""
    base_url = "http://localhost:5000"
    
    print("\n7️⃣  Testando ausência de dados históricos...")
    try:
        # Verificar resultados
        response = requests.get(f"{base_url}/api/results", timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f"📊 Resultados atuais: {results['total']} resultados")
            
            if results.get('session_only'):
                print("✅ Apenas dados da sessão atual (sem histórico)")
            else:
                print("⚠️  Dados históricos podem estar sendo carregados")
                
            if results['total'] == 0:
                print("✅ Sessão iniciada limpa (sem dados históricos)")
            else:
                print(f"ℹ️  Sessão tem {results['total']} resultados da sessão atual")
        else:
            print(f"❌ Erro ao obter resultados: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste de dados históricos: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes de correção de conexão...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor não está respondendo. Inicie o servidor primeiro.")
            sys.exit(1)
    except Exception as e:
        print("❌ Servidor não está rodando. Inicie o servidor primeiro.")
        print("   Execute: python backend/polling_app.py")
        sys.exit(1)
    
    # Executar testes
    test_connection()
    test_manual_result()
    test_session_clear()
    test_no_historical_data()
    
    print("\n🎉 Todos os testes concluídos!")
    print("💡 Se o sistema ainda não estiver recebendo resultados, verifique:")
    print("   - A conexão com a internet")
    print("   - Se a PlayNabets está funcionando")
    print("   - Os logs do servidor para erros específicos")
    print("\n🧹 Para limpar a sessão manualmente:")
    print("   curl -X POST http://localhost:5000/api/session/clear")
