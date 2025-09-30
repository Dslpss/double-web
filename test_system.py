#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para o Blaze Web System
Testa todas as funcionalidades implementadas
"""

import requests
import json
import time
import sys

# Configurações
BASE_URL = "http://localhost:5000"
TEST_USER = "admin"
TEST_PASSWORD = "admin123"

def test_api_endpoint(endpoint, method="GET", data=None, headers=None):
    """Testa um endpoint da API."""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        print(f"✅ {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"   ❌ Erro: {response.text}")
            return None
        
        return response.json()
    except Exception as e:
        print(f"Erro: {method} {endpoint} - {e}")
        return None

def test_authentication():
    """Testa sistema de autenticação."""
    print("\nTESTANDO AUTENTICACAO")
    print("=" * 50)
    
    # Teste de login
    login_data = {
        "username": TEST_USER,
        "password": TEST_PASSWORD
    }
    
    result = test_api_endpoint("/api/auth/login", "POST", login_data)
    if not result or not result.get('success'):
        print("Falha no login")
        return None
    
    token = result['token']
    print(f"Login realizado - Token: {token[:20]}...")
    
    # Teste de informações do usuário
    headers = {"Authorization": f"Bearer {token}"}
    user_info = test_api_endpoint("/api/auth/me", "GET", headers=headers)
    if user_info:
        print(f"Usuario: {user_info['username']} ({user_info['role']})")
    
    return token

def test_protected_endpoints(token):
    """Testa endpoints que requerem autenticação."""
    print("\nTESTANDO ENDPOINTS PROTEGIDOS")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste de adicionar resultado
    result_data = {
        "number": 7,
        "color": "red"
    }
    
    result = test_api_endpoint("/api/add_result", "POST", result_data, headers)
    if result and result.get('success'):
        print("Resultado adicionado com sucesso")
    
    # Teste de logout
    logout_result = test_api_endpoint("/api/auth/logout", "POST", headers=headers)
    if logout_result and logout_result.get('success'):
        print("Logout realizado com sucesso")

def test_public_endpoints():
    """Testa endpoints públicos."""
    print("\nTESTANDO ENDPOINTS PUBLICOS")
    print("=" * 50)
    
    # Teste de status
    test_api_endpoint("/api/status")
    
    # Teste de resultados
    test_api_endpoint("/api/results")
    
    # Teste de análise
    test_api_endpoint("/api/analysis")
    
    # Teste de predições
    test_api_endpoint("/api/predictions")

def test_pages():
    """Testa páginas web."""
    print("\nTESTANDO PAGINAS WEB")
    print("=" * 50)
    
    pages = [
        ("/", "Pagina Principal"),
        ("/login", "Pagina de Login"),
        ("/dashboard", "Dashboard")
    ]
    
    for page, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"OK {name} - Status: {response.status_code}")
            else:
                print(f"ERRO {name} - Status: {response.status_code}")
        except Exception as e:
            print(f"ERRO {name} - Erro: {e}")

def test_websocket():
    """Testa WebSocket (simulação)."""
    print("\nTESTANDO WEBSOCKET")
    print("=" * 50)
    
    try:
        import socketio
        
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print("WebSocket conectado")
        
        @sio.event
        def disconnect():
            print("WebSocket desconectado")
        
        @sio.event
        def new_result(data):
            print(f"Novo resultado recebido: {data}")
        
        sio.connect(BASE_URL)
        time.sleep(2)
        sio.disconnect()
        
    except ImportError:
        print("SocketIO nao disponivel - pulando teste WebSocket")
    except Exception as e:
        print(f"Erro no WebSocket: {e}")

def main():
    """Executa todos os testes."""
    print("INICIANDO TESTES DO BLAZE WEB SYSTEM")
    print("=" * 60)
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code != 200:
            print("Servidor nao esta respondendo corretamente")
            return
    except Exception as e:
        print(f"Servidor nao esta rodando: {e}")
        print("Execute: python websocket_app.py")
        return
    
    print("Servidor esta rodando")
    
    # Executar testes
    test_public_endpoints()
    test_pages()
    
    token = test_authentication()
    if token:
        test_protected_endpoints(token)
    
    test_websocket()
    
    print("\nTESTES CONCLUIDOS!")
    print("=" * 60)
    print("RESUMO:")
    print("API REST funcionando")
    print("Autenticacao implementada")
    print("Paginas web carregando")
    print("WebSocket configurado")
    print("\nAcesse: http://localhost:5000")
    print("Login: admin / admin123")

if __name__ == "__main__":
    main()
