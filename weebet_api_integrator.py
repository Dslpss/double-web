#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador WeeBet/PlayNaBets API
Conecta com a API real usando credenciais de login
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import jwt
import threading

logger = logging.getLogger(__name__)

@dataclass
class WeeBetCredentials:
    """Credenciais do WeeBet."""
    token: str
    token_cassino: str
    user_id: int
    user_name: str
    cookie: str
    expires_at: datetime
    
    @classmethod
    def from_login_response(cls, response_data: Dict) -> 'WeeBetCredentials':
        """Cria credenciais a partir da resposta de login."""
        results = response_data.get('results', {})
        user = results.get('user', {})
        
        # Decodificar token para pegar expiração
        token = results.get('token', '')
        expires_at = datetime.now() + timedelta(hours=24)  # Default
        
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            if 'exp' in decoded:
                expires_at = datetime.fromtimestamp(decoded['exp'])
        except:
            pass
        
        return cls(
            token=token,
            token_cassino=results.get('tokenCassino', ''),
            user_id=user.get('id', 0),
            user_name=user.get('nome', ''),
            cookie=user.get('cookie', ''),
            expires_at=expires_at
        )
    
    def is_expired(self) -> bool:
        """Verifica se o token está expirado."""
        return datetime.now() >= self.expires_at
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers com autenticação."""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://playnabets.com/',
            'Origin': 'https://playnabets.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0'
        }

class WeeBetAPI:
    """Cliente para API do WeeBet/PlayNaBets."""
    
    def __init__(self, email: str = None, password: str = None):
        """Inicializa o cliente da API."""
        self.base_url = "https://loki1.weebet.tech"
        self.email = email or "dennisemannuel93@gmail.com"
        self.password = password or "Flamengo.019"
        self.credentials: Optional[WeeBetCredentials] = None
        
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Referer': 'https://playnabets.com/',
            'Origin': 'https://playnabets.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Te': 'trailers'
        }
        
        logger.info("WeeBet API inicializada")
    
    async def login(self) -> Optional[WeeBetCredentials]:
        """Faz login na API e obtém credenciais."""
        try:
            url = f"{self.base_url}/auth/login"
            
            login_data = {
                "username": self.email,
                "password": self.password,
                "googleId": "",
                "googleIdToken": "",
                "loginMode": "email",
                "cookie": "",
                "ignorarValidacaoEmailObrigatoria": True,
                "betting_shop_code": None
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.session_headers, json=login_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get('success'):
                            self.credentials = WeeBetCredentials.from_login_response(result)
                            
                            logger.info(f"✅ Login realizado - Usuário: {self.credentials.user_name}")
                            logger.info(f"🆔 ID: {self.credentials.user_id}")
                            logger.info(f"🕐 Token expira em: {self.credentials.expires_at}")
                            
                            return self.credentials
                        else:
                            logger.error("❌ Login falhou - credenciais inválidas")
                            return None
                    else:
                        logger.error(f"❌ Erro HTTP no login: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return None
    
    async def verify_account(self) -> Optional[Dict]:
        """Verifica informações da conta."""
        if not self.credentials or self.credentials.is_expired():
            logger.warning("Credenciais inválidas ou expiradas")
            return None
        
        try:
            url = f"{self.base_url}/user/account-verification"
            headers = self.credentials.get_auth_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        logger.info(f"💰 Saldo: R$ {data.get('balance', '0.00')}")
                        logger.info(f"✅ Conta verificada: {data.get('account_verified', False)}")
                        
                        return data
                    else:
                        logger.error(f"Erro ao verificar conta: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao verificar conta: {e}")
            return None
    
    async def get_games_data(self) -> Optional[Dict]:
        """Obtém dados de jogos disponíveis."""
        if not self.credentials or self.credentials.is_expired():
            await self.login()
        
        if not self.credentials:
            return None
        
        try:
            # Testar diferentes endpoints possíveis
            endpoints = [
                "/games",
                "/games/list",
                "/casino/games",
                "/api/games",
                "/user/games",
                "/roulette/games",
                "/live/games"
            ]
            
            headers = self.credentials.get_auth_headers()
            
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        url = f"{self.base_url}{endpoint}"
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                logger.info(f"✅ Dados obtidos de {endpoint}")
                                return data
                            else:
                                logger.debug(f"❌ {endpoint}: {response.status}")
                    except Exception as e:
                        logger.debug(f"Erro em {endpoint}: {e}")
            
            logger.warning("Nenhum endpoint de jogos encontrado")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de jogos: {e}")
            return None
    
    async def get_roulette_results(self) -> Optional[Dict]:
        """Obtém resultados da roleta."""
        if not self.credentials or self.credentials.is_expired():
            await self.login()
        
        if not self.credentials:
            return None
        
        try:
            # Testar endpoints específicos da roleta
            endpoints = [
                "/roulette/results",
                "/roulette/history",
                "/games/roulette/results",
                "/live/roulette/results",
                "/api/roulette",
                "/casino/roulette"
            ]
            
            headers = self.credentials.get_auth_headers()
            
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        url = f"{self.base_url}{endpoint}"
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                logger.info(f"🎲 Resultados da roleta obtidos de {endpoint}")
                                return data
                            else:
                                logger.debug(f"❌ {endpoint}: {response.status}")
                    except Exception as e:
                        logger.debug(f"Erro em {endpoint}: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter resultados da roleta: {e}")
            return None

class WeeBetMonitor:
    """Monitor completo do WeeBet."""
    
    def __init__(self, email: str = None, password: str = None):
        """Inicializa o monitor."""
        self.api = WeeBetAPI(email, password)
        self.running = False
        self.monitor_thread = None
        
        # Cache de dados
        self.account_data = {}
        self.games_data = {}
        self.roulette_results = []
        
        logger.info("WeeBet Monitor inicializado")
    
    async def start(self):
        """Inicia o monitor."""
        logger.info("🚀 Iniciando monitor WeeBet...")
        
        # Fazer login inicial
        credentials = await self.api.login()
        
        if credentials:
            logger.info(f"✅ Conectado como: {credentials.user_name}")
            
            # Verificar conta
            account_info = await self.api.verify_account()
            if account_info:
                self.account_data = account_info
            
            # Tentar obter dados de jogos
            games_data = await self.api.get_games_data()
            if games_data:
                self.games_data = games_data
            
            # Tentar obter resultados da roleta
            roulette_data = await self.api.get_roulette_results()
            if roulette_data:
                self.roulette_results = roulette_data
            
            self.running = True
            
            # Iniciar monitoramento contínuo
            await self.monitor_loop()
        else:
            logger.error("❌ Não foi possível conectar ao WeeBet")
    
    async def monitor_loop(self):
        """Loop principal de monitoramento."""
        check_count = 0
        
        while self.running:
            try:
                check_count += 1
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                print(f"\n🔍 Verificação WeeBet #{check_count} - {timestamp}")
                print("-" * 60)
                
                # Verificar se token ainda é válido
                if self.api.credentials and self.api.credentials.is_expired():
                    logger.info("🔄 Token expirado, fazendo novo login...")
                    await self.api.login()
                
                # Atualizar dados da conta
                account_info = await self.api.verify_account()
                if account_info:
                    self.account_data = account_info
                    print(f"💰 Saldo: R$ {account_info.get('balance', '0.00')}")
                
                # Tentar obter novos dados
                games_data = await self.api.get_games_data()
                if games_data:
                    self.games_data = games_data
                    print(f"🎮 Dados de jogos atualizados")
                
                roulette_data = await self.api.get_roulette_results()
                if roulette_data:
                    self.roulette_results = roulette_data
                    print(f"🎲 Resultados da roleta atualizados")
                
                # Aguardar próxima verificação
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Para o monitor."""
        self.running = False
        logger.info("🛑 Monitor WeeBet parado")
    
    def get_dashboard_data(self) -> Dict:
        """Retorna dados para dashboard."""
        return {
            'account': self.account_data,
            'games': self.games_data,
            'roulette_results': self.roulette_results,
            'credentials': {
                'user_name': self.api.credentials.user_name if self.api.credentials else None,
                'user_id': self.api.credentials.user_id if self.api.credentials else None,
                'expires_at': self.api.credentials.expires_at.isoformat() if self.api.credentials else None,
                'is_expired': self.api.credentials.is_expired() if self.api.credentials else True
            },
            'stats': {
                'balance': self.account_data.get('balance', '0.00'),
                'account_verified': self.account_data.get('account_verified', False),
                'games_count': len(self.games_data) if isinstance(self.games_data, list) else 0,
                'roulette_results_count': len(self.roulette_results) if isinstance(self.roulette_results, list) else 0
            }
        }

async def test_weebet_api():
    """Testa a API do WeeBet."""
    print("🧪 TESTE DA API WEEBET/PLAYNABETS")
    print("=" * 60)
    
    monitor = WeeBetMonitor()
    
    # Testar login
    print("1. Fazendo login...")
    credentials = await monitor.api.login()
    
    if credentials:
        print(f"✅ Usuário: {credentials.user_name}")
        print(f"🆔 ID: {credentials.user_id}")
        print(f"🕐 Expira em: {credentials.expires_at}")
        
        # Testar verificação de conta
        print("\n2. Verificando conta...")
        account_info = await monitor.api.verify_account()
        
        if account_info:
            print(f"💰 Saldo: R$ {account_info.get('balance', '0.00')}")
            print(f"✅ Verificada: {account_info.get('account_verified', False)}")
        
        # Testar obtenção de dados de jogos
        print("\n3. Tentando obter dados de jogos...")
        games_data = await monitor.api.get_games_data()
        
        if games_data:
            print(f"🎮 Dados de jogos: {json.dumps(games_data, indent=2)}")
        else:
            print("❌ Nenhum dado de jogo encontrado")
        
        # Testar resultados da roleta
        print("\n4. Tentando obter resultados da roleta...")
        roulette_data = await monitor.api.get_roulette_results()
        
        if roulette_data:
            print(f"🎲 Dados da roleta: {json.dumps(roulette_data, indent=2)}")
        else:
            print("❌ Nenhum resultado da roleta encontrado")
        
        # Mostrar dados do dashboard
        print("\n5. Dados do dashboard:")
        dashboard_data = monitor.get_dashboard_data()
        print(json.dumps(dashboard_data, indent=2, default=str))
        
    else:
        print("❌ Falha no login")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_weebet_api())
