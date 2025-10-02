#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Descobridor de endpoints PlayNaBets
Explora sistematicamente a API para encontrar endpoints de jogos/roleta
"""

import asyncio
import aiohttp
import json
import time

async def discover_endpoints():
    """Descobre endpoints da API PlayNaBets."""
    print("🔍 DESCOBRINDO ENDPOINTS PLAYNABETS")
    print("=" * 60)
    
    base_url = "https://central.playnabet.com"
    jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkzNzE2NzMsImV4cCI6MTc1OTk3NjQ3MywidXNlciI6eyJpZCI6NjMzMTR9fQ.mc98Vco9SO3NLY2bur9aeUzPluiC_6Mu8NMUfiq4McA"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Origin': 'https://playnabets.com',
        'Referer': 'https://playnabets.com/',
        'Authorization': f'Bearer {jwt_token}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Te': 'trailers'
    }
    
    # Primeiro, vamos ver o que tem no endpoint do usuário
    print("1. Analisando dados do usuário...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/api/clientes/getCliente/63314", headers=headers) as response:
            if response.status == 200:
                user_data = await response.json()
                print("📋 Estrutura dos dados do usuário:")
                print(json.dumps(user_data, indent=2)[:1000] + "...")
    
    # Endpoints mais prováveis baseados em padrões comuns
    print("\n2. Testando endpoints comuns...")
    common_endpoints = [
        # Histórico e transações
        "/api/transacoes",
        "/api/transacoes/historico", 
        "/api/historico",
        "/api/historico/jogos",
        "/api/apostas",
        "/api/apostas/historico",
        
        # Jogos e casino
        "/api/jogos",
        "/api/casino",
        "/api/cassino", 
        "/api/games",
        "/api/live-casino",
        "/api/live",
        
        # Específicos da roleta
        "/api/roulette",
        "/api/roleta",
        "/api/brazilian-roulette",
        "/api/pragmatic-play",
        "/api/pragmatic",
        
        # Resultados e estatísticas
        "/api/resultados",
        "/api/results",
        "/api/statistics",
        "/api/estatisticas",
        "/api/history",
        
        # Sessões e atividade
        "/api/sessoes",
        "/api/sessions",
        "/api/atividade",
        "/api/activity",
        
        # Configurações e perfil
        "/api/perfil",
        "/api/profile",
        "/api/configuracoes",
        "/api/settings",
        
        # Dashboard e métricas
        "/api/dashboard",
        "/api/metrics",
        "/api/metricas",
        "/api/summary",
        "/api/resumo"
    ]
    
    working_endpoints = []
    
    async with aiohttp.ClientSession() as session:
        for endpoint in common_endpoints:
            url = f"{base_url}{endpoint}"
            print(f"🔍 {endpoint.ljust(30)}", end=" ")
            
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"✅ 200 (JSON) - Chaves: {list(data.keys())[:3]}")
                            working_endpoints.append((endpoint, data))
                        except:
                            text = await response.text()
                            print(f"✅ 200 (TEXT) - {len(text)} chars")
                            working_endpoints.append((endpoint, text))
                    elif response.status == 401:
                        print("🔑 401 (Não autorizado)")
                    elif response.status == 403:
                        print("🚫 403 (Proibido)")
                    elif response.status == 404:
                        print("❌ 404 (Não encontrado)")
                    else:
                        print(f"⚠️ {response.status}")
                        
            except Exception as e:
                print(f"💥 Erro: {str(e)[:30]}")
    
    # Testar com POST também
    print("\n3. Testando endpoints com POST...")
    post_endpoints = [
        "/api/jogos/buscar",
        "/api/casino/buscar",
        "/api/historico/buscar",
        "/api/resultados/buscar",
        "/api/search",
        "/api/query"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in post_endpoints:
            url = f"{base_url}{endpoint}"
            print(f"POST {endpoint.ljust(25)}", end=" ")
            
            try:
                # Tentar diferentes payloads
                payloads = [
                    {},
                    {"game": "roulette"},
                    {"tipo": "roleta"},
                    {"categoria": "casino"},
                    {"limit": 10}
                ]
                
                for payload in payloads:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"✅ 200 (JSON) - Payload: {payload}")
                                working_endpoints.append((f"POST {endpoint}", data))
                                break
                            except:
                                text = await response.text()
                                print(f"✅ 200 (TEXT) - Payload: {payload}")
                                working_endpoints.append((f"POST {endpoint}", text))
                                break
                else:
                    print("❌ Nenhum payload funcionou")
                    
            except Exception as e:
                print(f"💥 Erro: {str(e)[:30]}")
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS:")
    print("=" * 60)
    
    if working_endpoints:
        print(f"✅ {len(working_endpoints)} endpoints funcionando:")
        
        for endpoint, data in working_endpoints:
            print(f"\n🔗 {endpoint}")
            if isinstance(data, dict):
                print(f"   Tipo: JSON")
                print(f"   Chaves: {list(data.keys())}")
                if 'results' in data or 'data' in data or 'items' in data:
                    print(f"   📋 Dados: {json.dumps(data, indent=2)[:300]}...")
            else:
                print(f"   Tipo: Text ({len(str(data))} chars)")
                print(f"   Amostra: {str(data)[:100]}...")
    else:
        print("❌ Nenhum endpoint adicional encontrado")
    
    # Sugestões baseadas no que encontramos
    print(f"\n💡 PRÓXIMOS PASSOS:")
    print("1. Verificar se há endpoints específicos do Pragmatic Play")
    print("2. Tentar acessar dados de sessão/atividade do usuário")
    print("3. Procurar por WebSockets ou Server-Sent Events")
    print("4. Verificar se há endpoints que requerem parâmetros específicos")

if __name__ == "__main__":
    asyncio.run(discover_endpoints())
