#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor da Roleta Brasileira WeeBet/PlayNaBets
Captura sinais em tempo real da Roleta Brasileira Pragmatic Play
"""

import asyncio
import aiohttp
import json
import time
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sqlite3
from urllib.parse import parse_qs, urlparse
from weebet_api_integrator import WeeBetAPI

logger = logging.getLogger(__name__)

@dataclass
class RouletteResult:
    """Resultado da roleta brasileira."""
    number: int
    color: str
    color_name: str
    timestamp: datetime
    game_id: str
    source: str = "weebet_pragmatic"
    
    def to_dict(self) -> Dict:
        return {
            'number': self.number,
            'color': self.color,
            'color_name': self.color_name,
            'timestamp': self.timestamp.isoformat(),
            'game_id': self.game_id,
            'source': self.source
        }

class WeeBetRouletteDatabase:
    """Banco de dados para resultados da roleta."""
    
    def __init__(self, db_path: str = "weebet_roulette.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roulette_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL,
                color TEXT NOT NULL,
                color_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                game_id TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados da roleta WeeBet inicializado")
    
    def save_result(self, result: RouletteResult):
        """Salva um resultado no banco."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO roulette_results 
            (number, color, color_name, timestamp, game_id, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            result.number,
            result.color,
            result.color_name,
            result.timestamp.isoformat(),
            result.game_id,
            result.source
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_results(self, limit: int = 50) -> List[RouletteResult]:
        """Obtém resultados recentes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT number, color, color_name, timestamp, game_id, source
            FROM roulette_results
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(RouletteResult(
                number=row[0],
                color=row[1],
                color_name=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                game_id=row[4],
                source=row[5]
            ))
        
        conn.close()
        return results

class WeeBetRouletteMonitor:
    """Monitor da Roleta Brasileira WeeBet."""
    
    def __init__(self):
        self.api = WeeBetAPI()
        self.database = WeeBetRouletteDatabase()
        self.running = False
        
        # Dados do jogo
        self.game_url = None
        self.game_token = None
        self.game_id = "237"  # ID da Roleta Brasileira
        
        # Cache de resultados
        self.results_cache = []
        self.last_result = None
        
        logger.info("Monitor da Roleta Brasileira WeeBet inicializado")
    
    async def get_game_url(self) -> Optional[str]:
        """Obtém URL do jogo da roleta."""
        try:
            # Fazer login se necessário
            if not self.api.credentials:
                await self.api.login()
            
            if not self.api.credentials:
                return None
            
            # Simular requisição para obter URL do jogo
            url = f"{self.api.base_url}/casino/game-url"
            headers = self.api.credentials.get_auth_headers()
            
            # Payload baseado na estrutura que vimos
            payload = {
                "gameId": self.game_id,
                "fornecedor": "pragmatic",
                "category": "roulette"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'gameURL' in data:
                            self.game_url = data['gameURL']
                            
                            # Extrair token da URL
                            self._extract_token_from_url()
                            
                            logger.info(f"✅ URL do jogo obtida: {self.game_url[:100]}...")
                            return self.game_url
                    else:
                        logger.error(f"Erro ao obter URL do jogo: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erro ao obter URL do jogo: {e}")
        
        return None
    
    def _extract_token_from_url(self):
        """Extrai token da URL do jogo."""
        if not self.game_url:
            return
        
        try:
            # Extrair token da URL
            # URL: https://qcxjeqo01e.cjlcqchead.net/gs2c/playGame.do?key=token%3D...
            parsed = urlparse(self.game_url)
            params = parse_qs(parsed.query)
            
            if 'key' in params:
                key_param = params['key'][0]
                # Decodificar URL
                import urllib.parse
                decoded_key = urllib.parse.unquote(key_param)
                
                # Extrair token
                token_match = re.search(r'token=([^%|&]+)', decoded_key)
                if token_match:
                    self.game_token = token_match.group(1)
                    logger.info(f"🔑 Token extraído: {self.game_token[:50]}...")
                    
        except Exception as e:
            logger.error(f"Erro ao extrair token: {e}")
    
    async def monitor_game_api(self):
        """Monitora a API do jogo para capturar resultados."""
        if not self.game_url or not self.game_token:
            logger.error("URL ou token do jogo não disponível")
            return
        
        # Extrair base URL do jogo
        parsed = urlparse(self.game_url)
        base_game_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Endpoints possíveis para resultados
        possible_endpoints = [
            "/gs2c/history",
            "/gs2c/results",
            "/gs2c/getHistory",
            "/gs2c/getResults",
            "/gs2c/gameHistory",
            "/gs2c/rouletteHistory",
            "/gs2c/api/history",
            "/gs2c/api/results",
            "/api/history",
            "/api/results",
            "/history",
            "/results"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Referer': self.game_url,
            'Authorization': f'Bearer {self.game_token}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        async with aiohttp.ClientSession() as session:
            for endpoint in possible_endpoints:
                try:
                    url = f"{base_game_url}{endpoint}"
                    
                    # Tentar GET
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                logger.info(f"✅ Dados obtidos de {endpoint}: {json.dumps(data, indent=2)}")
                                return data
                            except:
                                text = await response.text()
                                if text and len(text.strip()) > 0:
                                    logger.info(f"✅ Texto obtido de {endpoint}: {text[:200]}...")
                        else:
                            logger.debug(f"❌ {endpoint}: {response.status}")
                    
                    # Tentar POST
                    post_payloads = [
                        {},
                        {"token": self.game_token},
                        {"gameId": self.game_id},
                        {"limit": 50},
                        {"count": 20}
                    ]
                    
                    for payload in post_payloads:
                        async with session.post(url, headers=headers, json=payload) as response:
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    logger.info(f"✅ POST dados obtidos de {endpoint}: {json.dumps(data, indent=2)}")
                                    return data
                                except:
                                    pass
                    
                except Exception as e:
                    logger.debug(f"Erro em {endpoint}: {e}")
        
        return None
    
    async def monitor_websocket(self):
        """Tenta conectar via WebSocket para dados em tempo real."""
        if not self.game_url:
            return
        
        parsed = urlparse(self.game_url)
        
        # Possíveis URLs de WebSocket
        ws_urls = [
            f"wss://{parsed.netloc}/gs2c/websocket",
            f"wss://{parsed.netloc}/websocket",
            f"wss://{parsed.netloc}/ws",
            f"ws://{parsed.netloc}/gs2c/websocket",
            f"ws://{parsed.netloc}/websocket"
        ]
        
        for ws_url in ws_urls:
            try:
                logger.info(f"🔌 Tentando WebSocket: {ws_url}")
                
                import websockets
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                    'Origin': f"{parsed.scheme}://{parsed.netloc}"
                }
                
                async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                    logger.info(f"✅ WebSocket conectado: {ws_url}")
                    
                    # Enviar autenticação se necessário
                    if self.game_token:
                        auth_msg = json.dumps({
                            "type": "auth",
                            "token": self.game_token,
                            "gameId": self.game_id
                        })
                        await websocket.send(auth_msg)
                    
                    # Escutar mensagens
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            logger.info(f"📨 WebSocket message: {data}")
                            
                            # Processar resultado se encontrado
                            result = self._parse_websocket_result(data)
                            if result:
                                await self._process_new_result(result)
                                
                        except json.JSONDecodeError:
                            logger.debug(f"Mensagem não-JSON: {message}")
                        except Exception as e:
                            logger.error(f"Erro ao processar mensagem: {e}")
                            
            except Exception as e:
                logger.debug(f"Erro WebSocket {ws_url}: {e}")
    
    def _parse_websocket_result(self, data: Dict) -> Optional[RouletteResult]:
        """Extrai resultado da mensagem WebSocket."""
        try:
            # Diferentes formatos possíveis
            if 'result' in data:
                number = int(data['result'])
            elif 'number' in data:
                number = int(data['number'])
            elif 'winningNumber' in data:
                number = int(data['winningNumber'])
            else:
                return None
            
            # Determinar cor (roleta europeia 0-36)
            if number == 0:
                color = '🟢'
                color_name = 'VERDE'
            elif number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
                color = '🔴'
                color_name = 'VERMELHO'
            else:
                color = '⚫'
                color_name = 'PRETO'
            
            return RouletteResult(
                number=number,
                color=color,
                color_name=color_name,
                timestamp=datetime.now(),
                game_id=data.get('gameId', f'game_{int(time.time())}'),
                source='weebet_pragmatic_ws'
            )
            
        except Exception as e:
            logger.error(f"Erro ao extrair resultado: {e}")
            return None
    
    async def _process_new_result(self, result: RouletteResult):
        """Processa novo resultado."""
        # Evitar duplicatas
        if self.last_result and self.last_result.number == result.number:
            return
        
        self.last_result = result
        self.results_cache.append(result)
        
        # Manter cache limitado
        if len(self.results_cache) > 100:
            self.results_cache.pop(0)
        
        # Salvar no banco
        self.database.save_result(result)
        
        # Log do resultado
        logger.info(f"🎲 NOVO RESULTADO: {result.number} {result.color} {result.color_name}")
        print(f"🎲 ROLETA BRASILEIRA: {result.number} {result.color} {result.color_name} - {result.timestamp.strftime('%H:%M:%S')}")
    
    async def start(self):
        """Inicia o monitor."""
        logger.info("🚀 Iniciando monitor da Roleta Brasileira WeeBet...")
        
        # Obter URL do jogo
        game_url = await self.get_game_url()
        
        if not game_url:
            logger.error("❌ Não foi possível obter URL do jogo")
            return
        
        self.running = True
        
        # Carregar resultados iniciais do banco
        recent_results = self.database.get_recent_results(20)
        self.results_cache = recent_results
        logger.info(f"📊 {len(recent_results)} resultados carregados do banco")
        
        # Iniciar monitoramento
        tasks = [
            self.monitor_game_api(),
            self.monitor_websocket()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
    
    def stop(self):
        """Para o monitor."""
        self.running = False
        logger.info("🛑 Monitor da Roleta Brasileira parado")
    
    def get_dashboard_data(self) -> Dict:
        """Retorna dados para dashboard."""
        return {
            'recent_results': [r.to_dict() for r in self.results_cache[-20:]],
            'total_results': len(self.results_cache),
            'last_result': self.last_result.to_dict() if self.last_result else None,
            'game_info': {
                'game_id': self.game_id,
                'game_url': self.game_url[:100] + '...' if self.game_url else None,
                'has_token': bool(self.game_token),
                'running': self.running
            }
        }

async def test_roulette_monitor():
    """Testa o monitor da roleta."""
    print("🧪 TESTE DO MONITOR DA ROLETA BRASILEIRA WEEBET")
    print("=" * 60)
    
    monitor = WeeBetRouletteMonitor()
    
    # Testar obtenção da URL do jogo
    print("1. Obtendo URL do jogo...")
    game_url = await monitor.get_game_url()
    
    if game_url:
        print(f"✅ URL obtida: {game_url[:100]}...")
        
        if monitor.game_token:
            print(f"🔑 Token extraído: {monitor.game_token[:50]}...")
        
        # Testar monitoramento da API
        print("\n2. Testando monitoramento da API...")
        api_data = await monitor.monitor_game_api()
        
        if api_data:
            print("✅ Dados da API obtidos")
        else:
            print("❌ Nenhum dado da API encontrado")
        
        # Mostrar dados do dashboard
        print("\n3. Dados do dashboard:")
        dashboard_data = monitor.get_dashboard_data()
        print(json.dumps(dashboard_data, indent=2, default=str))
        
    else:
        print("❌ Não foi possível obter URL do jogo")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_roulette_monitor())
