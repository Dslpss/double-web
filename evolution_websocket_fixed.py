#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema WebSocket Evolution Gaming - VERSÃO CORRIGIDA
Sem extra_headers, compatível com versões antigas do websockets
"""

import asyncio
import websockets
import json
import time
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import ssl

logger = logging.getLogger(__name__)

@dataclass
class EvolutionResult:
    """Resultado da roleta Evolution Gaming."""
    game_id: str
    number: int
    color: str
    color_name: str
    timestamp: datetime
    source: str = "evolution_websocket"
    
    def to_dict(self) -> Dict:
        return {
            'game_id': self.game_id,
            'number': self.number,
            'color': self.color,
            'color_name': self.color_name,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }

class EvolutionWebSocketFixed:
    """Sistema WebSocket Evolution - VERSÃO COMPATÍVEL."""
    
    def __init__(self):
        # Configurações Evolution Gaming
        self.host = "betmotionmx.evo-games.com"
        self.table_id = "PorROU0000000001"
        self.evosessionid = "tfrwcpjq37obsukstgrrabuhascutlyrc22c2e4e973638ec726e85b21beb31603f18100a5320baa3"
        
        # Estado do sistema
        self.running = False
        self.websocket = None
        self.monitor_thread = None
        self.results_cache = []
        self.message_count = 0
        
        logger.info("Sistema WebSocket Evolution Fixed inicializado")
    
    def parse_evolution_message(self, message_text: str) -> Optional[EvolutionResult]:
        """Parseia mensagem do WebSocket Evolution."""
        try:
            # Tentar parsear como JSON
            data = json.loads(message_text)
            
            # Log das primeiras mensagens para entender o formato
            if self.message_count < 5:
                logger.info(f"Mensagem Evolution #{self.message_count}: {json.dumps(data, indent=2)[:300]}...")
            
            # Procurar por resultados em diferentes formatos
            result_number = None
            game_id = None
            
            # Formato 1: data.outcome.number
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], dict):
                    inner_data = data['data']
                    
                    # Procurar número em vários campos
                    for field in ['outcome', 'result', 'number', 'value']:
                        if field in inner_data:
                            field_data = inner_data[field]
                            if isinstance(field_data, dict):
                                if 'number' in field_data:
                                    result_number = field_data['number']
                                elif 'value' in field_data:
                                    result_number = field_data['value']
                            elif isinstance(field_data, (int, str)):
                                result_number = field_data
                            
                            if result_number is not None:
                                break
                    
                    # Procurar game ID
                    for id_field in ['gameId', 'id', 'roundId', 'game_id']:
                        if id_field in inner_data:
                            game_id = inner_data[id_field]
                            break
                
                # Formato 2: direto no data
                if result_number is None:
                    for field in ['number', 'outcome', 'result', 'value']:
                        if field in data:
                            field_data = data[field]
                            if isinstance(field_data, dict) and 'number' in field_data:
                                result_number = field_data['number']
                            elif isinstance(field_data, (int, str)):
                                result_number = field_data
                            
                            if result_number is not None:
                                break
                
                # Procurar game ID no nível superior
                if game_id is None:
                    for id_field in ['gameId', 'id', 'roundId', 'game_id']:
                        if id_field in data:
                            game_id = data[id_field]
                            break
            
            # Se encontrou número, criar resultado
            if result_number is not None:
                try:
                    number = int(result_number)
                    
                    # Validar número da roleta (0-36)
                    if 0 <= number <= 36:
                        # Determinar cor
                        if number == 0:
                            color, color_name = '🟢', 'GREEN'
                        elif number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
                            color, color_name = '🔴', 'RED'
                        else:
                            color, color_name = '⚫', 'BLACK'
                        
                        # ID do jogo
                        if not game_id:
                            game_id = f"evo_{int(time.time())}"
                        
                        return EvolutionResult(
                            game_id=str(game_id),
                            number=number,
                            color=color,
                            color_name=color_name,
                            timestamp=datetime.now(),
                            source="evolution_websocket"
                        )
                except ValueError:
                    pass
            
        except json.JSONDecodeError:
            # Mensagem não é JSON
            if self.message_count < 3:
                logger.debug(f"Mensagem não-JSON: {message_text[:100]}...")
        except Exception as e:
            logger.error(f"Erro ao parsear mensagem Evolution: {e}")
        
        return None
    
    async def websocket_listener(self):
        """Listener do WebSocket sem extra_headers."""
        # URL simples do WebSocket
        websocket_url = f"wss://{self.host}/public/roulette/player/game/{self.table_id}/socket"
        
        # Adicionar parâmetros básicos
        websocket_url += f"?EVOSESSIONID={self.evosessionid}&messageFormat=json"
        
        try:
            logger.info(f"🔌 Conectando ao WebSocket Evolution (modo compatível)")
            logger.info(f"URL: {websocket_url[:80]}...")
            
            # Conectar sem extra_headers
            async with websockets.connect(websocket_url, ping_interval=30) as websocket:
                self.websocket = websocket
                logger.info("✅ WebSocket Evolution conectado!")
                
                # Loop de recepção
                async for message in websocket:
                    if not self.running:
                        break
                    
                    self.message_count += 1
                    
                    # Log periódico
                    if self.message_count % 20 == 0:
                        logger.info(f"📡 {self.message_count} mensagens recebidas")
                    
                    # Tentar extrair resultado
                    result = self.parse_evolution_message(message)
                    
                    if result:
                        # Adicionar ao cache
                        self.results_cache.append(result)
                        if len(self.results_cache) > 100:
                            self.results_cache = self.results_cache[-100:]
                        
                        logger.info(f"🎲 EVOLUTION: {result.number} {result.color} {result.color_name} (ID: {result.game_id})")
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("🔌 Conexão WebSocket fechada")
        except Exception as e:
            logger.error(f"Erro no WebSocket: {e}")
        finally:
            self.websocket = None
    
    async def monitor_loop(self):
        """Loop de monitoramento."""
        retry_count = 0
        max_retries = 3
        
        while self.running and retry_count < max_retries:
            try:
                logger.info(f"🚀 Tentativa WebSocket #{retry_count + 1}")
                await self.websocket_listener()
                
                if self.running:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"⏳ Reconectando em 10s...")
                        await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Erro no monitor: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(15)
        
        if retry_count >= max_retries:
            logger.error("❌ Máximo de tentativas excedido")
    
    def start(self):
        """Inicia o sistema."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._run_monitor, daemon=True)
            self.monitor_thread.start()
            logger.info("🚀 Sistema WebSocket Evolution Fixed iniciado")
            return True
        return False
    
    def stop(self):
        """Para o sistema."""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("🛑 Sistema WebSocket Evolution Fixed parado")
            return True
        return False
    
    def _run_monitor(self):
        """Executa monitor em thread."""
        asyncio.run(self.monitor_loop())
    
    def get_dashboard_data(self) -> Dict:
        """Dados do dashboard."""
        recent_results = self.results_cache[-20:] if self.results_cache else []
        
        color_freq = {'RED': 0, 'BLACK': 0, 'GREEN': 0}
        for result in recent_results:
            color_freq[result.color_name] += 1
        
        return {
            'recent_results': [r.to_dict() for r in recent_results],
            'statistics': {
                'total_games': len(self.results_cache),
                'color_frequency': color_freq
            },
            'status': {
                'running': self.running,
                'websocket_connected': self.websocket is not None,
                'messages_received': self.message_count
            },
            'last_update': datetime.now().isoformat()
        }

async def test_evolution_fixed():
    """Testa sistema corrigido."""
    print("🔧 TESTANDO WEBSOCKET EVOLUTION - VERSÃO CORRIGIDA")
    print("=" * 60)
    print("🔌 Sem extra_headers (compatível)")
    print("🇵🇹 Roleta Portuguesa Evolution Gaming")
    print("⚡ Teste por 90 segundos")
    print()
    
    system = EvolutionWebSocketFixed()
    
    print("1. Iniciando sistema corrigido...")
    system.start()
    
    try:
        start_time = time.time()
        last_count = 0
        
        while time.time() - start_time < 90:  # 90 segundos
            await asyncio.sleep(10)
            
            current_count = len(system.results_cache)
            elapsed = int(time.time() - start_time)
            
            if current_count > last_count:
                new_results = current_count - last_count
                print(f"⏱️  {elapsed:2}s | 🎮 +{new_results} EVOLUTION! Total: {current_count}")
                
                recent = system.results_cache[-new_results:]
                for result in recent:
                    print(f"     🇵🇹 {result.number:2} {result.color} {result.color_name}")
                
                last_count = current_count
            else:
                status = "🔌 Conectado" if system.websocket else "🔄 Conectando"
                msgs = system.message_count
                print(f"⏱️  {elapsed:2}s | {status} (Msgs: {msgs}, Results: {current_count})")
        
        print(f"\n✅ Teste concluído!")
        
        dashboard_data = system.get_dashboard_data()
        stats = dashboard_data.get('statistics', {})
        status = dashboard_data.get('status', {})
        
        print(f"📊 Resultados: {len(system.results_cache)}")
        print(f"📡 Mensagens: {status.get('messages_received', 0)}")
        print(f"🔌 Conectado: {status.get('websocket_connected', False)}")
        
        color_freq = stats.get('color_frequency', {})
        print(f"🔴 Vermelhos: {color_freq.get('RED', 0)}")
        print(f"⚫ Pretos: {color_freq.get('BLACK', 0)}")
        print(f"🟢 Verdes: {color_freq.get('GREEN', 0)}")
        
    finally:
        system.stop()
        print("\n🛑 Sistema parado")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_evolution_fixed())
