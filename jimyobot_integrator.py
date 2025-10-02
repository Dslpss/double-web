#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador JimyoBot API
Conecta com a API jimyobot.vip para obter dados de jogos
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import jwt
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JimyoBotCredentials:
    """Credenciais do JimyoBot."""
    session_data: str
    tokens: List[str]
    user_name: str
    balance: float
    trial: int
    
    @classmethod
    def from_response(cls, response_data: Dict) -> 'JimyoBotCredentials':
        """Cria credenciais a partir da resposta da API."""
        return cls(
            session_data="",  # Será preenchido externamente
            tokens=response_data.get('tokens', []),
            user_name=response_data.get('name', ''),
            balance=response_data.get('balance', 0),
            trial=response_data.get('trial', 0)
        )

class JimyoBotAPI:
    """Cliente para API do JimyoBot."""
    
    def __init__(self):
        """Inicializa o cliente da API."""
        self.base_url = "https://jimyobot.vip"
        self.session_data = "63314_D_76fb546386a10e4822da218d22e969bc"  # Da requisição capturada
        self.credentials: Optional[JimyoBotCredentials] = None
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
        
        logger.info("JimyoBot API inicializada")
    
    async def check_session(self) -> Optional[JimyoBotCredentials]:
        """Verifica sessão e obtém credenciais."""
        try:
            url = f"{self.base_url}/ap/check"
            params = {'t': str(int(time.time() * 1000))}
            
            data = {
                "sessionData": self.session_data
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get('success'):
                            self.credentials = JimyoBotCredentials.from_response(result)
                            self.credentials.session_data = self.session_data
                            
                            logger.info(f"✅ Sessão válida - Usuário: {self.credentials.user_name}")
                            logger.info(f"💰 Saldo: {self.credentials.balance}")
                            logger.info(f"🎫 Tokens: {len(self.credentials.tokens)}")
                            
                            return self.credentials
                        else:
                            logger.error("❌ Sessão inválida")
                            return None
                    else:
                        logger.error(f"❌ Erro HTTP: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao verificar sessão: {e}")
            return None
    
    def decode_jwt_token(self, token: str) -> Optional[Dict]:
        """Decodifica token JWT (sem verificação de assinatura)."""
        try:
            # Decodificar sem verificar assinatura (apenas para ver conteúdo)
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            logger.error(f"Erro ao decodificar JWT: {e}")
            return None
    
    async def get_live_games(self) -> Optional[Dict]:
        """Obtém dados de jogos ao vivo do endpoint /ap/live."""
        try:
            url = f"{self.base_url}/ap/live"
            params = {'oid': '1'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Dados de jogos obtidos: {len(data.get('games', []))} jogos")
                        return data
                    else:
                        logger.error(f"❌ Erro ao obter jogos: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao obter dados de jogos: {e}")
            return None
    
    def extract_roulette_data(self, games_data: Dict) -> Optional[Dict]:
        """Extrai dados específicos da roleta brasileira."""
        try:
            games = games_data.get('games', [])
            
            for game in games:
                if game.get('name') == 'Roleta Brasileira' and game.get('cat') == 'Live':
                    roulette_data = {
                        'id': game.get('id'),
                        'name': game.get('name'),
                        'status': game.get('status'),
                        'percentage': game.get('percentage'),
                        'streak': game.get('streak', []),
                        'strategy': game.get('strat', {}),
                        'enabled': game.get('enabled', False),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Extrair informações da estratégia se disponível
                    if 'strat' in game and game['strat']:
                        strategy = game['strat']
                        roulette_data['strategy_details'] = {
                            'gale': strategy.get('gale', 0),
                            'tentativa': strategy.get('tentativa', 0),
                            'trigger_pattern': strategy.get('triggerPattern', ''),
                            'max_gales': strategy.get('maxGales', 0),
                            'after': strategy.get('after', 0),
                            'ndx': strategy.get('ndx', ''),
                            'state': strategy.get('state', {})
                        }
                    
                    logger.info(f"🎲 Roleta encontrada - Status: {roulette_data['status']}")
                    return roulette_data
            
            logger.warning("❌ Roleta Brasileira não encontrada nos jogos")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da roleta: {e}")
            return None
    
    async def get_game_data(self) -> Optional[Dict]:
        """Obtém dados de jogos - método mantido para compatibilidade."""
        return await self.get_live_games()
    
    async def monitor_games(self, callback=None):
        """Monitora jogos em tempo real."""
        logger.info("🔍 Iniciando monitoramento JimyoBot...")
        
        while True:
            try:
                # Verificar sessão periodicamente
                if not self.credentials:
                    await self.check_session()
                
                # Obter dados de jogos ao vivo
                games_data = await self.get_live_games()
                
                if games_data:
                    # Processar todos os jogos
                    if callback:
                        callback(games_data)
                    
                    # Extrair dados específicos da roleta
                    roulette_data = self.extract_roulette_data(games_data)
                    if roulette_data:
                        logger.info(f"🎲 Roleta - Status: {roulette_data['status']}, "
                                  f"Percentual: {roulette_data['percentage']}")
                        
                        # Se há uma estratégia ativa, mostrar detalhes
                        if roulette_data.get('strategy_details'):
                            strategy = roulette_data['strategy_details']
                            logger.info(f"📊 Estratégia - Gale: {strategy['gale']}, "
                                      f"Pattern: {strategy['trigger_pattern']}")
                
                # Aguardar antes da próxima verificação (reduzido para capturar mudanças mais rápido)
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                await asyncio.sleep(5)

class JimyoBotIntegrator:
    """Integrador completo do JimyoBot."""
    
    def __init__(self):
        """Inicializa o integrador."""
        self.api = JimyoBotAPI()
        self.running = False
        self.results_cache = []
        
    async def start(self):
        """Inicia o integrador."""
        logger.info("🚀 Iniciando integrador JimyoBot...")
        
        # Verificar sessão inicial
        credentials = await self.api.check_session()
        
        if credentials:
            logger.info(f"✅ Conectado como: {credentials.user_name}")
            self.running = True
            
            # Iniciar monitoramento
            await self.api.monitor_games(self.process_game_data)
        else:
            logger.error("❌ Não foi possível conectar ao JimyoBot")
    
    async def get_roulette_game_url(self) -> Optional[str]:
        """Constrói URL do jogo da roleta com token JWT."""
        if not self.api.credentials or not self.api.credentials.tokens:
            logger.warning("Credenciais não disponíveis para URL do jogo")
            return None
        
        try:
            # Usar o segundo token (baseado na captura)
            game_token = self.api.credentials.tokens[1] if len(self.api.credentials.tokens) > 1 else self.api.credentials.tokens[0]
            
            # Parâmetros do jogo da roleta
            game_params = {
                'token': game_token,
                'pn': 'playnabet',
                'lang': 'pt',
                'game': 'evo-oss-xs-roleta-ao-vivo',
                'currency': 'BRL',
                'type': 'CHARGE'
            }
            
            # Construir URL
            base_url = "https://api.salsagator.com/game"
            params_str = "&".join([f"{k}={v}" for k, v in game_params.items()])
            game_url = f"{base_url}?{params_str}"
            
            logger.info(f"🎲 URL do jogo da roleta construída")
            return game_url
            
        except Exception as e:
            logger.error(f"Erro ao construir URL do jogo: {e}")
            return None
    
    def process_game_data(self, data: Dict):
        """Processa dados de jogos recebidos."""
        try:
            # Extrair dados específicos da roleta
            roulette_data = self.api.extract_roulette_data(data)
            
            # Preparar dados processados
            processed_data = {
                'timestamp': datetime.now().isoformat(),
                'total_games': len(data.get('games', [])),
                'roulette_data': roulette_data,
                'raw_data': data
            }
            
            # Log resumido
            if roulette_data:
                logger.info(f"🎲 Roleta - Status: {roulette_data['status']}, "
                          f"Enabled: {roulette_data['enabled']}, "
                          f"Percentage: {roulette_data['percentage']}")
            
            # Adicionar ao cache
            self.results_cache.append(processed_data)
            
            # Manter apenas últimos 100 resultados
            if len(self.results_cache) > 100:
                self.results_cache.pop(0)
                
        except Exception as e:
            logger.error(f"Erro ao processar dados: {e}")
    
    def get_roulette_status(self) -> Optional[Dict]:
        """Obtém status atual da roleta."""
        if not self.results_cache:
            return None
        
        latest_data = self.results_cache[-1]
        return latest_data.get('roulette_data')
    
    def get_roulette_history(self, limit: int = 10) -> List[Dict]:
        """Obtém histórico da roleta."""
        roulette_history = []
        
        for entry in self.results_cache[-limit:]:
            if entry.get('roulette_data'):
                roulette_history.append(entry['roulette_data'])
        
        return roulette_history
    
    def get_recent_results(self, limit: int = 20) -> List[Dict]:
        """Obtém resultados recentes."""
        return self.results_cache[-limit:] if self.results_cache else []

async def test_jimyobot_api():
    """Testa a API do JimyoBot com os novos endpoints."""
    print("🧪 TESTE COMPLETO DA API JIMYOBOT")
    print("=" * 60)
    
    integrator = JimyoBotIntegrator()
    
    # Testar verificação de sessão
    print("1. 🔐 Verificando sessão...")
    credentials = await integrator.api.check_session()
    
    if credentials:
        print(f"   ✅ Usuário: {credentials.user_name}")
        print(f"   💰 Saldo: {credentials.balance}")
        print(f"   🎫 Tokens: {len(credentials.tokens)}")
        
        # Testar decodificação de tokens
        print("\n2. 🔑 Analisando tokens JWT...")
        for i, token in enumerate(credentials.tokens):
            token_data = integrator.api.decode_jwt_token(token)
            if token_data:
                exp_time = datetime.fromtimestamp(token_data.get('exp', 0))
                print(f"   Token {i+1}: Expira em {exp_time}")
            else:
                print(f"   Token {i+1}: Não foi possível decodificar")
        
        # Testar endpoint de jogos ao vivo
        print("\n3. 🎮 Obtendo dados de jogos ao vivo...")
        games_data = await integrator.api.get_live_games()
        
        if games_data:
            games = games_data.get('games', [])
            print(f"   ✅ {len(games)} jogos encontrados")
            
            # Mostrar resumo dos jogos
            for game in games:
                status_icon = "🟢" if game.get('enabled') else "🔴"
                print(f"   {status_icon} {game.get('name')} ({game.get('cat')}) - {game.get('status')}")
            
            # Testar extração de dados da roleta
            print("\n4. 🎲 Analisando dados da Roleta Brasileira...")
            roulette_data = integrator.api.extract_roulette_data(games_data)
            
            if roulette_data:
                print(f"   ✅ Roleta encontrada!")
                print(f"   📊 Status: {roulette_data['status']}")
                print(f"   📈 Percentual: {roulette_data['percentage']}")
                print(f"   🎯 Enabled: {roulette_data['enabled']}")
                print(f"   🔄 Streak: {roulette_data['streak']}")
                
                if roulette_data.get('strategy_details'):
                    strategy = roulette_data['strategy_details']
                    print(f"   🧠 Estratégia ativa:")
                    print(f"      - Gale: {strategy['gale']}")
                    print(f"      - Pattern: {strategy['trigger_pattern']}")
                    print(f"      - Max Gales: {strategy['max_gales']}")
            else:
                print("   ❌ Roleta não encontrada ou não ativa")
            
            # Testar construção da URL do jogo
            print("\n5. 🔗 Construindo URL do jogo da roleta...")
            game_url = await integrator.get_roulette_game_url()
            
            if game_url:
                print(f"   ✅ URL construída com sucesso")
                print(f"   🔗 {game_url[:100]}...")
            else:
                print("   ❌ Não foi possível construir URL do jogo")
                
        else:
            print("   ❌ Nenhum dado de jogo encontrado")
            
        # Testar processamento de dados
        print("\n6. 📊 Testando processamento de dados...")
        if games_data:
            integrator.process_game_data(games_data)
            roulette_status = integrator.get_roulette_status()
            
            if roulette_status:
                print(f"   ✅ Status da roleta processado: {roulette_status['status']}")
            else:
                print("   ❌ Nenhum status de roleta processado")
                
    else:
        print("   ❌ Falha na verificação de sessão")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_jimyobot_api())
