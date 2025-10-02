#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor da página real do Pragmatic Play Live Casino
URL: https://client.pragmaticplaylive.net/desktop/classic-roulette2/
"""

import asyncio
import aiohttp
import json
import re
import time
from datetime import datetime
from collections import deque

class PragmaticLiveMonitor:
    """Monitor da página real do Pragmatic Play."""
    
    def __init__(self):
        self.game_url = "https://client.pragmaticplaylive.net/desktop/classic-roulette2/?tabletype=classic-roulette2&casino_id=ppcbr00000004697&gameLoaderKey=classic-roulette2&web_server=https://gs12.pragmaticplaylive.net&config_url=/cgibin/appconfig/xml/configs/urls.xml&JSESSIONID=l1mibhSOQTfHiOHOJse3RQ_UppC_S9oJvaPyZ7V2-PywackJH43N!693708646-0bfaaff6&table_id=rwbrzportrwa16rg&userId=ppc1735209252826&socket_server=wss://gs12.pragmaticplaylive.net/game&token=l1mibhSOQTfHiOHOJse3RQ_UppC_S9oJvaPyZ7V2-PywackJH43N!693708646-0bfaaff6&stats_collector_uuid=29cd258e-e155-4b63-addd-a96b1cb9765f&actual_web_server=https://gs12.pragmaticplaylive.net&socket_port=443&uiAddress=https://client.pragmaticplaylive.net/desktop/classic-roulette2/&uiversion=1.15.2&gametype=roulette&operator_theme=default/crl_chroma_brazilian_portuguese_roulette&game_mode=html5_desktop&lobby_version=2&lang=pt&swf_lobby_path=/member/games/lobby.swf&meta_server=https://games.pragmaticplaylive.net&lobbyGameSymbol=null&"
        self.running = False
        self.results = deque(maxlen=100)
        self.last_content = ""
        self.check_count = 0
        
    def get_headers(self):
        """Headers para acessar a página do jogo."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://playnabets.com/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
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
    
    def extract_roulette_data(self, content):
        """Extrai dados da roleta do conteúdo."""
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
            r'game_result\s*=\s*(\d+)',
            r'rouletteResult\s*=\s*(\d+)',
            r'currentNumber\s*=\s*(\d+)',
            r'lastResult\s*=\s*(\d+)',
            r'gameNumber\s*=\s*(\d+)',
            r'resultNumber\s*=\s*(\d+)',
            r'winning_number\s*:\s*(\d+)',
            r'last_number\s*:\s*(\d+)',
            r'roulette_number\s*:\s*(\d+)',
            r'game_result\s*:\s*(\d+)',
            r'rouletteResult\s*:\s*(\d+)',
            r'currentNumber\s*:\s*(\d+)',
            r'lastResult\s*:\s*(\d+)',
            r'gameNumber\s*:\s*(\d+)',
            r'resultNumber\s*:\s*(\d+)',
            r'roulette\s*result\s*:\s*(\d+)',
            r'winning\s*number\s*:\s*(\d+)',
            r'last\s*result\s*:\s*(\d+)',
            r'game\s*result\s*:\s*(\d+)'
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
        
        # Procurar por JSONs no conteúdo
        json_matches = re.findall(r'\{[^{}]*\}', content)
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                for key in ['number', 'result', 'value', 'winningNumber', 'lastNumber', 
                           'rouletteNumber', 'gameResult', 'winning_number', 'last_number',
                           'roulette_number', 'game_result', 'rouletteResult', 'currentNumber',
                           'lastResult', 'gameNumber', 'resultNumber']:
                    if key in data:
                        try:
                            num = int(data[key])
                            if 0 <= num <= 36:
                                numbers.add(num)
                        except:
                            continue
            except:
                continue
        
        # Procurar por arrays de números
        array_matches = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', content)
        for array_str in array_matches:
            try:
                numbers_list = [int(x.strip()) for x in array_str.split(',')]
                for num in numbers_list:
                    if 0 <= num <= 36:
                        numbers.add(num)
            except:
                continue
        
        return list(numbers)
    
    def process_content(self, content):
        """Processa o conteúdo do jogo."""
        try:
            # Extrair números
            numbers = self.extract_roulette_data(content)
            
            if numbers:
                print(f"🎲 Números encontrados: {sorted(numbers)}")
                
                # Processar cada número
                for number in numbers:
                    color = self.get_color(number)
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    
                    result = {
                        'number': number,
                        'color': color,
                        'timestamp': timestamp,
                        'source': 'pragmatic_live',
                        'round_id': f'round_{int(time.time())}'
                    }
                    
                    self.results.append(result)
                    
                    print(f"  {number}: {color}")
                
                # Mostrar estatísticas a cada 5 números
                if len(self.results) % 5 == 0:
                    self.show_statistics()
                
                return True
            else:
                print("⏳ Nenhum número de roleta encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao processar conteúdo: {e}")
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
        print("=" * 60)
    
    async def monitor_game(self):
        """Monitora o jogo em tempo real."""
        try:
            print(f"🔍 Monitorando jogo: Brazilian Roulette (Pragmatic Play)")
            print(f"URL: {self.game_url[:100]}...")
            
            async with aiohttp.ClientSession(headers=self.get_headers()) as session:
                while self.running:
                    try:
                        self.check_count += 1
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        
                        print(f"🔍 Verificação #{self.check_count} - {timestamp}")
                        
                        async with session.get(self.game_url) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Verificar se o conteúdo mudou
                                if content != self.last_content:
                                    self.last_content = content
                                    print(f"✅ Conteúdo atualizado ({len(content)} caracteres)")
                                    
                                    # Processar conteúdo
                                    self.process_content(content)
                                else:
                                    print("⏳ Conteúdo inalterado")
                                
                            else:
                                print(f"❌ Erro HTTP: {response.status}")
                        
                        # Aguardar antes da próxima verificação
                        print("⏳ Aguardando 20 segundos...")
                        await asyncio.sleep(20)
                        
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
                loop.run_until_complete(self.monitor_game())
            except KeyboardInterrupt:
                print("\n🛑 Monitor interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
            finally:
                loop.close()
        
        import threading
        self.thread = threading.Thread(target=run_async, name="PragmaticLiveMonitor")
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
    print("🎯 Monitor Pragmatic Play Live - Brazilian Roulette")
    print("=" * 60)
    print("Acessando página real do jogo")
    print("Pressione Ctrl+C para parar")
    print()
    
    monitor = PragmaticLiveMonitor()
    
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
