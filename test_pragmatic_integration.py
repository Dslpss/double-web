#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para integração com Pragmatic Play
"""

from pragmatic_play_integrator import PragmaticPlayIntegrator
import time

def main():
    print("=" * 60)
    print("🎰 TESTE DE INTEGRAÇÃO PRAGMATIC PLAY LIVE ROULETTE")
    print("=" * 60)
    print()
    
    # Inicializar integrador
    print("1️⃣  Inicializando integrador...")
    integrator = PragmaticPlayIntegrator(
        table_id="rwbrzportrwa16rg",
        session_id="6Dyk5pcHZ940gAb7TIUV2F_fHQ06A9wOcRC1-JD-Qu8e95yDHxiQ!1928883527-df6535db"
    )
    print(f"   ✅ Table ID: {integrator.table_id}")
    print()
    
    # Buscar histórico
    print("2️⃣  Buscando histórico (últimos 100 jogos)...")
    results = integrator.fetch_history(100)
    
    if not results:
        print("   ❌ Nenhum resultado obtido")
        return
    
    print(f"   ✅ {len(results)} resultados obtidos")
    print()
    
    # Mostrar últimos 10 resultados
    print("3️⃣  Últimos 10 resultados:")
    print("   " + "-" * 50)
    for i, result in enumerate(results[:10], 1):
        color_emoji = {
            'red': '🔴',
            'black': '⚫',
            'green': '🟢'
        }.get(result['color'], '⚪')
        
        print(f"   {i:2d}. {color_emoji} Número: {result['number']:2d} ({result['color'].upper()}) | Game ID: {result['game_id']}")
    print()
    
    # Estatísticas
    print("4️⃣  Estatísticas gerais:")
    stats = integrator.get_statistics()
    print("   " + "-" * 50)
    print(f"   Total de jogos: {stats['total_games']}")
    print(f"   🔴 Vermelho: {stats['red_count']} ({stats['red_percentage']}%)")
    print(f"   ⚫ Preto: {stats['black_count']} ({stats['black_percentage']}%)")
    print(f"   🟢 Verde (0): {stats['green_count']} ({stats['green_percentage']}%)")
    print(f"   Último Game ID: {stats['last_game_id']}")
    print()
    
    # Formato para analyzer
    print("5️⃣  Formato para Analyzer (primeiros 5):")
    print("   " + "-" * 50)
    formatted = integrator.format_for_analyzer(results[:5])
    for item in formatted:
        print(f"   {item}")
    print()
    
    # Teste de busca de novos resultados
    print("6️⃣  Testando busca de novos resultados...")
    print("   Aguardando 5 segundos...")
    time.sleep(5)
    
    new_results = integrator.get_new_results()
    if new_results:
        print(f"   ✅ {len(new_results)} novos resultados encontrados")
        for result in new_results:
            color_emoji = {
                'red': '🔴',
                'black': '⚫',
                'green': '🟢'
            }.get(result['color'], '⚪')
            print(f"   {color_emoji} Novo: {result['number']} ({result['color'].upper()})")
    else:
        print("   ℹ️  Nenhum resultado novo (esperado em teste rápido)")
    print()
    
    # Resumo final
    print("=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print()
    print("📝 Próximos passos:")
    print("   1. Integrar com o app.py (endpoints já criados)")
    print("   2. Testar com: python app.py")
    print("   3. Fazer requisições para:")
    print("      - POST /api/pragmatic/fetch (buscar histórico)")
    print("      - GET /api/pragmatic/results (obter resultados)")
    print("      - GET /api/pragmatic/new (novos resultados)")
    print("      - GET /api/pragmatic/statistics (estatísticas)")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
