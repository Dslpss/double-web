#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor de resultados da Roleta brasileira em tempo real
"""

import asyncio
import aiohttp
import json
import time
import threading
from datetime import datetime
from collections import deque

class RouletteMonitor:
    """Monitor de resultados da roleta em tempo real."""
    
    def __init__(self):
        self.base_url = "https://central.playnabet.com"
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
        self.token_usuario = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkwMjQ2NjQsImV4cCI6MTc1OTYyOTQ2NCwidXNlciI6eyJpZCI6NjMzMTR9fQ.BgvAuiW2_rUF8TUI9IdiV2swr3El7xN8qTrIgISN9AU"
        
        self.running = False
        self.results = deque(maxlen=100)  # Últimos 100 resultados
        self.last_numbers = []
        
    def get_headers(self):
        """Headers para requisições."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://playnabets.com/',
            'Content-Type': 'application/json',
            'Origin': 'https://playnabets.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Authorization': f'Bearer {self.token_usuario}',
            'Te': 'trailers'
        }
    
    async def get_game_url(self, game_id):
        """Obtém URL do jogo."""
        try:
            url = f"{self.base_url}/casino/games/url"
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
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('gameURL')
                    return None
        except Exception as e:
            print(f"❌ Erro ao obter URL: {e}")
            return None
    
    def extract_numbers_from_content(self, content):
        """Extrai números da roleta do conteúdo."""
        import re
        
        numbers = []
        
        # Procurar por números de roleta (0-36)
        number_matches = re.findall(r'\b([0-3]?[0-6])\b', content)
        valid_numbers = [int(n) for n in number_matches if 0 <= int(n) <= 36]
        
        # Procurar por padrões específicos de roleta
        patterns = [
            r'"number":\s*(\d+)',
            r'"result":\s*(\d+)',
            r'"value":\s*(\d+)',
            r'number\s*=\s*(\d+)',
            r'result\s*=\s*(\d+)',
            r'winningNumber\s*=\s*(\d+)',
            r'lastNumber\s*=\s*(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    num = int(match)
                    if 0 <= num <= 36:
                        numbers.append(num)
                except:
                    continue
        
        # Procurar por dados JSON
        json_matches = re.findall(r'\{[^{}]*\}', content)
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                if 'number' in data:
                    num = int(data['number'])
                    if 0 <= num <= 36:
                        numbers.append(num)
                if 'result' in data:
                    num = int(data['result'])
                    if 0 <= num <= 36:
                        numbers.append(num)
            except:
                continue
        
        return list(set(numbers))  # Remove duplicatas
    
    def get_color(self, number):
        """Determina a cor do número."""
        if number == 0:
            return '🟢 VERDE'
        elif number % 2 == 1:  # Ímpares
            return '🔴 VERMELHO'
        else:  # Pares
            return '⚫ PRETO'
    
    def analyze_patterns(self):
        """Analisa padrões nos números."""
        if len(self.results) < 5:
            return "Precisa de mais dados para análise"
        
        recent = list(self.results)[-10:]  # Últimos 10
        numbers = [r['number'] for r in recent]
        
        # Análise básica
        red_count = sum(1 for n in numbers if n % 2 == 1 and n != 0)
        black_count = sum(1 for n in numbers if n % 2 == 0 and n != 0)
        green_count = sum(1 for n in numbers if n == 0)
        
        analysis = f"""
📊 ANÁLISE DOS ÚLTIMOS {len(recent)} NÚMEROS:
🔴 Vermelhos: {red_count}
⚫ Pretos: {black_count}
🟢 Verdes: {green_count}

🎯 Últimos números: {', '.join(map(str, numbers[-5:]))}
        """
        
        return analysis
    
    async def monitor_roulette(self, game_id, game_name):
        """Monitora uma roleta específica."""
        print(f"🎯 Monitorando: {game_name}")
        
        game_url = await self.get_game_url(game_id)
        if not game_url:
            print(f"❌ Não foi possível obter URL para {game_name}")
            return
        
        print(f"🔗 URL: {game_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Referer': 'https://playnabets.com/'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                while self.running:
                    try:
                        async with session.get(game_url, verify_ssl=False) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Extrair números
                                numbers = self.extract_numbers_from_content(content)
                                
                                if numbers:
                                    # Verificar se há números novos
                                    for number in numbers:
                                        if number not in self.last_numbers:
                                            color = self.get_color(number)
                                            timestamp = datetime.now().strftime("%H:%M:%S")
                                            
                                            result = {
                                                'number': number,
                                                'color': color,
                                                'timestamp': timestamp,
                                                'game': game_name
                                            }
                                            
                                            self.results.append(result)
                                            self.last_numbers.append(number)
                                            
                                            # Manter apenas últimos 50 números
                                            if len(self.last_numbers) > 50:
                                                self.last_numbers = self.last_numbers[-50:]
                                            
                                            print(f"🎲 [{timestamp}] {game_name}: {number} {color}")
                                            
                                            # Mostrar análise a cada 5 números
                                            if len(self.results) % 5 == 0:
                                                print(self.analyze_patterns())
                                
                            else:
                                print(f"⚠️ Status {response.status} para {game_name}")
                                
                    except Exception as e:
                        print(f"❌ Erro ao monitorar {game_name}: {e}")
                    
                    await asyncio.sleep(3)  # Verificar a cada 3 segundos
                    
        except Exception as e:
            print(f"❌ Erro no monitoramento de {game_name}: {e}")
    
    async def start_monitoring(self):
        """Inicia o monitoramento."""
        print("🚀 Iniciando monitoramento da Roleta brasileira...")
        print("=" * 60)
        
        # Jogos de roleta para monitorar
        roulette_games = [
            ('237', 'Brazilian Roulette'),
            ('210', 'Auto Mega Roulette'),
            ('203', 'Speed Roulette 1')
        ]
        
        tasks = []
        for game_id, game_name in roulette_games:
            task = asyncio.create_task(
                self.monitor_roulette(game_id, game_name)
            )
            tasks.append(task)
        
        # Aguardar todas as tarefas
        if tasks:
            await asyncio.gather(*tasks)
    
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
                loop.run_until_complete(self.start_monitoring())
            except KeyboardInterrupt:
                print("\n🛑 Monitor interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
            finally:
                loop.close()
        
        self.thread = threading.Thread(target=run_async, name="RouletteMonitor")
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
    
    def show_statistics(self):
        """Mostra estatísticas dos resultados."""
        if not self.results:
            print("❌ Nenhum resultado disponível")
            return
        
        numbers = [r['number'] for r in self.results]
        
        print("\n📊 ESTATÍSTICAS:")
        print(f"Total de números capturados: {len(numbers)}")
        print(f"Últimos 10 números: {numbers[-10:]}")
        
        # Contagem por cor
        red_count = sum(1 for n in numbers if n % 2 == 1 and n != 0)
        black_count = sum(1 for n in numbers if n % 2 == 0 and n != 0)
        green_count = sum(1 for n in numbers if n == 0)
        
        print(f"🔴 Vermelhos: {red_count}")
        print(f"⚫ Pretos: {black_count}")
        print(f"🟢 Verdes: {green_count}")

# Função principal para teste
async def main():
    """Função principal."""
    print("🎯 Monitor de Roleta Brasileira - PlayNabet")
    print("=" * 50)
    
    monitor = RouletteMonitor()
    
    try:
        # Iniciar monitoramento
        monitor.start()
        
        # Aguardar um pouco para capturar dados
        print("⏳ Aguardando dados... (Pressione Ctrl+C para parar)")
        
        while monitor.running:
            await asyncio.sleep(10)
            
            # Mostrar estatísticas a cada 10 segundos
            if monitor.results:
                monitor.show_statistics()
                print("-" * 30)
    
    except KeyboardInterrupt:
        print("\n🛑 Parando monitor...")
        monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())
