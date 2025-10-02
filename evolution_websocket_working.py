#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema WebSocket Evolution Gaming - VERSÃO FUNCIONANDO
Com EVOSESSIONID e cookies corretos do usuário
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

logger = logging.getLogger(__name__)

@dataclass
class EvolutionResult:
    """Resultado da roleta Evolution Gaming."""
    game_id: str
    number: int
    color: str
    color_name: str
    timestamp: datetime
    source: str = "evolution_working"
    
    def to_dict(self) -> Dict:
        return {
            'game_id': self.game_id,
            'number': self.number,
            'color': self.color,
            'color_name': self.color_name,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }

class EvolutionWebSocketWorking:
    """Sistema WebSocket Evolution - COM PARÂMETROS CORRETOS."""
    
    def __init__(self):
        # Configurações corretas do usuário
        self.host = "betmotionmx.evo-games.com"
        self.table_id = "PorROU0000000001"
        self.table_config = "sgotw3xmkwsle55x"
        self.instance = "24D4DA-90D446-934FD5"
        self.client_version = "6.20251001.93245.55664-1d75f7f99a"
        
        # EVOSESSIONID atualizado
        self.evosessionid = "tfrwcpjq37obsukstgrrv5uzvtkeabale75fa411ab52f3051115f2687f5c83af0d6d0a46c66ccc1e"
        
        # Cookies completos
        self.bm_s = "YAAQCgkTAmKa+aCZAQAANDobowQcoFLZtXNEsL2w+MRzhQIiu+LD4dyjrKe2bgFM9hmZX8nV12z+eYNIXaKTrjJcB/y1taGfhEyHiGL3e86wZ040nSjNhIQxiywtKdaDHfHEzlelckgfa/7VrrUJ68hw8ogj9Znr9TbC4gpS+ZFrTdIUgsAbbbrGrbxVabTXmJ9kSO3wax0bdIcuuhc7IWJTbEAlhryDPDuEasx0fP9IkhhmCnVGNo3ll3xs43uShpTLfS0Xh2l+oE604coiiE302IBz1yAk/bW4oOL7C5UPl4Muy57AbfJsp1A7Z8qWTxxPSeo7ysGC10qJLFJUWdrRA5fwUhNgAOT2ZB3t+IFI6AeGHQO2h9lmSjGeNpAKs+y37835PWEZj/miUs1T9TL6vQBR"
        self.bm_sv = "8F75DE8CFF2E9176B4A5438D5C4C76D3~YAAQCgkTAmOa+aCZAQAANDobox3oKHPm2e6nlRGgf4wcE/IxHP8L6cQYunBP89/wf+Sx23Pps/rK3f+drbNr8KrAxVMuENa9KVztaSZNscJ4DsF5KZ6pZ8tuvfba2VGd965V1yf9/Wt07YgAQE9oE+NnrrYpqKGM9p9NnwCnG8GJhJlJO5on6JLxmBVxRirL1BaBXCyL28tvPau6MIiuD71TEbAGqeHNZXP/WQvFuDX78joWmrT2fo5vM0QeYWc3D+ORbg==~1"
        
        # Estado do sistema
        self.running = False
        self.websocket = None
        self.monitor_thread = None
        self.results_cache = []
        self.message_count = 0
        self.connection_successful = False
        
        logger.info("Sistema WebSocket Evolution Working inicializado")
    
    def build_websocket_url(self) -> str:
        """Constrói URL do WebSocket com parâmetros corretos."""
        base_url = f"wss://{self.host}/public/roulette/player/game/{self.table_id}/socket"
        
        params = {
            'messageFormat': 'json',
            'tableConfig': self.table_config,
            'EVOSESSIONID': self.evosessionid,
            'client_version': self.client_version,
            'instance': self.instance
        }
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def build_cookie_header(self) -> str:
        """Constrói header de cookies completo."""
        cookies = [
            f"EVOSESSIONID={self.evosessionid}",
            f"bm_s={self.bm_s}",
            f"bm_sv={self.bm_sv}",
            "bm_ss=ab8e18ef4e"
        ]
        return "; ".join(cookies)
    
    def parse_evolution_message(self, message_text: str) -> Optional[EvolutionResult]:
        """Parseia mensagem do WebSocket Evolution."""
        try:
            data = json.loads(message_text)
            
            # Log das primeiras mensagens para debug
            if self.message_count <= 10:
                logger.info(f"Mensagem #{self.message_count}: {json.dumps(data, indent=2)[:400]}...")
            
            # Procurar por resultados da roleta
            result_number = None
            game_id = None
            
            # Diferentes formatos de mensagem Evolution
            if isinstance(data, dict):
                # Formato 1: Resultado direto
                if 'outcome' in data:
                    outcome = data['outcome']
                    if isinstance(outcome, dict) and 'number' in outcome:
                        result_number = outcome['number']
                        game_id = data.get('gameId') or data.get('id')
                
                # Formato 2: Data wrapper
                elif 'data' in data:
                    inner_data = data['data']
                    if isinstance(inner_data, dict):
                        # Procurar resultado
                        for key in ['outcome', 'result', 'number', 'value']:
                            if key in inner_data:
                                value = inner_data[key]
                                if isinstance(value, dict) and 'number' in value:
                                    result_number = value['number']
                                elif isinstance(value, (int, str)):
                                    try:
                                        result_number = int(value)
                                    except:
                                        pass
                                
                                if result_number is not None:
                                    break
                        
                        # Procurar game ID
                        game_id = inner_data.get('gameId') or inner_data.get('id') or inner_data.get('roundId')
                
                # Formato 3: Evento de jogo
                elif 'type' in data and data['type'] in ['game_result', 'outcome', 'result']:
                    payload = data.get('payload', {})
                    if 'number' in payload:
                        result_number = payload['number']
                        game_id = payload.get('gameId') or payload.get('id')
                
                # Formato 4: Busca genérica
                if result_number is None:
                    for key in ['number', 'outcome', 'result']:
                        if key in data:
                            value = data[key]
                            if isinstance(value, (int, str)):
                                try:
                                    result_number = int(value)
                                    break
                                except:
                                    pass
            
            # Se encontrou número válido, criar resultado
            if result_number is not None:
                try:
                    number = int(result_number)
                    
                    # Validar número da roleta (0-36)
                    if 0 <= number <= 36:
                        # Determinar cor (roleta europeia)
                        if number == 0:
                            color, color_name = '🟢', 'GREEN'
                        elif number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
                            color, color_name = '🔴', 'RED'
                        else:
                            color, color_name = '⚫', 'BLACK'
                        
                        # Game ID
                        if not game_id:
                            game_id = f"evo_{int(time.time())}"
                        
                        return EvolutionResult(
                            game_id=str(game_id),
                            number=number,
                            color=color,
                            color_name=color_name,
                            timestamp=datetime.now(),
                            source="evolution_working"
                        )
                except ValueError:
                    pass
            
        except json.JSONDecodeError:
            # Mensagem não é JSON
            if self.message_count <= 5:
                logger.debug(f"Mensagem não-JSON: {message_text[:100]}...")
        except Exception as e:
            if self.message_count <= 5:
                logger.error(f"Erro ao parsear mensagem: {e}")
        
        return None
    
    async def websocket_listener(self):
        """Listener do WebSocket com parâmetros corretos."""
        websocket_url = self.build_websocket_url()
        cookie_header = self.build_cookie_header()
        
        # Headers corretos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Origin': f'https://{self.host}',
            'Cookie': cookie_header,
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        try:
            logger.info(f"🔌 Conectando Evolution com parâmetros corretos...")
            logger.info(f"URL: {websocket_url[:100]}...")
            logger.info(f"Cookies: {len(cookie_header)} chars")
            
            # Conectar com headers
            async with websockets.connect(
                websocket_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            ) as websocket:
                
                self.websocket = websocket
                self.connection_successful = True
                logger.info("✅ WebSocket Evolution conectado com sucesso!")
                
                # Loop de recepção
                async for message in websocket:
                    if not self.running:
                        break
                    
                    self.message_count += 1
                    
                    # Log periódico
                    if self.message_count % 50 == 0:
                        logger.info(f"📡 {self.message_count} mensagens recebidas")
                    
                    # Tentar extrair resultado
                    result = self.parse_evolution_message(message)
                    
                    if result:
                        # Adicionar ao cache
                        self.results_cache.append(result)
                        if len(self.results_cache) > 200:
                            self.results_cache = self.results_cache[-200:]
                        
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
                
                if self.running and not self.connection_successful:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 15 * retry_count
                        logger.info(f"⏳ Reconectando em {wait_time}s...")
                        await asyncio.sleep(wait_time)
                elif self.connection_successful:
                    # Se conectou com sucesso mas desconectou, tentar reconectar
                    logger.info("🔄 Reconectando após desconexão...")
                    await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Erro no monitor: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(20)
        
        if retry_count >= max_retries and not self.connection_successful:
            logger.error("❌ Não foi possível conectar ao WebSocket")
    
    def start(self):
        """Inicia o sistema."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._run_monitor, daemon=True)
            self.monitor_thread.start()
            logger.info("🚀 Sistema WebSocket Evolution Working iniciado")
            return True
        return False
    
    def stop(self):
        """Para o sistema."""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("🛑 Sistema WebSocket Evolution Working parado")
            return True
        return False
    
    def _run_monitor(self):
        """Executa monitor em thread."""
        asyncio.run(self.monitor_loop())
    
    def get_dashboard_data(self) -> Dict:
        """Dados do dashboard."""
        recent_results = self.results_cache[-20:] if self.results_cache else []
        
        color_freq = {'RED': 0, 'BLACK': 0, 'GREEN': 0}
        number_freq = {}
        
        for result in recent_results:
            color_freq[result.color_name] += 1
            number_freq[result.number] = number_freq.get(result.number, 0) + 1
        
        return {
            'recent_results': [r.to_dict() for r in recent_results],
            'statistics': {
                'total_games': len(self.results_cache),
                'color_frequency': color_freq,
                'number_frequency': number_freq
            },
            'status': {
                'running': self.running,
                'websocket_connected': self.websocket is not None,
                'connection_successful': self.connection_successful,
                'messages_received': self.message_count,
                'table_id': self.table_id
            },
            'last_update': datetime.now().isoformat()
        }

async def test_evolution_working():
    """Testa sistema com parâmetros corretos."""
    print("🎮 TESTANDO WEBSOCKET EVOLUTION - PARÂMETROS CORRETOS")
    print("=" * 60)
    print("🔑 EVOSESSIONID atualizado")
    print("🍪 Cookies completos")
    print("📋 Parâmetros corretos do usuário")
    print("⚡ Teste por 2 minutos")
    print()
    
    system = EvolutionWebSocketWorking()
    
    print("1. Iniciando sistema com parâmetros corretos...")
    system.start()
    
    try:
        start_time = time.time()
        last_count = 0
        
        while time.time() - start_time < 120:  # 2 minutos
            await asyncio.sleep(10)
            
            current_count = len(system.results_cache)
            elapsed = int(time.time() - start_time)
            
            if current_count > last_count:
                new_results = current_count - last_count
                print(f"⏱️  {elapsed:2}s | 🎮 +{new_results} EVOLUTION! Total: {current_count}")
                
                recent = system.results_cache[-new_results:]
                for result in recent:
                    print(f"     🇵🇹 {result.number:2} {result.color} {result.color_name} (ID: {result.game_id})")
                
                last_count = current_count
            else:
                if system.connection_successful:
                    status = "🔌 Conectado"
                elif system.websocket:
                    status = "🔄 Conectando"
                else:
                    status = "❌ Desconectado"
                
                msgs = system.message_count
                print(f"⏱️  {elapsed:2}s | {status} (Msgs: {msgs}, Results: {current_count})")
        
        print(f"\n✅ Teste concluído!")
        
        dashboard_data = system.get_dashboard_data()
        stats = dashboard_data.get('statistics', {})
        status = dashboard_data.get('status', {})
        
        print(f"📊 Resultados: {len(system.results_cache)}")
        print(f"📡 Mensagens: {status.get('messages_received', 0)}")
        print(f"🔌 Conectou: {status.get('connection_successful', False)}")
        print(f"🎮 Mesa: {status.get('table_id', 'N/A')}")
        
        color_freq = stats.get('color_frequency', {})
        print(f"🔴 Vermelhos: {color_freq.get('RED', 0)}")
        print(f"⚫ Pretos: {color_freq.get('BLACK', 0)}")
        print(f"🟢 Verdes: {color_freq.get('GREEN', 0)}")
        
    finally:
        system.stop()
        print("\n🛑 Sistema parado")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_evolution_working())
