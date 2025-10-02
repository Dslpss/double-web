#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para integração da Roleta brasileira da PlayNabet
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class RouletteTester:
    """Testador para integração da Roleta brasileira."""
    
    def __init__(self):
        self.base_url = "https://central.playnabet.com"
        self.game_url = None
        self.session = None
        
        # Tokens da sua requisição
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
        self.token_usuario = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkwMjQ2NjQsImV4cCI6MTc1OTYyOTQ2NCwidXNlciI6eyJpZCI6NjMzMTR9fQ.BgvAuiW2_rUF8TUI9IdiV2swr3El7xN8qTrIgISN9AU"
        
    def get_headers(self):
        """Retorna headers para requisições."""
        return {
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
            'Authorization': f'Bearer {self.token_usuario}',
            'Te': 'trailers'
        }
    
    async def test_get_game_url(self):
        """Testa obtenção da URL do jogo."""
        print("🔍 Testando obtenção da URL do jogo...")
        
        try:
            url = f"{self.base_url}/casino/games/url"
            params = {
                'token': self.token,
                'tokenUsuario': self.token_usuario,
                'symbol': 'rla',  # Roleta brasileira
                'language': 'pt',
                'playMode': 'REAL',
                'cashierUr': 'https://playnabet.com/clientes/deposito',
                'lobbyUrl': 'https://playnabet.com/casino',
                'fornecedor': 'pragmatic',
                'isMobile': 'false',
                'plataforma': 'pc'
            }
            
            async with aiohttp.ClientSession(headers=self.get_headers()) as session:
                async with session.get(url, params=params) as response:
                    print(f"📡 Status: {response.status}")
                    print(f"📡 Headers: {dict(response.headers)}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Resposta JSON:")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                        
                        self.game_url = data.get('gameURL')
                        if self.game_url:
                            print(f"🎯 URL do jogo: {self.game_url}")
                            return True
                        else:
                            print("❌ URL do jogo não encontrada na resposta")
                            return False
                    else:
                        text = await response.text()
                        print(f"❌ Erro: {response.status}")
                        print(f"❌ Resposta: {text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Erro ao testar URL do jogo: {e}")
            return False
    
    async def test_game_access(self):
        """Testa acesso ao jogo."""
        if not self.game_url:
            print("❌ URL do jogo não disponível")
            return False
            
        print(f"🎮 Testando acesso ao jogo: {self.game_url}")
        
        try:
            # Headers específicos para o jogo
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
            
            async with aiohttp.ClientSession(headers=game_headers) as session:
                async with session.get(self.game_url) as response:
                    print(f"📡 Status: {response.status}")
                    print(f"📡 Headers: {dict(response.headers)}")
                    
                    if response.status == 200:
                        content = await response.text()
                        print(f"✅ Conteúdo recebido ({len(content)} caracteres)")
                        
                        # Procurar por dados JSON no conteúdo
                        if 'json' in response.headers.get('content-type', '').lower():
                            try:
                                data = await response.json()
                                print(f"📊 Dados JSON encontrados:")
                                print(json.dumps(data, indent=2, ensure_ascii=False))
                            except:
                                print("⚠️ Resposta não é JSON válido")
                        
                        # Salvar conteúdo para análise
                        with open('game_response.html', 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("💾 Conteúdo salvo em 'game_response.html'")
                        
                        return True
                    else:
                        text = await response.text()
                        print(f"❌ Erro: {response.status}")
                        print(f"❌ Resposta: {text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Erro ao testar acesso ao jogo: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Testa conexão WebSocket se disponível."""
        print("🔌 Testando conexão WebSocket...")
        
        # URLs WebSocket comuns para jogos de roleta
        ws_urls = [
            "wss://qcxjeqo01e.cjlcqchead.net/gs2c/",
            "wss://qcxjeqo01e.cjlcqchead.net/gs2c/playGame.do",
            "wss://qcxjeqo01e.cjlcqchead.net/gs2c/roulette"
        ]
        
        for ws_url in ws_urls:
            try:
                print(f"🔌 Tentando conectar em: {ws_url}")
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(ws_url) as ws:
                        print(f"✅ Conectado em: {ws_url}")
                        
                        # Aguardar algumas mensagens
                        for i in range(5):
                            try:
                                msg = await asyncio.wait_for(ws.receive(), timeout=5)
                                print(f"📨 Mensagem {i+1}: {msg}")
                            except asyncio.TimeoutError:
                                print(f"⏰ Timeout na mensagem {i+1}")
                                break
                        
                        return True
                        
            except Exception as e:
                print(f"❌ Erro ao conectar em {ws_url}: {e}")
                continue
        
        print("❌ Nenhuma conexão WebSocket funcionou")
        return False
    
    def analyze_captured_data(self, request_data, response_data):
        """Analisa dados capturados no Burp."""
        print("🔍 Analisando dados capturados...")
        
        print("\n📤 REQUISIÇÃO:")
        print(f"URL: {request_data.get('url', 'N/A')}")
        print(f"Method: {request_data.get('method', 'N/A')}")
        print(f"Headers: {json.dumps(request_data.get('headers', {}), indent=2)}")
        print(f"Body: {request_data.get('body', 'N/A')}")
        
        print("\n📥 RESPOSTA:")
        print(f"Status: {response_data.get('status', 'N/A')}")
        print(f"Headers: {json.dumps(response_data.get('headers', {}), indent=2)}")
        print(f"Body: {response_data.get('body', 'N/A')}")
        
        # Procurar por padrões de dados da roleta
        body = response_data.get('body', '')
        if isinstance(body, str):
            # Procurar por números de roleta (0-36)
            import re
            numbers = re.findall(r'\b([0-3]?[0-6])\b', body)
            if numbers:
                print(f"🎲 Números encontrados: {numbers}")
            
            # Procurar por cores
            colors = re.findall(r'\b(red|black|green|vermelho|preto|verde)\b', body, re.IGNORECASE)
            if colors:
                print(f"🎨 Cores encontradas: {colors}")
            
            # Procurar por JSON
            json_matches = re.findall(r'\{[^{}]*\}', body)
            if json_matches:
                print(f"📊 Possíveis JSONs encontrados: {len(json_matches)}")
                for i, json_str in enumerate(json_matches[:3]):  # Mostrar apenas os 3 primeiros
                    try:
                        parsed = json.loads(json_str)
                        print(f"  JSON {i+1}: {json.dumps(parsed, indent=2)}")
                    except:
                        print(f"  JSON {i+1} (inválido): {json_str[:100]}...")
    
    async def run_full_test(self):
        """Executa teste completo."""
        print("🚀 Iniciando teste completo da integração da Roleta...")
        print("=" * 60)
        
        # Teste 1: Obter URL do jogo
        print("\n1️⃣ Testando obtenção da URL do jogo...")
        url_success = await self.test_get_game_url()
        
        if url_success:
            # Teste 2: Acessar o jogo
            print("\n2️⃣ Testando acesso ao jogo...")
            game_success = await self.test_game_access()
            
            if game_success:
                # Teste 3: Tentar WebSocket
                print("\n3️⃣ Testando conexão WebSocket...")
                await self.test_websocket_connection()
        
        print("\n" + "=" * 60)
        print("✅ Teste completo finalizado!")
        
        return url_success

async def main():
    """Função principal."""
    tester = RouletteTester()
    
    print("🎯 Testador de Integração da Roleta Brasileira")
    print("=" * 50)
    
    # Executar teste automático
    await tester.run_full_test()
    
    print("\n" + "=" * 50)
    print("📝 Próximos passos:")
    print("1. Envie dados capturados no Burp para análise")
    print("2. Verifique o arquivo 'game_response.html' gerado")
    print("3. Teste com dados reais da roleta")

if __name__ == "__main__":
    asyncio.run(main())
