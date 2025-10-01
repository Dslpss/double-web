#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador para conectar dados reais da PlayNabets com o sistema web
"""

import asyncio
import aiohttp
import json
import re
import threading
import time
import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path para importar config
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config import (
        PLAYNABETS_WS_URL, 
        get_playnabets_headers, 
        get_playnabets_url,
        extract_result_from_payload
    )
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Aviso: Config não disponível: {e}")
    CONFIG_AVAILABLE = False
    # Valores padrão se config não estiver disponível
    PLAYNABETS_WS_URL = 'wss://play.soline.bet:5903/Game'
    def get_playnabets_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://soline.bet',
            'Referer': 'https://soline.bet/'
        }
    def get_playnabets_url():
        return PLAYNABETS_WS_URL
    def extract_result_from_payload(data):
        try:
            if 'value' not in data:
                return None
            value = data['value']
            number = int(value) if isinstance(value, (int, float)) else int(str(value))
            if not (0 <= number <= 14):
                return None
            color = 'white' if number == 0 else 'red' if 1 <= number <= 7 else 'black'
            return {
                'number': number,
                'color': color,
                'round_id': data.get('round_id', f'round_{int(time.time())}'),
                'timestamp': int(time.time()),
                'source': 'playnabets'
            }
        except Exception:
            return None

JSON_RE = re.compile(r"(\{.*\})", re.DOTALL)

class PlayNabetsIntegrator:
    """Integra dados reais da PlayNabets com o sistema web."""
    
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
        self.ws_url = PLAYNABETS_WS_URL
        self.connected = False
        self.running = False
        self.last_result = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5  # segundos
        self.last_heartbeat = time.time()
        self.heartbeat_timeout = 30  # segundos
        
    def extract_json(self, payload: str):
        """Extrai JSON do payload."""
        m = JSON_RE.search(payload)
        if not m:
            return None
        try:
            return json.loads(m.group(1))
        except Exception:
            return None
    
    def process_result(self, data):
        """Processa resultado da PlayNabets usando configuração centralizada."""
        try:
            # Usar função centralizada de extração
            result = extract_result_from_payload(data)
            
            if result:
                print(f"Resultado PlayNabets: {result['number']} ({result['color']}) - Round: {result['round_id']}")
                
                # Enviar para analyzer se disponível
                if self.analyzer:
                    self.analyzer.add_manual_result(result['number'], result['color'])
                
                self.last_result = result
                return result
            else:
                print("Falha ao extrair resultado do payload")
                return None
                
        except Exception as e:
            print(f"Erro ao processar resultado: {e}")
            return None
    
    async def listen_playnabets(self):
        """Escuta dados da PlayNabets com reconexão automática."""
        while self.running:
            try:
                await self._connect_and_listen()
            except Exception as e:
                print(f"[ERRO] Erro na conexão PlayNabets: {e}")
                self.connected = False
                
                if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
                    self.reconnect_attempts += 1
                    print(f"[RECONEXAO] Tentativa {self.reconnect_attempts}/{self.max_reconnect_attempts} em {self.reconnect_delay}s...")
                    await asyncio.sleep(self.reconnect_delay)
                    # Aumentar delay progressivamente
                    self.reconnect_delay = min(self.reconnect_delay * 1.5, 60)
                else:
                    if self.reconnect_attempts >= self.max_reconnect_attempts:
                        print("[ERRO] Máximo de tentativas de reconexão atingido. Parando...")
                        break
                    else:
                        print("[ERRO] Sistema parado. Não tentando reconectar.")
                        break

    async def _connect_and_listen(self):
        """Conecta e escuta dados da PlayNabets."""
        headers = get_playnabets_headers()
        url = get_playnabets_url()
        
        print(f"[CONEXAO] Conectando a PlayNabets: {url}")
        
        # Timeout maior para conexões instáveis
        timeout = aiohttp.ClientTimeout(total=60, connect=30)
        
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            async with session.ws_connect(url) as ws:
                print("[CONEXAO] Conectado a PlayNabets!")
                self.connected = True
                self.reconnect_attempts = 0  # Reset contador de reconexão
                self.last_heartbeat = time.time()
                
                while self.running:
                    try:
                        # Verificar heartbeat
                        if time.time() - self.last_heartbeat > self.heartbeat_timeout:
                            print("[HEARTBEAT] Timeout detectado. Reconectando...")
                            break
                        
                        # Timeout menor para recebimento de mensagens
                        msg = await ws.receive(timeout=15)
                        
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            raw = msg.data
                            data = self.extract_json(raw)
                            
                            if data is not None:
                                # Atualizar heartbeat
                                self.last_heartbeat = time.time()
                                
                                # Processar resultado se for um resultado de jogo
                                if 'value' in data:
                                    self.process_result(data)
                                # Processar outros tipos de mensagem (ping, pong, etc.)
                                elif 'ping' in str(data).lower():
                                    print("[PING] Recebido ping da PlayNabets")
                                elif 'pong' in str(data).lower():
                                    print("[PONG] Recebido pong da PlayNabets")
                                    
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            print("[CONEXAO] Conexão PlayNabets fechada pelo servidor")
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print(f"[ERRO] Erro na conexão PlayNabets: {ws.exception()}")
                            break
                            
                    except asyncio.TimeoutError:
                        # Enviar ping para manter conexão ativa
                        try:
                            await ws.ping()
                            print("[PING] Enviado ping para manter conexão ativa")
                        except Exception as e:
                            print(f"[ERRO] Erro ao enviar ping: {e}")
                            break
                        continue
                    except Exception as e:
                        print(f"[ERRO] Erro ao processar mensagem: {e}")
                        # Não quebrar o loop por erros de processamento
                        continue
                        
            # Conexão fechada
            self.connected = False
            print("[CONEXAO] Conexão WebSocket fechada")
    
    def start(self):
        """Inicia o integrador."""
        if self.running:
            print("[AVISO] Integrador já está rodando")
            return
            
        self.running = True
        self.reconnect_attempts = 0
        self.reconnect_delay = 5  # Reset delay
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.listen_playnabets())
            except Exception as e:
                print(f"[ERRO] Erro no loop principal: {e}")
            finally:
                loop.close()
        
        # Não usar daemon=True para evitar terminação inesperada
        self.thread = threading.Thread(target=run_async, name="PlayNabetsIntegrator")
        self.thread.start()
        
        print("🚀 Integrador PlayNabets iniciado!")
    
    def stop(self):
        """Para o integrador."""
        print("[PARANDO] Parando integrador PlayNabets...")
        self.running = False
        self.connected = False
        
        # Aguardar thread terminar
        if hasattr(self, 'thread') and self.thread.is_alive():
            print("[AGUARDANDO] Aguardando thread terminar...")
            self.thread.join(timeout=10)
            if self.thread.is_alive():
                print("[AVISO] Thread não terminou em 10s, continuando...")
        
        print("[PARADO] Integrador PlayNabets parado!")
    
    def get_status(self):
        """Retorna status do integrador."""
        return {
            'connected': self.connected,
            'running': self.running,
            'last_result': self.last_result,
            'ws_url': self.ws_url,
            'reconnect_attempts': self.reconnect_attempts,
            'max_reconnect_attempts': self.max_reconnect_attempts,
            'last_heartbeat': self.last_heartbeat,
            'heartbeat_timeout': self.heartbeat_timeout,
            'time_since_last_heartbeat': time.time() - self.last_heartbeat if self.last_heartbeat else None
        }

# Instância global
playnabets_integrator = None

def init_playnabets_integrator(analyzer=None):
    """Inicializa o integrador PlayNabets."""
    global playnabets_integrator
    playnabets_integrator = PlayNabetsIntegrator(analyzer)
    return playnabets_integrator

def start_playnabets_connection():
    """Inicia conexão com PlayNabets."""
    global playnabets_integrator
    if playnabets_integrator:
        playnabets_integrator.start()

def stop_playnabets_connection():
    """Para conexão com PlayNabets."""
    global playnabets_integrator
    if playnabets_integrator:
        playnabets_integrator.stop()

def get_playnabets_status():
    """Retorna status da conexão PlayNabets."""
    global playnabets_integrator
    if playnabets_integrator:
        return playnabets_integrator.get_status()
    return {'connected': False, 'running': False}
