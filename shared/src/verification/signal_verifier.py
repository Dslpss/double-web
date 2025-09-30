#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de verificação automática de acertos/erros dos sinais.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SignalResult:
    """Resultado de um sinal verificado."""
    signal_id: str
    predicted_color: str
    actual_color: str
    is_correct: bool
    confidence: float
    method: str
    created_at: datetime
    verified_at: datetime
    result_id: Optional[str] = None

class SignalVerifier:
    """Sistema de verificação automática de sinais."""
    
    def __init__(self, db_manager, config: Optional[Dict] = None):
        """
        Inicializa o verificador de sinais.
        
        Args:
            db_manager: Gerenciador do banco de dados
            config: Configurações do verificador
        """
        self.db_manager = db_manager
        self.config = config or {}
        self.verification_window = self.config.get('verification_window', 10)  # minutos
        self.auto_verify = self.config.get('auto_verify', True)
        
        # Cache de sinais pendentes
        self.pending_signals = {}
        
        logger.info("SignalVerifier inicializado")
    
    def register_signal(self, signal_data: Dict) -> str:
        """
        Registra um novo sinal para verificação.
        
        Args:
            signal_data: Dados do sinal (cor, confiança, método, etc.)
            
        Returns:
            str: ID do sinal registrado
        """
        try:
            signal_id = f"signal_{int(time.time() * 1000)}"
            
            # Dados do sinal
            signal_info = {
                'id': signal_id,
                'predicted_color': signal_data.get('color', ''),
                'confidence': signal_data.get('confidence', 0.0),
                'method': signal_data.get('method', 'unknown'),
                'created_at': datetime.now(),
                'verified': False,
                'result': None
            }
            
            # Armazenar no cache
            self.pending_signals[signal_id] = signal_info
            
            # Salvar no banco de dados
            self._save_signal_to_db(signal_info)
            
            logger.info(f"Sinal registrado: {signal_id} - {signal_info['predicted_color']}")
            return signal_id
            
        except Exception as e:
            logger.error(f"Erro ao registrar sinal: {e}")
            return None
    
    def verify_signals(self, new_results: List[Dict]) -> List[SignalResult]:
        """
        Verifica sinais pendentes com base nos novos resultados.
        
        Args:
            new_results: Lista de novos resultados do jogo
            
        Returns:
            List[SignalResult]: Lista de sinais verificados
        """
        verified_signals = []
        
        try:
            for result in new_results:
                result_color = result.get('color', '')
                result_id = result.get('id', '')
                result_time = result.get('created_at', '')
                
                # Verificar sinais pendentes
                for signal_id, signal_info in list(self.pending_signals.items()):
                    if signal_info['verified']:
                        continue
                    
                    # Verificar se o sinal é recente o suficiente
                    if self._is_signal_recent(signal_info['created_at']):
                        is_correct = self._check_prediction(
                            signal_info['predicted_color'], 
                            result_color
                        )
                        
                        # Criar resultado da verificação
                        signal_result = SignalResult(
                            signal_id=signal_id,
                            predicted_color=signal_info['predicted_color'],
                            actual_color=result_color,
                            is_correct=is_correct,
                            confidence=signal_info['confidence'],
                            method=signal_info['method'],
                            created_at=signal_info['created_at'],
                            verified_at=datetime.now(),
                            result_id=result_id
                        )
                        
                        verified_signals.append(signal_result)
                        
                        # Marcar como verificado
                        signal_info['verified'] = True
                        signal_info['result'] = signal_result
                        
                        # Atualizar no banco de dados
                        self._update_signal_verification(signal_id, is_correct, result_id)
                        
                        logger.info(f"Sinal verificado: {signal_id} - {'✅ ACERTO' if is_correct else '❌ ERRO'}")
            
            return verified_signals
            
        except Exception as e:
            logger.error(f"Erro ao verificar sinais: {e}")
            return []
    
    def _is_signal_recent(self, signal_time: datetime) -> bool:
        """Verifica se o sinal é recente o suficiente para verificação."""
        time_diff = datetime.now() - signal_time
        return time_diff.total_seconds() <= (self.verification_window * 60)
    
    def _check_prediction(self, predicted_color: str, actual_color: str) -> bool:
        """Verifica se a predição está correta."""
        # Normalizar cores
        predicted = predicted_color.lower().strip()
        actual = actual_color.lower().strip()
        
        # Mapeamento de cores
        color_mapping = {
            'red': ['red', 'vermelho', 'r'],
            'black': ['black', 'preto', 'b'],
            'white': ['white', 'branco', 'w']
        }
        
        # Verificar correspondência
        for color, variants in color_mapping.items():
            if predicted in variants and actual in variants:
                return True
        
        return False
    
    def _save_signal_to_db(self, signal_info: Dict):
        """Salva sinal no banco de dados."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO predictions (
                        result_id, prediction_color, confidence, method, created_at, correct
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    None,  # result_id será preenchido na verificação
                    signal_info['predicted_color'],
                    signal_info['confidence'],
                    signal_info['method'],
                    signal_info['created_at'],
                    None  # correct será preenchido na verificação
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar sinal no banco: {e}")
    
    def _update_signal_verification(self, signal_id: str, is_correct: bool, result_id: str):
        """Atualiza verificação do sinal no banco de dados."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE predictions 
                    SET correct = ?, result_id = ?
                    WHERE id = (SELECT id FROM predictions WHERE prediction_color = ? ORDER BY created_at DESC LIMIT 1)
                ''', (is_correct, result_id, self.pending_signals[signal_id]['predicted_color']))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao atualizar verificação: {e}")
    
    def get_pending_signals(self) -> List[Dict]:
        """Retorna lista de sinais pendentes de verificação."""
        return [signal for signal in self.pending_signals.values() if not signal['verified']]
    
    def get_verified_signals(self, limit: int = 50) -> List[Dict]:
        """Retorna lista de sinais verificados recentemente."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        id, prediction_color, confidence, method, created_at, correct, result_id
                    FROM predictions 
                    WHERE correct IS NOT NULL
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'predicted_color': row[1],
                        'confidence': row[2],
                        'method': row[3],
                        'created_at': row[4],
                        'correct': row[5],
                        'result_id': row[6]
                    })
                
                return results
        except Exception as e:
            logger.error(f"Erro ao buscar sinais verificados: {e}")
            return []
    
    def get_accuracy_stats(self, days: int = 7) -> Dict:
        """Retorna estatísticas de precisão dos sinais."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct,
                        AVG(confidence) as avg_confidence
                    FROM predictions 
                    WHERE correct IS NOT NULL 
                    AND created_at >= datetime('now', '-{} days')
                '''.format(days))
                
                row = cursor.fetchone()
                if row and row[0] > 0:
                    total = row[0]
                    correct = row[1]
                    accuracy = (correct / total) * 100 if total > 0 else 0
                    
                    return {
                        'total_signals': total,
                        'correct_signals': correct,
                        'accuracy_percentage': round(accuracy, 2),
                        'average_confidence': round(row[2], 3)
                    }
                else:
                    return {
                        'total_signals': 0,
                        'correct_signals': 0,
                        'accuracy_percentage': 0,
                        'average_confidence': 0
                    }
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {
                'total_signals': 0,
                'correct_signals': 0,
                'accuracy_percentage': 0,
                'average_confidence': 0
            }
