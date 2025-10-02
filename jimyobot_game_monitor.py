#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor de Jogos JimyoBot
Monitora dados de jogos da API JimyoBot em tempo real
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JimyoBotGame:
    """Representa um jogo do JimyoBot."""
    id: int
    name: str
    providers: List[str]
    image: str
    category: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'JimyoBotGame':
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            providers=data.get('providers', []),
            image=data.get('image', ''),
            category=data.get('cat', '')
        )

class JimyoBotGameMonitor:
    """Monitor de jogos do JimyoBot."""
    
    def __init__(self):
        """Inicializa o monitor."""
        self.base_url = "https://jimyobot.vip"
        self.session_data = "63314_D_76fb546386a10e4822da218d22e969bc"
        self.auth_token = None
        self.running = False
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://jimyobot.vip/',
            'Content-Type': 'application/json',
            'Origin': 'https://jimyobot.vip',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=4',
            'Te': 'trailers'
        }
        
        # Cache de dados
        self.games_cache = []
        self.live_games = []
        self.history_cache = []
        
        logger.info("JimyoBot Game Monitor inicializado")
    
    async def authenticate(self) -> bool:
        """Autentica com a API."""
        try:
            url = f"{self.base_url}/ap/check"
            params = {'t': str(int(time.time() * 1000))}
            
            data = {"sessionData": self.session_data}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success') and result.get('tokens'):
                            self.auth_token = result['tokens'][0]
                            logger.info(f"✅ Autenticado como: {result.get('name', 'Usuário')}")
                            return True
            
            logger.error("❌ Falha na autenticação")
            return False
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return False
    
    async def get_games_history(self) -> Optional[Dict]:
        """Obtém histórico de jogos."""
        try:
            if not self.auth_token:
                return None
            
            url = f"{self.base_url}/ap/history"
            headers = self.headers.copy()
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Processar jogos
                        if 'games' in data:
                            self.games_cache = [JimyoBotGame.from_dict(game) for game in data['games']]
                            logger.info(f"📊 {len(self.games_cache)} jogos carregados")
                        
                        # Processar histórico
                        if 'list' in data:
                            self.history_cache = data['list']
                            logger.info(f"📜 {len(self.history_cache)} entradas de histórico")
                        
                        return data
                    else:
                        logger.error(f"Erro ao obter histórico: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return None
    
    async def get_live_games(self) -> Optional[Dict]:
        """Obtém jogos ao vivo."""
        try:
            if not self.auth_token:
                return None
            
            url = f"{self.base_url}/ap/live"
            headers = self.headers.copy()
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'games' in data:
                            self.live_games = data['games']
                            if self.live_games:
                                logger.info(f"🔴 {len(self.live_games)} jogos ao vivo")
                            else:
                                logger.debug("Nenhum jogo ao vivo no momento")
                        
                        return data
                    else:
                        logger.error(f"Erro ao obter jogos ao vivo: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao obter jogos ao vivo: {e}")
            return None
    
    async def get_aviator_data(self) -> Optional[Dict]:
        """Obtém dados do Aviator."""
        try:
            if not self.auth_token:
                return None
            
            url = f"{self.base_url}/ap/aviator"
            headers = self.headers.copy()
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            logger.info("✈️ Dados do Aviator obtidos")
                        else:
                            logger.debug("Aviator não disponível no momento")
                        
                        return data
                    else:
                        logger.error(f"Erro ao obter dados do Aviator: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao obter dados do Aviator: {e}")
            return None
    
    async def get_mines_data(self) -> Optional[Dict]:
        """Obtém dados do Mines."""
        try:
            if not self.auth_token:
                return None
            
            url = f"{self.base_url}/ap/mines"
            headers = self.headers.copy()
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            logger.info("💎 Dados do Mines obtidos")
                        else:
                            logger.debug("Mines não disponível no momento")
                        
                        return data
                    else:
                        logger.error(f"Erro ao obter dados do Mines: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao obter dados do Mines: {e}")
            return None
    
    async def monitor_loop(self):
        """Loop principal de monitoramento."""
        logger.info("🔍 Iniciando monitoramento JimyoBot...")
        
        check_count = 0
        
        while self.running:
            try:
                check_count += 1
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                print(f"\n🔍 Verificação #{check_count} - {timestamp}")
                print("-" * 50)
                
                # Obter dados de todos os endpoints
                history_data = await self.get_games_history()
                live_data = await self.get_live_games()
                aviator_data = await self.get_aviator_data()
                mines_data = await self.get_mines_data()
                
                # Mostrar resumo
                print(f"📊 Jogos disponíveis: {len(self.games_cache)}")
                print(f"🔴 Jogos ao vivo: {len(self.live_games)}")
                print(f"📜 Entradas de histórico: {len(self.history_cache)}")
                
                # Mostrar jogos disponíveis (primeiros 5)
                if self.games_cache:
                    print("\n🎮 JOGOS DISPONÍVEIS:")
                    for game in self.games_cache[:5]:
                        print(f"   {game.id}: {game.name} ({game.category})")
                    
                    if len(self.games_cache) > 5:
                        print(f"   ... e mais {len(self.games_cache) - 5} jogos")
                
                # Mostrar jogos ao vivo
                if self.live_games:
                    print("\n🔴 JOGOS AO VIVO:")
                    for game in self.live_games:
                        print(f"   {json.dumps(game, indent=2)}")
                
                # Aguardar próxima verificação
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(5)
    
    async def start(self):
        """Inicia o monitor."""
        # Autenticar primeiro
        if not await self.authenticate():
            logger.error("❌ Não foi possível autenticar")
            return False
        
        # Iniciar monitoramento
        self.running = True
        await self.monitor_loop()
        
        return True
    
    def stop(self):
        """Para o monitor."""
        self.running = False
        logger.info("🛑 Monitor parado")
    
    def get_dashboard_data(self) -> Dict:
        """Retorna dados para dashboard."""
        return {
            'games': [
                {
                    'id': game.id,
                    'name': game.name,
                    'category': game.category,
                    'image': game.image,
                    'providers': game.providers
                }
                for game in self.games_cache
            ],
            'live_games': self.live_games,
            'history': self.history_cache,
            'stats': {
                'total_games': len(self.games_cache),
                'live_games': len(self.live_games),
                'history_entries': len(self.history_cache)
            }
        }

async def test_monitor():
    """Testa o monitor."""
    print("🧪 TESTE DO MONITOR JIMYOBOT")
    print("=" * 60)
    
    monitor = JimyoBotGameMonitor()
    
    # Autenticar
    if await monitor.authenticate():
        print("✅ Autenticação bem-sucedida")
        
        # Testar cada endpoint
        print("\n📊 Testando endpoints...")
        
        history = await monitor.get_games_history()
        if history:
            print(f"✅ Histórico: {len(monitor.games_cache)} jogos")
        
        live = await monitor.get_live_games()
        if live:
            print(f"✅ Ao vivo: {len(monitor.live_games)} jogos")
        
        aviator = await monitor.get_aviator_data()
        if aviator:
            print("✅ Aviator: Dados obtidos")
        
        mines = await monitor.get_mines_data()
        if mines:
            print("✅ Mines: Dados obtidos")
        
        # Mostrar dados do dashboard
        dashboard_data = monitor.get_dashboard_data()
        print(f"\n📋 Dashboard: {json.dumps(dashboard_data, indent=2)}")
        
    else:
        print("❌ Falha na autenticação")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_monitor())
