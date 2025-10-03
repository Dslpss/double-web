#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador da Roleta Brasileira da Pragmatic Play
Com renovação automática de JSESSIONID
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
        Lança o jogo para obter JSESSIONID com múltiplas estratégias e retry.
        
        Returns:
            bool: True se obteve JSESSIONID
        """
        try:
            logger.info("Lançando jogo para obter JSESSIONID...")
            
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
            
            logger.info(f"URL do jogo: {game_launch_url[:100]}...")
            
            # Tentar múltiplas estratégias
            strategies = [
                {
                    "name": "Redirect OFF + Timeout 20s",
                    "allow_redirects": False,
                    "timeout": 20,
                    "headers": {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Referer': 'https://playnabets.com/',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'cross-site',
                        'Sec-Fetch-User': '?1'
                    }
                },
                {
                    "name": "Redirect ON + Timeout 25s",
                    "allow_redirects": True,
                    "timeout": 25,
                    "headers": {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Referer': 'https://playnabets.com/',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    }
                },
                {
                    "name": "Redirect OFF + Timeout 30s + Authorization",
                    "allow_redirects": False,
                    "timeout": 30,
                    "headers": {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Referer': 'https://playnabets.com/',
                        'Authorization': f'Bearer {self.token_cassino}',
                        'Sec-Fetch-Dest': 'iframe',
                        'Sec-Fetch-Mode': 'navigate'
                    }
                }
            ]
            
            for attempt, strategy in enumerate(strategies, 1):
                try:
                    logger.info(f"🔄 Tentativa {attempt}/{len(strategies)}: {strategy['name']}")
                    
                    # Delay entre tentativas (exceto primeira)
                    if attempt > 1:
                        wait_time = 2 ** (attempt - 1)  # 2s, 4s
                        logger.info(f"⏳ Aguardando {wait_time}s...")
                        time.sleep(wait_time)
                    
                    # Fazer requisição
                    response = self.session.get(
                        game_launch_url,
                        headers=strategy['headers'],
                        allow_redirects=strategy['allow_redirects'],
                        timeout=strategy['timeout']
                    )
                    
                    logger.info(f"📡 Status: {response.status_code}")
                    
                    # Tentar extrair JSESSIONID de várias formas
                    jsessionid = self._extract_jsessionid(response)
                    
                    if jsessionid:
                        self.jsessionid = jsessionid
                        self.last_login_time = time.time()
                        logger.info(f"✅ JSESSIONID obtido com sucesso: {jsessionid[:30]}...")
                        return True
                    
                    # Log de erro específico
                    if response.status_code == 500:
                        logger.error("❌ API retornou 500 - possível bloqueio de IP ou região")
                        logger.error(f"Resposta: {response.text[:300]}")
                    elif response.status_code == 403:
                        logger.error("❌ API retornou 403 - acesso negado")
                        break  # Não adianta tentar novamente
                    elif response.status_code == 401:
                        logger.error("❌ API retornou 401 - token inválido")
                        break  # Token problem
                    else:
                        logger.warning(f"⚠️ Status {response.status_code} mas JSESSIONID não encontrado")
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"⏱️ Timeout na tentativa {attempt}/{len(strategies)}")
                except requests.exceptions.ConnectionError as e:
                    logger.warning(f"🔌 Erro de conexão: {e}")
                except Exception as e:
                    logger.error(f"❌ Erro na tentativa {attempt}: {e}")
            
            # Se chegou aqui, todas as tentativas falharam
            logger.error("❌ Todas as tentativas de obter JSESSIONID falharam")
            logger.warning("💡 Possíveis causas:")
            logger.warning("   1. IP do Railway bloqueado pela Pragmatic Play")
            logger.warning("   2. Rate limiting ativado")
            logger.warning("   3. Região geográfica não permitida")
            logger.warning("   4. API da Pragmatic temporariamente indisponível")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro geral ao lançar jogo: {e}")
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
        Renova sessão automaticamente se necessário.
        
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
                    logger.info(f"Obtidos {len(history)} resultados")
                    return self._parse_history(history)
                else:
                    logger.error(f"Erro na API: {data.get('description')}")
                    # Tentar renovar sessão e tentar novamente
                    self.jsessionid = None
                    return self.get_history(num_games)
            else:
                logger.error(f"Erro HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar histórico: {e}")
            return None
    
    def _parse_history(self, history: List[Dict]) -> List[Dict]:
        """
        Processa o histórico bruto da API.
        
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
        print(f"JSESSIONID: {integrator.jsessionid[:50]}...\n")
        
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
