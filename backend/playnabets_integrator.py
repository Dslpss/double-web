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
from datetime import datetime
from config import (
    PLAYNABETS_WS_URL, 
    get_playnabets_headers, 
    get_playnabets_url,
    extract_result_from_payload
)

JSON_RE = re.compile(r"(\{.*\})", re.DOTALL)

class PlayNabetsIntegrator:
    """Integra dados reais da PlayNabets com o sistema web."""
    
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
        self.ws_url = PLAYNABETS_WS_URL
        self.connected = False
        self.running = False
        self.last_result = None
        
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
        """Escuta dados da PlayNabets."""
        headers = get_playnabets_headers()
        url = get_playnabets_url()
        
        print(f"Conectando a PlayNabets: {url}")
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.ws_connect(url, timeout=30) as ws:
                    print("Conectado a PlayNabets!")
                    self.connected = True
                    
                    while self.running:
                        try:
                            msg = await ws.receive(timeout=10)
                            
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                raw = msg.data
                                data = self.extract_json(raw)
                                
                                if data is not None:
                                    # Processar resultado se for um resultado de jogo
                                    if 'value' in data:
                                        self.process_result(data)
                                        
                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                print("🔌 Conexão PlayNabets fechada")
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                print(f"❌ Erro na conexão PlayNabets: {ws.exception()}")
                                break
                                
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            print(f"❌ Erro ao processar mensagem: {e}")
                            continue
                            
        except Exception as e:
            print(f"❌ Erro na conexão PlayNabets: {e}")
            self.connected = False
    
    def start(self):
        """Inicia o integrador."""
        if self.running:
            return
            
        self.running = True
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.listen_playnabets())
        
        self.thread = threading.Thread(target=run_async, daemon=True)
        self.thread.start()
        
        print("🚀 Integrador PlayNabets iniciado!")
    
    def stop(self):
        """Para o integrador."""
        self.running = False
        self.connected = False
        print("⏹️ Integrador PlayNabets parado!")
    
    def get_status(self):
        """Retorna status do integrador."""
        return {
            'connected': self.connected or self.running,
            'running': self.running,
            'last_result': self.last_result,
            'ws_url': self.ws_url
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
