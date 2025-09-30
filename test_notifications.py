#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar se as notificações estão funcionando
"""

import requests
import json
import time

def test_notifications_api():
    """Testa a API de notificações."""
    base_url = "http://localhost:5000"
    
    print("Testando API de notificacoes...")
    print("=" * 50)
    
    try:
        # Testar endpoint de notificações
        response = requests.get(f"{base_url}/api/notifications/web", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"OK - Notificacoes recebidas: {data['total']} total")
            print(f"   Notificacoes retornadas: {len(data['notifications'])}")
            
            if data['notifications']:
                print("   Detalhes das notificacoes:")
                for i, notif in enumerate(data['notifications'][-3:]):  # Últimas 3
                    print(f"     {i+1}. Tipo: {notif.get('type', 'N/A')}")
                    print(f"        Pattern: {notif.get('pattern_type', 'N/A')}")
                    print(f"        Confianca: {notif.get('confidence', 'N/A')}")
                    print(f"        Timestamp: {notif.get('timestamp', 'N/A')}")
            else:
                print("   Nenhuma notificacao encontrada")
        else:
            print(f"ERRO - Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"ERRO - Erro na requisicao: {e}")

def test_pattern_status():
    """Testa o status da detecção de padrões."""
    base_url = "http://localhost:5000"
    
    print("\nTestando status de deteccao de padroes...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/debug/pattern_status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"OK - Status obtido")
            print(f"   Analyzer disponivel: {status.get('analyzer_available', False)}")
            print(f"   Dados manuais: {status.get('manual_data_count', 0)}")
            print(f"   Dados API: {status.get('api_data_count', 0)}")
            print(f"   Notificacoes web: {status.get('total_web_notifications', 0)}")
            print(f"   Notificacoes de padroes: {status.get('pattern_notifications', 0)}")
            print(f"   Notificador habilitado: {status.get('notifier_enabled', False)}")
            print(f"   Callback web configurado: {status.get('web_callback_configured', False)}")
            
            if status.get('last_5_results'):
                print("   Ultimos 5 resultados:")
                for result in status['last_5_results']:
                    print(f"     {result.get('number', 'N/A')} ({result.get('color', 'N/A')})")
        else:
            print(f"ERRO - Status: {response.status_code}")
            
    except Exception as e:
        print(f"ERRO - Erro na requisicao: {e}")

def test_force_pattern_detection():
    """Testa forçar detecção de padrões."""
    base_url = "http://localhost:5000"
    
    print("\nTestando forcar deteccao de padroes...")
    print("=" * 50)
    
    try:
        response = requests.post(f"{base_url}/api/debug/force_pattern_detection", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("OK - Deteccao forcada com sucesso")
                print(f"   Mensagem: {result.get('message', 'N/A')}")
                
                # Aguardar um pouco e verificar se notificação foi criada
                time.sleep(2)
                print("\nVerificando se notificacao foi criada...")
                test_notifications_api()
            else:
                print(f"ERRO - Falha na deteccao: {result.get('error', 'N/A')}")
        else:
            print(f"ERRO - Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"ERRO - Erro na requisicao: {e}")

def test_session_status():
    """Testa o status da sessão."""
    base_url = "http://localhost:5000"
    
    print("\nTestando status da sessao...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/session/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"OK - Status da sessao obtido")
            print(f"   Total de resultados: {status.get('total_results', 0)}")
            print(f"   Analise disponivel: {status.get('last_analysis_available', False)}")
            print(f"   Notificacoes web: {status.get('web_notifications_count', 0)}")
            print(f"   Dados manuais analyzer: {status.get('analyzer_manual_data', 0)}")
            print(f"   Dados API analyzer: {status.get('analyzer_api_data', 0)}")
            print(f"   PlayNabets conectado: {status.get('playnabets_connected', False)}")
        else:
            print(f"ERRO - Status: {response.status_code}")
            
    except Exception as e:
        print(f"ERRO - Erro na requisicao: {e}")

if __name__ == "__main__":
    print("Testando sistema de notificacoes...")
    print("=" * 50)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code != 200:
            print("ERRO - Servidor nao esta respondendo. Inicie o servidor primeiro.")
            exit(1)
    except Exception as e:
        print("ERRO - Servidor nao esta rodando. Inicie o servidor primeiro.")
        print("   Execute: python backend/polling_app.py")
        exit(1)
    
    # Executar testes
    test_session_status()
    test_pattern_status()
    test_notifications_api()
    test_force_pattern_detection()
    
    print("\n" + "=" * 50)
    print("Teste de notificacoes concluido!")
    print("\nSe as notificacoes nao estao aparecendo na interface:")
    print("1. Verifique se o callback web esta configurado")
    print("2. Verifique se o notificador esta habilitado")
    print("3. Verifique se ha dados suficientes para analise")
    print("4. Tente forcar a deteccao de padroes")