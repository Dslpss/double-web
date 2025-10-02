#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor contínuo para capturar números da roleta em tempo real
"""

import asyncio
import aiohttp
import json
import re
import time
from datetime import datetime
from collections import deque

class ContinuousRouletteMonitor:
    """Monitor contínuo da roleta."""
    
    def __init__(self):
        self.base_url = "https://central.playnabet.com"
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
        self.token_usuario = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkwMjQ2NjQsImV4cCI6MTc1OTYyOTQ2NCwidXNlciI6eyJpZCI6NjMzMTR9fQ.BgvAuiW2_rUF8TUI9IdiV2swr3El7xN8qTrIgISN9AU"
        
        self.running = False
        self.results = deque(maxlen=100)  # Últimos 100 resultados
        self.last_numbers = set()
        self.check_count = 0
        
    def get_headers(self):
        """Headers para requisições."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt',
            'Authorization': f'Bearer {self.token_usuario}',
            'Content-Type': 'application/json'
        }
    
    def get_color(self, number):
        """Determina a cor do número."""
        if number == 0:
            return '🟢 VERDE'
        elif number % 2 == 1:
            return '🔴 VERMELHO'
        else:
            return '⚫ PRETO'
    
    def extract_numbers(self, content):
        """Extrai números da roleta do conteúdo."""
        numbers = set()
        
        # Padrões específicos para roleta
        patterns = [
            r'\b([0-3]?[0-6])\b',  # Números 0-36
            r'"number":\s*(\d+)',
            r'"result":\s*(\d+)',
            r'"value":\s*(\d+)',
            r'"winningNumber":\s*(\d+)',
            r'"lastNumber":\s*(\d+)',
            r'"rouletteNumber":\s*(\d+)',
            r'"gameResult":\s*(\d+)',
            r'number\s*=\s*(\d+)',
            r'result\s*=\s*(\d+)',
            r'winningNumber\s*=\s*(\d+)',
            r'lastNumber\s*=\s*(\d+)',
            r'rouletteNumber\s*=\s*(\d+)',
            r'gameResult\s*=\s*(\d+)',
            r'winning_number\s*=\s*(\d+)',
            r'last_number\s*=\s*(\d+)',
            r'roulette_number\s*=\s*(\d+)',
            r'game_result\s*=\s*(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    num = int(match)
                    if 0 <= num <= 36:
                        numbers.add(num)
                except:
                    continue
        
        # Procurar por JSONs
        json_matches = re.findall(r'\{[^{}]*\}', content)
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                for key in ['number', 'result', 'value', 'winningNumber', 'lastNumber', 
                           'rouletteNumber', 'gameResult', 'winning_number', 'last_number',
                           'roulette_number', 'game_result']:
                    if key in data:
                        try:
                            num = int(data[key])
                            if 0 <= num <= 36:
                                numbers.add(num)
                        except:
                            continue
            except:
                continue
        
        return list(numbers)
    
    async def check_game(self, game_id, game_name):
        """Verifica um jogo específico."""
        try:
            # Obter URL do jogo
            params = {
                'token': self.token,
                'tokenUsuario': self.token_usuario,
                'symbol': game_id,
                'language': 'pt',
                'playMode': 'REAL',
                'cashierUr': 'https://playnabet.com/clientes/deposito',
                'lobbyUrl': 'https://playnabet.com/casino',
                'fornecedor': 'pragmatic',
                'isMobile': 'false',
                'plataforma': 'pc'
            }
            
            async with aiohttp.ClientSession(headers=self.get_headers()) as session:
                async with session.get(f"{self.base_url}/casino/games/url", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        game_url = data.get('gameURL')
                        
                        if game_url:
                            # Acessar o jogo
                            game_headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                                'Referer': 'https://playnabets.com/'
                            }
                            
                            async with aiohttp.ClientSession(headers=game_headers) as game_session:
                                async with game_session.get(game_url, verify_ssl=False) as game_response:
                                    if game_response.status == 200:
                                        content = await game_response.text()
                                        
                                        # Extrair números
                                        numbers = self.extract_numbers(content)
                                        
                                        # Verificar se há números novos
                                        new_numbers = []
                                        for number in numbers:
                                            if number not in self.last_numbers:
                                                new_numbers.append(number)
                                                self.last_numbers.add(number)
                                                
                                                # Adicionar resultado
                                                result = {
                                                    'number': number,
                                                    'color': self.get_color(number),
                                                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                                                    'game': game_name,
                                                    'round_id': f'round_{int(time.time())}'
                                                }
                                                
                                                self.results.append(result)
                                                
                                                print(f"🎲 [{result['timestamp']}] {game_name}: {number} {result['color']}")
                                                
                                                # Mostrar estatísticas a cada 5 números
                                                if len(self.results) % 5 == 0:
                                                    self.show_statistics()
                                        
                                        if new_numbers:
                                            print(f"✅ {game_name}: {len(new_numbers)} novos números: {new_numbers}")
                                        else:
                                            print(f"⏳ {game_name}: Nenhum número novo")
                                        
                                        return len(new_numbers) > 0
                                    
        except Exception as e:
            print(f"❌ Erro em {game_name}: {e}")
        
        return False
    
    def show_statistics(self):
        """Mostra estatísticas dos resultados."""
        if not self.results:
            return
        
        numbers = [r['number'] for r in self.results]
        
        print(f"\n📊 ESTATÍSTICAS ({len(numbers)} números):")
        print(f"Últimos 10: {numbers[-10:]}")
        
        # Contagem por cor
        red_count = sum(1 for n in numbers if n % 2 == 1 and n != 0)
        black_count = sum(1 for n in numbers if n % 2 == 0 and n != 0)
        green_count = sum(1 for n in numbers if n == 0)
        
        print(f"🔴 Vermelhos: {red_count} | ⚫ Pretos: {black_count} | 🟢 Verdes: {green_count}")
        print("-" * 50)
    
    async def monitor_continuously(self):
        """Monitora continuamente os jogos."""
        print("🚀 Iniciando monitoramento contínuo...")
        print("=" * 60)
        print("Pressione Ctrl+C para parar")
        print()
        
        # Jogos para monitorar
        games = [
            ('237', 'Brazilian Roulette'),
            ('210', 'Auto Mega Roulette'),
            ('203', 'Speed Roulette 1')
        ]
        
        while self.running:
            try:
                self.check_count += 1
                print(f"🔍 Verificação #{self.check_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                for game_id, game_name in games:
                    if not self.running:
                        break
                    
                    await self.check_game(game_id, game_name)
                    await asyncio.sleep(2)  # Aguardar entre jogos
                
                # Aguardar antes da próxima verificação
                print("⏳ Aguardando 15 segundos...")
                await asyncio.sleep(15)
                
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                await asyncio.sleep(10)
    
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
                loop.run_until_complete(self.monitor_continuously())
            except KeyboardInterrupt:
                print("\n🛑 Monitor interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
            finally:
                loop.close()
        
        import threading
        self.thread = threading.Thread(target=run_async, name="ContinuousRouletteMonitor")
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
    print("🎯 Monitor Contínuo de Roleta - PlayNabet")
    print("=" * 60)
    
    monitor = ContinuousRouletteMonitor()
    
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
