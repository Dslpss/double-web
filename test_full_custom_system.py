#!/usr/bin/env python3
"""
Script para testar o sistema completo de padrões personalizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
import time

def test_full_custom_pattern_system():
    """Teste completo do sistema de padrões personalizados"""
    print("🔍 Teste Completo do Sistema de Padrões Personalizados")
    print("=" * 60)
    
    try:
        # Inicializar analyzer
        print("🚀 Inicializando analyzer...")
        analyzer = BlazeAnalyzerEnhanced(use_official_api=False)
        print("✅ Analyzer inicializado")
        
        # Verificar se padrões personalizados estão disponíveis
        if hasattr(analyzer, 'custom_pattern_manager') and analyzer.custom_pattern_manager:
            print("✅ Sistema de padrões personalizados disponível")
            patterns = analyzer.custom_pattern_manager.get_all_patterns()
            print(f"📋 {len(patterns)} padrões carregados")
            
            for pattern in patterns:
                print(f"   • {pattern.name} ({'ATIVO' if pattern.enabled else 'INATIVO'})")
        else:
            print("❌ Sistema de padrões personalizados NÃO disponível")
            return
        
        # Simular dados de teste que devem ativar os padrões
        print("\n🧪 Simulando dados que devem ativar padrões...")
        
        # Dados que devem ativar "1 Red → Jogar Red"
        test_data = [
            {"id": "1", "color": "red", "roll": 1, "timestamp": time.time() - 600},
            {"id": "2", "color": "red", "roll": 3, "timestamp": time.time() - 540},
            {"id": "3", "color": "red", "roll": 1, "timestamp": time.time() - 480},
            {"id": "4", "color": "red", "roll": 5, "timestamp": time.time() - 420},
            {"id": "5", "color": "red", "roll": 1, "timestamp": time.time() - 360},
            {"id": "6", "color": "red", "roll": 7, "timestamp": time.time() - 300},
            {"id": "7", "color": "red", "roll": 1, "timestamp": time.time() - 240},
            {"id": "8", "color": "red", "roll": 9, "timestamp": time.time() - 180},
            {"id": "9", "color": "red", "roll": 1, "timestamp": time.time() - 120},
            {"id": "10", "color": "red", "roll": 12, "timestamp": time.time() - 60},
        ]
        
        print("📊 Dados de teste:")
        for i, item in enumerate(test_data, 1):
            print(f"   {i:2d}. Número: {item['roll']:2d}, Cor: {item['color']:5s}")
        
        # Primeiro, vamos adicionar os dados ao analyzer
        print("\n📥 Adicionando dados ao analyzer...")
        for data in test_data:
            analyzer.add_manual_result(data['roll'], data['color'])
        
        # Executar análise
        print("\n🔍 Executando análise...")
        analysis_result = analyzer.analyze_comprehensive(use_manual_data=True)
        
        print(f"✅ Análise concluída")
        print(f"📊 Tipo do resultado: {type(analysis_result)}")
        
        if isinstance(analysis_result, dict):
            print("📋 Chaves do resultado:")
            for key in analysis_result.keys():
                print(f"   • {key}: {type(analysis_result[key])}")
            
            # Verificar padrões personalizados
            custom_patterns = analysis_result.get('custom_patterns', [])
            print(f"\n🎯 Padrões personalizados detectados: {len(custom_patterns)}")
            
            if custom_patterns:
                for pattern_info in custom_patterns:
                    pattern = pattern_info.get('pattern')
                    if pattern:
                        print(f"   ✅ {pattern.name}")
                        print(f"      Confiança: {pattern_info.get('confidence', 'N/A')}")
                        print(f"      Razão: {pattern_info.get('reasoning', 'N/A')}")
                        print(f"      Sugestão: {pattern_info.get('suggestion', 'N/A')}")
            else:
                print("   ❌ Nenhum padrão personalizado detectado")
                
                # Debug: testar diretamente o manager
                print("\n🔧 Debug: testando manager diretamente...")
                formatted_data = analyzer._format_data_for_custom_patterns(test_data)
                print("📊 Dados formatados:")
                for i, item in enumerate(formatted_data[:5], 1):
                    print(f"   {i}. {item}")
                
                triggered = analyzer.custom_pattern_manager.check_patterns(formatted_data)
                print(f"🎯 Padrões ativados diretamente: {len(triggered)}")
                
                for pattern_info in triggered:
                    pattern = pattern_info.get('pattern')
                    if pattern:
                        print(f"   ✅ {pattern.name}")
        else:
            print(f"❌ Resultado inesperado: {analysis_result}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_custom_pattern_system()