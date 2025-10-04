"""
Gerenciador de Proxy para contornar bloqueios anti-bot
"""
import requests
import random
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador de proxies para contornar bloqueios."""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.failed_proxies = set()
        self.load_free_proxies()
    
    def load_free_proxies(self):
        """Carrega lista de proxies gratuitos."""
        # Lista de proxies gratuitos (exemplo)
        self.proxies = [
            # Proxies HTTP gratuitos (exemplo - substituir por proxies reais)
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:3128",
            "http://proxy3.example.com:8080",
        ]
        
        # Proxies SOCKS5 (exemplo)
        self.socks_proxies = [
            "socks5://proxy1.example.com:1080",
            "socks5://proxy2.example.com:1080",
        ]
        
        logger.info(f"📡 Carregados {len(self.proxies)} proxies HTTP e {len(self.socks_proxies)} proxies SOCKS5")
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Retorna um proxy aleatório que não falhou recentemente."""
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available_proxies:
            logger.warning("⚠️ Nenhum proxy disponível")
            return None
        
        proxy_url = random.choice(available_proxies)
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def mark_proxy_failed(self, proxy_url: str):
        """Marca um proxy como falhou."""
        self.failed_proxies.add(proxy_url)
        logger.warning(f"❌ Proxy marcado como falhou: {proxy_url}")
    
    def test_proxy(self, proxy: Dict) -> bool:
        """Testa se um proxy está funcionando."""
        try:
            test_url = "https://httpbin.org/ip"
            response = requests.get(
                test_url, 
                proxies=proxy, 
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Proxy funcionando: {proxy}")
                return True
            else:
                logger.warning(f"⚠️ Proxy retornou {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar proxy: {e}")
            return False
    
    def get_working_proxy(self) -> Optional[Dict]:
        """Retorna um proxy que está funcionando."""
        max_attempts = 5
        attempts = 0
        
        while attempts < max_attempts:
            proxy = self.get_random_proxy()
            if not proxy:
                break
            
            if self.test_proxy(proxy):
                return proxy
            else:
                self.mark_proxy_failed(list(proxy.values())[0])
                attempts += 1
                time.sleep(1)
        
        logger.error("❌ Nenhum proxy funcionando encontrado")
        return None

class AntiDetectionManager:
    """Gerenciador de técnicas anti-detecção."""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0'
        ]
        
        self.accept_languages = [
            'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
            'pt-BR,pt;q=0.9,en;q=0.8',
            'en-US,en;q=0.9'
        ]
    
    def get_random_headers(self) -> Dict[str, str]:
        """Retorna headers aleatórios para evitar detecção."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    def get_api_headers(self) -> Dict[str, str]:
        """Retorna headers específicos para APIs."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://client.pragmaticplaylive.net',
            'Referer': 'https://client.pragmaticplaylive.net/',
            'Sec-Ch-Ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Priority': 'u=1, i',
            'X-Requested-With': 'XMLHttpRequest'
        }
    
    def add_random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Adiciona delay aleatório para simular comportamento humano."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

# Instâncias globais
proxy_manager = ProxyManager()
anti_detection = AntiDetectionManager()
