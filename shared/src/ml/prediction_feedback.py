#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Feedback de Predições para o Double da Blaze.
Avisa sobre acertos/erros e fornece análises de performance.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class FeedbackMessage:
    """Mensagem de feedback."""
    title: str
    message: str
    message_type: str  # 'success', 'error', 'info', 'warning'
    prediction_data: Dict[str, Any]
    timestamp: datetime

class PredictionFeedback:
    """
    Sistema de feedback para predições.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o sistema de feedback.
        
        Args:
            config: Configurações do feedback
        """
        self.config = config or {}
        
        # Configurações
        self.show_popup_alerts = self.config.get('show_popup_alerts', True)
        self.show_console_feedback = self.config.get('show_console_feedback', True)
        self.play_sound = self.config.get('play_sound', True)
        self.feedback_delay = self.config.get('feedback_delay', 1.0)  # segundos
        
        # Histórico de feedback
        self.feedback_history: List[FeedbackMessage] = []
        
        # Callbacks para diferentes tipos de feedback
        self.feedback_callbacks = {
            'popup': self._show_popup_feedback,
            'console': self._show_console_feedback,
            'sound': self._play_feedback_sound
        }
        
        logger.info("PredictionFeedback inicializado")
    
    def process_prediction_result(self, prediction_result: Dict[str, Any]) -> None:
        """
        Processa resultado de uma predição e gera feedback.
        
        Args:
            prediction_result: Resultado da validação da predição
        """
        try:
            status = prediction_result.get('status')
            predicted_color = prediction_result.get('predicted_color')
            actual_color = prediction_result.get('actual_color')
            confidence = prediction_result.get('confidence', 0)
            pattern_id = prediction_result.get('pattern_id', 'unknown')
            reasoning = prediction_result.get('reasoning', '')
            
            if status == 'correct':
                self._handle_correct_prediction(prediction_result)
            elif status == 'incorrect':
                self._handle_incorrect_prediction(prediction_result)
            elif status == 'expired':
                self._handle_expired_prediction(prediction_result)
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado da predição: {e}")
    
    def _handle_correct_prediction(self, prediction_result: Dict[str, Any]) -> None:
        """Processa predição correta."""
        predicted_color = prediction_result.get('predicted_color')
        confidence = prediction_result.get('confidence', 0)
        pattern_id = prediction_result.get('pattern_id', 'unknown')
        validation_delay = prediction_result.get('validation_delay', 0)
        
        # Criar mensagem de sucesso
        message = FeedbackMessage(
            title="🎯 PREDIÇÃO CORRETA!",
            message=f"Saiu {predicted_color.upper()} como previsto!\n\n"
                   f"Confiança: {confidence:.1%}\n"
                   f"Padrão: {pattern_id}\n"
                   f"Tempo de validação: {validation_delay:.1f}s",
            message_type='success',
            prediction_data=prediction_result,
            timestamp=datetime.now()
        )
        
        # Enviar feedback
        self._send_feedback(message)
        
        logger.info(f"Predição CORRETA: {predicted_color} ({confidence:.1%})")
    
    def _handle_incorrect_prediction(self, prediction_result: Dict[str, Any]) -> None:
        """Processa predição incorreta."""
        predicted_color = prediction_result.get('predicted_color')
        actual_color = prediction_result.get('actual_color')
        confidence = prediction_result.get('confidence', 0)
        pattern_id = prediction_result.get('pattern_id', 'unknown')
        
        # Criar mensagem de erro
        message = FeedbackMessage(
            title="❌ PREDIÇÃO INCORRETA",
            message=f"Predito: {predicted_color.upper()}\n"
                   f"Real: {actual_color.upper()}\n\n"
                   f"Confiança: {confidence:.1%}\n"
                   f"Padrão: {pattern_id}\n\n"
                   f"⚠️ Reavaliando padrões...",
            message_type='error',
            prediction_data=prediction_result,
            timestamp=datetime.now()
        )
        
        # Enviar feedback
        self._send_feedback(message)
        
        logger.warning(f"Predição INCORRETA: Predito {predicted_color}, Real {actual_color} ({confidence:.1%})")
    
    def _handle_expired_prediction(self, prediction_result: Dict[str, Any]) -> None:
        """Processa predição expirada."""
        predicted_color = prediction_result.get('predicted_color')
        confidence = prediction_result.get('confidence', 0)
        
        # Criar mensagem de aviso
        message = FeedbackMessage(
            title="⏰ PREDIÇÃO EXPIRADA",
            message=f"Predição para {predicted_color.upper()} expirou\n"
                   f"Confiança: {confidence:.1%}\n\n"
                   f"Não foi possível validar a tempo.",
            message_type='warning',
            prediction_data=prediction_result,
            timestamp=datetime.now()
        )
        
        # Enviar feedback
        self._send_feedback(message)
        
        logger.info(f"Predição EXPIRADA: {predicted_color} ({confidence:.1%})")
    
    def _send_feedback(self, message: FeedbackMessage) -> None:
        """Envia feedback através dos canais configurados."""
        # Adicionar ao histórico
        self.feedback_history.append(message)
        
        # Limitar histórico
        if len(self.feedback_history) > 100:
            self.feedback_history = self.feedback_history[-100:]
        
        # Enviar através dos canais configurados
        if self.show_popup_alerts:
            self._send_popup_feedback(message)
        
        if self.show_console_feedback:
            self._send_console_feedback(message)
        
        if self.play_sound:
            self._send_sound_feedback(message)
    
    def _send_popup_feedback(self, message: FeedbackMessage) -> None:
        """Envia feedback via popup."""
        def show_popup():
            try:
                # Aguardar um pouco para não interferir com outros popups
                time.sleep(self.feedback_delay)
                
                if message.message_type == 'success':
                    messagebox.showinfo(message.title, message.message)
                elif message.message_type == 'error':
                    messagebox.showerror(message.title, message.message)
                elif message.message_type == 'warning':
                    messagebox.showwarning(message.title, message.message)
                else:
                    messagebox.showinfo(message.title, message.message)
            except Exception as e:
                logger.error(f"Erro ao mostrar popup: {e}")
        
        # Executar em thread separada para não bloquear
        threading.Thread(target=show_popup, daemon=True).start()
    
    def _send_console_feedback(self, message: FeedbackMessage) -> None:
        """Envia feedback via console."""
        print(f"\n{'='*50}")
        print(f"{message.title}")
        print(f"{'='*50}")
        print(message.message)
        print(f"{'='*50}\n")
    
    def _send_sound_feedback(self, message: FeedbackMessage) -> None:
        """Envia feedback via som."""
        try:
            import winsound
            
            if message.message_type == 'success':
                # Som de sucesso (frequência alta)
                winsound.Beep(800, 200)
            elif message.message_type == 'error':
                # Som de erro (frequência baixa)
                winsound.Beep(300, 300)
            elif message.message_type == 'warning':
                # Som de aviso (frequência média)
                winsound.Beep(500, 150)
        except ImportError:
            # winsound não disponível (Linux/Mac)
            pass
        except Exception as e:
            logger.error(f"Erro ao reproduzir som: {e}")
    
    def _show_popup_feedback(self, message: FeedbackMessage) -> None:
        """Mostra popup de feedback."""
        self._send_popup_feedback(message)
    
    def _show_console_feedback(self, message: FeedbackMessage) -> None:
        """Mostra feedback no console."""
        self._send_console_feedback(message)
    
    def _play_feedback_sound(self, message: FeedbackMessage) -> None:
        """Reproduz som de feedback."""
        self._send_sound_feedback(message)
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do feedback."""
        if not self.feedback_history:
            return {'total_feedback': 0}
        
        # Contar por tipo
        type_counts = {}
        for feedback in self.feedback_history:
            msg_type = feedback.message_type
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        # Feedback recente (últimas 24 horas)
        recent_time = datetime.now() - timedelta(hours=24)
        recent_feedback = [f for f in self.feedback_history if f.timestamp > recent_time]
        
        return {
            'total_feedback': len(self.feedback_history),
            'recent_feedback': len(recent_feedback),
            'type_counts': type_counts,
            'last_feedback': self.feedback_history[-1].timestamp.isoformat() if self.feedback_history else None
        }
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna feedback recente."""
        recent = sorted(self.feedback_history, key=lambda f: f.timestamp, reverse=True)
        return [
            {
                'title': feedback.title,
                'message': feedback.message,
                'type': feedback.message_type,
                'timestamp': feedback.timestamp.isoformat(),
                'prediction_data': feedback.prediction_data
            }
            for feedback in recent[:limit]
        ]
