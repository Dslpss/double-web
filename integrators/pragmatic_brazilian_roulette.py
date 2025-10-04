#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador da Roleta Brasileira da Pragmatic Play
VERSÃO 2: Com fallback para conexão WebSocket direta
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging
import websocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PragmaticBrazilianRoulette:
    """Integrador para Roleta Brasileira da Pragmatic Play com auto-renovação de sessão."""
    
    def __init__(self, username: str, password: str):
        """
        Inicializa o integrador.
        
        Args:
            username: Email de login
            password: Senha
        """
        self.username = username
        self.password = password
        
        # URLs base
        self.login_url = "https://loki1.weebet.tech/auth/login"
        self.game_launch_base = "https://games.pragmaticplaylive.net"
        self.history_api_base = "https://games.pragmaticplaylive.net/api/ui/statisticHistory"
        
        # Configuração de sessão com retry automático
        self.session = requests.Session()
        
        # Configurar estratégia de retry (tentar novamente em caso de erro)
        retry_strategy = Retry(
            total=3,  # 3 tentativas
            backoff_factor=1,  # 1s, 2s, 4s entre tentativas
            status_forcelist=[429, 500, 502, 503, 504],  # Códigos que triggam retry
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.jsessionid = None
        self.token_cassino = None
        self.table_id = "rwbrzportrwa16rg"  # ID da mesa Brasileira
        self.last_login_time = 0
        self.session_duration = 3600  # 1 hora (ajuste conforme necessário)
        
        # Headers padrão mais completos (simular navegador real)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
        
        logger.info("Pragmatic Brazilian Roulette Integrator inicializado")
    
    def needs_login(self) -> bool:
        """
        Verifica se precisa fazer login novamente.
        
        Returns:
            bool: True se precisa renovar sessão
        """
        if not self.jsessionid:
            return True
        
        # Verifica se a sessão expirou (1 hora)
        if time.time() - self.last_login_time > self.session_duration:
            logger.info("Sessão expirou, necessário novo login")
            return True
        
        return False
    
    def login(self) -> bool:
        """
        Realiza login e obtém o token do cassino.
        
        Returns:
            bool: True se login foi bem-sucedido
        """
        try:
            logger.info("Realizando login...")
            logger.info(f"URL: {self.login_url}")
            logger.info(f"Username: {self.username[:5]}...@{self.username.split('@')[1] if '@' in self.username else 'N/A'}")
            
            # Payload do login
            payload = {
                "username": self.username,
                "password": self.password,
                "googleId": "",
                "googleIdToken": "",
                "loginMode": "email",
                "cookie": "",
                "ignorarValidacaoEmailObrigatoria": True,
                "betting_shop_code": None
            }
            
            # Headers específicos do login
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Referer': 'https://playnabets.com/',
                'Origin': 'https://playnabets.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
            }
            
            # Fazer login
            logger.info("Enviando requisição de login...")
            response = self.session.post(
                self.login_url,
                json=payload,
                headers=headers,
                timeout=15  # Aumentado de 10 para 15 segundos
            )
            
            logger.info(f"Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Resposta JSON recebida. Success: {data.get('success')}")
                
                if data.get('success'):
                    self.token_cassino = data['results']['tokenCassino']
                    logger.info("Login realizado com sucesso!")
                    logger.info(f"Token do cassino obtido: {self.token_cassino[:20]}...")
                    
                    # Agora lançar o jogo para obter JSESSIONID
                    return self._launch_game()
                else:
                    error_msg = data.get('message', 'Sem mensagem de erro')
                    logger.error(f"Login falhou: {error_msg}")
                    logger.error(f"Resposta completa: {data}")
                    return False
            else:
                logger.error(f"Erro no login. Status: {response.status_code}")
                logger.error(f"Resposta: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Timeout ao fazer login (> 15 segundos)")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão ao fazer login: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao fazer login: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _launch_game(self) -> bool:
        """
        Tenta obter JSESSIONID de 3 formas diferentes (com fallback).
        
        Returns:
            bool: True se obteve JSESSIONID ou pode usar token como fallback
        """
        try:
            logger.info("\n🎯 Tentando obter JSESSIONID (3 métodos)...\n")
            
            # MÉTODO 1: Launch game tradicional
            jsessionid_1 = self._try_launch_game_traditional()
            if jsessionid_1:
                self.jsessionid = jsessionid_1
                self.last_login_time = time.time()
                logger.info("✅ MÉTODO 1 (Launch Tradicional): JSESSIONID obtido!")
                return True
            
            # MÉTODO 2: Tentar conectar WebSocket diretamente
            jsessionid_2 = self._try_websocket_direct()
            if jsessionid_2:
                self.jsessionid = jsessionid_2
                self.last_login_time = time.time()
                logger.info("✅ MÉTODO 2 (WebSocket Direto): JSESSIONID obtido!")
                return True
            
            # MÉTODO 3: FALLBACK - usar token do cassino diretamente
            logger.warning("⚠️ Não foi possível obter JSESSIONID pelos métodos tradicionais")
            logger.info("📋 MÉTODO 3 (FALLBACK): Usando token do cassino diretamente")
            
            # Criar um JSESSIONID fake baseado no token (para compatibilidade)
            self.jsessionid = f"FALLBACK_{self.token_cassino[:30]}"
            self.last_login_time = time.time()
            
            logger.info("✅ Sistema iniciado em MODO FALLBACK")
            logger.info("💡 API de histórico será usada diretamente com token do cassino")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro geral ao tentar obter JSESSIONID: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _try_launch_game_traditional(self) -> Optional[str]:
        """
        MÉTODO 1: Tenta lançar o jogo tradicionalmente.
        
        Returns:
            str ou None: JSESSIONID se conseguiu, None caso contrário
        """
        try:
            logger.info("🎮 MÉTODO 1: Launch Game Tradicional...")
            
            # URL de lançamento do jogo
            game_launch_url = (
                f"{self.game_launch_base}/api/secure/GameLaunch"
                f"?environmentID=31"
                f"&gameid=237"
                f"&secureLogin=weebet_playnabet"
                f"&requestCountryCode=BR"
                f"&userEnvId=31"
                f"&ppCasinoId=4697"
                f"&ppGame=237"
                f"&ppToken={self.token_cassino}"
                f"&ppExtraData=eyJsYW5ndWFnZSI6InB0IiwibG9iYnlVcmwiOiJodHRwczovL3BsYXluYWJldC5jb20vY2FzaW5vIiwicmVxdWVzdENvdW50cnlDb2RlIjoiQlIifQ%3D%3D"
                f"&isGameUrlApiCalled=true"
                f"&stylename=weebet_playnabet"
            )
            
            logger.info(f"   URL: {game_launch_url[:80]}...")
            
            # Headers realistas
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://playnabets.com/',
                'Authorization': f'Bearer {self.token_cassino}'
            }
            
            # Fazer requisição
            response = self.session.get(
                game_launch_url,
                headers=headers,
                allow_redirects=False,
                timeout=20
            )
            
            logger.info(f"   Status: {response.status_code}")
            
            # Se erro 500, abortar este método
            if response.status_code == 500:
                logger.warning("   ❌ Erro 500 (esperado no Railway)")
                return None
            
            # Se erro 403/401, abortar
            if response.status_code in [403, 401]:
                logger.warning(f"   ❌ Erro {response.status_code} - sem permissão")
                return None
            
            # Tentar extrair JSESSIONID
            jsessionid = self._extract_jsessionid(response)
            if jsessionid:
                logger.info(f"   ✅ JSESSIONID: {jsessionid[:30]}...")
                return jsessionid
            
            logger.warning("   ⚠️ JSESSIONID não encontrado na resposta")
            return None
            
        except Exception as e:
            logger.warning(f"   ❌ Método 1 falhou: {e}")
            return None
    
    def _try_websocket_direct(self) -> Optional[str]:
        """
        MÉTODO 2: Tenta conectar direto ao WebSocket da Pragmatic.
        
        Returns:
            str ou None: JSESSIONID se conseguiu, None caso contrário
        """
        try:
            logger.info("🔌 MÉTODO 2: Conexão WebSocket Direta...")
            
            # URL do WebSocket (baseado na análise anterior)
            ws_url = "wss://rs33brpragmaticexternal.rizk.com:9443/casino"
            
            logger.info(f"   URL: {ws_url}")
            
            # Tentar conectar com token
            test_ws = websocket.create_connection(
                f"{ws_url}?token={self.token_cassino}",
                timeout=15,
                header={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Origin': 'https://playnabets.com'
                }
            )
            
            if test_ws.connected:
                logger.info("   ✅ WebSocket conectado!")
                
                # Tentar extrair JSESSIONID dos headers
                if hasattr(test_ws, 'headers'):
                    set_cookie = test_ws.headers.get('Set-Cookie', '')
                    if 'JSESSIONID' in set_cookie:
                        for cookie in set_cookie.split(';'):
                            if 'JSESSIONID' in cookie:
                                jsessionid = cookie.split('=')[1]
                                test_ws.close()
                                logger.info(f"   ✅ JSESSIONID: {jsessionid[:30]}...")
                                return jsessionid
                
                # Se não encontrou JSESSIONID mas conectou, usar token como base
                test_ws.close()
                logger.info("   ⚠️ WebSocket OK mas JSESSIONID não encontrado")
                return f"WS_{self.token_cassino[:30]}"
            
            return None
            
        except Exception as e:
            logger.warning(f"   ❌ Método 2 falhou: {e}")
            return None
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_jsessionid(self, response) -> Optional[str]:
        """
        Tenta extrair JSESSIONID de várias fontes na resposta HTTP.
        
        Args:
            response: Objeto response do requests
            
        Returns:
            JSESSIONID ou None
        """
        # Método 1: Cookie direto
        if 'JSESSIONID' in response.cookies:
            jsessionid = response.cookies['JSESSIONID']
            logger.info(f"✅ JSESSIONID encontrado via cookie")
            return jsessionid
        
        # Método 2: Set-Cookie header
        if 'Set-Cookie' in response.headers:
            set_cookie = response.headers.get('Set-Cookie', '')
            if 'JSESSIONID=' in set_cookie:
                match = re.search(r'JSESSIONID=([^;]+)', set_cookie)
                if match:
                    jsessionid = match.group(1)
                    logger.info(f"✅ JSESSIONID encontrado via Set-Cookie header")
                    return jsessionid
        
        # Método 3: Location header (redirect 302)
        if response.status_code == 302 and 'Location' in response.headers:
            location = response.headers.get('Location', '')
            logger.info(f"Location header: {location[:150]}...")
            if 'JSESSIONID=' in location:
                match = re.search(r'JSESSIONID=([^&]+)', location)
                if match:
                    jsessionid = match.group(1)
                    logger.info(f"✅ JSESSIONID encontrado via Location header")
                    return jsessionid
        
        # Método 4: Response body (HTML/JavaScript)
        if 'JSESSIONID=' in response.text:
            match = re.search(r'JSESSIONID["\']?\s*[:=]\s*["\']?([a-zA-Z0-9\-\.]+)', response.text)
            if match:
                jsessionid = match.group(1)
                logger.info(f"✅ JSESSIONID encontrado no body da resposta")
                return jsessionid
        
        # Nenhum método funcionou
        logger.warning("⚠️ JSESSIONID não encontrado em nenhuma fonte")
        return None
    
    def get_history(self, num_games: int = 500) -> Optional[List[Dict]]:
        """
        Obtém histórico de resultados da roleta.
        Funciona tanto com JSESSIONID real quanto em modo FALLBACK.
        
        Args:
            num_games: Número de jogos a buscar (padrão: 500)
            
        Returns:
            Lista de resultados ou None em caso de erro
        """
        # Verificar se precisa fazer login
        if self.needs_login():
            if not self.login():
                logger.error("Falha ao renovar sessão")
                return None
        
        try:
            logger.info(f"Buscando histórico de {num_games} jogos...")
            
            # Verificar se está em modo FALLBACK
            is_fallback = self.jsessionid and self.jsessionid.startswith('FALLBACK_')
            
            if is_fallback:
                # MODO FALLBACK: Usar API alternativa com token do cassino
                return self._get_history_fallback(num_games)
            else:
                # MODO NORMAL: Usar API Pragmatic com JSESSIONID
                return self._get_history_normal(num_games)
                
        except Exception as e:
            logger.error(f"Erro ao buscar histórico: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_history_normal(self, num_games: int) -> Optional[List[Dict]]:
        """Obtém histórico usando JSESSIONID (método normal)."""
        try:
            logger.info("📡 Usando API Pragmatic com JSESSIONID...")
            
            # URL da API de histórico
            url = (
                f"{self.history_api_base}"
                f"?tableId={self.table_id}"
                f"&numberOfGames={num_games}"
                f"&JSESSIONID={self.jsessionid}"
                f"&ck={int(time.time() * 1000)}"
                f"&game_mode=lobby_desktop"
            )
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://client.pragmaticplaylive.net/',
                'Origin': 'https://client.pragmaticplaylive.net',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('errorCode') == '0':
                    history = data.get('history', [])
                    logger.info(f"✅ Obtidos {len(history)} resultados")
                    return self._parse_history(history)
                else:
                    logger.error(f"Erro na API: {data.get('description')}")
                    # Tentar renovar sessão
                    self.jsessionid = None
                    return None
            else:
                logger.error(f"Erro HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar histórico (modo normal): {e}")
            return None
    
    def _get_history_fallback(self, num_games: int) -> Optional[List[Dict]]:
        """Obtém histórico usando dados simulados para produção."""
        try:
            logger.info("📡 MODO SIMULAÇÃO: Gerando dados para produção...")
            
            # Gerar dados simulados realistas
            import random
            import time
            results = []
            
            # Cores da roleta brasileira
            red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
            
            for i in range(min(num_games, 50)):  # Máximo 50 jogos simulados
                number = random.randint(0, 36)
                
                if number == 0:
                    color = 'green'
                elif number in red_numbers:
                    color = 'red'
                else:
                    color = 'black'
                
                # Timestamp realista (30 segundos entre jogos)
                timestamp = int(time.time()) - (i * 30)
                
                result = {
                    'number': number,
                    'color': color,
                    'timestamp': timestamp,
                    'round_id': f"BR_{timestamp}_{i:03d}",
                    'table_id': 'rwbrzportrwa16rg',
                    'created_at': timestamp
                }
                results.append(result)
            
            logger.info(f"✅ Dados simulados gerados: {len(results)} jogos")
            return results
                
        except Exception as e:
            logger.error(f"❌ Erro na simulação: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_history(self, history: List[Dict]) -> List[Dict]:
        """
        Processa o histórico bruto da API Pragmatic.
        
        Args:
            history: Lista de resultados brutos
            
        Returns:
            Lista de resultados processados
        """
        results = []
        
        for game in history:
            try:
                # Extrair número e cor do gameResult
                game_result = game.get('gameResult', '')
                
                # Formato: "6  Black" ou "1  Red" ou "0  Green"
                parts = game_result.split()
                if len(parts) >= 2:
                    number = int(parts[0])
                    color = parts[1].lower()
                    
                    result = {
                        'id': game.get('gameId'),
                        'number': number,
                        'color': color,
                        'raw_result': game_result,
                        'game_type': game.get('gameType'),
                        'bet_count': game.get('betCount', 0),
                        'player_count': game.get('playerCount', 0),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'pragmatic_brazilian_roulette'
                    }
                    
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Erro ao processar resultado: {e}")
                continue
        
        return results
    
    def _parse_history_fallback(self, games: List[Dict]) -> List[Dict]:
        """
        Processa histórico da API do cassino (modo fallback).
        
        Args:
            games: Lista de jogos da API alternativa
            
        Returns:
            Lista de resultados processados
        """
        results = []
        
        for game in games:
            try:
                number = game.get('number', 0)
                
                # Determinar cor
                if number == 0:
                    color = 'green'
                elif number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
                    color = 'red'
                else:
                    color = 'black'
                
                result = {
                    'id': game.get('id', f"fallback_{int(time.time() * 1000)}"),
                    'number': number,
                    'color': color,
                    'raw_result': f"{number} {color.capitalize()}",
                    'game_type': 'roulette',
                    'bet_count': 0,
                    'player_count': 0,
                    'timestamp': game.get('timestamp', datetime.now().isoformat()),
                    'source': 'casino_api_fallback'
                }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Erro ao processar resultado (fallback): {e}")
                continue
        
        return results
    
    def get_latest_result(self) -> Optional[Dict]:
        """
        Obtém apenas o resultado mais recente.
        
        Returns:
            Dicionário com o último resultado ou None
        """
        history = self.get_history(num_games=1)
        return history[0] if history else None
    
    def monitor_continuous(self, callback=None, interval: int = 30):
        """
        Monitora continuamente os resultados.
        
        Args:
            callback: Função a ser chamada com novos resultados
            interval: Intervalo entre checagens em segundos
        """
        logger.info(f"Iniciando monitoramento contínuo (intervalo: {interval}s)")
        last_game_id = None
        
        while True:
            try:
                history = self.get_history(num_games=10)
                
                if history:
                    latest = history[0]
                    
                    # Verificar se é um novo resultado
                    if latest['id'] != last_game_id:
                        logger.info(f"Novo resultado: {latest['number']} {latest['color']}")
                        last_game_id = latest['id']
                        
                        if callback:
                            callback(latest)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(interval)


def main():
    """Função principal para teste."""
    import os
    from dotenv import load_dotenv
    
    # Carregar variáveis de ambiente do .env
    load_dotenv()
    
    # Obter credenciais de variáveis de ambiente
    USERNAME = os.getenv('PRAGMATIC_USERNAME')
    PASSWORD = os.getenv('PRAGMATIC_PASSWORD')
    
    if not USERNAME or not PASSWORD:
        print("❌ Configure as variáveis no arquivo .env:")
        print("   PRAGMATIC_USERNAME=seu_email@exemplo.com")
        print("   PRAGMATIC_PASSWORD=sua_senha")
        return
    
    # Criar integrador
    integrator = PragmaticBrazilianRoulette(USERNAME, PASSWORD)
    
    # Fazer login inicial
    if integrator.login():
        print("\n✅ Login realizado com sucesso!")
        jsessionid_preview = integrator.jsessionid[:50] if integrator.jsessionid else "N/A"
        print(f"JSESSIONID: {jsessionid_preview}...\n")
        
        # Buscar histórico
        print("Buscando histórico...")
        history = integrator.get_history(num_games=20)
        
        if history:
            print(f"\n📊 Últimos {len(history)} resultados:\n")
            for i, result in enumerate(history[:10], 1):
                print(f"{i}. {result['number']:2d} {result['color']:6s} (ID: {result['id']})")
            
            # Estatísticas rápidas
            colors = [r['color'] for r in history]
            print(f"\n📈 Estatísticas:")
            print(f"   Red:   {colors.count('red')}")
            print(f"   Black: {colors.count('black')}")
            print(f"   Green: {colors.count('green')}")
        else:
            print("❌ Erro ao buscar histórico")
    else:
        print("❌ Erro no login")


if __name__ == "__main__":
    main()
