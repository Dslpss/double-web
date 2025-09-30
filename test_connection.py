#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar a conexão e diagnóstico do sistema
"""

import requests
import json
import time

def test_api_connection():
    """Testa a conexão com a API"""
    try:
        print("[TESTE] Conectando com a API...")
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] API conectada!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Analyzer: {'OK' if data.get('analyzer_ready') else 'ERRO'}")
            print(f"   WebSocket: {'OK' if data.get('ws_connected') else 'ERRO'}")
            return True
        else:
            print(f"[ERRO] API retornou: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERRO] Nao foi possivel conectar a API (servidor nao esta rodando?)")
        return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_results_endpoint():
    """Testa o endpoint de resultados"""
    try:
        print("\n[TESTE] Endpoint de resultados...")
        response = requests.get('http://localhost:5000/api/results', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Endpoint de resultados funcionando!")
            print(f"   Total de resultados: {data.get('total', 0)}")
            if data.get('results'):
                latest = data['results'][0]
                print(f"   Ultimo resultado: {latest.get('number')} ({latest.get('color')})")
            return True
        else:
            print(f"[ERRO] Endpoint de resultados: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_playnabets_status():
    """Testa o status da PlayNabets"""
    try:
        print("\n[TESTE] Status da PlayNabets...")
        response = requests.get('http://localhost:5000/api/playnabets/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Status da PlayNabets obtido!")
            print(f"   Conectado: {'OK' if data.get('connected') else 'ERRO'}")
            print(f"   Rodando: {'OK' if data.get('running') else 'ERRO'}")
            if data.get('last_result'):
                result = data['last_result']
                print(f"   Ultimo resultado: {result.get('number')} ({result.get('color')})")
            return True
        else:
            print(f"[ERRO] Status da PlayNabets: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_add_manual_result():
    """Testa adicionar resultado manual"""
    try:
        print("\n[TESTE] Adicao de resultado manual...")
        import random
        number = random.randint(0, 14)
        color = 'red' if number in [1, 3, 5, 7, 9, 12, 14] else 'black' if number != 0 else 'white'
        
        data = {'number': number, 'color': color}
        response = requests.post('http://localhost:5000/api/add_result', 
                               json=data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Resultado manual adicionado: {number} ({color})")
            return True
        else:
            print(f"[ERRO] Adicionar resultado: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def main():
    print("[INICIANDO] Diagnostico do sistema...\n")
    
    # Testar conexão básica
    if not test_api_connection():
        print("\n[ERRO] Sistema nao esta rodando. Execute: python start.py")
        return
    
    # Testar endpoints
    test_results_endpoint()
    test_playnabets_status()
    test_add_manual_result()
    
    print("\n[OK] Diagnostico concluido!")

if __name__ == "__main__":
    main()
