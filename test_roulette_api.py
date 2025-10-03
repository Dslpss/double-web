#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar as rotas da API da Roleta Brasileira
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_roulette_status():
    """Testa status da roleta."""
    print("\n=== Testando /api/roulette/status ===")
    try:
        response = requests.get(f'{BASE_URL}/api/roulette/status')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_roulette_start():
    """Testa início do monitoramento."""
    print("\n=== Testando /api/roulette/start ===")
    try:
        response = requests.post(f'{BASE_URL}/api/roulette/start')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_roulette_results():
    """Testa busca de resultados."""
    print("\n=== Testando /api/roulette/results ===")
    try:
        response = requests.get(f'{BASE_URL}/api/roulette/results')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_roulette_analysis():
    """Testa análise de padrões."""
    print("\n=== Testando /api/roulette/analysis ===")
    try:
        response = requests.get(f'{BASE_URL}/api/roulette/analysis')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_roulette_stop():
    """Testa parada do monitoramento."""
    print("\n=== Testando /api/roulette/stop ===")
    try:
        response = requests.post(f'{BASE_URL}/api/roulette/stop')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"Erro: {e}")
        return None

def main():
    """Executa todos os testes."""
    print("=" * 80)
    print("TESTE DAS ROTAS DA API DA ROLETA BRASILEIRA")
    print("=" * 80)
    
    # 1. Verificar status inicial
    status = test_roulette_status()
    
    # 2. Iniciar monitoramento
    start_result = test_roulette_start()
    
    if start_result and start_result.get('success'):
        # Aguardar alguns segundos para coletar dados
        print("\n⏳ Aguardando 10 segundos para coletar resultados...")
        time.sleep(10)
        
        # 3. Buscar resultados
        results = test_roulette_results()
        
        # 4. Buscar análise
        analysis = test_roulette_analysis()
        
        # 5. Verificar status após início
        status = test_roulette_status()
        
        # 6. Parar monitoramento
        stop_result = test_roulette_stop()
    else:
        print("\n❌ Falha ao iniciar monitoramento. Verifique as credenciais no .env")
    
    print("\n" + "=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)

if __name__ == '__main__':
    main()
