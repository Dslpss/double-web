#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lógica de Sinal Simples - Estilo Bots do Telegram
Sistema simplificado que envia sinais baseado em sequências claras
"""

import time
from typing import Dict, List, Optional, Any
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TelegramBotLogic:
    """
    Implementa a lógica simples dos bots de Telegram para Double.
    Foca em sequências claras e sinais frequentes.
    """
    
    def __init__(self):
        # Configurações simples
        self.min_sequence_for_signal = 3  # Mínimo de 3 da mesma cor para sinal
        self.signal_cooldown = 120  # 2 minutos entre sinais (mais frequente)
        self.last_signal_time = 0
        self.gale_enabled = True  # Sistema de Gale ativo
        self.max_gales = 2  # Máximo de 2 gales
        
        # Estatísticas
        self.signals_sent = 0
        self.last_signal = None
        
        logger.info("🤖 TelegramBotLogic inicializado - Estilo bots de sinal")
    
    def should_send_signal(self, results: List[Dict[str, Any]]) -> bool:
        """
        Verifica se deve enviar um sinal agora.
        Lógica simples: cooldown básico + dados mínimos
        """
        # Precisa de pelo menos 5 resultados
        if len(results) < 5:
            return False
        
        # Verificar cooldown (2 minutos)
        current_time = time.time()
        if current_time - self.last_signal_time < self.signal_cooldown:
            return False
        
        return True
    
    def detect_simple_pattern(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Detecta padrões simples como os bots do Telegram:
        - Sequência de 3+ cores iguais → Apostar na cor oposta
        - Alternância (vermelho/preto/vermelho/preto) → Seguir padrão
        """
        if len(results) < 3:
            return None
        
        # Pegar últimos 10 resultados para análise
        recent = results[-10:]
        colors = [r.get('color', '') for r in recent]
        
        # 1. SEQUÊNCIA SIMPLES: 3+ da mesma cor
        last_3 = colors[-3:]
        if len(set(last_3)) == 1 and last_3[0] in ['red', 'black']:
            # Todas as últimas 3 são da mesma cor
            dominant_color = last_3[0]
            sequence_length = 1
            
            # Contar quantas são da mesma cor consecutivas
            for i in range(len(colors) - 1, -1, -1):
                if colors[i] == dominant_color:
                    sequence_length += 1
                else:
                    break
            
            # Se tem 3 ou mais da mesma cor, apostar na oposta (martingale reverso)
            if sequence_length >= 3:
                opposite_color = 'black' if dominant_color == 'red' else 'red'
                confidence = min(0.85, 0.60 + (sequence_length - 3) * 0.05)
                
                return {
                    'signal_type': 'SEQUÊNCIA',
                    'detected_pattern': f'{sequence_length}x {dominant_color.upper()}',
                    'bet_color': opposite_color,
                    'confidence': confidence,
                    'reasoning': f'Sequência de {sequence_length} {dominant_color.upper()}s - Apostar na reversão',
                    'gale': self.max_gales,
                    'emoji': '🔴' if opposite_color == 'red' else '⚫'
                }
        
        # 2. PREDOMINÂNCIA: 7+ de uma cor nos últimos 10
        if len(colors) >= 8:
            color_count = Counter(colors)
            # Remover white da contagem
            if 'white' in color_count:
                del color_count['white']
            
            if color_count:
                most_common = color_count.most_common(1)[0]
                dominant_color, count = most_common
                
                # Se uma cor aparece 7+ vezes em 10, apostar nela (hot hand)
                if count >= 7 and dominant_color in ['red', 'black']:
                    confidence = min(0.80, 0.55 + (count - 7) * 0.05)
                    
                    return {
                        'signal_type': 'PREDOMINÂNCIA',
                        'detected_pattern': f'{count}/10 {dominant_color.upper()}',
                        'bet_color': dominant_color,
                        'confidence': confidence,
                        'reasoning': f'{count} {dominant_color.upper()}s nos últimos 10 - Apostar na continuação',
                        'gale': self.max_gales,
                        'emoji': '🔴' if dominant_color == 'red' else '⚫'
                    }
        
        # 3. ALTERNÂNCIA CLARA: R-B-R-B-R-B
        if len(colors) >= 6:
            last_6 = colors[-6:]
            # Verificar alternância perfeita
            is_alternating = True
            for i in range(len(last_6) - 1):
                if last_6[i] == last_6[i + 1] or last_6[i] == 'white' or last_6[i + 1] == 'white':
                    is_alternating = False
                    break
            
            if is_alternating:
                # Seguir o padrão de alternância
                last_color = last_6[-1]
                next_color = 'black' if last_color == 'red' else 'red'
                
                return {
                    'signal_type': 'ALTERNÂNCIA',
                    'detected_pattern': 'Alternância R-B-R-B',
                    'bet_color': next_color,
                    'confidence': 0.75,
                    'reasoning': 'Padrão de alternância detectado - Seguir sequência',
                    'gale': self.max_gales,
                    'emoji': '🔴' if next_color == 'red' else '⚫'
                }
        
        return None
    
    def generate_telegram_style_signal(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Gera um sinal no estilo dos bots do Telegram.
        Retorna um dict com informações do sinal ou None se não houver sinal.
        """
        # Verificar se pode enviar sinal
        if not self.should_send_signal(results):
            return None
        
        # Detectar padrão simples
        pattern = self.detect_simple_pattern(results)
        
        if not pattern:
            return None
        
        # Marcar que enviou sinal
        self.last_signal_time = time.time()
        self.signals_sent += 1
        self.last_signal = pattern
        
        # Obter último número que saiu
        last_number = 0
        if results:
            last_result = results[-1]
            last_number = last_result.get('roll', last_result.get('number', 0))
        
        # Montar mensagem estilo Telegram
        bet_color_pt = 'VERMELHO' if pattern['bet_color'] == 'red' else 'PRETO'
        emoji = pattern['emoji']
        
        # Mensagem simples como os bots
        message = f"""
🎯 SINAL DETECTADO! 🎯

{emoji} ENTRE EM {bet_color_pt} {emoji}

📊 Padrão: {pattern['detected_pattern']}
💰 Proteção: Até {pattern['gale']} GALES
⚡ Confiança: {pattern['confidence']:.0%}

🔄 {pattern['reasoning']}
        """.strip()
        
        return {
            'type': 'telegram_signal',
            'bet_color': pattern['bet_color'],
            'bet_color_pt': bet_color_pt,
            'confidence': pattern['confidence'],
            'pattern_type': pattern['signal_type'],
            'detected_pattern': pattern['detected_pattern'],
            'reasoning': pattern['reasoning'],
            'gale': pattern['gale'],
            'message': message,
            'emoji': emoji,
            'last_number': last_number,
            'timestamp': time.time()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos sinais enviados"""
        return {
            'total_signals': self.signals_sent,
            'cooldown_seconds': self.signal_cooldown,
            'last_signal_time': self.last_signal_time,
            'last_signal': self.last_signal,
            'gale_enabled': self.gale_enabled,
            'max_gales': self.max_gales
        }
    
    def set_cooldown(self, seconds: int):
        """Ajusta o cooldown entre sinais"""
        self.signal_cooldown = max(60, min(300, seconds))  # Entre 1-5 minutos
        logger.info(f"Cooldown ajustado para {self.signal_cooldown}s")
    
    def set_gale(self, enabled: bool, max_gales: int = 2):
        """Configura sistema de Gale"""
        self.gale_enabled = enabled
        self.max_gales = max(1, min(3, max_gales))  # Entre 1-3 gales
        logger.info(f"Gale {'ativado' if enabled else 'desativado'} - Máximo: {self.max_gales}")


# Instância global
telegram_logic = TelegramBotLogic()

def get_telegram_logic() -> TelegramBotLogic:
    """Retorna a instância global"""
    return telegram_logic
