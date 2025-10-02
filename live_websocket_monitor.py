#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor WebSocket em tempo real para capturar dados da roleta
"""

import asyncio
import websockets
import json
import time
from datetime import datetime
from collections import deque

class LiveWebSocketMonitor:
    """Monitor WebSocket em tempo real."""
    
    def __init__(self):
        self.websocket_url = "wss://ws1.pragmaticplaylive.net/A16R-Generic"
        self.connected = False
        self.running = False
        self.results = deque(maxlen=100)
        self.message_count = 0
        self.start_time = None
        
    def get_color(self, number):
        """Determina a cor do número."""
        if number == 0:
            return '🟢 VERDE'
        elif number % 2 == 1:
            return '🔴 VERMELHO'
        else:
            return '⚫ PRETO'
    
    def extract_numbers(self, data):
        """Extrai números de roleta dos dados."""
        numbers = []
        
        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, (int, float)) and 0 <= value <= 36:
                        numbers.append({
                            'number': int(value),
                            'path': current_path,
                            'value': value
                        })
                    elif isinstance(value, str) and value.isdigit():
                        num = int(value)
                        if 0 <= num <= 36:
                            numbers.append({
                                'number': num,
                                'path': current_path,
                                'value': value
                            })
                    else:
                        search_recursive(value, current_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    search_recursive(item, current_path)
        
        search_recursive(data)
        return numbers
    
    def process_message(self, message):
        """Processa mensagem recebida."""
        try:
            self.message_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"📨 [{timestamp}] Mensagem #{self.message_count} ({len(message)} chars)")
            
            # Tentar parsear JSON
            try:
                data = json.loads(message)
                print(f"   JSON: {type(data)} - {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
                
                # Extrair números
                numbers = self.extract_numbers(data)
                
                if numbers:
                    print(f"   🎲 NÚMEROS ENCONTRADOS ({len(numbers)}):")
                    for num_info in numbers:
                        number = num_info['number']
                        path = num_info['path']
                        color = self.get_color(number)
                        
                        print(f"      {number} {color} (em {path})")
                        
                        # Adicionar resultado
                        result = {
                            'number': number,
                            'color': color,
                            'timestamp': timestamp,
                            'path': path,
                            'message_id': self.message_count
                        }
                        
                        self.results.append(result)
                        
                        # Mostrar estatísticas a cada 5 números
                        if len(self.results) % 5 == 0:
                            self.show_statistics()
                
                else:
                    print(f"   ⏳ Nenhum número de roleta encontrado")
                    
                    # Mostrar estrutura dos dados para debug
                    if isinstance(data, dict):
                        print(f"   🔍 Chaves principais: {list(data.keys())}")
                        for key, value in data.items():
                            if isinstance(value, (dict, list)):
                                print(f"      {key}: {type(value)} (tamanho: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                            else:
                                print(f"      {key}: {value}")
                
            except json.JSONDecodeError:
                print(f"   ❌ Não é JSON válido")
                print(f"   Conteúdo: {message[:100]}...")
            
            print("-" * 60)
            
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
        print("=" * 60)
    
    async def monitor(self):
        """Monitora o WebSocket."""
        try:
            print(f"🔌 Conectando ao WebSocket: {self.websocket_url}")
            
            async with websockets.connect(self.websocket_url) as websocket:
                self.connected = True
                self.start_time = datetime.now()
                
                print("✅ Conectado ao WebSocket!")
                print("🎯 Monitorando dados da roleta...")
                print("Pressione Ctrl+C para parar")
                print("=" * 60)
                
                while self.running:
                    try:
                        # Aguardar mensagem
                        message = await asyncio.wait_for(websocket.recv(), timeout=10)
                        
                        # Processar mensagem
                        self.process_message(message)
                        
                    except asyncio.TimeoutError:
                        # Enviar ping para manter conexão
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
                loop.run_until_complete(self.monitor())
            except KeyboardInterrupt:
                print("\n🛑 Monitor interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
            finally:
                loop.close()
        
        import threading
        self.thread = threading.Thread(target=run_async, name="LiveWebSocketMonitor")
        self.thread.start()
    
    def stop(self):
        """Para o monitor."""
        print("🛑 Parando monitor...")
        self.running = False
        
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=5)
    
    def get_status(self):
        """Retorna status do monitor."""
        return {
            'connected': self.connected,
            'running': self.running,
            'message_count': self.message_count,
            'results_count': len(self.results),
            'uptime': (datetime.now() - self.start_time).seconds if self.start_time else 0
        }

# Função principal
async def main():
    """Função principal."""
    print("🎯 Monitor WebSocket em Tempo Real - Pragmatic Play")
    print("=" * 60)
    
    monitor = LiveWebSocketMonitor()
    
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
