#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste rápido para o integrador da Roleta Brasileira
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrators.pragmatic_brazilian_roulette import PragmaticBrazilianRoulette


def test_login_and_history():
    """Testa login e busca de histórico."""
    
    print("=" * 60)
    print("TESTE: Pragmatic Brazilian Roulette Integrator")
    print("=" * 60)
    print()
    
    # Carregar variáveis de ambiente do .env
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    USERNAME = os.getenv('PRAGMATIC_USERNAME')
    PASSWORD = os.getenv('PRAGMATIC_PASSWORD')
    
    if not USERNAME or not PASSWORD:
        print("❌ Configure as variáveis no arquivo .env")
        return
    
    print("1️⃣  Criando integrador...")
    integrator = PragmaticBrazilianRoulette(USERNAME, PASSWORD)
    print("✅ Integrador criado\n")
    
    print("2️⃣  Fazendo login...")
    if integrator.login():
        print("✅ Login realizado com sucesso!")
        if integrator.jsessionid:
            print(f"   JSESSIONID: {integrator.jsessionid[:50]}...")
        if integrator.token_cassino:
            print(f"   Token: {integrator.token_cassino[:30]}...\n")
    else:
        print("❌ Erro no login")
        return
    
    print("3️⃣  Buscando histórico (últimos 20 jogos)...")
    history = integrator.get_history(num_games=20)
    
    if history:
        print(f"✅ Obtidos {len(history)} resultados\n")
        
        print("📊 Últimos 10 resultados:")
        print("-" * 60)
        print(f"{'#':<4} {'Número':<8} {'Cor':<10} {'Game ID':<20}")
        print("-" * 60)
        
        for i, result in enumerate(history[:10], 1):
            print(f"{i:<4} {result['number']:<8} {result['color']:<10} {result['id']:<20}")
        
        print("-" * 60)
        
        # Estatísticas
        colors = [r['color'] for r in history]
        red_count = colors.count('red')
        black_count = colors.count('black')
        green_count = colors.count('green')
        
        print(f"\n📈 Estatísticas dos {len(history)} resultados:")
        print(f"   🔴 Red:   {red_count:2d} ({red_count/len(history)*100:.1f}%)")
        print(f"   ⚫ Black: {black_count:2d} ({black_count/len(history)*100:.1f}%)")
        print(f"   🟢 Green: {green_count:2d} ({green_count/len(history)*100:.1f}%)")
        
    else:
        print("❌ Erro ao buscar histórico")
        return
    
    print("\n4️⃣  Testando renovação de sessão...")
    print("   Forçando expiração da sessão...")
    integrator.jsessionid = None
    
    print("   Buscando histórico novamente (deve fazer login automático)...")
    history2 = integrator.get_history(num_games=5)
    
    if history2:
        print(f"✅ Renovação automática funcionou! Obtidos {len(history2)} resultados")
        if integrator.jsessionid:
            print(f"   Novo JSESSIONID: {integrator.jsessionid[:50]}...")
    else:
        print("❌ Erro na renovação automática")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)


def test_continuous_monitor():
    """Testa monitoramento contínuo."""
    
    print("=" * 60)
    print("TESTE: Monitoramento Contínuo")
    print("=" * 60)
    print()
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    USERNAME = os.getenv('PRAGMATIC_USERNAME')
    PASSWORD = os.getenv('PRAGMATIC_PASSWORD')
    
    if not USERNAME or not PASSWORD:
        print("❌ Configure as variáveis no arquivo .env")
        return
    
    integrator = PragmaticBrazilianRoulette(USERNAME, PASSWORD)
    
    def on_new_result(result):
        """Callback para novos resultados."""
        print(f"\n🎰 NOVO RESULTADO: {result['number']} {result['color']} (ID: {result['id']})")
    
    print("Iniciando monitoramento (Ctrl+C para parar)...\n")
    integrator.monitor_continuous(callback=on_new_result, interval=10)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        test_continuous_monitor()
    else:
        test_login_and_history()
