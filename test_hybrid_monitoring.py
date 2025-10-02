#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste do sistema híbrido de monitoramento
API real + simulação inteligente
"""

import asyncio
import time
from pragmatic_roulette_api_monitor import PragmaticRouletteAPIMonitor

async def test_hybrid_system():
    """Testa sistema híbrido por 2 minutos."""
    print("🔥 TESTE DO SISTEMA HÍBRIDO")
    print("=" * 50)
    print("🎲 Monitorando por 2 minutos...")
    print("✨ API real + simulação inteligente")
    print()
    
    monitor = PragmaticRouletteAPIMonitor()
    
    # Iniciar o monitor
    monitor.start()
    
    try:
        start_time = time.time()
        last_count = len(monitor.results_cache)
        
        while time.time() - start_time < 120:  # 2 minutos
            await asyncio.sleep(15)  # Verificar a cada 15 segundos
            
            current_count = len(monitor.results_cache)
            elapsed = int(time.time() - start_time)
            
            if current_count > last_count:
                new_results = current_count - last_count
                print(f"⏱️  {elapsed:3}s | 🎲 +{new_results} novos! Total: {current_count}")
                
                # Mostrar os últimos resultados
                recent = monitor.results_cache[-new_results:]
                for result in recent:
                    source_icon = "🎮" if result.source == "pragmatic_play" else "🤖"
                    print(f"     {source_icon} {result.number:2} {result.color} {result.color_name}")
                
                last_count = current_count
            else:
                print(f"⏱️  {elapsed:3}s | ⏳ Aguardando... (Total: {current_count})")
        
        print(f"\n✅ Teste concluído!")
        
        # Estatísticas finais
        dashboard_data = monitor.get_dashboard_data()
        stats = dashboard_data.get('statistics', {})
        color_freq = stats.get('color_frequency', {})
        
        print(f"📊 Resultados capturados: {len(monitor.results_cache)}")
        print(f"🔴 Vermelhos: {color_freq.get('RED', 0)}")
        print(f"⚫ Pretos: {color_freq.get('BLACK', 0)}")
        print(f"🟢 Verdes: {color_freq.get('GREEN', 0)}")
        
        # Mostrar últimos 5 resultados
        print(f"\n🎲 Últimos 5 resultados:")
        for i, result in enumerate(monitor.results_cache[-5:], 1):
            source_icon = "🎮" if result.source == "pragmatic_play" else "🤖"
            print(f"   {i}. {source_icon} {result.number:2} {result.color} {result.color_name}")
        
    finally:
        monitor.stop()
        print("\n🛑 Monitor parado")

if __name__ == "__main__":
    asyncio.run(test_hybrid_system())
