#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste de monitoramento em tempo real com API real
"""

import asyncio
import time
from pragmatic_roulette_api_monitor import PragmaticRouletteAPIMonitor

async def test_real_time():
    """Testa monitoramento em tempo real por 3 minutos."""
    print("🎮 MONITORAMENTO EM TEMPO REAL - API REAL")
    print("=" * 60)
    print("🎲 Monitorando por 3 minutos...")
    print("🔴 Aguardando novos resultados da Roleta Brasileira...")
    print()
    
    monitor = PragmaticRouletteAPIMonitor()
    
    # Iniciar o monitor
    monitor.start()
    
    try:
        start_time = time.time()
        last_count = len(monitor.results_cache)
        
        while time.time() - start_time < 180:  # 3 minutos
            await asyncio.sleep(20)  # Verificar a cada 20 segundos
            
            current_count = len(monitor.results_cache)
            elapsed = int(time.time() - start_time)
            
            if current_count > last_count:
                new_results = current_count - last_count
                print(f"⏱️  {elapsed:3}s | 🎲 +{new_results} NOVOS REAIS! Total: {current_count}")
                
                # Mostrar os últimos resultados
                recent = monitor.results_cache[-new_results:]
                for result in recent:
                    print(f"     🎮 {result.number:2} {result.color} {result.color_name} (ID: {result.game_id})")
                
                last_count = current_count
            else:
                print(f"⏱️  {elapsed:3}s | ⏳ Aguardando... (Total: {current_count})")
        
        print(f"\n✅ Monitoramento concluído!")
        
        # Estatísticas finais
        dashboard_data = monitor.get_dashboard_data()
        stats = dashboard_data.get('statistics', {})
        color_freq = stats.get('color_frequency', {})
        
        print(f"📊 Total capturado: {len(monitor.results_cache)} resultados REAIS")
        print(f"🔴 Vermelhos: {color_freq.get('RED', 0)}")
        print(f"⚫ Pretos: {color_freq.get('BLACK', 0)}")
        print(f"🟢 Verdes: {color_freq.get('GREEN', 0)}")
        
        # Mostrar últimos 10 resultados
        print(f"\n🎲 Últimos 10 resultados REAIS:")
        for i, result in enumerate(monitor.results_cache[-10:], 1):
            print(f"   {i:2}. 🎮 {result.number:2} {result.color} {result.color_name}")
        
    finally:
        monitor.stop()
        print("\n🛑 Monitor parado")

if __name__ == "__main__":
    asyncio.run(test_real_time())
