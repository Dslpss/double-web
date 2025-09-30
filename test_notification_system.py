#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar o sistema de notificações diretamente
"""

import sys
import os

# Adicionar o diretório shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

def test_notification_system():
    """Testa o sistema de notificações."""
    print("Testando sistema de notificacoes...")
    print("=" * 50)
    
    try:
        from src.notifications.pattern_notifier import get_notifier, notify_pattern
        
        # Obter notificador
        notifier = get_notifier()
        if not notifier:
            print("ERRO - Notificador nao disponivel")
            return False
        
        print(f"OK - Notificador obtido")
        print(f"   Habilitado: {notifier.enabled}")
        print(f"   Confianca minima: {notifier.min_confidence}")
        print(f"   Callback web: {notifier.web_callback is not None}")
        
        # Configurar callback de teste
        web_notifications = []
        
        def test_callback(data):
            web_notifications.append(data)
            print(f"   Callback recebeu: {data['type']} - {data.get('pattern_type', 'N/A')}")
        
        notifier.set_web_callback(test_callback)
        print("OK - Callback de teste configurado")
        
        # Testar notificação
        print("\nEnviando notificacao de teste...")
        success = notify_pattern(
            pattern_type="Teste Manual",
            detected_number=7,
            predicted_color="red",
            confidence=0.8,
            reasoning="Teste de notificacao manual",
            pattern_id="test_manual"
        )
        
        if success:
            print("OK - Notificacao enviada com sucesso")
            print(f"   Notificacoes recebidas: {len(web_notifications)}")
            
            if web_notifications:
                notif = web_notifications[0]
                print(f"   Tipo: {notif['type']}")
                print(f"   Pattern: {notif['pattern_type']}")
                print(f"   Cor: {notif['predicted_color']}")
                print(f"   Confianca: {notif['confidence']}")
        else:
            print("ERRO - Falha ao enviar notificacao")
        
        return success
        
    except Exception as e:
        print(f"ERRO - Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analyzer_notifications():
    """Testa notificações através do analyzer."""
    print("\nTestando notificacoes via analyzer...")
    print("=" * 50)
    
    try:
        from blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
        
        # Criar analyzer
        analyzer = BlazeAnalyzerEnhanced(use_official_api=False)
        print("OK - Analyzer criado")
        
        # Configurar callback de teste
        web_notifications = []
        
        def test_callback(data):
            web_notifications.append(data)
            print(f"   Callback analyzer recebeu: {data['type']} - {data.get('pattern_type', 'N/A')}")
        
        # Configurar callback no notificador
        from src.notifications.pattern_notifier import get_notifier
        notifier = get_notifier()
        if notifier:
            notifier.set_web_callback(test_callback)
            print("OK - Callback configurado no analyzer")
        
        # Adicionar alguns resultados para análise
        print("Adicionando resultados para analise...")
        for i in range(5):
            analyzer.add_manual_result(i + 1, 'red' if i % 2 == 0 else 'black')
        
        print("OK - Resultados adicionados")
        
        # Forçar análise
        print("Executando analise...")
        analysis = analyzer.analyze_comprehensive()
        
        if analysis:
            print("OK - Analise executada")
            print(f"   Notificacoes geradas: {len(web_notifications)}")
        else:
            print("AVISO - Analise nao retornou dados")
        
        return True
        
    except Exception as e:
        print(f"ERRO - Erro no teste do analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testando sistema de notificacoes completo...")
    print("=" * 50)
    
    success1 = test_notification_system()
    success2 = test_analyzer_notifications()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("SUCESSO - Sistema de notificacoes funcionando!")
    else:
        print("ERRO - Problemas encontrados no sistema de notificacoes")
    
    print("\nSe as notificacoes nao aparecem na interface web:")
    print("1. Verifique se o callback web esta configurado corretamente")
    print("2. Verifique se o notificador esta habilitado")
    print("3. Verifique se a confianca minima nao esta muito alta")
    print("4. Verifique se ha dados suficientes para detectar padroes")
