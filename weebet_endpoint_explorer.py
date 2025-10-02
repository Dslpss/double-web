#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Explorador de Endpoints WeeBet
Descobre todas as rotas disponíveis na API
"""

import asyncio
import aiohttp
import json
import logging
from weebet_api_integrator import WeeBetAPI

logger = logging.getLogger(__name__)

class WeeBetEndpointExplorer:
    """Explora endpoints da API WeeBet."""
    
    def __init__(self):
        self.api = WeeBetAPI()
        self.successful_endpoints = []
    
    async def explore_all_endpoints(self):
        """Explora todos os endpoints possíveis."""
        print("🔍 EXPLORANDO ENDPOINTS WEEBET/PLAYNABETS")
        print("=" * 70)
        
        # Fazer login primeiro
        credentials = await self.api.login()
        if not credentials:
            print("❌ Não foi possível fazer login")
            return
        
        print(f"✅ Logado como: {credentials.user_name}")
        print()
        
        # Lista extensa de endpoints para testar
        endpoints_to_test = [
            # Endpoints de usuário
            "/user/profile",
            "/user/balance",
            "/user/history",
            "/user/transactions",
            "/user/bets",
            "/user/games",
            "/user/settings",
            "/user/info",
            "/user/data",
            
            # Endpoints de jogos
            "/games",
            "/games/list",
            "/games/available",
            "/games/live",
            "/games/history",
            "/games/results",
            "/games/roulette",
            "/games/slots",
            "/games/crash",
            "/games/aviator",
            "/games/mines",
            
            # Endpoints de cassino
            "/casino",
            "/casino/games",
            "/casino/live",
            "/casino/roulette",
            "/casino/slots",
            "/casino/history",
            "/casino/results",
            
            # Endpoints de roleta específicos
            "/roulette",
            "/roulette/live",
            "/roulette/history",
            "/roulette/results",
            "/roulette/current",
            "/roulette/last",
            "/roulette/statistics",
            
            # Endpoints de live games
            "/live",
            "/live/games",
            "/live/roulette",
            "/live/results",
            "/live/history",
            "/live/current",
            
            # Endpoints de API
            "/api",
            "/api/games",
            "/api/roulette",
            "/api/live",
            "/api/user",
            "/api/casino",
            "/api/results",
            "/api/history",
            
            # Endpoints v1/v2
            "/v1/games",
            "/v1/roulette",
            "/v1/live",
            "/v2/games",
            "/v2/roulette",
            "/v2/live",
            
            # Endpoints específicos de providers
            "/pragmatic",
            "/pragmatic/roulette",
            "/evolution",
            "/evolution/roulette",
            "/playtech",
            "/playtech/roulette",
            
            # Endpoints de dados
            "/data",
            "/data/games",
            "/data/roulette",
            "/data/live",
            "/results",
            "/history",
            "/statistics",
            "/stats",
            
            # Endpoints de WebSocket info
            "/ws",
            "/websocket",
            "/socket",
            "/realtime",
            "/stream",
            
            # Outros possíveis
            "/dashboard",
            "/lobby",
            "/tables",
            "/rooms",
            "/sessions",
            "/status",
            "/health"
        ]
        
        print(f"🧪 Testando {len(endpoints_to_test)} endpoints...")
        print()
        
        headers = credentials.get_auth_headers()
        
        # Testar todos os endpoints
        async with aiohttp.ClientSession() as session:
            for i, endpoint in enumerate(endpoints_to_test, 1):
                print(f"[{i:3d}/{len(endpoints_to_test)}] {endpoint:30} ", end='')
                
                try:
                    url = f"{self.api.base_url}{endpoint}"
                    async with session.get(url, headers=headers) as response:
                        await self._process_endpoint_response(endpoint, response)
                        
                except Exception as e:
                    print(f"❌ ERRO: {str(e)[:30]}")
                
                # Pequena pausa para não sobrecarregar
                await asyncio.sleep(0.1)
        
        # Mostrar resultados
        print("\n" + "=" * 70)
        print("📊 RESULTADOS DA EXPLORAÇÃO:")
        print("=" * 70)
        
        if self.successful_endpoints:
            print(f"✅ {len(self.successful_endpoints)} endpoints funcionando:\n")
            
            for result in self.successful_endpoints:
                print(f"🔗 {result['endpoint']}")
                print(f"   Status: {result['status']}")
                if result.get('content_type'):
                    print(f"   Tipo: {result['content_type']}")
                if result.get('data_keys'):
                    print(f"   Chaves: {result['data_keys']}")
                if result.get('data_length'):
                    print(f"   Tamanho: {result['data_length']}")
                if result.get('sample_data'):
                    print(f"   Amostra: {result['sample_data'][:100]}...")
                print()
        else:
            print("❌ Nenhum endpoint de dados encontrado")
            print("\n💡 POSSÍVEIS RAZÕES:")
            print("   1. API usa endpoints diferentes")
            print("   2. Requer parâmetros específicos")
            print("   3. Usa métodos POST ao invés de GET")
            print("   4. Endpoints estão em subdomínios diferentes")
    
    async def _process_endpoint_response(self, endpoint: str, response):
        """Processa resposta de um endpoint."""
        status = response.status
        
        if status == 200:
            try:
                # Tentar JSON primeiro
                data = await response.json()
                
                result = {
                    'endpoint': endpoint,
                    'status': status,
                    'success': True,
                    'content_type': 'json',
                    'data_type': type(data).__name__,
                    'data_keys': list(data.keys()) if isinstance(data, dict) else None,
                    'data_length': len(data) if isinstance(data, (list, dict)) else None,
                    'sample_data': str(data)
                }
                
                self.successful_endpoints.append(result)
                print("✅ JSON")
                
            except:
                try:
                    # Tentar texto
                    text = await response.text()
                    
                    if text and len(text.strip()) > 0:
                        result = {
                            'endpoint': endpoint,
                            'status': status,
                            'success': True,
                            'content_type': 'text',
                            'sample_data': text[:200]
                        }
                        
                        self.successful_endpoints.append(result)
                        print("✅ TEXT")
                    else:
                        print("✅ VAZIO")
                        
                except:
                    print("✅ BINÁRIO")
        
        elif status == 401:
            print("🔐 401 (Auth)")
        elif status == 403:
            print("🚫 403 (Forbidden)")
        elif status == 404:
            print("❌ 404 (Not Found)")
        elif status == 405:
            print("⚠️ 405 (Method)")
        elif status == 500:
            print("💥 500 (Server Error)")
        else:
            print(f"❓ {status}")
    
    async def test_post_endpoints(self):
        """Testa endpoints com método POST."""
        print("\n🔄 TESTANDO ENDPOINTS COM POST...")
        print("-" * 50)
        
        if not self.api.credentials:
            await self.api.login()
        
        post_endpoints = [
            "/games/search",
            "/roulette/bet",
            "/roulette/history",
            "/live/join",
            "/casino/enter",
            "/api/games/list",
            "/api/roulette/results"
        ]
        
        headers = self.api.credentials.get_auth_headers()
        
        async with aiohttp.ClientSession() as session:
            for endpoint in post_endpoints:
                print(f"POST {endpoint:30} ", end='')
                
                try:
                    url = f"{self.api.base_url}{endpoint}"
                    
                    # Tentar com payload vazio
                    async with session.post(url, headers=headers, json={}) as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"✅ JSON: {str(data)[:50]}...")
                            except:
                                print("✅ SUCCESS")
                        else:
                            print(f"❌ {response.status}")
                            
                except Exception as e:
                    print(f"❌ ERRO: {str(e)[:20]}")

async def main():
    """Função principal."""
    logging.basicConfig(level=logging.WARNING)  # Reduzir logs
    
    explorer = WeeBetEndpointExplorer()
    
    # Explorar endpoints GET
    await explorer.explore_all_endpoints()
    
    # Testar alguns endpoints POST
    await explorer.test_post_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
