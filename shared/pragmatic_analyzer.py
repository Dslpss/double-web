#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analisador Pragmatic Play com Playwright
Solução robusta para contornar bloqueios e conectar WebSocket no Railway
"""

import asyncio
import json
import logging
import os
import re
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable
from urllib.parse import urlparse, parse_qs
import websocket
from websocket import WebSocketConnectionClosedException, WebSocketTimeoutException
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Playwright imports
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright não disponível. Instale com: pip install playwright && playwright install chromium")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PragmaticAnalyzer:
    """Analisador Pragmatic Play com Playwright e WebSocket robusto."""
    
    def __init__(self, username: str, password: str, callback: Optional[Callable] = None):
        """
        Inicializa o analisador.
        
        Args:
            username: Email de login na Playnabets
            password: Senha
            callback: Função para receber resultados (opcional)
        """
        self.username = username
        self.password = password
        self.callback = callback
        
        # URLs
        self.playnabets_login = "https://playnabets.com/login"
        self.game_launch_url = "https://pragmaticplaylive.net/api/secure/GameLaunch"
        self.websocket_base = "wss://ws1.pragmaticplaylive.net/A16R-Generic"
        
        # Estado da conexão
        self.jsessionid = None
        self.token = None
        self.table_id = "rwbrzportrwa16rg"
        self.socket_server = None
        self.websocket = None
        self.is_connected = False
        self.is_monitoring = False
        self.last_result_time = 0
        
        # Playwright
        self.browser = None
        self.context = None
        self.page = None
        
        # Threading
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
        # Reconexão
        self.reconnect_interval = 30  # 30 minutos
        self.last_reconnect = 0
        self.max_reconnect_attempts = 5
        self.reconnect_attempts = 0
        
        # Headers para WebSocket
        self.ws_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Origin': 'https://client.pragmaticplaylive.net',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Sec-WebSocket-Version': '13',
        }
        
        logger.info("PragmaticAnalyzer inicializado")
    
    async def initialize_playwright(self) -> bool:
        """Inicializa Playwright."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright não está disponível")
            return False
        
        try:
            logger.info("Inicializando Playwright...")
            self.playwright = await async_playwright().start()
            
            # Configurações para Railway (headless obrigatório)
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Contexto com configurações para evitar detecção
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='pt-BR',
                timezone_id='America/Sao_Paulo'
            )
            
            self.page = await self.context.new_page()
            
            # Interceptar requisições para capturar tokens
            await self.page.route("**/*", self._handle_request)
            
            logger.info("✅ Playwright inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Playwright: {e}")
            return False
    
    async def _handle_request(self, route):
        """Intercepta requisições para capturar tokens."""
        try:
            request = route.request
            url = request.url
            
            # Capturar resposta do GameLaunch
            if "GameLaunch" in url:
                response = await route.fetch()
                await route.fulfill(response=response)
                
                # Extrair JSESSIONID do header Location
                location_header = response.headers.get('location', '')
                if location_header:
                    await self._extract_session_data(location_header)
            else:
                await route.continue_()
                
        except Exception as e:
            logger.error(f"Erro ao interceptar requisição: {e}")
            await route.continue_()
    
    async def _extract_session_data(self, location_url: str):
        """Extrai dados da sessão da URL de redirecionamento."""
        try:
            logger.info(f"Extraindo dados da URL: {location_url[:100]}...")
            
            # Parse da URL
            parsed = urlparse(location_url)
            query_params = parse_qs(parsed.query)
            
            # Extrair JSESSIONID
            jsessionid = query_params.get('JSESSIONID', [None])[0]
            if jsessionid:
                self.jsessionid = jsessionid
                logger.info(f"✅ JSESSIONID extraído: {jsessionid[:20]}...")
            
            # Extrair token
            token = query_params.get('token', [None])[0]
            if token:
                self.token = token
                logger.info(f"✅ Token extraído: {token[:20]}...")
            
            # Extrair table_id
            table_id = query_params.get('table_id', [None])[0]
            if table_id:
                self.table_id = table_id
                logger.info(f"✅ Table ID extraído: {table_id}")
            
            # Extrair socket_server
            socket_server = query_params.get('socket_server', [None])[0]
            if socket_server:
                self.socket_server = socket_server
                logger.info(f"✅ Socket server extraído: {socket_server}")
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da sessão: {e}")
    
    async def login_and_get_session(self) -> bool:
        """Faz login e obtém dados da sessão."""
        if not self.page:
            logger.error("Playwright não inicializado")
            return False
        
        try:
            logger.info("🔐 Fazendo login na Playnabets...")
            
            # Navegar para página de login
            await self.page.goto(self.playnabets_login, wait_until='networkidle')
            
            # Preencher credenciais
            await self.page.fill('input[name="username"], input[type="email"]', self.username)
            await self.page.fill('input[name="password"], input[type="password"]', self.password)
            
            # Clicar no botão de login
            await self.page.click('button[type="submit"], .login-button, #login-button')
            
            # Aguardar redirecionamento
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Verificar se login foi bem-sucedido
            current_url = self.page.url
            if "login" in current_url.lower():
                logger.error("❌ Login falhou - ainda na página de login")
                return False
            
            logger.info("✅ Login realizado com sucesso")
            
            # Agora tentar acessar o jogo para obter JSESSIONID
            return await self._launch_game()
            
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            return False
    
    async def _launch_game(self) -> bool:
        """Lança o jogo para obter JSESSIONID."""
        try:
            logger.info("🎰 Lançando jogo da Roleta Brasileira...")
            
            # Construir URL do GameLaunch
            game_url = f"{self.game_launch_url}?ppToken={self.token}&game=237&table_id={self.table_id}"
            
            # Navegar para o GameLaunch
            await self.page.goto(game_url, wait_until='networkidle')
            
            # Aguardar um pouco para capturar dados
            await asyncio.sleep(2)
            
            # Verificar se obtivemos os dados necessários
            if self.jsessionid and self.token:
                logger.info("✅ Dados da sessão obtidos com sucesso!")
                return True
            else:
                logger.warning("⚠️ Não foi possível obter todos os dados da sessão")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao lançar jogo: {e}")
            return False
    
    def connect_websocket(self) -> bool:
        """Conecta ao WebSocket da Pragmatic Play."""
        if not self.jsessionid or not self.token:
            logger.error("❌ JSESSIONID ou Token não disponíveis")
            return False
        
        try:
            # Construir URL do WebSocket
            ws_url = f"{self.websocket_base}?JSESSIONID={self.jsessionid}&token={self.token}&table_id={self.table_id}"
            
            logger.info(f"🔌 Conectando ao WebSocket: {ws_url[:100]}...")
            
            # Configurar cookies
            cookies = f"JSESSIONID={self.jsessionid}; token={self.token}"
            self.ws_headers['Cookie'] = cookies
            
            # Conectar WebSocket
            self.websocket = websocket.WebSocket()
            self.websocket.connect(
                ws_url,
                header=self.ws_headers,
                timeout=10
            )
            
            self.is_connected = True
            self.reconnect_attempts = 0
            logger.info("✅ WebSocket conectado com sucesso!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar WebSocket: {e}")
            self.is_connected = False
            return False
    
    def start_monitoring(self) -> bool:
        """Inicia monitoramento em thread separada."""
        if self.is_monitoring:
            logger.warning("⚠️ Monitoramento já está ativo")
            return True
        
        if not self.is_connected:
            logger.error("❌ WebSocket não está conectado")
            return False
        
        try:
            self.is_monitoring = True
            self.stop_event.clear()
            
            # Iniciar thread de monitoramento
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("✅ Monitoramento iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar monitoramento: {e}")
            self.is_monitoring = False
            return False
    
    def _monitor_loop(self):
        """Loop principal de monitoramento."""
        logger.info("🔄 Iniciando loop de monitoramento...")
        
        while self.is_monitoring and not self.stop_event.is_set():
            try:
                # Verificar se precisa reconectar
                if self._should_reconnect():
                    if not self._reconnect():
                        logger.error("❌ Falha na reconexão, parando monitoramento")
                        break
                
                # Ler mensagem do WebSocket
                if self.websocket and self.is_connected:
                    try:
                        message = self.websocket.recv()
                        self._process_message(message)
                    except WebSocketTimeoutException:
                        # Timeout é normal, continuar
                        continue
                    except WebSocketConnectionClosedException:
                        logger.warning("⚠️ WebSocket desconectado")
                        self.is_connected = False
                        continue
                    except Exception as e:
                        logger.error(f"❌ Erro ao ler WebSocket: {e}")
                        self.is_connected = False
                        continue
                
                # Aguardar um pouco
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(1)
        
        logger.info("🛑 Loop de monitoramento finalizado")
    
    def _should_reconnect(self) -> bool:
        """Verifica se precisa reconectar."""
        if not self.is_connected:
            return True
        
        # Reconectar a cada 30 minutos
        if time.time() - self.last_reconnect > self.reconnect_interval * 60:
            return True
        
        return False
    
    def _reconnect(self) -> bool:
        """Reconecta WebSocket."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("❌ Máximo de tentativas de reconexão atingido")
            return False
        
        self.reconnect_attempts += 1
        logger.info(f"🔄 Tentativa de reconexão {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        try:
            # Fechar conexão atual
            if self.websocket:
                self.websocket.close()
            
            # Reconectar
            success = self.connect_websocket()
            if success:
                self.last_reconnect = time.time()
                self.reconnect_attempts = 0
                logger.info("✅ Reconexão bem-sucedida!")
                return True
            else:
                logger.warning(f"⚠️ Reconexão falhou, tentando novamente em 30s...")
                time.sleep(30)
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na reconexão: {e}")
            time.sleep(30)
            return False
    
    def _process_message(self, message: str):
        """Processa mensagem do WebSocket."""
        try:
            # Tentar parsear como JSON
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                # Se não for JSON, pode ser uma string simples
                logger.debug(f"Mensagem não-JSON recebida: {message[:100]}...")
                return
            
            # Verificar tipo de evento
            event_type = data.get('event', '')
            
            if event_type in ['spin_result', 'ball_land', 'game_result']:
                self._handle_game_result(data)
            elif event_type == 'ping':
                # Responder ping com pong
                self._send_pong()
            else:
                logger.debug(f"Evento não processado: {event_type}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
    
    def _handle_game_result(self, data: Dict):
        """Processa resultado do jogo."""
        try:
            # Extrair dados do resultado
            number = data.get('number', data.get('result', 0))
            color = data.get('color', '')
            multiplier = data.get('multiplier', 1.0)
            timestamp = data.get('time', data.get('timestamp', int(time.time())))
            
            # Determinar cor se não fornecida
            if not color and number is not None:
                color = self._get_color_from_number(number)
            
            # Criar resultado padronizado
            result = {
                'number': number,
                'color': color,
                'multiplier': multiplier,
                'timestamp': timestamp,
                'time': datetime.now().isoformat(),
                'source': 'pragmatic_play'
            }
            
            logger.info(f"🎲 Resultado: {number} ({color}) - Multiplicador: {multiplier}")
            
            # Chamar callback se disponível
            if self.callback:
                try:
                    self.callback(result)
                except Exception as e:
                    logger.error(f"❌ Erro no callback: {e}")
            
            self.last_result_time = time.time()
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado: {e}")
    
    def _get_color_from_number(self, number: int) -> str:
        """Determina cor baseada no número."""
        if number == 0:
            return 'green'
        elif number in [1, 3, 5, 7, 9, 12, 14]:
            return 'red'
        elif number in [2, 4, 6, 8, 10, 11, 13]:
            return 'black'
        else:
            return 'unknown'
    
    def _send_pong(self):
        """Envia pong em resposta ao ping."""
        try:
            if self.websocket and self.is_connected:
                self.websocket.send(json.dumps({'event': 'pong'}))
        except Exception as e:
            logger.error(f"❌ Erro ao enviar pong: {e}")
    
    def stop_monitoring(self):
        """Para o monitoramento."""
        logger.info("🛑 Parando monitoramento...")
        
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        if self.websocket:
            try:
                self.websocket.close()
            except:
                pass
        
        self.is_connected = False
        logger.info("✅ Monitoramento parado")
    
    async def cleanup(self):
        """Limpa recursos."""
        logger.info("🧹 Limpando recursos...")
        
        self.stop_monitoring()
        
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        logger.info("✅ Recursos limpos")
    
    def get_status(self) -> Dict:
        """Retorna status do analisador."""
        return {
            'connected': self.is_connected,
            'monitoring': self.is_monitoring,
            'has_session': bool(self.jsessionid and self.token),
            'last_result_time': self.last_result_time,
            'reconnect_attempts': self.reconnect_attempts,
            'playwright_available': PLAYWRIGHT_AVAILABLE
        }


# Função de conveniência para uso síncrono
def create_pragmatic_analyzer(username: str, password: str, callback: Optional[Callable] = None) -> PragmaticAnalyzer:
    """Cria e inicializa um analisador Pragmatic Play."""
    analyzer = PragmaticAnalyzer(username, password, callback)
    return analyzer


# Função para inicialização completa
async def initialize_pragmatic_analyzer(username: str, password: str, callback: Optional[Callable] = None) -> Optional[PragmaticAnalyzer]:
    """Inicializa completamente o analisador Pragmatic Play."""
    try:
        analyzer = PragmaticAnalyzer(username, password, callback)
        
        # Inicializar Playwright
        if not await analyzer.initialize_playwright():
            return None
        
        # Fazer login e obter sessão
        if not await analyzer.login_and_get_session():
            await analyzer.cleanup()
            return None
        
        # Conectar WebSocket
        if not analyzer.connect_websocket():
            await analyzer.cleanup()
            return None
        
        logger.info("✅ PragmaticAnalyzer inicializado completamente!")
        return analyzer
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        return None


if __name__ == "__main__":
    # Teste básico
    async def test_callback(result):
        print(f"🎲 Resultado recebido: {result}")
    
    async def main():
        username = os.getenv('PLAYNABETS_USER', '')
        password = os.getenv('PLAYNABETS_PASS', '')
        
        if not username or not password:
            print("❌ Configure PLAYNABETS_USER e PLAYNABETS_PASS no .env")
            return
        
        analyzer = await initialize_pragmatic_analyzer(username, password, test_callback)
        if analyzer:
            analyzer.start_monitoring()
            
            # Manter rodando
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await analyzer.cleanup()
    
    asyncio.run(main())
