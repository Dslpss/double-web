#!/usr/bin/env python3
"""
Script para testar alertas absolutos de padrões personalizados
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def wait_for_server():
    """Aguarda o servidor estar disponível"""
    print("🔄 Aguardando servidor estar disponível...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Servidor disponível!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"⏳ Tentativa {i+1}/30...")
    
    print("❌ Servidor não está disponível")
    return False

def add_test_data():
    """Adiciona dados de teste para ativar padrões"""
    print("\n📊 Adicionando dados de teste...")
    
    # Dados que devem ativar o padrão "1 Red → Jogar Red"
    test_data = [
        {"number": 1, "color": "red", "timestamp": int(time.time())},
        {"number": 5, "color": "black", "timestamp": int(time.time()) + 1},
        {"number": 3, "color": "red", "timestamp": int(time.time()) + 2},
        {"number": 7, "color": "red", "timestamp": int(time.time()) + 3},
        {"number": 2, "color": "black", "timestamp": int(time.time()) + 4},
    ]
    
    for i, data in enumerate(test_data):
        try:
            response = requests.post(
                f"{BASE_URL}/api/add_result",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print(f"  ✅ Dados {i+1} adicionados: {data['number']} ({data['color']})")
            else:
                print(f"  ❌ Erro ao adicionar dados {i+1}: {response.text}")
        except Exception as e:
            print(f"  ❌ Erro ao conectar: {e}")
        
        time.sleep(1)  # Pausa entre adições

def check_patterns():
    """Verifica se os padrões foram ativados"""
    print("\n🔍 Verificando padrões ativados...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/custom-patterns/check",
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                triggered = result.get('triggered_patterns', [])
                if triggered:
                    print(f"🎯 {len(triggered)} PADRÃO(ÕES) PERSONALIZADO(S) ATIVADO(S)!")
                    for pattern in triggered:
                        print(f"  ✅ {pattern.get('name', 'Padrão')}: {pattern.get('suggestion', 'Alerta')}")
                        print(f"     Confiança: {pattern.get('confidence', 0):.1%}")
                        print(f"     Razão: {pattern.get('reasoning', 'N/A')}")
                else:
                    print("  Nenhum padrão ativado ainda")
            else:
                print(f"  ❌ Erro na verificação: {result.get('error')}")
        else:
            print(f"  ❌ Erro HTTP: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Erro ao verificar padrões: {e}")

def trigger_analysis():
    """Força uma análise completa"""
    print("\n🔬 Forçando análise completa...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/debug/force_analysis",
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("  ✅ Análise forçada com sucesso")
                analysis = result.get('analysis', {})
                custom_patterns = analysis.get('custom_patterns', [])
                if custom_patterns:
                    print(f"  🎯 {len(custom_patterns)} padrão(ões) personalizado(s) detectado(s) na análise!")
                else:
                    print("  ℹ️ Nenhum padrão personalizado detectado na análise")
            else:
                print(f"  ❌ Erro na análise: {result.get('error')}")
        else:
            print(f"  ❌ Erro HTTP: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Erro ao forçar análise: {e}")

def main():
    print("🎯 Testando Alertas Absolutos de Padrões Personalizados")
    print("=" * 60)
    
    if not wait_for_server():
        return
    
    # Adicionar dados de teste
    add_test_data()
    
    # Aguardar um pouco
    print("\n⏳ Aguardando processamento...")
    time.sleep(3)
    
    # Verificar padrões
    check_patterns()
    
    # Forçar análise
    trigger_analysis()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
    print("🌐 Verifique o navegador em http://localhost:5000/double")
    print("   para ver os alertas visuais!")

if __name__ == "__main__":
    main()
