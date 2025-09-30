#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Estratégias Configuráveis para Blaze Double
"""

import logging
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """Tipos de estratégia"""
    PATTERN_BASED = "pattern_based"
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    HYBRID = "hybrid"

@dataclass
class StrategySignal:
    """Sinal gerado por uma estratégia"""
    action: str  # 'bet', 'skip', 'wait'
    predicted_color: str
    confidence: float
    reasoning: str
    risk_level: str  # 'low', 'medium', 'high'
    bet_size_multiplier: float = 1.0
    metadata: Dict[str, Any] = None

class BaseStrategy(ABC):
    """Classe base para todas as estratégias"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.max_confidence = self.config.get('max_confidence', 0.95)
        self.risk_level = self.config.get('risk_level', 'medium')
        
        # Histórico de sinais
        self.signal_history = []
        self.performance_metrics = {
            'total_signals': 0,
            'correct_signals': 0,
            'accuracy': 0.0,
            'last_updated': None
        }
    
    @abstractmethod
    def get_signal(self, historical_data: List[Dict], current_data: Dict) -> Optional[StrategySignal]:
        """Gera sinal baseado nos dados históricos e atuais"""
        pass
    
    def update_performance(self, signal: StrategySignal, actual_result: Dict):
        """Atualiza métricas de performance da estratégia"""
        self.performance_metrics['total_signals'] += 1
        
        # Verificar se o sinal foi correto
        if signal.action == 'bet':
            predicted_color = signal.predicted_color
            actual_color = self._get_color(actual_result.get('roll', 0))
            
            if predicted_color == actual_color:
                self.performance_metrics['correct_signals'] += 1
        
        # Calcular precisão
        if self.performance_metrics['total_signals'] > 0:
            self.performance_metrics['accuracy'] = (
                self.performance_metrics['correct_signals'] / 
                self.performance_metrics['total_signals']
            )
        
        self.performance_metrics['last_updated'] = datetime.now()
    
    def _get_color(self, roll: int) -> str:
        """Determina a cor baseada no número"""
        if roll == 0:
            return 'white'
        elif 1 <= roll <= 7:
            return 'red'
        else:
            return 'black'
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance da estratégia"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'total_signals': self.performance_metrics['total_signals'],
            'accuracy': self.performance_metrics['accuracy'],
            'last_updated': self.performance_metrics['last_updated']
        }

class PatternBasedStrategy(BaseStrategy):
    """Estratégia baseada em padrões"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.pattern_types = self.config.get('pattern_types', ['sequence', 'alternation'])
        self.min_pattern_length = self.config.get('min_pattern_length', 3)
        self.pattern_weights = self.config.get('pattern_weights', {})
    
    def get_signal(self, historical_data: List[Dict], current_data: Dict) -> Optional[StrategySignal]:
        """Gera sinal baseado em padrões"""
        if not historical_data or len(historical_data) < self.min_pattern_length:
            return None
        
        # Analisar padrões
        patterns = self._analyze_patterns(historical_data)
        
        if not patterns:
            return None
        
        # Escolher melhor padrão
        best_pattern = max(patterns, key=lambda p: p['confidence'])
        
        if best_pattern['confidence'] < self.min_confidence:
            return None
        
        # Gerar sinal
        predicted_color = best_pattern['predicted_color']
        confidence = min(best_pattern['confidence'], self.max_confidence)
        reasoning = f"Padrão {best_pattern['type']} detectado: {best_pattern['description']}"
        
        return StrategySignal(
            action='bet',
            predicted_color=predicted_color,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=self.risk_level,
            bet_size_multiplier=self._calculate_bet_multiplier(confidence),
            metadata={'pattern': best_pattern}
        )
    
    def _analyze_patterns(self, data: List[Dict]) -> List[Dict]:
        """Analisa padrões nos dados"""
        patterns = []
        
        # Padrão de sequência
        if 'sequence' in self.pattern_types:
            seq_pattern = self._detect_sequence_pattern(data)
            if seq_pattern:
                patterns.append(seq_pattern)
        
        # Padrão de alternância
        if 'alternation' in self.pattern_types:
            alt_pattern = self._detect_alternation_pattern(data)
            if alt_pattern:
                patterns.append(alt_pattern)
        
        # Padrão de números quentes/frios
        if 'hot_cold' in self.pattern_types:
            hc_pattern = self._detect_hot_cold_pattern(data)
            if hc_pattern:
                patterns.append(hc_pattern)
        
        return patterns
    
    def _detect_sequence_pattern(self, data: List[Dict]) -> Optional[Dict]:
        """Detecta padrão de sequência"""
        if len(data) < 4:
            return None
        
        colors = [self._get_color(r.get('roll', 0)) for r in data[-10:]]
        
        # Verificar sequências de mesma cor
        for length in range(3, min(6, len(colors))):
            if len(set(colors[-length:])) == 1:  # Todas iguais
                color = colors[-1]
                predicted_color = 'white' if color != 'white' else 'red'
                
                return {
                    'type': 'sequence',
                    'predicted_color': predicted_color,
                    'confidence': min(0.9, 0.5 + (length - 3) * 0.1),
                    'description': f'Sequência de {length} {color}s consecutivos'
                }
        
        return None
    
    def _detect_alternation_pattern(self, data: List[Dict]) -> Optional[Dict]:
        """Detecta padrão de alternância"""
        if len(data) < 6:
            return None
        
        colors = [self._get_color(r.get('roll', 0)) for r in data[-8:]]
        
        # Verificar alternância
        is_alternating = True
        for i in range(1, len(colors)):
            if colors[i] == colors[i-1]:
                is_alternating = False
                break
        
        if is_alternating and len(colors) >= 4:
            last_color = colors[-1]
            predicted_color = 'black' if last_color == 'red' else 'red'
            
            return {
                'type': 'alternation',
                'predicted_color': predicted_color,
                'confidence': min(0.8, 0.4 + len(colors) * 0.05),
                'description': f'Alternância detectada ({len(colors)} cores)'
            }
        
        return None
    
    def _detect_hot_cold_pattern(self, data: List[Dict]) -> Optional[Dict]:
        """Detecta padrão de números quentes/frios"""
        if len(data) < 20:
            return None
        
        # Analisar últimos 20 resultados
        recent_data = data[-20:]
        color_counts = {}
        
        for result in recent_data:
            color = self._get_color(result.get('roll', 0))
            color_counts[color] = color_counts.get(color, 0) + 1
        
        # Encontrar cor mais frequente
        most_frequent = max(color_counts.items(), key=lambda x: x[1])
        least_frequent = min(color_counts.items(), key=lambda x: x[1])
        
        if most_frequent[1] >= 8:  # Pelo menos 8 ocorrências
            predicted_color = least_frequent[0]  # Apostar na menos frequente
            
            return {
                'type': 'hot_cold',
                'predicted_color': predicted_color,
                'confidence': min(0.7, 0.3 + (most_frequent[1] - 6) * 0.05),
                'description': f'{most_frequent[0]} quente ({most_frequent[1]}/20), apostar em {predicted_color}'
            }
        
        return None
    
    def _calculate_bet_multiplier(self, confidence: float) -> float:
        """Calcula multiplicador de aposta baseado na confiança"""
        if confidence >= 0.8:
            return 1.5
        elif confidence >= 0.7:
            return 1.2
        elif confidence >= 0.6:
            return 1.0
        else:
            return 0.8

class StatisticalStrategy(BaseStrategy):
    """Estratégia baseada em análise estatística"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.window_size = self.config.get('window_size', 50)
        self.statistical_tests = self.config.get('statistical_tests', ['mean_reversion', 'momentum'])
    
    def get_signal(self, historical_data: List[Dict], current_data: Dict) -> Optional[StrategySignal]:
        """Gera sinal baseado em análise estatística"""
        if len(historical_data) < self.window_size:
            return None
        
        # Analisar dados recentes
        recent_data = historical_data[-self.window_size:]
        colors = [self._get_color(r.get('roll', 0)) for r in recent_data]
        
        # Aplicar testes estatísticos
        signals = []
        
        if 'mean_reversion' in self.statistical_tests:
            mr_signal = self._mean_reversion_test(colors)
            if mr_signal:
                signals.append(mr_signal)
        
        if 'momentum' in self.statistical_tests:
            mom_signal = self._momentum_test(colors)
            if mom_signal:
                signals.append(mom_signal)
        
        if not signals:
            return None
        
        # Escolher melhor sinal
        best_signal = max(signals, key=lambda s: s['confidence'])
        
        if best_signal['confidence'] < self.min_confidence:
            return None
        
        return StrategySignal(
            action='bet',
            predicted_color=best_signal['predicted_color'],
            confidence=best_signal['confidence'],
            reasoning=best_signal['reasoning'],
            risk_level=self.risk_level,
            bet_size_multiplier=self._calculate_bet_multiplier(best_signal['confidence']),
            metadata={'test': best_signal['test']}
        )
    
    def _mean_reversion_test(self, colors: List[str]) -> Optional[Dict]:
        """Teste de reversão à média"""
        if len(colors) < 10:
            return None
        
        # Calcular distribuição de cores
        color_counts = {}
        for color in colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        total = len(colors)
        expected = total / 3  # Esperado igual distribuição
        
        # Encontrar cor mais desbalanceada
        max_deviation = 0
        most_deviant_color = None
        
        for color, count in color_counts.items():
            deviation = abs(count - expected) / expected
            if deviation > max_deviation:
                max_deviation = deviation
                most_deviant_color = color
        
        if max_deviation > 0.3:  # Desvio significativo
            # Apostar na cor oposta (menos frequente)
            other_colors = [c for c in ['red', 'black', 'white'] if c != most_deviant_color]
            predicted_color = min(other_colors, key=lambda c: color_counts.get(c, 0))
            
            return {
                'test': 'mean_reversion',
                'predicted_color': predicted_color,
                'confidence': min(0.8, 0.4 + max_deviation),
                'reasoning': f'Reversão à média: {most_deviant_color} muito frequente ({color_counts[most_deviant_color]}/{total})'
            }
        
        return None
    
    def _momentum_test(self, colors: List[str]) -> Optional[Dict]:
        """Teste de momentum"""
        if len(colors) < 6:
            return None
        
        # Analisar tendência recente
        recent_colors = colors[-6:]
        color_counts = {}
        for color in recent_colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        # Se uma cor domina nos últimos 6
        most_frequent = max(color_counts.items(), key=lambda x: x[1])
        if most_frequent[1] >= 4:  # Pelo menos 4 de 6
            predicted_color = most_frequent[0]  # Continuar momentum
            
            return {
                'test': 'momentum',
                'predicted_color': predicted_color,
                'confidence': min(0.7, 0.3 + (most_frequent[1] - 3) * 0.1),
                'reasoning': f'Momentum: {most_frequent[0]} dominando ({most_frequent[1]}/6)'
            }
        
        return None
    
    def _calculate_bet_multiplier(self, confidence: float) -> float:
        """Calcula multiplicador de aposta"""
        return min(1.5, 0.5 + confidence)

class StrategyEngine:
    """Engine para gerenciar múltiplas estratégias"""
    
    def __init__(self):
        self.strategies = {}
        self.active_strategies = []
        self.signal_history = []
        
        logger.info("Strategy Engine inicializado")
    
    def add_strategy(self, strategy: BaseStrategy):
        """Adiciona uma estratégia"""
        self.strategies[strategy.name] = strategy
        if strategy.enabled:
            self.active_strategies.append(strategy)
        
        logger.info(f"Estratégia adicionada: {strategy.name}")
    
    def remove_strategy(self, name: str):
        """Remove uma estratégia"""
        if name in self.strategies:
            del self.strategies[name]
            self.active_strategies = [s for s in self.active_strategies if s.name != name]
            logger.info(f"Estratégia removida: {name}")
    
    def enable_strategy(self, name: str):
        """Habilita uma estratégia"""
        if name in self.strategies:
            strategy = self.strategies[name]
            strategy.enabled = True
            if strategy not in self.active_strategies:
                self.active_strategies.append(strategy)
            logger.info(f"Estratégia habilitada: {name}")
    
    def disable_strategy(self, name: str):
        """Desabilita uma estratégia"""
        if name in self.strategies:
            strategy = self.strategies[name]
            strategy.enabled = False
            self.active_strategies = [s for s in self.active_strategies if s.name != name]
            logger.info(f"Estratégia desabilitada: {name}")
    
    def get_combined_signal(self, historical_data: List[Dict], current_data: Dict) -> Optional[StrategySignal]:
        """Obtém sinal combinado de todas as estratégias ativas"""
        if not self.active_strategies:
            return None
        
        signals = []
        
        # Obter sinais de todas as estratégias ativas
        for strategy in self.active_strategies:
            try:
                signal = strategy.get_signal(historical_data, current_data)
                if signal:
                    signals.append((strategy.name, signal))
            except Exception as e:
                logger.error(f"Erro na estratégia {strategy.name}: {e}")
        
        if not signals:
            return None
        
        # Combinar sinais
        return self._combine_signals(signals)
    
    def _combine_signals(self, signals: List[Tuple[str, StrategySignal]]) -> StrategySignal:
        """Combina sinais de múltiplas estratégias"""
        if len(signals) == 1:
            return signals[0][1]
        
        # Agrupar por cor predita
        color_votes = {}
        total_confidence = 0
        
        for strategy_name, signal in signals:
            color = signal.predicted_color
            confidence = signal.confidence
            
            if color not in color_votes:
                color_votes[color] = {
                    'count': 0,
                    'total_confidence': 0,
                    'strategies': []
                }
            
            color_votes[color]['count'] += 1
            color_votes[color]['total_confidence'] += confidence
            color_votes[color]['strategies'].append(strategy_name)
            total_confidence += confidence
        
        # Escolher cor com mais votos e maior confiança
        best_color = max(color_votes.items(), 
                        key=lambda x: (x[1]['count'], x[1]['total_confidence']))
        
        predicted_color = best_color[0]
        avg_confidence = best_color[1]['total_confidence'] / best_color[1]['count']
        combined_confidence = min(0.95, avg_confidence * (1 + best_color[1]['count'] * 0.1))
        
        # Gerar reasoning
        strategies_used = best_color[1]['strategies']
        reasoning = f"Consenso de {len(strategies_used)} estratégias: {', '.join(strategies_used)}"
        
        # Determinar nível de risco
        if combined_confidence >= 0.8:
            risk_level = 'low'
        elif combined_confidence >= 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return StrategySignal(
            action='bet',
            predicted_color=predicted_color,
            confidence=combined_confidence,
            reasoning=reasoning,
            risk_level=risk_level,
            bet_size_multiplier=1.0 + (len(strategies_used) - 1) * 0.2,
            metadata={
                'strategies_used': strategies_used,
                'vote_count': best_color[1]['count'],
                'total_strategies': len(signals)
            }
        )
    
    def update_performance(self, signal: StrategySignal, actual_result: Dict):
        """Atualiza performance de todas as estratégias"""
        for strategy in self.active_strategies:
            strategy.update_performance(signal, actual_result)
        
        # Registrar no histórico
        self.signal_history.append({
            'timestamp': datetime.now(),
            'signal': signal,
            'actual_result': actual_result
        })
    
    def get_strategy_performance(self) -> Dict[str, Dict]:
        """Retorna performance de todas as estratégias"""
        performance = {}
        for name, strategy in self.strategies.items():
            performance[name] = strategy.get_performance_summary()
        
        return performance
    
    def export_strategies_config(self, filename: str = None) -> str:
        """Exporta configuração das estratégias"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"strategies_config_{timestamp}.json"
        
        config = {
            'timestamp': datetime.now().isoformat(),
            'strategies': {}
        }
        
        for name, strategy in self.strategies.items():
            config['strategies'][name] = {
                'type': strategy.__class__.__name__,
                'enabled': strategy.enabled,
                'config': strategy.config,
                'performance': strategy.get_performance_summary()
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Configuração das estratégias exportada para: {filename}")
        return filename

