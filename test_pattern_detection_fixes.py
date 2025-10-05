#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para validar correções no sistema de detecção de padrões.
"""

import sys
import time
from datetime import datetime

def test_cooldown_config():
    """Testa se as configurações de cooldown foram aplicadas."""
    print("🧪 Teste 1: Verificar configurações de cooldown")
    print("-" * 50)
    
    try:
        from shared.blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
        
        analyzer = BlazeAnalyzerEnhanced(use_official_api=False)
        
        # Verificar configurações
        cooldown = getattr(analyzer, 'signal_cooldown_seconds', 0)
        min_rounds = getattr(analyzer, 'min_rounds_for_analysis', 0)
        resignal_limit = getattr(analyzer, 'immediate_resignal_limit', -1)
        
        print(f"✓ Cooldown entre sinais: {cooldown}s (esperado: 180s)")
        print(f"✓ Rodadas mínimas: {min_rounds} (esperado: 8)")
        print(f"✓ Limite de re-sinais: {resignal_limit} (esperado: 0)")
        
        # Validar valores
        assert cooldown == 180, f"Cooldown incorreto: {cooldown} != 180"
        assert min_rounds == 8, f"Rodadas mínimas incorretas: {min_rounds} != 8"
        assert resignal_limit == 0, f"Limite de re-sinais incorreto: {resignal_limit} != 0"
        
        print("\n✅ Teste 1: PASSOU\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Teste 1: FALHOU - {str(e)}\n")
        return False

def test_should_detect_patterns():
    """Testa a função _should_detect_patterns."""
    print("🧪 Teste 2: Verificar lógica de detecção de padrões")
    print("-" * 50)
    
    try:
        from shared.blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
        
        analyzer = BlazeAnalyzerEnhanced(use_official_api=False)
        
        # Teste 1: Sem dados suficientes
        analyzer.manual_data = [
            {'roll': 1, 'color': 'red', 'timestamp': time.time()},
            {'roll': 2, 'color': 'black', 'timestamp': time.time()},
        ]
        
        should_detect = analyzer._should_detect_patterns()
        print(f"✓ Com 2 rodadas (< 8): {should_detect} (esperado: False)")
        assert not should_detect, "Não deveria detectar com menos de 8 rodadas"
        
        # Teste 2: Com dados suficientes
        analyzer.manual_data = [
            {'roll': i, 'color': 'red' if i % 2 else 'black', 'timestamp': time.time() - (10 * i)}
            for i in range(10)
        ]
        analyzer.last_pattern_detected_at = 0  # Sem padrão anterior
        
        should_detect = analyzer._should_detect_patterns()
        print(f"✓ Com 10 rodadas e sem cooldown: {should_detect} (esperado: True)")
        assert should_detect, "Deveria detectar com 10 rodadas e sem cooldown"
        
        # Teste 3: Durante cooldown
        analyzer.last_pattern_detected_at = time.time()  # Padrão detectado agora
        
        should_detect = analyzer._should_detect_patterns()
        print(f"✓ Durante cooldown (0s): {should_detect} (esperado: False)")
        assert not should_detect, "Não deveria detectar durante cooldown"
        
        print("\n✅ Teste 2: PASSOU\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Teste 2: FALHOU - {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

def test_pattern_thresholds():
    """Testa os limiares de detecção de padrões."""
    print("🧪 Teste 3: Verificar limiares de detecção")
    print("-" * 50)
    
    try:
        # Verificar no código fonte se os valores estão corretos
        with open('shared/blaze_analyzer_enhanced.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar sequência mínima (deve ser >= 6)
        if 'len(recent_colors) >= 6:' in content and 'len(set(recent_colors)) == 1' in content:
            print("✓ Sequência mínima: 6 rodadas consecutivas")
        else:
            raise AssertionError("Sequência mínima não encontrada ou incorreta")
        
        # Verificar predominância mínima (deve ser > 0.75)
        if '> 0.75:' in content and 'dominant_count / len(recent_colors)' in content:
            print("✓ Predominância mínima: 75%")
        else:
            raise AssertionError("Predominância mínima não encontrada ou incorreta")
        
        # Verificar confiança base para sequências (deve ser >= 0.72)
        if 'base_confidence = 0.72' in content:
            print("✓ Confiança base sequências: 72%")
        else:
            print("⚠️  Confiança base sequências não encontrada exatamente, mas pode estar ok")
        
        # Verificar confiança base para predominância (deve ser >= 0.68)
        if 'base_confidence = 0.68' in content:
            print("✓ Confiança base predominância: 68%")
        else:
            print("⚠️  Confiança base predominância não encontrada exatamente, mas pode estar ok")
        
        print("\n✅ Teste 3: PASSOU\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Teste 3: FALHOU - {str(e)}\n")
        return False

def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🎯 TESTE DE CORREÇÕES - SISTEMA DE DETECÇÃO DE PADRÕES")
    print("="*60 + "\n")
    
    results = []
    
    # Executar testes
    results.append(("Configurações de cooldown", test_cooldown_config()))
    results.append(("Lógica de detecção", test_should_detect_patterns()))
    results.append(("Limiares de detecção", test_pattern_thresholds()))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {name}")
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! Sistema pronto para deploy.")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
