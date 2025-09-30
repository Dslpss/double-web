#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de notificações para padrões detectados no Blaze Double
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Cores para terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

@dataclass
class PatternNotification:
    """Notificação de padrão detectado"""
    pattern_type: str
    detected_number: int
    predicted_color: str
    confidence: float
    reasoning: str
    timestamp: datetime
    pattern_id: str = ""

class PatternNotifier:
    """Sistema de notificações para padrões detectados"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.notifications_history = []
        self.max_history = 100
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.enabled = self.config.get('enabled', True)
        
        # Configurações de exibição
        self.show_timestamp = self.config.get('show_timestamp', True)
        self.show_confidence = self.config.get('show_confidence', True)
        self.show_reasoning = self.config.get('show_reasoning', True)
        
        # Callback para notificações web
        self.web_callback = None
        
        # Limpar tela no início
        self._clear_screen()
        self._print_header()
    
    def _clear_screen(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self):
        """Imprime cabeçalho do sistema"""
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}{'BLAZE DOUBLE - SISTEMA DE NOTIFICACOES DE PADROES':^80}{Colors.END}")
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.YELLOW}Status: {Colors.GREEN}ATIVO{Colors.END}")
        print(f"{Colors.YELLOW}Confianca minima: {Colors.WHITE}{self.min_confidence:.1%}{Colors.END}")
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
        print()
    
    def notify_pattern_detected(self, 
                              pattern_type: str,
                              detected_number: int,
                              predicted_color: str,
                              confidence: float,
                              reasoning: str,
                              pattern_id: str = "") -> bool:
        """
        Notifica quando um padrão é detectado
        
        Args:
            pattern_type: Tipo do padrão detectado
            detected_number: Número que saiu
            predicted_color: Cor prevista para próxima rodada
            confidence: Confiança da previsão (0.0 a 1.0)
            reasoning: Explicação do padrão
            pattern_id: ID único do padrão
            
        Returns:
            bool: True se notificação foi exibida
        """
        # Reduzir confiança mínima para detectar mais padrões (aceitar qualquer confiança acima de 25%)
        min_confidence = min(0.25, self.min_confidence)
        
        if not self.enabled or confidence < min_confidence:
            return False
        
        # Criar notificação
        notification = PatternNotification(
            pattern_type=pattern_type,
            detected_number=detected_number,
            predicted_color=predicted_color,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now(),
            pattern_id=pattern_id
        )
        
        # Adicionar ao histórico
        self.notifications_history.append(notification)
        if len(self.notifications_history) > self.max_history:
            self.notifications_history = self.notifications_history[-self.max_history:]
        
        # Exibir notificação
        self._display_notification(notification)
        
        # Enviar para web
        self._send_web_notification(notification)
        
        return True
    
    def _display_notification(self, notification: PatternNotification):
        """Exibe a notificação na tela"""
        # Notificação principal - foco na ação
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'PADRAO DETECTADO - APOSTE AGORA!':^80}{Colors.END}")
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
        
        # Número que saiu
        number_color = self._get_number_color(notification.detected_number)
        print(f"{Colors.WHITE}Saiu numero: {Colors.BOLD}{number_color}{notification.detected_number}{Colors.END}")
        
        # Próxima aposta - DESTAQUE PRINCIPAL
        next_color_display = self._get_color_display(notification.predicted_color)
        print(f"{Colors.BOLD}{Colors.WHITE}Na proxima rodada apostar: {Colors.BOLD}{next_color_display}{notification.predicted_color.upper()}{Colors.END}")
        
        # Confiança - DESTAQUE
        if self.show_confidence:
            confidence_color = self._get_confidence_color(notification.confidence)
            print(f"{Colors.BOLD}{Colors.WHITE}Confianca: {confidence_color}{notification.confidence:.1%}{Colors.END}")
        
        # Tipo de padrão (menos destaque)
        print(f"{Colors.WHITE}Padrao: {Colors.YELLOW}{notification.pattern_type}{Colors.END}")
        
        # Timestamp
        if self.show_timestamp:
            time_str = notification.timestamp.strftime("%H:%M:%S")
            print(f"{Colors.WHITE}Detectado em: {Colors.CYAN}{time_str}{Colors.END}")
        
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'APOSTE AGORA NA COR ACIMA!':^80}{Colors.END}")
        print()
        
        # Pausa para visualização
        time.sleep(3)
    
    def _get_number_color(self, number: int) -> str:
        """Retorna cor baseada no número"""
        if number == 0:
            return Colors.WHITE
        elif 1 <= number <= 7:
            return Colors.RED
        else:
            return Colors.BLUE  # Preto representado como azul para melhor visibilidade
    
    def _get_color_display(self, color: str) -> str:
        """Retorna cor de exibição para a previsão"""
        color_map = {
            'red': Colors.RED,
            'black': Colors.BLUE,
            'white': Colors.WHITE
        }
        return color_map.get(color.lower(), Colors.WHITE)
    
    def _get_confidence_color(self, confidence: float) -> str:
        """Retorna cor baseada na confiança"""
        if confidence >= 0.8:
            return Colors.GREEN
        elif confidence >= 0.6:
            return Colors.YELLOW
        else:
            return Colors.RED
    
    def notify_result(self, number: int, color: str, was_correct: bool = None):
        """Notifica resultado da rodada (apenas no console, sem spam na web)"""
        number_color = self._get_number_color(number)
        color_display = self._get_color_display(color)
        
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print(f"{Colors.WHITE}Resultado: {Colors.BOLD}{number_color}{number}{Colors.END} ({color_display}{color.upper()}{Colors.END})")
        
        if was_correct is not None:
            if was_correct:
                print(f"{Colors.GREEN}PREVISAO CORRETA!{Colors.END}")
            else:
                print(f"{Colors.RED}PREVISAO INCORRETA{Colors.END}")
        
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print()
        
        # NÃO enviar para web - apenas padrões detectados vão para web
    
    def get_recent_notifications(self, count: int = 10) -> List[PatternNotification]:
        """Retorna notificações recentes"""
        return self.notifications_history[-count:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das notificações"""
        if not self.notifications_history:
            return {}
        
        total = len(self.notifications_history)
        high_confidence = len([n for n in self.notifications_history if n.confidence >= 0.8])
        medium_confidence = len([n for n in self.notifications_history if 0.6 <= n.confidence < 0.8])
        low_confidence = len([n for n in self.notifications_history if n.confidence < 0.6])
        
        return {
            'total_notifications': total,
            'high_confidence': high_confidence,
            'medium_confidence': medium_confidence,
            'low_confidence': low_confidence,
            'average_confidence': sum(n.confidence for n in self.notifications_history) / total
        }
    
    def clear_screen(self):
        """Limpa a tela e reimprime cabeçalho"""
        self._clear_screen()
        self._print_header()
    
    def set_enabled(self, enabled: bool):
        """Habilita/desabilita notificações"""
        self.enabled = enabled
        if enabled:
            print(f"{Colors.GREEN}Notificações habilitadas{Colors.END}")
        else:
            print(f"{Colors.RED}Notificações desabilitadas{Colors.END}")
    
    def set_min_confidence(self, confidence: float):
        """Define confiança mínima para notificações"""
        self.min_confidence = max(0.0, min(1.0, confidence))
        print(f"{Colors.YELLOW}Confiança mínima alterada para: {self.min_confidence:.1%}{Colors.END}")
    
    def set_web_callback(self, callback):
        """Define callback para notificações web"""
        self.web_callback = callback
    
    def _send_web_notification(self, notification: PatternNotification):
        """Envia notificação para o frontend via callback"""
        if self.web_callback:
            try:
                web_data = {
                    'type': 'pattern_detected',
                    'pattern_type': notification.pattern_type,
                    'detected_number': notification.detected_number,
                    'predicted_color': notification.predicted_color,
                    'confidence': notification.confidence,
                    'reasoning': notification.reasoning,
                    'timestamp': notification.timestamp.isoformat(),
                    'pattern_id': notification.pattern_id
                }
                print(f"Enviando notificacao web: {notification.pattern_type} -> {notification.predicted_color} ({notification.confidence:.1%})")
                self.web_callback(web_data)
                print(f"Notificacao web enviada com sucesso!")
            except Exception as e:
                print(f"ERRO - Erro ao enviar notificacao web: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"AVISO - Callback web NAO configurado! Notificacao nao sera enviada para interface.")
    
    def _send_web_result(self, number: int, color: str, was_correct: bool = None):
        """Envia resultado para o frontend via callback"""
        if self.web_callback:
            try:
                web_data = {
                    'type': 'result',
                    'number': number,
                    'color': color,
                    'was_correct': was_correct,
                    'timestamp': datetime.now().isoformat()
                }
                self.web_callback(web_data)
            except Exception as e:
                print(f"Erro ao enviar resultado web: {e}")

# Instância global do notificador
notifier = PatternNotifier()

def notify_pattern(pattern_type: str, 
                  detected_number: int, 
                  predicted_color: str, 
                  confidence: float, 
                  reasoning: str = "",
                  pattern_id: str = "") -> bool:
    """
    Função de conveniência para notificar padrão detectado
    
    Args:
        pattern_type: Tipo do padrão
        detected_number: Número que saiu
        predicted_color: Cor prevista
        confidence: Confiança (0.0 a 1.0)
        reasoning: Explicação
        pattern_id: ID do padrão
        
    Returns:
        bool: True se notificação foi exibida
    """
    return notifier.notify_pattern_detected(
        pattern_type, detected_number, predicted_color, 
        confidence, reasoning, pattern_id
    )

def notify_result(number: int, color: str, was_correct: bool = None):
    """Função de conveniência para notificar resultado"""
    notifier.notify_result(number, color, was_correct)

def get_notifier() -> PatternNotifier:
    """Retorna instância do notificador"""
    return notifier
