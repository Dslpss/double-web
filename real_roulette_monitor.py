#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor para capturar dados reais da roleta
Baseado no JSON capturado: roulette.tableState
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from collections import deque

class RealRouletteMonitor:
    """Monitor para dados reais da roleta."""
    
    def __init__(self):
        self.base_url = "https://central.playnabet.com"
        self.notifications_url = "https://betsolution.net/roleta/notifications.php"
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
        self.token_usuario = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkwMjQ2NjQsImV4cCI6MTc1OTYyOTQ2NCwidXNlciI6eyJpZCI6NjMzMTR9fQ.BgvAuiW2_rUF8TUI9IdiV2swr3El7xN8qTrIgISN9AU"
        
        self.running = False
        self.results = deque(maxlen=100)
        self.last_game_id = None
        
    def get_headers(self):
        """Headers para requisições."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://playnabets.com/',
            'Origin': 'https://playnabets.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=4',
            'Te': 'trailers'
        }
    
    def get_color(self, number):
        """Determina a cor do número."""
        if number == 0:
            return '🟢 VERDE'
        elif number % 2 == 1:
            return '🔴 VERMELHO'
        else:
            return '⚫ PRETO'
    
    def process_roulette_data(self, data):
        """Processa dados da roleta."""
        try:
            if not isinstance(data, list):
                return
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                # Procurar por dados de roleta
                if 'type' in item and 'roulette' in item['type']:
                    args = item.get('args', {})
                    
                    if args.get('state') == 'GAME_RESOLVED':
                        game_id = args.get('gameId')
                        result = args.get('result', [])
                        game_number = args.get('gameNumber', '')
                        
                        # Verificar se é um jogo novo
                        if game_id and game_id != self.last_game_id:
                            self.last_game_id = game_id
                            
                            if result and len(result) > 0:
                                number = int(result[0])
                                
                                if 0 <= number <= 36:
                                    color = self.get_color(number)
                                    timestamp = datetime.now().strftime('%H:%M:%S')
                                    
                                    result_data = {
                                        'number': number,
                                        'color': color,
                                        'timestamp': timestamp,
                                        'game_id': game_id,
                                        'game_number': game_number,
                                        'source': 'real_roulette',
                                        'round_id': f'round_{int(time.time())}'
                                    }
                                    
                                    self.results.append(result_data)
                                    
                                    print(f"🎲 [{timestamp}] RESULTADO REAL: {number} {color}")
                                    print(f"   Jogo: {game_number} (ID: {game_id})")
                                    
                                    # Mostrar estatísticas a cada 5 números
                                    if len(self.results) % 5 == 0:
                                        self.show_statistics()
                                    
                                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro ao processar dados: {e}")
            return False
    
    def show_statistics(self):
        """Mostra estatísticas dos resultados."""
        if not self.results:
            return
        
        numbers = [r['number'] for r in self.results]
        
        print(f"\n📊 ESTATÍSTICAS REAIS ({len(numbers)} números):")
        print(f"Últimos 10: {numbers[-10:]}")
        
        # Contagem por cor
        red_count = sum(1 for n in numbers if n % 2 == 1 and n != 0)
        black_count = sum(1 for n in numbers if n % 2 == 0 and n != 0)
        green_count = sum(1 for n in numbers if n == 0)
        
        print(f"🔴 Vermelhos: {red_count} | ⚫ Pretos: {black_count} | 🟢 Verdes: {green_count}")
        print("=" * 60)
    
    async def monitor_notifications(self):
        """Monitora as notificações da roleta."""
        try:
            print("🔍 Monitorando notificações da roleta...")
            
            async with aiohttp.ClientSession(headers=self.get_headers()) as session:
                while self.running:
                    try:
                        # Fazer requisição para notifications.php
                        async with session.get(f"{self.notifications_url}?id=12") as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Tentar decodificar base64
                                try:
                                    import base64
                                    decoded = base64.b64decode(content).decode('utf-8')
                                    data = json.loads(decoded)
                                    
                                    # Processar dados
                                    if self.process_roulette_data(data):
                                        print("✅ Novo resultado capturado!")
                                    else:
                                        print("⏳ Nenhum resultado novo")
                                
                                except Exception as e:
                                    print(f"❌ Erro ao decodificar: {e}")
                                    
                            else:
                                print(f"❌ Erro HTTP: {response.status}")
                        
                        # Aguardar antes da próxima verificação
                        await asyncio.sleep(5)
                        
                    except Exception as e:
                        print(f"❌ Erro na requisição: {e}")
                        await asyncio.sleep(10)
        
        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")
    
    def start(self):
        """Inicia o monitor."""
        if self.running:
            print("⚠️ Monitor já está rodando")
            return
            
        self.running = True
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.monitor_notifications())
            except KeyboardInterrupt:
                print("\n🛑 Monitor interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
            finally:
                loop.close()
        
        import threading
        self.thread = threading.Thread(target=run_async, name="RealRouletteMonitor")
        self.thread.start()
    
    def stop(self):
        """Para o monitor."""
        print("🛑 Parando monitor...")
        self.running = False
        
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=5)
    
    def get_recent_results(self, count=10):
        """Retorna os resultados recentes."""
        return list(self.results)[-count:]

# Função principal
async def main():
    """Função principal."""
    print("🎯 Monitor de Roleta Real - Dados em Tempo Real")
    print("=" * 60)
    print("Baseado no JSON capturado: roulette.tableState")
    print("Pressione Ctrl+C para parar")
    print()
    
    monitor = RealRouletteMonitor()
    
    try:
        monitor.start()
        
        # Aguardar indefinidamente
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Parando monitor...")
        monitor.stop()
        print("✅ Monitor parado!")

if __name__ == "__main__":
    asyncio.run(main())
