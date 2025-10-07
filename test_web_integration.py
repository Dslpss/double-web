#!/usr/bin/env python3
"""
Script para testar o sistema completo de padrões personalizados com web callbacks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import time

BASE_URL = "http://localhost:5000"

def test_custom_patterns_web_integration():
    """Teste de integração web dos padrões personalizados"""
    print("🔍 Teste de Integração Web - Padrões Personalizados")
    print("=" * 60)
    
    try:
        # 1. Verificar status do sistema
        print("1. 📊 Verificando status do sistema...")
        response = requests.get(f"{BASE_URL}/api/custom-patterns/status")
        if response.status_code == 200:
            status = response.json()
            if status.get('success'):
                status_info = status['status']
                print("✅ Status do sistema:")
                print(f"   • Manager disponível: {status_info['custom_pattern_manager_available']}")
                print(f"   • Analyzer disponível: {status_info['analyzer_available']}")
                print(f"   • Analyzer tem manager: {status_info['analyzer_has_custom_manager']}")
                print(f"   • Notifier disponível: {status_info['notifier_available']}")
                print(f"   • Callback web configurado: {status_info['web_callback_configured']}")
                print(f"   • Total de padrões: {status_info['patterns_count']}")
                print(f"   • Padrões habilitados: {status_info['enabled_patterns_count']}")
                
                if not status_info['web_callback_configured']:
                    print("⚠️ PROBLEMA: Callback web não configurado!")
                    return False
            else:
                print(f"❌ Erro ao verificar status: {status.get('error')}")
                return False
        else:
            print(f"❌ Erro HTTP ao verificar status: {response.status_code}")
            return False
        
        # 2. Listar padrões personalizados
        print("\n2. 📋 Listando padrões personalizados...")
        response = requests.get(f"{BASE_URL}/api/custom-patterns")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                patterns = result.get('patterns', [])
                print(f"✅ {len(patterns)} padrões encontrados:")
                for pattern in patterns:
                    print(f"   • {pattern['name']} ({'ATIVO' if pattern['enabled'] else 'INATIVO'})")
            else:
                print(f"❌ Erro ao listar padrões: {result.get('error')}")
                return False
        else:
            print(f"❌ Erro HTTP ao listar padrões: {response.status_code}")
            return False
        
        # 3. Adicionar resultados que devem ativar padrões
        print("\n3. 🎯 Adicionando resultados que devem ativar padrões...")
        
        # Sequência que deve ativar "1 Red → Jogar Red"
        test_sequence = [
            {"number": 1, "color": "red"},
            {"number": 3, "color": "red"},
            {"number": 1, "color": "red"},
            {"number": 5, "color": "red"},
            {"number": 1, "color": "red"},
            {"number": 7, "color": "red"},
            {"number": 1, "color": "red"},
            {"number": 9, "color": "red"},
            {"number": 1, "color": "red"},
            {"number": 12, "color": "red"},
        ]
        
        for i, result in enumerate(test_sequence, 1):
            print(f"   Adicionando resultado {i}: {result['number']} {result['color']}")
            
            response = requests.post(f"{BASE_URL}/api/add-manual-result", json=result)
            if response.status_code == 200:
                result_data = response.json()
                if result_data.get('success'):
                    print(f"   ✅ Resultado adicionado: {result_data.get('message', 'OK')}")
                    
                    # Verificar se houve alertas de padrões personalizados
                    analysis = result_data.get('analysis', {})
                    custom_patterns = analysis.get('custom_patterns', [])
                    if custom_patterns:
                        print(f"   🎯 PADRÃO PERSONALIZADO DETECTADO! {len(custom_patterns)} padrão(ões)")
                        for pattern_info in custom_patterns:
                            pattern = pattern_info.get('pattern', {})
                            print(f"      ✅ {pattern.get('name', 'Padrão')}")
                            print(f"         Confiança: {pattern_info.get('confidence', 'N/A')}")
                            print(f"         Sugestão: {pattern_info.get('suggestion', 'N/A')}")
                else:
                    print(f"   ❌ Erro: {result_data.get('error')}")
            else:
                print(f"   ❌ Erro HTTP: {response.status_code}")
            
            # Pequena pausa entre resultados
            time.sleep(0.5)
        
        # 4. Verificar notificações web
        print("\n4. 🔔 Verificando notificações web...")
        response = requests.get(f"{BASE_URL}/api/notifications")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                notifications = result.get('notifications', [])
                custom_notifications = [n for n in notifications if n.get('type') == 'pattern_detected' and 'CUSTOM' in n.get('pattern_type', '')]
                
                print(f"✅ {len(notifications)} notificações totais")
                print(f"🎯 {len(custom_notifications)} notificações de padrões personalizados")
                
                if custom_notifications:
                    print("   Últimas notificações de padrões personalizados:")
                    for notif in custom_notifications[-3:]:  # Últimas 3
                        print(f"      • {notif.get('pattern_type', 'N/A')} -> {notif.get('predicted_color', 'N/A')}")
                        print(f"        Confiança: {notif.get('confidence', 'N/A')}%")
                        print(f"        Horário: {notif.get('timestamp', 'N/A')}")
                else:
                    print("⚠️ Nenhuma notificação de padrão personalizado encontrada")
            else:
                print(f"❌ Erro ao verificar notificações: {result.get('error')}")
        else:
            print(f"❌ Erro HTTP ao verificar notificações: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("✅ Teste de integração concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_custom_patterns_web_integration()