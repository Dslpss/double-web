#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste avançado da integração da Roleta brasileira com contorno de SSL
"""

import requests
import json
import ssl
import urllib3
import urllib.parse
from datetime import datetime

# Desabilitar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_roulette_advanced():
    """Teste avançado com contorno de SSL."""
    
    print("🎯 Teste Avançado - Roleta Brasileira PlayNabet")
    print("=" * 60)
    
    # Configurações
    base_url = "https://central.playnabet.com"
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
    token_usuario = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkwMjQ2NjQsImV4cCI6MTc1OTYyOTQ2NCwidXNlciI6eyJpZCI6NjMzMTR9fQ.BgvAuiW2_rUF8TUI9IdiV2swr3El7xN8qTrIgISN9AU"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://playnabets.com/',
        'Content-Type': 'application/json',
        'Origin': 'https://playnabets.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Authorization': f'Bearer {token_usuario}',
        'Te': 'trailers'
    }
    
    params = {
        'token': token,
        'tokenUsuario': token_usuario,
        'symbol': 'rla',
        'language': 'pt',
        'playMode': 'REAL',
        'cashierUr': 'https://playnabet.com/clientes/deposito',
        'lobbyUrl': 'https://playnabet.com/casino',
        'fornecedor': 'pragmatic',
        'isMobile': 'false',
        'plataforma': 'pc'
    }
    
    try:
        print("📡 1. Obtendo URL do jogo...")
        response = requests.get(f"{base_url}/casino/games/url", params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            game_url = data.get('gameURL')
            print(f"✅ URL obtida: {game_url}")
            
            # Decodificar URL para análise
            from urllib.parse import unquote, parse_qs
            decoded_url = unquote(game_url)
            print(f"🔍 URL decodificada: {decoded_url}")
            
            # Extrair parâmetros da URL
            parsed_url = urllib.parse.urlparse(game_url)
            query_params = parse_qs(parsed_url.query)
            print(f"📊 Parâmetros da URL: {json.dumps(query_params, indent=2)}")
            
            # Testar diferentes abordagens para acessar o jogo
            print("\n🎮 2. Testando acesso ao jogo...")
            
            # Abordagem 1: Sem verificação SSL
            print("   🔧 Tentativa 1: Sem verificação SSL...")
            try:
                game_response = requests.get(game_url, verify=False, timeout=15)
                print(f"   📊 Status: {game_response.status_code}")
                print(f"   📊 Content-Type: {game_response.headers.get('content-type', 'N/A')}")
                
                if game_response.status_code == 200:
                    content = game_response.text
                    print(f"   ✅ Conteúdo recebido: {len(content)} caracteres")
                    
                    # Salvar conteúdo
                    with open('roulette_game_advanced.html', 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("   💾 Conteúdo salvo em 'roulette_game_advanced.html'")
                    
                    # Analisar conteúdo
                    analyze_game_content(content)
                    
                else:
                    print(f"   ❌ Erro: {game_response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Erro SSL: {e}")
            
            # Abordagem 2: Com headers específicos
            print("\n   🔧 Tentativa 2: Com headers específicos...")
            try:
                game_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://playnabets.com/',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'cross-site',
                    'Sec-Fetch-User': '?1'
                }
                
                game_response = requests.get(game_url, headers=game_headers, verify=False, timeout=15)
                print(f"   📊 Status: {game_response.status_code}")
                
                if game_response.status_code == 200:
                    content = game_response.text
                    print(f"   ✅ Conteúdo recebido: {len(content)} caracteres")
                    analyze_game_content(content)
                else:
                    print(f"   ❌ Erro: {game_response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Abordagem 3: Testar endpoints alternativos
            print("\n   🔧 Tentativa 3: Testando endpoints alternativos...")
            base_game_url = "https://qcxjeqo01e.cjlcqchead.net/gs2c/"
            
            endpoints = [
                "playGame.do",
                "roulette",
                "game",
                "api/game",
                "api/roulette"
            ]
            
            for endpoint in endpoints:
                try:
                    test_url = f"{base_game_url}{endpoint}"
                    print(f"   🔍 Testando: {test_url}")
                    
                    test_response = requests.get(test_url, verify=False, timeout=10)
                    print(f"   📊 Status: {test_response.status_code}")
                    
                    if test_response.status_code == 200:
                        print(f"   ✅ Endpoint funcionando: {endpoint}")
                        content = test_response.text
                        if len(content) > 100:
                            print(f"   📄 Conteúdo: {content[:200]}...")
                    
                except Exception as e:
                    print(f"   ❌ Erro em {endpoint}: {e}")
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def analyze_game_content(content):
    """Analisa o conteúdo do jogo em busca de dados da roleta."""
    print("\n🔍 Análise do conteúdo do jogo:")
    print("=" * 40)
    
    # Procurar por padrões de roleta
    import re
    
    # Números de roleta (0-36)
    numbers = re.findall(r'\b([0-3]?[0-6])\b', content)
    if numbers:
        print(f"🎲 Números encontrados: {numbers}")
    
    # Cores
    colors = re.findall(r'\b(red|black|green|vermelho|preto|verde)\b', content, re.IGNORECASE)
    if colors:
        print(f"🎨 Cores encontradas: {colors}")
    
    # JSONs
    json_matches = re.findall(r'\{[^{}]*\}', content)
    if json_matches:
        print(f"📊 {len(json_matches)} possíveis JSONs encontrados")
        for i, json_str in enumerate(json_matches[:5]):
            try:
                parsed = json.loads(json_str)
                print(f"  JSON {i+1}: {json.dumps(parsed, indent=2)}")
            except:
                print(f"  JSON {i+1}: {json_str[:100]}...")
    
    # WebSocket URLs
    ws_matches = re.findall(r'wss?://[^\s"\'<>]+', content)
    if ws_matches:
        print(f"🔌 WebSocket URLs encontradas: {ws_matches}")
    
    # API endpoints
    api_matches = re.findall(r'https?://[^\s"\'<>]+/api/[^\s"\'<>]+', content)
    if api_matches:
        print(f"🌐 API endpoints encontrados: {api_matches}")
    
    # Procurar por dados de jogo específicos
    game_data_patterns = [
        r'gameData\s*[:=]\s*\{[^}]*\}',
        r'rouletteData\s*[:=]\s*\{[^}]*\}',
        r'result\s*[:=]\s*\{[^}]*\}',
        r'lastResult\s*[:=]\s*\{[^}]*\}'
    ]
    
    for pattern in game_data_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"🎮 Dados de jogo encontrados: {matches}")

if __name__ == "__main__":
    test_roulette_advanced()
