#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste de Endpoints JimyoBot
Descobre que endpoints estão disponíveis na API
"""

import asyncio
import aiohttp
import json
import time
import logging

logger = logging.getLogger(__name__)

class JimyoBotEndpointTester:
    """Testa endpoints da API JimyoBot."""
    
    def __init__(self):
        self.base_url = "https://jimyobot.vip"
        self.session_data = "63314_D_76fb546386a10e4822da218d22e969bc"
        self.auth_token = None
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
    
    async def get_auth_token(self):
        """Obtém token de autenticação."""
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
                            print(f"✅ Token obtido: {self.auth_token[:50]}...")
                            return True
                    return False
        except Exception as e:
            print(f"❌ Erro ao obter token: {e}")
            return False
    
    async def test_endpoint(self, endpoint: str, method: str = 'GET', data: dict = None):
        """Testa um endpoint específico."""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = self.headers.copy()
            
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            async with aiohttp.ClientSession() as session:
                if method == 'GET':
                    async with session.get(url, headers=headers) as response:
                        return await self._process_response(endpoint, response)
                elif method == 'POST':
                    async with session.post(url, headers=headers, json=data) as response:
                        return await self._process_response(endpoint, response)
                        
        except Exception as e:
            return {'endpoint': endpoint, 'status': 'error', 'error': str(e)}
    
    async def _process_response(self, endpoint: str, response):
        """Processa resposta do endpoint."""
        try:
            status = response.status
            
            if status == 200:
                try:
                    data = await response.json()
                    return {
                        'endpoint': endpoint,
                        'status': status,
                        'success': True,
                        'data_type': type(data).__name__,
                        'data_keys': list(data.keys()) if isinstance(data, dict) else None,
                        'data_length': len(data) if isinstance(data, (list, dict)) else None,
                        'sample_data': str(data)[:200] + '...' if len(str(data)) > 200 else str(data)
                    }
                except:
                    text = await response.text()
                    return {
                        'endpoint': endpoint,
                        'status': status,
                        'success': True,
                        'content_type': 'text',
                        'sample_data': text[:200] + '...' if len(text) > 200 else text
                    }
            else:
                return {
                    'endpoint': endpoint,
                    'status': status,
                    'success': False,
                    'error': f'HTTP {status}'
                }
                
        except Exception as e:
            return {
                'endpoint': endpoint,
                'status': 'error',
                'error': str(e)
            }
    
    async def discover_endpoints(self):
        """Descobre endpoints disponíveis."""
        print("🔍 DESCOBRINDO ENDPOINTS JIMYOBOT")
        print("=" * 60)
        
        # Obter token primeiro
        if not await self.get_auth_token():
            print("❌ Não foi possível obter token de autenticação")
            return
        
        # Lista de endpoints para testar
        endpoints_to_test = [
            # Endpoints de API comuns
            '/api',
            '/api/status',
            '/api/games',
            '/api/data',
            '/api/results',
            '/api/history',
            '/api/live',
            '/api/double',
            '/api/roulette',
            '/api/crash',
            '/api/mines',
            '/api/aviator',
            
            # Endpoints específicos do app
            '/ap',
            '/ap/status',
            '/ap/games',
            '/ap/data',
            '/ap/results',
            '/ap/history',
            '/ap/live',
            '/ap/double',
            '/ap/roulette',
            '/ap/crash',
            '/ap/mines',
            '/ap/aviator',
            
            # Endpoints de usuário
            '/user',
            '/user/profile',
            '/user/balance',
            '/user/history',
            
            # Endpoints de bot
            '/bot',
            '/bot/status',
            '/bot/config',
            '/bot/signals',
            
            # Outros possíveis
            '/v1/games',
            '/v1/data',
            '/data',
            '/games',
            '/results',
            '/live',
            '/signals'
        ]
        
        print(f"🧪 Testando {len(endpoints_to_test)} endpoints...")
        print()
        
        successful_endpoints = []
        
        # Testar todos os endpoints
        for i, endpoint in enumerate(endpoints_to_test, 1):
            print(f"[{i:2d}/{len(endpoints_to_test)}] Testando {endpoint}...", end=' ')
            
            result = await self.test_endpoint(endpoint)
            
            if result.get('success'):
                print("✅")
                successful_endpoints.append(result)
            elif result.get('status') == 404:
                print("❌ (404)")
            elif result.get('status') == 401:
                print("🔐 (401)")
            elif result.get('status') == 403:
                print("🚫 (403)")
            else:
                print(f"❌ ({result.get('status', 'error')})")
            
            # Pequena pausa para não sobrecarregar
            await asyncio.sleep(0.1)
        
        # Mostrar resultados
        print()
        print("📊 RESULTADOS:")
        print("=" * 60)
        
        if successful_endpoints:
            print(f"✅ {len(successful_endpoints)} endpoints funcionando:")
            print()
            
            for result in successful_endpoints:
                print(f"🔗 {result['endpoint']}")
                print(f"   Status: {result['status']}")
                if result.get('data_keys'):
                    print(f"   Chaves: {result['data_keys']}")
                if result.get('data_length'):
                    print(f"   Tamanho: {result['data_length']}")
                if result.get('sample_data'):
                    print(f"   Dados: {result['sample_data']}")
                print()
        else:
            print("❌ Nenhum endpoint de dados encontrado")
            print()
            print("💡 POSSÍVEIS RAZÕES:")
            print("   1. API requer parâmetros específicos")
            print("   2. Endpoints usam métodos POST")
            print("   3. Autenticação adicional necessária")
            print("   4. API não expõe dados publicamente")

async def main():
    """Função principal."""
    logging.basicConfig(level=logging.WARNING)  # Reduzir logs
    
    tester = JimyoBotEndpointTester()
    await tester.discover_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
