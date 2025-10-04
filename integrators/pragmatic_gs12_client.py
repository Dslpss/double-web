#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cliente especializado para acessar a API gs12.pragmaticplaylive.net
Este módulo implementa técnicas anti-detecção avançadas para contornar bloqueios
"""

import requests
import time
import json
import random
import logging
import os
from typing import Dict, List, Optional, Tuple, Union
import re
from datetime import datetime
import traceback

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PragmaticGS12Client:
    """
    Cliente especializado para acessar APIs da Pragmatic Play (GS12).
    Implementa técnicas anti-detecção avançadas para contornar bloqueios.
    """
    
    def __init__(self):
        """Inicializa o cliente com configurações avançadas anti-detecção."""
        self.session = requests.Session()
        
        # Carregar configurações de variáveis de ambiente
        self.bypass_detection = os.environ.get('PRAGMATIC_BYPASS_DETECTION', 'true').lower() == 'true'
        self.rotate_user_agents = os.environ.get('PRAGMATIC_ROTATE_USER_AGENTS', 'true').lower() == 'true'
        self.use_cookies = os.environ.get('PRAGMATIC_USE_COOKIES', 'true').lower() == 'true'
        self.emulate_browser = os.environ.get('PRAGMATIC_EMULATE_BROWSER', 'true').lower() == 'true'
        
        # Configuração de delays para simular comportamento humano
        self.delay_min = float(os.environ.get('PRAGMATIC_REQUEST_DELAY_MIN', '1.0'))
        self.delay_max = float(os.environ.get('PRAGMATIC_REQUEST_DELAY_MAX', '3.0'))
        
        # Autenticação e sessão
        self.jsessionid = os.environ.get('PRAGMATIC_JSESSIONID', None)
        self.fallback_jsessionid = 'kziwijo1wNzNh2TKOAQFUEWPNpWsB2-f60AUVqoGNAtbmJGkFdt7!-80873102-f6cb893a'
        self.require_auth = os.environ.get('PRAGMATIC_REQUIRE_AUTH', 'true').lower() == 'true'
        self.token_cassino = None
        self.last_login_time = 0
        
        # Rotação de User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/99.0.1150.30',
            'Mozilla/5.0 (iPad; CPU OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/93.0.4577.63 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'
        ]
        
        # Rotação de Accept-Language
        self.languages = [
            'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
            'pt-PT,pt;q=0.9,en;q=0.8,es;q=0.7',
        ]
        
        # URLs base
        self.base_url = "https://gs12.pragmaticplaylive.net"
        self.game_url = f"{self.base_url}/game"
        
        # Cookies e sessão
        self.cookies = {}
        self.last_request_time = None
        self.configure_session()
        
        # Tentar obter JSESSIONID do roulette_integrator se existir
        try:
            from app import roulette_integrator
            if roulette_integrator and roulette_integrator.jsessionid:
                self.jsessionid = roulette_integrator.jsessionid
                logger.info(f"✅ JSESSIONID obtido do roulette_integrator")
        except ImportError:
            logger.warning(f"⚠️ Não foi possível importar roulette_integrator")
            
        logger.info("✅ PragmaticGS12Client inicializado")
        logger.info(f"   Bypass detection: {self.bypass_detection}")
        logger.info(f"   Rotate user agents: {self.rotate_user_agents}")
        logger.info(f"   Use cookies: {self.use_cookies}")
        logger.info(f"   Emulate browser: {self.emulate_browser}")
        logger.info(f"   JSESSIONID: {'✅ Configurado' if self.jsessionid else '❌ Não configurado'}")
    
    def configure_session(self):
        """Configura a sessão HTTP com técnicas anti-detecção."""
        # Configurar retry strategy
        from urllib3.util.retry import Retry
        from requests.adapters import HTTPAdapter
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "HEAD", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Headers base
        self.update_headers()
        
        logger.info("✅ Sessão HTTP configurada com anti-detecção")
    
    def update_headers(self):
        """Atualiza headers para simular navegador real."""
        user_agent = random.choice(self.user_agents)
        accept_language = random.choice(self.languages)
        
        # Headers Chrome-like
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://client.pragmaticplaylive.net',
            'Referer': 'https://client.pragmaticplaylive.net/',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Ch-Ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        })
        
        # Adicionar headers mais específicos dependendo do user-agent
        if 'Firefox' in user_agent:
            self.session.headers.update({
                'Sec-Ch-Ua': '""',
                'TE': 'trailers'
            })
        
        # Se for Edge
        elif 'Edge' in user_agent:
            self.session.headers.update({
                'Sec-Ch-Ua': '"Microsoft Edge";v="99", "Chromium";v="99", "Not?A_Brand";v="24"',
            })
    
    def fetch_game_data(self) -> Tuple[int, Union[Dict, str]]:
        """
        Obtém dados do jogo diretamente do endpoint GS12.
        
        Returns:
            Tuple[int, Union[Dict, str]]: código de status e resposta (json ou texto)
        """
        try:
            # Verificar se temos JSESSIONID
            current_jsessionid = self.jsessionid or self.fallback_jsessionid
            
            # Adicionar timestamp para evitar cache
            timestamp = int(time.time() * 1000)
            
            # Montar URL com parâmetros de autenticação
            url = f"{self.game_url}?_={timestamp}"
            if self.require_auth:
                url = f"{self.game_url}?JSESSIONID={current_jsessionid}&_={timestamp}&currencyCode=BRL"
            
            logger.info(f"🔑 Usando JSESSIONID: {current_jsessionid[:20]}...")
            
            # Atualizar headers para esta requisição
            if self.rotate_user_agents or self.bypass_detection:
                self.update_headers()
            
            # Adicionar delay para parecer comportamento humano
            if self.bypass_detection and self.last_request_time:
                elapsed = time.time() - self.last_request_time
                if elapsed < self.delay_min:
                    time.sleep(random.uniform(self.delay_min, self.delay_max))
            
            # Realizar requisição OPTIONS primeiro para parecer navegador
            if self.emulate_browser:
                logger.info("🔄 Enviando requisição OPTIONS para simular navegador")
                self.session.options(url)
            
            logger.info(f"📡 Enviando requisição GET para {url}")
            
            # Preparar cookies com JSESSIONID
            if self.use_cookies:
                if 'JSESSIONID' not in self.cookies and current_jsessionid:
                    self.cookies['JSESSIONID'] = current_jsessionid
            
            # Realizar requisição principal
            response = self.session.get(
                url, 
                timeout=15,
                cookies=self.cookies if self.use_cookies else None
            )
            
            self.last_request_time = time.time()
            logger.info(f"✅ Resposta recebida: {response.status_code}")
            
            # Salvar cookies para próximas requisições
            if self.use_cookies and response.cookies:
                self.cookies.update(dict(response.cookies))
                logger.info(f"🍪 Cookies atualizados: {len(self.cookies)} cookies")
                
                # Verificar se recebemos um novo JSESSIONID
                if 'JSESSIONID' in response.cookies:
                    self.jsessionid = response.cookies['JSESSIONID']
                    logger.info(f"🔑 Novo JSESSIONID recebido: {self.jsessionid[:20]}...")
            
            # Verificar se é JSON ou XML
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"📄 Content-Type: {content_type}")
            
            # Mostrar os primeiros caracteres da resposta para debug
            preview = response.text[:100] if len(response.text) > 100 else response.text
            logger.info(f"📄 Preview da resposta: {preview}...")
            
            # Verificar se é uma página de manutenção programada
            if 'scheduled-maintenance.html' in response.text:
                logger.warning("⚠️ Detecção de manutenção programada")
                return 503, {'maintenance': True, 'message': 'Manutenção programada em andamento', 'raw': response.text[:500]}
            
            if 'json' in content_type:
                return response.status_code, response.json()
            elif 'xml' in content_type or '<' in response.text[:100]:
                return response.status_code, response.text
            else:
                return response.status_code, response.text
                
        except requests.RequestException as e:
            logger.error(f"❌ Erro na requisição: {e}")
            traceback.print_exc()
            return 500, {"error": str(e)}
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            traceback.print_exc()
            return 500, {"error": str(e)}
    
    def extract_game_results(self, response_data: Union[Dict, str]) -> List[Dict]:
        """
        Extrai resultados do jogo a partir da resposta.
        
        Args:
            response_data: Dados da resposta (JSON ou texto)
            
        Returns:
            List[Dict]: Lista de resultados extraídos
        """
        results = []
        
        try:
            # Verificar se é uma página de manutenção programada
            if isinstance(response_data, str) and 'scheduled-maintenance.html' in response_data:
                logger.warning("⚠️ Detecção de manutenção programada na resposta")
                return [{'id': 'maintenance', 'number': None, 'color': None, 'time': datetime.now().strftime('%H:%M:%S'), 
                        'maintenance': True, 'message': 'Manutenção programada em andamento'}]
            
            # Se for texto, tentar extrair XML
            if isinstance(response_data, str):
                # Extrair elementos gameresult do XML
                pattern = r'<gameresult\s+([^>]*)>(.*?)<\/gameresult>'
                matches = re.finditer(pattern, response_data)
                
                for match in matches:
                    attributes = match.group(1)
                    content = match.group(2)
                    
                    # Extrair atributos
                    score = re.search(r'score="([^"]+)"', attributes)
                    color = re.search(r'color="([^"]+)"', attributes)
                    game_id = re.search(r'id="([^"]+)"', attributes)
                    time_str = re.search(r'time="([^"]+)"', attributes)
                    
                    result = {
                        'number': int(score.group(1)) if score else None,
                        'color': color.group(1) if color else None,
                        'id': game_id.group(1) if game_id else None,
                        'time': time_str.group(1) if time_str else None,
                        'content': content.strip()
                    }
                    
                    results.append(result)
            
            # Se for dicionário, processar conforme estrutura
            elif isinstance(response_data, dict):
                # Implementar processamento de JSON se necessário
                pass
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair resultados: {e}")
            traceback.print_exc()
        
        return results

# Cliente singleton para ser usado em toda aplicação
gs12_client = PragmaticGS12Client()