#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analisador do JavaScript da Roleta Brasileira
Procura por APIs, WebSockets e endpoints nos arquivos JS
"""

import asyncio
import aiohttp
import re
import json
from urllib.parse import urljoin, urlparse

async def analyze_roulette_javascript():
    """Analisa os arquivos JavaScript da roleta para encontrar APIs."""
    print("🔍 ANALISANDO JAVASCRIPT DA ROLETA BRASILEIRA")
    print("=" * 60)
    
    base_url = "https://qcxjeqo01e.cjlcqchead.net"
    
    # URLs dos arquivos JavaScript encontrados no HTML
    js_files = [
        "/desktop/classic-roulette2/polyfills-6B4J2F6V.js",
        "/desktop/classic-roulette2/scripts-UXZT3BKZ.js", 
        "/desktop/classic-roulette2/main-QIEGLKFM.js",
        "/desktop/classic-roulette2/chunk-GZTYKGLE.js",
        "/desktop/classic-roulette2/chunk-OZD2G75A.js",
        "/desktop/classic-roulette2/chunk-GHA2AOC5.js",
        "/desktop/classic-roulette2/chunk-N6ICA46G.js",
        "/desktop/classic-roulette2/chunk-VXC2346K.js",
        "/desktop/classic-roulette2/chunk-AD2LIJAI.js",
        "/desktop/classic-roulette2/chunk-T5WGVR76.js",
        "/desktop/classic-roulette2/chunk-22IGHFZA.js",
        "/desktop/classic-roulette2/chunk-BAIMLRXU.js",
        "/desktop/classic-roulette2/chunk-V43HXODZ.js"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://qcxjeqo01e.cjlcqchead.net/gs2c/playGame.do'
    }
    
    # Padrões para procurar APIs e WebSockets
    api_patterns = [
        # WebSocket URLs
        r'(wss?://[^"\'\s]+)',
        r'new\s+WebSocket\s*\(\s*["\']([^"\']+)',
        r'websocket["\']?\s*:\s*["\']([^"\']+)',
        
        # API endpoints
        r'["\']([^"\']*api[^"\']*)["\']',
        r'["\']([^"\']*history[^"\']*)["\']',
        r'["\']([^"\']*results[^"\']*)["\']',
        r'["\']([^"\']*roulette[^"\']*)["\']',
        r'["\']([^"\']*game[^"\']*)["\']',
        
        # HTTP requests
        r'\.get\s*\(\s*["\']([^"\']+)',
        r'\.post\s*\(\s*["\']([^"\']+)',
        r'fetch\s*\(\s*["\']([^"\']+)',
        r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\'],\s*["\']([^"\']+)',
        
        # URLs em geral
        r'url["\']?\s*:\s*["\']([^"\']+)',
        r'endpoint["\']?\s*:\s*["\']([^"\']+)',
        r'baseUrl["\']?\s*:\s*["\']([^"\']+)',
        
        # Pragmatic Play específico
        r'pragmatic[^"\']*["\']([^"\']+)',
        r'pp[A-Z][^"\']*["\']([^"\']+)',
    ]
    
    found_urls = set()
    found_websockets = set()
    found_apis = set()
    
    async with aiohttp.ClientSession() as session:
        for js_file in js_files:
            url = urljoin(base_url, js_file)
            print(f"\n📄 Analisando: {js_file}")
            
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        print(f"   ✅ Carregado ({len(content)} chars)")
                        
                        # Procurar por padrões
                        for pattern in api_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if match.startswith(('http', 'ws')):
                                    if 'websocket' in match.lower() or match.startswith('ws'):
                                        found_websockets.add(match)
                                    else:
                                        found_urls.add(match)
                                elif 'api' in match.lower() or 'history' in match.lower() or 'result' in match.lower():
                                    found_apis.add(match)
                        
                        # Procurar por configurações específicas
                        config_patterns = [
                            r'config\s*:\s*\{([^}]+)\}',
                            r'settings\s*:\s*\{([^}]+)\}',
                            r'endpoints\s*:\s*\{([^}]+)\}',
                            r'urls\s*:\s*\{([^}]+)\}'
                        ]
                        
                        for pattern in config_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                            for match in matches:
                                print(f"   📋 Config encontrado: {match[:200]}...")
                        
                        # Procurar por strings que podem ser endpoints
                        endpoint_strings = re.findall(r'["\']\/[a-zA-Z0-9\/\-_]+["\']', content)
                        for endpoint in endpoint_strings:
                            clean_endpoint = endpoint.strip('"\'')
                            if any(keyword in clean_endpoint.lower() for keyword in ['api', 'ws', 'socket', 'history', 'result', 'game', 'roulette']):
                                found_apis.add(clean_endpoint)
                    
                    else:
                        print(f"   ❌ Erro: {response.status}")
                        
            except Exception as e:
                print(f"   💥 Erro: {e}")
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DA ANÁLISE:")
    print("=" * 60)
    
    if found_websockets:
        print(f"\n🔌 WebSockets encontrados ({len(found_websockets)}):")
        for ws in sorted(found_websockets):
            print(f"   {ws}")
    
    if found_urls:
        print(f"\n🌐 URLs encontradas ({len(found_urls)}):")
        for url in sorted(found_urls):
            print(f"   {url}")
    
    if found_apis:
        print(f"\n📡 Possíveis APIs/Endpoints ({len(found_apis)}):")
        for api in sorted(found_apis):
            print(f"   {api}")
    
    # Testar endpoints encontrados
    if found_apis:
        print(f"\n🧪 TESTANDO ENDPOINTS ENCONTRADOS:")
        print("-" * 40)
        
        test_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://qcxjeqo01e.cjlcqchead.net/gs2c/playGame.do',
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso'
        }
        
        async with aiohttp.ClientSession() as session:
            for api in sorted(found_apis)[:10]:  # Testar apenas os primeiros 10
                if api.startswith('/'):
                    test_url = urljoin(base_url, api)
                    print(f"\n🔍 Testando: {api}")
                    
                    try:
                        # Testar GET
                        async with session.get(test_url, headers=test_headers) as response:
                            print(f"   GET {response.status}")
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    print(f"   ✅ JSON: {json.dumps(data, indent=2)[:200]}...")
                                except:
                                    text = await response.text()
                                    if text and not text.startswith('<!DOCTYPE'):
                                        print(f"   ✅ Text: {text[:200]}...")
                        
                        # Testar POST se GET não funcionou
                        if response.status != 200:
                            async with session.post(test_url, headers=test_headers, json={}) as post_response:
                                print(f"   POST {post_response.status}")
                                if post_response.status == 200:
                                    try:
                                        data = await post_response.json()
                                        print(f"   ✅ POST JSON: {json.dumps(data, indent=2)[:200]}...")
                                    except:
                                        text = await post_response.text()
                                        if text and not text.startswith('<!DOCTYPE'):
                                            print(f"   ✅ POST Text: {text[:200]}...")
                                            
                    except Exception as e:
                        print(f"   💥 Erro: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_roulette_javascript())
