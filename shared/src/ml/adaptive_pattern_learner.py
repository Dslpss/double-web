#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Aprendizado Adaptativo de Padrões para o Double da Blaze.
Este sistema aprende e evolui continuamente com os resultados que chegam.
"""

import logging
import numpy as np
from collections import defaultdict, deque, Counter
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import json
import pickle
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Tipos de padrões que o sistema pode aprender."""
    SEQUENCE = "sequence"
    ALTERNATION = "alternation"
    FREQUENCY = "frequency"
    TEMPORAL = "temporal"
    STATISTICAL = "statistical"
    CUSTOM = "custom"

@dataclass
class LearnedPattern:
    """Representa um padrão aprendido pelo sistema."""
    pattern_id: str
    pattern_type: PatternType
    pattern_data: Dict[str, Any]
    confidence: float
    frequency: int
    last_seen: datetime
    success_rate: float
    total_predictions: int
    correct_predictions: int
    created_at: datetime
    updated_at: datetime

@dataclass
class PredictionResult:
    """Resultado de uma predição."""
    pattern_id: str
    predicted_color: str
    confidence: float
    timestamp: datetime
    actual_result: Optional[str] = None
    is_correct: Optional[bool] = None

class AdaptivePatternLearner:
    """
    Sistema de aprendizado adaptativo que evolui continuamente com os resultados.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o sistema de aprendizado adaptativo.
        
        Args:
            config: Configurações do sistema
        """
        self.config = config or {}
        
        # Configurações
        self.min_pattern_frequency = self.config.get('min_pattern_frequency', 3)
        self.min_confidence_threshold = self.config.get('min_confidence_threshold', 0.6)
        self.max_patterns = self.config.get('max_patterns', 100)
        self.learning_rate = self.config.get('learning_rate', 0.1)
        self.decay_factor = self.config.get('decay_factor', 0.95)
        
        # Armazenamento de padrões aprendidos
        self.learned_patterns: Dict[str, LearnedPattern] = {}
        self.pattern_counter = 0
        
        # Histórico de dados
        self.data_history = deque(maxlen=self.config.get('history_size', 1000))
        self.prediction_history: List[PredictionResult] = []
        
        # Estatísticas
        self.total_predictions = 0
        self.correct_predictions = 0
        self.overall_accuracy = 0.0
        
        # Cache de análises
        self.analysis_cache = {}
        self.cache_ttl = timedelta(minutes=5)
        
        logger.info("AdaptivePatternLearner inicializado")
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """
        Adiciona um novo resultado e atualiza o aprendizado.
        
        Args:
            result: Resultado do jogo (deve conter 'roll', 'color', 'timestamp')
        """
        try:
            # Validar resultado
            if not self._validate_result(result):
                logger.warning(f"Resultado inválido ignorado: {result}")
                return
            
            # Adicionar ao histórico
            self.data_history.append(result)
            
            # Verificar se há predições pendentes para validar
            self._validate_pending_predictions(result)
            
            # Aprender novos padrões
            self._learn_from_new_data()
            
            # Atualizar padrões existentes
            self._update_existing_patterns()
            
            # Limpar padrões obsoletos
            self._cleanup_obsolete_patterns()
            
            logger.debug(f"Resultado adicionado: {result.get('roll')} ({result.get('color')})")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar resultado: {e}")
    
    def predict_next(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz uma predição baseada nos padrões aprendidos.
        
        Args:
            context: Contexto adicional para a predição
            
        Returns:
            Dict com predição, confiança e padrões utilizados
        """
        try:
            if len(self.data_history) < 10:
                return self._get_default_prediction()
            
            # Analisar padrões atuais
            current_patterns = self._analyze_current_patterns()
            
            # Combinar predições de diferentes padrões
            combined_prediction = self._combine_pattern_predictions(current_patterns)
            
            # Criar resultado da predição
            prediction_result = PredictionResult(
                pattern_id=combined_prediction.get('pattern_id', 'combined'),
                predicted_color=combined_prediction.get('color', 'unknown'),
                confidence=combined_prediction.get('confidence', 0.0),
                timestamp=datetime.now()
            )
            
            # Armazenar predição para validação futura
            self.prediction_history.append(prediction_result)
            
            return {
                'predicted_color': prediction_result.predicted_color,
                'confidence': prediction_result.confidence,
                'pattern_id': prediction_result.pattern_id,
                'patterns_used': combined_prediction.get('patterns_used', []),
                'reasoning': combined_prediction.get('reasoning', ''),
                'timestamp': prediction_result.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao fazer predição: {e}")
            return self._get_default_prediction()
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do aprendizado.
        
        Returns:
            Dict com estatísticas do sistema
        """
        return {
            'total_patterns_learned': len(self.learned_patterns),
            'total_predictions': self.total_predictions,
            'correct_predictions': self.correct_predictions,
            'overall_accuracy': self.overall_accuracy,
            'data_history_size': len(self.data_history),
            'prediction_history_size': len(self.prediction_history),
            'active_patterns': len([p for p in self.learned_patterns.values() 
                                  if p.confidence > self.min_confidence_threshold]),
            'pattern_types': Counter(p.pattern_type.value for p in self.learned_patterns.values())
        }
    
    def save_learned_patterns(self, filepath: str) -> bool:
        """
        Salva os padrões aprendidos em arquivo.
        
        Args:
            filepath: Caminho do arquivo para salvar
            
        Returns:
            True se salvou com sucesso
        """
        try:
            data = {
                'learned_patterns': self.learned_patterns,
                'pattern_counter': self.pattern_counter,
                'total_predictions': self.total_predictions,
                'correct_predictions': self.correct_predictions,
                'overall_accuracy': self.overall_accuracy,
                'config': self.config,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Padrões aprendidos salvos em: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar padrões: {e}")
            return False
    
    def load_learned_patterns(self, filepath: str) -> bool:
        """
        Carrega padrões aprendidos de arquivo.
        
        Args:
            filepath: Caminho do arquivo para carregar
            
        Returns:
            True se carregou com sucesso
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Arquivo não encontrado: {filepath}")
                return False
            
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.learned_patterns = data.get('learned_patterns', {})
            self.pattern_counter = data.get('pattern_counter', 0)
            self.total_predictions = data.get('total_predictions', 0)
            self.correct_predictions = data.get('correct_predictions', 0)
            self.overall_accuracy = data.get('overall_accuracy', 0.0)
            
            logger.info(f"Padrões aprendidos carregados de: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar padrões: {e}")
            return False
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Valida se o resultado tem os campos necessários."""
        required_fields = ['roll', 'color']
        return all(field in result for field in required_fields)
    
    def _validate_pending_predictions(self, result: Dict[str, Any]) -> None:
        """Valida predições pendentes com o novo resultado."""
        actual_color = result.get('color')
        
        for prediction in self.prediction_history:
            if prediction.actual_result is None:
                prediction.actual_result = actual_color
                prediction.is_correct = (prediction.predicted_color == actual_color)
                
                # Atualizar estatísticas
                self.total_predictions += 1
                if prediction.is_correct:
                    self.correct_predictions += 1
                
                self.overall_accuracy = self.correct_predictions / self.total_predictions
                
                # Atualizar padrão usado
                if prediction.pattern_id in self.learned_patterns:
                    pattern = self.learned_patterns[prediction.pattern_id]
                    pattern.total_predictions += 1
                    if prediction.is_correct:
                        pattern.correct_predictions += 1
                    pattern.success_rate = pattern.correct_predictions / pattern.total_predictions
                    pattern.updated_at = datetime.now()
    
    def _learn_from_new_data(self) -> None:
        """Aprende novos padrões dos dados recentes."""
        if len(self.data_history) < 20:
            return
        
        # Extrair sequências de cores
        colors = [r.get('color') for r in list(self.data_history)[-50:]]
        
        # Detectar padrões de sequência
        self._detect_sequence_patterns(colors)
        
        # Detectar padrões de alternação
        self._detect_alternation_patterns(colors)
        
        # Detectar padrões de frequência
        self._detect_frequency_patterns(colors)
        
        # Detectar padrões temporais
        self._detect_temporal_patterns()
    
    def _detect_sequence_patterns(self, colors: List[str]) -> None:
        """Detecta padrões de sequência."""
        for length in range(3, 8):
            for i in range(len(colors) - length):
                sequence = colors[i:i+length]
                pattern_key = ''.join(sequence)
                
                # Verificar se já existe
                if pattern_key in self.learned_patterns:
                    continue
                
                # Verificar frequência
                frequency = self._count_pattern_frequency(pattern_key, colors)
                if frequency >= self.min_pattern_frequency:
                    confidence = min(0.9, frequency / len(colors))
                    
                    pattern = LearnedPattern(
                        pattern_id=f"seq_{self.pattern_counter}",
                        pattern_type=PatternType.SEQUENCE,
                        pattern_data={
                            'sequence': sequence,
                            'length': length,
                            'pattern_key': pattern_key
                        },
                        confidence=confidence,
                        frequency=frequency,
                        last_seen=datetime.now(),
                        success_rate=0.0,
                        total_predictions=0,
                        correct_predictions=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    self.learned_patterns[pattern_key] = pattern
                    self.pattern_counter += 1
                    logger.info(f"Novo padrão de sequência aprendido: {pattern_key}")
    
    def _detect_alternation_patterns(self, colors: List[str]) -> None:
        """Detecta padrões de alternação."""
        alternations = []
        current_alt = [colors[0]]
        
        for i in range(1, len(colors)):
            if colors[i] != colors[i-1]:
                current_alt.append(colors[i])
            else:
                if len(current_alt) >= 3:
                    alternations.append(current_alt)
                current_alt = [colors[i]]
        
        if len(current_alt) >= 3:
            alternations.append(current_alt)
        
        for alt in alternations:
            pattern_key = f"alt_{len(alt)}"
            if pattern_key not in self.learned_patterns:
                frequency = len(alternations)
                confidence = min(0.8, frequency / len(colors))
                
                pattern = LearnedPattern(
                    pattern_id=f"alt_{self.pattern_counter}",
                    pattern_type=PatternType.ALTERNATION,
                    pattern_data={
                        'alternation_length': len(alt),
                        'pattern': alt
                    },
                    confidence=confidence,
                    frequency=frequency,
                    last_seen=datetime.now(),
                    success_rate=0.0,
                    total_predictions=0,
                    correct_predictions=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.learned_patterns[pattern_key] = pattern
                self.pattern_counter += 1
                logger.info(f"Novo padrão de alternação aprendido: {pattern_key}")
    
    def _detect_frequency_patterns(self, colors: List[str]) -> None:
        """Detecta padrões de frequência."""
        color_counts = Counter(colors)
        total = len(colors)
        
        for color, count in color_counts.items():
            frequency = count / total
            
            # Padrão de alta frequência
            if frequency > 0.5:
                pattern_key = f"freq_high_{color}"
                if pattern_key not in self.learned_patterns:
                    pattern = LearnedPattern(
                        pattern_id=f"freq_{self.pattern_counter}",
                        pattern_type=PatternType.FREQUENCY,
                        pattern_data={
                            'color': color,
                            'frequency': frequency,
                            'type': 'high'
                        },
                        confidence=min(0.7, frequency),
                        frequency=count,
                        last_seen=datetime.now(),
                        success_rate=0.0,
                        total_predictions=0,
                        correct_predictions=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    self.learned_patterns[pattern_key] = pattern
                    self.pattern_counter += 1
                    logger.info(f"Novo padrão de frequência aprendido: {pattern_key}")
    
    def _detect_temporal_patterns(self) -> None:
        """Detecta padrões temporais."""
        # Implementar detecção de padrões baseados em tempo
        # Por exemplo, padrões por hora do dia, dia da semana, etc.
        pass
    
    def _count_pattern_frequency(self, pattern: str, colors: List[str]) -> int:
        """Conta a frequência de um padrão."""
        count = 0
        pattern_length = len(pattern)
        
        for i in range(len(colors) - pattern_length + 1):
            if ''.join(colors[i:i+pattern_length]) == pattern:
                count += 1
        
        return count
    
    def _update_existing_patterns(self) -> None:
        """Atualiza padrões existentes com novos dados."""
        for pattern in self.learned_patterns.values():
            # Aplicar decay na confiança
            pattern.confidence *= self.decay_factor
            
            # Atualizar timestamp
            pattern.updated_at = datetime.now()
    
    def _cleanup_obsolete_patterns(self) -> None:
        """Remove padrões obsoletos ou com baixa performance."""
        to_remove = []
        
        for pattern_id, pattern in self.learned_patterns.items():
            # Remover padrões com confiança muito baixa
            if pattern.confidence < 0.1:
                to_remove.append(pattern_id)
            
            # Remover padrões muito antigos sem uso
            days_since_update = (datetime.now() - pattern.updated_at).days
            if days_since_update > 7 and pattern.total_predictions == 0:
                to_remove.append(pattern_id)
        
        for pattern_id in to_remove:
            del self.learned_patterns[pattern_id]
            logger.info(f"Padrão obsoleto removido: {pattern_id}")
    
    def _analyze_current_patterns(self) -> List[LearnedPattern]:
        """Analisa padrões atuais nos dados recentes."""
        if len(self.data_history) < 10:
            return []
        
        recent_colors = [r.get('color') for r in list(self.data_history)[-20:]]
        active_patterns = []
        
        for pattern in self.learned_patterns.values():
            if pattern.confidence > self.min_confidence_threshold:
                # Verificar se o padrão está ativo nos dados recentes
                if self._is_pattern_active(pattern, recent_colors):
                    active_patterns.append(pattern)
        
        return active_patterns
    
    def _is_pattern_active(self, pattern: LearnedPattern, colors: List[str]) -> bool:
        """Verifica se um padrão está ativo nos dados recentes."""
        pattern_data = pattern.pattern_data
        
        if pattern.pattern_type == PatternType.SEQUENCE:
            sequence = pattern_data.get('sequence', [])
            pattern_key = ''.join(sequence)
            return pattern_key in ''.join(colors)
        
        elif pattern.pattern_type == PatternType.ALTERNATION:
            # Verificar alternações recentes
            alternations = 0
            for i in range(1, len(colors)):
                if colors[i] != colors[i-1]:
                    alternations += 1
            return alternations >= pattern_data.get('alternation_length', 3)
        
        elif pattern.pattern_type == PatternType.FREQUENCY:
            color = pattern_data.get('color')
            freq_type = pattern_data.get('type')
            count = colors.count(color)
            frequency = count / len(colors)
            
            if freq_type == 'high':
                return frequency > 0.4
            else:
                return frequency < 0.2
        
        return False
    
    def _combine_pattern_predictions(self, patterns: List[LearnedPattern]) -> Dict[str, Any]:
        """Combina predições de diferentes padrões."""
        if not patterns:
            return self._get_default_prediction()
        
        # Calcular pesos baseados na confiança e taxa de sucesso
        weights = []
        predictions = []
        
        for pattern in patterns:
            weight = pattern.confidence * (0.5 + pattern.success_rate * 0.5)
            weights.append(weight)
            
            # Gerar predição baseada no padrão
            prediction = self._generate_pattern_prediction(pattern)
            predictions.append(prediction)
        
        # Normalizar pesos
        total_weight = sum(weights)
        if total_weight == 0:
            return self._get_default_prediction()
        
        weights = [w / total_weight for w in weights]
        
        # Combinar predições
        color_probs = {'red': 0.0, 'black': 0.0, 'white': 0.0}
        
        for i, prediction in enumerate(predictions):
            color = prediction.get('color', 'red')
            confidence = prediction.get('confidence', 0.0)
            color_probs[color] += weights[i] * confidence
        
        # Determinar cor com maior probabilidade
        predicted_color = max(color_probs.keys(), key=lambda k: color_probs[k])
        confidence = color_probs[predicted_color]
        
        return {
            'color': predicted_color,
            'confidence': confidence,
            'pattern_id': 'combined',
            'patterns_used': [p.pattern_id for p in patterns],
            'reasoning': f"Baseado em {len(patterns)} padrões ativos"
        }
    
    def _generate_pattern_prediction(self, pattern: LearnedPattern) -> Dict[str, Any]:
        """Gera uma predição baseada em um padrão específico."""
        pattern_data = pattern.pattern_data
        
        if pattern.pattern_type == PatternType.SEQUENCE:
            sequence = pattern_data.get('sequence', [])
            if len(sequence) >= 2:
                # Predizer próxima cor baseada na sequência
                last_color = sequence[-1]
                if last_color == 'red':
                    predicted = 'black'
                elif last_color == 'black':
                    predicted = 'white'
                else:
                    predicted = 'red'
                
                return {
                    'color': predicted,
                    'confidence': pattern.confidence * 0.8
                }
        
        elif pattern.pattern_type == PatternType.ALTERNATION:
            # Predizer quebra da alternação
            return {
                'color': 'white',  # Branco é menos comum, pode quebrar alternação
                'confidence': pattern.confidence * 0.6
            }
        
        elif pattern.pattern_type == PatternType.FREQUENCY:
            color = pattern_data.get('color')
            freq_type = pattern_data.get('type')
            
            if freq_type == 'high':
                # Se uma cor está muito frequente, predizer mudança
                if color == 'red':
                    predicted = 'black'
                elif color == 'black':
                    predicted = 'white'
                else:
                    predicted = 'red'
            else:
                predicted = color  # Se está pouco frequente, pode voltar
            
            return {
                'color': predicted,
                'confidence': pattern.confidence * 0.7
            }
        
        return {
            'color': 'red',
            'confidence': 0.33
        }
    
    def _get_default_prediction(self) -> Dict[str, Any]:
        """Retorna uma predição padrão quando não há padrões suficientes."""
        return {
            'predicted_color': 'red',
            'confidence': 0.33,
            'pattern_id': 'default',
            'patterns_used': [],
            'reasoning': 'Predição padrão - dados insuficientes',
            'timestamp': datetime.now().isoformat()
        }
