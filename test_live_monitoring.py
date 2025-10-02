#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste de monitoramento em tempo real
Verifica se novos resultados estão sendo capturados continuamente
"""

import asyncio
import time
from pragmatic_roulette_api_monitor import PragmaticRouletteAPIMonitor

async def test_live_monitoring():
    """Testa monitoramento em tempo real por alguns minutos."""
    print("🔴 TESTE DE MONITORAMENTO EM TEMPO REAL")
    print("=" * 50)
    print("⏰ Monitorando por 3 minutos...")
    print("🎲 Aguardando novos resultados da roleta...")
    print()
    
    monitor = PragmaticRouletteAPIMonitor()
    
    # Iniciar o monitor
    monitor.start()
    
    try:
        # Monitorar por 3 minutos (180 segundos)
        start_time = time.time()
        last_count = len(monitor.results_cache)
        
        while time.time() - start_time < 180:  # 3 minutos
            await asyncio.sleep(10)  # Verificar a cada 10 segundos
            
            current_count = len(monitor.results_cache)
            elapsed = int(time.time() - start_time)
            
            if current_count > last_count:
                new_results = current_count - last_count
                print(f"⏱️  {elapsed:3}s | 🎲 +{new_results} novos resultados! Total: {current_count}")
                
                # Mostrar os últimos resultados
                recent = monitor.results_cache[-new_results:]
                for result in recent:
                    print(f"     → {result.number:2} {result.color} {result.color_name}")
                
                last_count = current_count
            else:
                print(f"⏱️  {elapsed:3}s | ⏳ Aguardando... (Total: {current_count})")
        
        print(f"\n✅ Teste concluído!")
        print(f"📊 Total de resultados capturados: {len(monitor.results_cache)}")
        
        # Mostrar estatísticas finais
        dashboard_data = monitor.get_dashboard_data()
        stats = dashboard_data.get('statistics', {})
        color_freq = stats.get('color_frequency', {})
        
        print(f"🔴 Vermelhos: {color_freq.get('RED', 0)}")
        print(f"⚫ Pretos: {color_freq.get('BLACK', 0)}")
        print(f"🟢 Verdes: {color_freq.get('GREEN', 0)}")
        
    finally:
        # Parar o monitor
        monitor.stop()
        print("\n🛑 Monitor parado")

if __name__ == "__main__":
    asyncio.run(test_live_monitoring())
