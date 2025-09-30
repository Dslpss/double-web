#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste rápido para verificar se as notificações de padrões estão funcionando
com requisitos reduzidos
"""

import sys
import os
import time
import json
from datetime import datetime

# Adicionar paths necessários
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_quick_patterns():
    """Testa detecção de padrões com requisitos reduzidos"""
    print("Testando deteccao de padroes com requisitos reduzidos...")
    
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
            print(f"NOTIFICACAO RECEBIDA: {notification_data['type']} - {notification_data.get('pattern_type', 'N/A')}")
        
        notifier.set_web_callback(test_callback)
        
        print("Notificador configurado")
        
        # Criar detector dual com configurações reduzidas
        dual_config = {
            'min_pattern_frequency': 1,
            'min_confidence_threshold': 0.2,
            'sequence_length_range': (2, 4)
        }
        dual_detector = DualColorPatternDetector(dual_config)
        
        # Criar learner adaptativo
        adaptive_learner = AdaptivePatternLearner()
        
        print("Detectores criados com configuracoes reduzidas")
        
        # Simular dados de teste - sequência que deve gerar padrões
        test_data = []
        colors = ['red', 'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red', 'black']
        
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
            for i, notif in enumerate(pattern_notifications[:5]):  # Mostrar até 5
                print(f"  {i+1}. {notif.get('pattern_type', 'N/A')} -> {notif.get('predicted_color', 'N/A')} ({notif.get('confidence', 0):.1%})")
        else:
            print("\nPROBLEMA: Nenhuma notificacao de padrao foi gerada")
            
        # Verificar estatísticas dos detectores
        print(f"\nEstatisticas Dual Detector:")
        print(f"  - Padroes detectados: {len(dual_detector.dual_patterns)}")
        print(f"  - Dados no historico: {len(dual_detector.data_history)}")
        
        print(f"\nEstatisticas Adaptive Learner:")
        print(f"  - Padroes aprendidos: {len(adaptive_learner.learned_patterns)}")
        print(f"  - Dados no historico: {len(adaptive_learner.data_history)}")
        
        # Mostrar padrões detectados
        if dual_detector.dual_patterns:
            print(f"\nPadroes dual detectados:")
            for key, pattern in dual_detector.dual_patterns.items():
                print(f"  - {key}: confianca {pattern.confidence:.1%}")
        
        if adaptive_learner.learned_patterns:
            print(f"\nPadroes adaptativos aprendidos:")
            for key, pattern in adaptive_learner.learned_patterns.items():
                print(f"  - {key}: confianca {pattern.confidence:.1%}")
        
        return len(pattern_notifications) > 0
        
    except Exception as e:
        print(f"Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando teste rapido de notificacoes...")
    print("=" * 60)
    
    success = test_quick_patterns()
    
    print("\n" + "=" * 60)
    if success:
        print("CORRECAO FUNCIONANDO! As notificacoes de padroes estao sendo geradas.")
        print("Agora reinicie o servidor para ver as notificacoes na interface!")
    else:
        print("Ainda ha problemas com as notificacoes de padroes.")
        print("Verifique os logs para mais detalhes.")
