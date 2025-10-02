#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor WebSocket para capturar números da roleta em tempo real
Baseado na conexão capturada: ws1.pragmaticplaylive.net/A16R-Generic
"""

import asyncio
import websockets
import json
import time
from datetime import datetime
from collections import deque

class WebSocketRouletteMonitor:
    """Monitor WebSocket da roleta Pragmatic Play."""
    
    def __init__(self):
        self.websocket_url = "wss://ws1.pragmaticplaylive.net/A16R-Generic"
        self.connected = False
        self.running = False
        self.results = deque(maxlen=100)  # Últimos 100 resultados
        self.last_numbers = set()
        
        # Headers da conexão capturada
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive, Upgrade',
            'Host': 'ws1.pragmaticplaylive.net',
            'Origin': 'https://client.pragmaticplaylive.net',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'websocket',
            'Sec-Fetch-Site': 'same-site',
            'Sec-WebSocket-Extensions': 'permessage-deflate',
            'Sec-WebSocket-Version': '13',
            'Upgrade': 'websocket',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0'
        }
    
    def get_color(self, number):
        """Determina a cor do número."""
        if number == 0:
            return '🟢 VERDE'
        elif number % 2 == 1:
            return '🔴 VERMELHO'
        else:
            return '⚫ PRETO'
    
    def extract_roulette_data(self, message):
        """Extrai dados da roleta da mensagem WebSocket."""
        try:
            # Tentar parsear como JSON
            if isinstance(message, str):
                data = json.loads(message)
            else:
                data = message
            
            # Procurar por números de roleta
            numbers = []
            
            # Padrões comuns para dados de roleta
            if isinstance(data, dict):
                # Procurar por campos que podem conter números
                for key, value in data.items():
                    if isinstance(value, (int, float)) and 0 <= value <= 36:
                        numbers.append(int(value))
                    elif isinstance(value, str) and value.isdigit():
                        num = int(value)
                        if 0 <= num <= 36:
                            numbers.append(num)
                    elif isinstance(value, dict):
                        # Procurar recursivamente
                        sub_numbers = self.extract_roulette_data(value)
                        numbers.extend(sub_numbers)
                    elif isinstance(value, list):
                        # Procurar em listas
                        for item in value:
                            if isinstance(item, (int, float)) and 0 <= item <= 36:
                                numbers.append(int(item))
                            elif isinstance(item, str) and item.isdigit():
                                num = int(item)
                                if 0 <= num <= 36:
                                    numbers.append(num)
            
            return list(set(numbers))  # Remove duplicatas
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados: {e}")
            return []
    
    def process_message(self, message):
        """Processa mensagem recebida do WebSocket."""
        try:
            print(f"📨 Mensagem recebida: {message[:200]}...")
            
            # Extrair números
            numbers = self.extract_roulette_data(message)
            
            if numbers:
                print(f"🎲 Números encontrados: {numbers}")
                
                # Processar cada número
                for number in numbers:
                    if number not in self.last_numbers:
                        self.last_numbers.add(number)
                        
                        result = {
                            'number': number,
                            'color': self.get_color(number),
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'source': 'websocket',
                            'round_id': f'round_{int(time.time())}'
                        }
                        
                        self.results.append(result)
                        
                        print(f"🎲 [{result['timestamp']}] NOVO: {number} {result['color']}")
                        
                        # Mostrar estatísticas a cada 5 números
                        if len(self.results) % 5 == 0:
                            self.show_statistics()
            
            else:
                print("⏳ Nenhum número de roleta encontrado na mensagem")
                
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
    
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
    
    async def connect_and_monitor(self):
        """Conecta e monitora o WebSocket."""
        try:
            print(f"🔌 Conectando ao WebSocket: {self.websocket_url}")
            
            async with websockets.connect(
                self.websocket_url,
                extra_headers=self.headers,
                ping_interval=20,
                ping_timeout=10
            ) as websocket:
                
                self.connected = True
                print("✅ Conectado ao WebSocket!")
                print("🎯 Aguardando dados da roleta...")
                print("Pressione Ctrl+C para parar")
                print("=" * 60)
                
                while self.running:
                    try:
                        # Aguardar mensagem
                        message = await asyncio.wait_for(websocket.recv(), timeout=30)
                        
                        # Processar mensagem
                        self.process_message(message)
                        
                    except asyncio.TimeoutError:
                        print("⏳ Timeout - enviando ping...")
                        await websocket.ping()
                        
                    except websockets.exceptions.ConnectionClosed:
                        print("❌ Conexão WebSocket fechada")
                        break
                        
                    except Exception as e:
                        print(f"❌ Erro na conexão: {e}")
                        break
                
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
        finally:
            self.connected = False
            print("🔌 Desconectado do WebSocket")
    
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
                loop.run_until_complete(self.connect_and_monitor())
            except KeyboardInterrupt:
                print("\n🛑 Monitor interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
            finally:
                loop.close()
        
        import threading
        self.thread = threading.Thread(target=run_async, name="WebSocketRouletteMonitor")
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
    print("🎯 Monitor WebSocket de Roleta - Pragmatic Play")
    print("=" * 60)
    print("Conectando ao WebSocket em tempo real...")
    print()
    
    monitor = WebSocketRouletteMonitor()
    
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
