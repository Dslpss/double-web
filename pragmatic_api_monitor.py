#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor da API real do Pragmatic Play Live Casino
URL: https://games.pragmaticplaylive.net/api/ui/statisticHistory
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from collections import deque

class PragmaticAPIMonitor:
    """Monitor da API real do Pragmatic Play."""
    
    def __init__(self):
        self.api_url = "https://games.pragmaticplaylive.net/api/ui/statisticHistory"
        self.table_id = "rwbrzportrwa16rg"
        self.running = False
        self.results = deque(maxlen=1000)
        self.last_game_id = None
        self.check_count = 0
        
    def get_headers(self):
        """Headers para acessar a API."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://client.pragmaticplaylive.net',
            'Referer': 'https://client.pragmaticplaylive.net/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
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
    
    def parse_game_result(self, game_result):
        """Extrai número e cor do resultado do jogo."""
        try:
            # Formato: "27 Red", "0 Green", "28 Black"
            parts = game_result.strip().split()
            if len(parts) >= 2:
                number = int(parts[0])
                color_text = parts[1].lower()
                
                # Mapear cores
                if color_text == 'green':
                    color = '🟢 VERDE'
                elif color_text == 'red':
                    color = '🔴 VERMELHO'
                elif color_text == 'black':
                    color = '⚫ PRETO'
                else:
                    color = self.get_color(number)
                
                return number, color
            else:
                # Tentar extrair apenas o número
                number = int(game_result.strip())
                color = self.get_color(number)
                return number, color
        except:
            return None, None
    
    def process_api_response(self, data):
        """Processa a resposta da API."""
        try:
            if 'history' not in data:
                print("❌ Resposta da API inválida")
                return False
            
            history = data['history']
            new_results = []
            
            for game in history:
                game_id = game.get('gameId')
                game_result = game.get('gameResult', '')
                
                # Pular se já processamos este jogo
                if self.last_game_id and game_id == self.last_game_id:
                    break
                
                # Processar resultado
                number, color = self.parse_game_result(game_result)
                if number is not None:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    
                    result = {
                        'game_id': game_id,
                        'number': number,
                        'color': color,
                        'timestamp': timestamp,
                        'source': 'pragmatic_api',
                        'round_id': f'round_{game_id}'
                    }
                    
                    new_results.append(result)
                    self.results.append(result)
            
            # Atualizar último game ID processado
            if history:
                self.last_game_id = history[0]['gameId']
            
            # Mostrar novos resultados
            if new_results:
                print(f"🎲 {len(new_results)} novos resultados encontrados:")
                for result in new_results[:10]:  # Mostrar apenas os 10 mais recentes
                    print(f"  {result['number']}: {result['color']} (ID: {result['game_id']})")
                
                if len(new_results) > 10:
                    print(f"  ... e mais {len(new_results) - 10} resultados")
                
                # Mostrar estatísticas a cada 10 novos resultados
                if len(self.results) % 10 == 0:
                    self.show_statistics()
                
                return True
            else:
                print("⏳ Nenhum novo resultado encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao processar resposta da API: {e}")
            return False
    
    def show_statistics(self):
        """Mostra estatísticas dos resultados."""
        if not self.results:
            return
        
        numbers = [r['number'] for r in self.results]
        
        print(f"\n📊 ESTATÍSTICAS ({len(numbers)} números):")
        print(f"Últimos 20: {numbers[-20:]}")
        
        # Contagem por cor
        red_count = sum(1 for n in numbers if n % 2 == 1 and n != 0)
        black_count = sum(1 for n in numbers if n % 2 == 0 and n != 0)
        green_count = sum(1 for n in numbers if n == 0)
        
        print(f"🔴 Vermelhos: {red_count} | ⚫ Pretos: {black_count} | 🟢 Verdes: {green_count}")
        
        # Análise de sequências
        if len(numbers) >= 5:
            last_5 = numbers[-5:]
            print(f"Últimos 5: {last_5}")
        
        print("=" * 60)
    
    async def monitor_api(self):
        """Monitora a API em tempo real."""
        try:
            print(f"🔍 Monitorando API: Pragmatic Play Live Casino")
            print(f"URL: {self.api_url}")
            print(f"Table ID: {self.table_id}")
            
            async with aiohttp.ClientSession(headers=self.get_headers()) as session:
                while self.running:
                    try:
                        self.check_count += 1
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        
                        print(f"🔍 Verificação #{self.check_count} - {timestamp}")
                        
                        # Parâmetros da API
                        params = {
                            'tableId': self.table_id,
                            'numberOfGames': 500,
                            'JSESSIONID': 'l1mibhSOQTfHiOHOJse3RQ_UppC_S9oJvaPyZ7V2-PywackJH43N!693708646-0bfaaff6',
                            'ck': str(int(time.time() * 1000)),
                            'game_mode': 'lobby_desktop'
                        }
                        
                        async with session.get(self.api_url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                if data.get('errorCode') == '0':
                                    print(f"✅ API respondeu com sucesso")
                                    
                                    # Processar dados
                                    self.process_api_response(data)
                                else:
                                    print(f"❌ Erro na API: {data.get('description', 'Erro desconhecido')}")
                                
                            else:
                                print(f"❌ Erro HTTP: {response.status}")
                        
                        # Aguardar antes da próxima verificação
                        print("⏳ Aguardando 30 segundos...")
                        await asyncio.sleep(30)
                        
                    except Exception as e:
                        print(f"❌ Erro na verificação: {e}")
                        await asyncio.sleep(5)
        
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
                loop.run_until_complete(self.monitor_api())
            except KeyboardInterrupt:
                print("\n🛑 Monitor interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
            finally:
                loop.close()
        
        import threading
        self.thread = threading.Thread(target=run_async, name="PragmaticAPIMonitor")
        self.thread.start()
    
    def stop(self):
        """Para o monitor."""
        print("🛑 Parando monitor...")
        self.running = False
        
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=5)
    
    def get_recent_results(self, count=20):
        """Retorna os resultados recentes."""
        return list(self.results)[-count:]

# Função principal
async def main():
    """Função principal."""
    print("🎯 Monitor Pragmatic Play API - Brazilian Roulette")
    print("=" * 60)
    print("Acessando API real dos resultados")
    print("Pressione Ctrl+C para parar")
    print()
    
    monitor = PragmaticAPIMonitor()
    
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
