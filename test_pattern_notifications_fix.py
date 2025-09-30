#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste para verificar se as notificações de padrões estão funcionando
"""

import sys
import os
import time
import json
from datetime import datetime

# Adicionar paths necessários
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_pattern_notifications():
    """Testa se as notificações de padrões estão funcionando"""
    print("Testando notificacoes de padroes...")
    
    try:
        # Importar módulos necessários
        from shared.src.analysis.dual_color_patterns import DualColorPatternDetector
        from shared.src.ml.adaptive_pattern_learner import AdaptivePatternLearner
        from shared.src.notifications.pattern_notifier import PatternNotifier
        
        print("Modulos importados com sucesso")
        
        # Criar notificador
        notifier = PatternNotifier()
        notifier.set_enabled(True)
        notifier.set_min_confidence(0.25)  # Reduzir confiança mínima
        
        # Configurar callback para capturar notificações
        notifications_received = []
        
        def test_callback(notification_data):
            notifications_received.append(notification_data)
            print(f"Notificacao recebida: {notification_data['type']} - {notification_data.get('pattern_type', 'N/A')}")
        
        notifier.set_web_callback(test_callback)
        
        print("Notificador configurado")
        
        # Criar detector dual
        dual_detector = DualColorPatternDetector()
        
        # Criar learner adaptativo
        adaptive_learner = AdaptivePatternLearner()
        
        print("Detectores criados")
        
        # Simular dados de teste
        test_data = []
        colors = ['red', 'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red', 'black']
        
        for i, color in enumerate(colors):
            result = {
                'roll': i + 1,
                'color': color,
                'timestamp': datetime.now().isoformat()
            }
            test_data.append(result)
            
            # Adicionar ao detector dual
            dual_detector.add_result(result)
            
            # Adicionar ao learner adaptativo
            adaptive_learner.add_result(result)
            
            print(f"Dados adicionados: {result['roll']} ({result['color']})")
            
            # Pequena pausa para simular tempo real
            time.sleep(0.1)
        
        print(f"\nTotal de notificacoes recebidas: {len(notifications_received)}")
        
        # Verificar tipos de notificação
        pattern_notifications = [n for n in notifications_received if n.get('type') == 'pattern_detected']
        result_notifications = [n for n in notifications_received if n.get('type') == 'result']
        
        print(f"Notificacoes de padroes: {len(pattern_notifications)}")
        print(f"Notificacoes de resultado: {len(result_notifications)}")
        
        if pattern_notifications:
            print("\nSUCESSO: Notificacoes de padroes estao funcionando!")
            for i, notif in enumerate(pattern_notifications[:3]):  # Mostrar apenas as 3 primeiras
                print(f"  {i+1}. {notif.get('pattern_type', 'N/A')} -> {notif.get('predicted_color', 'N/A')} ({notif.get('confidence', 0):.1%})")
        else:
            print("\nPROBLEMA: Nenhuma notificacao de padrao foi gerada")
            
        # Verificar estatísticas dos detectores
        print(f"\nEstatisticas Dual Detector:")
        print(f"  - Padroes detectados: {len(dual_detector.dual_patterns)}")
        
        print(f"\nEstatisticas Adaptive Learner:")
        print(f"  - Padroes aprendidos: {len(adaptive_learner.learned_patterns)}")
        
        return len(pattern_notifications) > 0
        
    except Exception as e:
        print(f"Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_notifications():
    """Testa as notificações via API web"""
    print("\nTestando notificacoes via API web...")
    
    try:
        import requests
        
        # Testar endpoint de notificações
        response = requests.get('http://localhost:5000/api/notifications/web', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"API respondeu: {data}")
            
            notifications = data.get('notifications', [])
            pattern_notifications = [n for n in notifications if n.get('type') == 'pattern_detected']
            
            print(f"Notificacoes na API: {len(notifications)}")
            print(f"Padroes detectados: {len(pattern_notifications)}")
            
            return len(pattern_notifications) > 0
        else:
            print(f"API retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Servidor nao esta rodando")
        return False
    except Exception as e:
        print(f"Erro na API: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando teste de notificacoes de padroes...")
    print("=" * 60)
    
    # Teste 1: Notificações diretas
    success1 = test_pattern_notifications()
    
    # Teste 2: Notificações via API (se servidor estiver rodando)
    success2 = test_web_notifications()
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES:")
    print(f"  - Notificacoes diretas: {'PASSOU' if success1 else 'FALHOU'}")
    print(f"  - Notificacoes via API: {'PASSOU' if success2 else 'FALHOU'}")
    
    if success1:
        print("\nCORRECAO FUNCIONANDO! As notificacoes de padroes estao sendo geradas.")
    else:
        print("\nAinda ha problemas com as notificacoes de padroes.")
