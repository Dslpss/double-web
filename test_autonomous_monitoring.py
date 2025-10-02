#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste do sistema autônomo em tempo real
"""

import asyncio
import time
from autonomous_roulette_system import AutonomousRouletteSystem

async def test_autonomous_monitoring():
    """Testa o sistema autônomo por 3 minutos."""
    print("🤖 SISTEMA AUTÔNOMO EM TEMPO REAL")
    print("=" * 60)
    print("🔄 Renovação automática a cada 20 min")
    print("🎲 Monitorando por 3 minutos...")
    print("🚫 Sistema à prova de erro 401")
    print()
    
    system = AutonomousRouletteSystem()
    
    # Usar JSESSIONID conhecido que funciona
    system.current_jsessionid = "TT-i7kAu6dD9JsG4ubagYrmYNH7jpmTCQitHDfOsC5QMKWdaX7PB!1928883527-12b99c5a"
    system.last_token_refresh = time.time()
    
    # Iniciar o sistema
    system.start()
    
    try:
        start_time = time.time()
        last_count = len(system.results_cache)
        
        while time.time() - start_time < 180:  # 3 minutos
            await asyncio.sleep(20)  # Verificar a cada 20 segundos
            
            current_count = len(system.results_cache)
            elapsed = int(time.time() - start_time)
            
            if current_count > last_count:
                new_results = current_count - last_count
                print(f"⏱️  {elapsed:3}s | 🤖 +{new_results} AUTÔNOMOS! Total: {current_count}")
                
                # Mostrar os últimos resultados
                recent = system.results_cache[-new_results:]
                for result in recent:
                    print(f"     🤖 {result.number:2} {result.color} {result.color_name} (ID: {result.game_id})")
                
                last_count = current_count
            else:
                print(f"⏱️  {elapsed:3}s | ⏳ Aguardando... (Total: {current_count})")
        
        print(f"\n✅ Teste autônomo concluído!")
        
        # Estatísticas finais
        dashboard_data = system.get_dashboard_data()
        stats = dashboard_data.get('statistics', {})
        color_freq = stats.get('color_frequency', {})
        
        print(f"🤖 Total autônomo: {len(system.results_cache)} resultados")
        print(f"🔴 Vermelhos: {color_freq.get('RED', 0)}")
        print(f"⚫ Pretos: {color_freq.get('BLACK', 0)}")
        print(f"🟢 Verdes: {color_freq.get('GREEN', 0)}")
        
        # Status do sistema
        status = dashboard_data.get('status', {})
        print(f"\n📊 Status do sistema:")
        print(f"   Running: {status.get('running', False)}")
        print(f"   JSESSIONID ativo: {status.get('jsessionid_active', False)}")
        print(f"   Última renovação: {status.get('last_refresh', 'N/A')}")
        
    finally:
        system.stop()
        print("\n🛑 Sistema autônomo parado")

if __name__ == "__main__":
    asyncio.run(test_autonomous_monitoring())
