#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Callbacks de Reavaliação para diferentes sistemas.
Implementa a lógica de reset e reavaliação para cada componente.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PatternAnalyzerReassessmentCallback:
    """Callback de reavaliação para o PatternAnalyzer."""
    
    def __init__(self, pattern_analyzer):
        """
        Inicializa o callback.
        
        Args:
            pattern_analyzer: Instância do PatternAnalyzer
        """
        self.pattern_analyzer = pattern_analyzer
        self.logger = logging.getLogger(f"{__name__}.PatternAnalyzer")
    
    def __call__(self, reassessment_context: Dict[str, Any]) -> None:
        """
        Executa reavaliação do PatternAnalyzer.
        
        Args:
            reassessment_context: Contexto da reavaliação
        """
        try:
            trigger = reassessment_context.get('trigger')
            context = reassessment_context.get('context', {})
            
            self.logger.info(f"Reavaliando PatternAnalyzer - Gatilho: {trigger}")
            
            # Reset de análises anteriores
            self._reset_pattern_analysis()
            
            # Reanalisar dados recentes
            self._reanalyze_recent_data(context)
            
            # Detectar novos padrões
            self._detect_fresh_patterns(context)
            
            self.logger.info("Reavaliação do PatternAnalyzer concluída")
            
        except Exception as e:
            self.logger.error(f"Erro na reavaliação do PatternAnalyzer: {e}")
    
    def _reset_pattern_analysis(self) -> None:
        """Reseta análises de padrões anteriores."""
        try:
            # Limpar cache de análises
            if hasattr(self.pattern_analyzer, 'analysis_cache'):
                self.pattern_analyzer.analysis_cache.clear()
            
            # Reset de gatilhos
            if hasattr(self.pattern_analyzer, 'trigger_cache'):
                self.pattern_analyzer.trigger_cache.clear()
            
            # Reset de estatísticas temporais
            if hasattr(self.pattern_analyzer, 'temporal_stats'):
                self.pattern_analyzer.temporal_stats = {}
            
            self.logger.info("Análises de padrões resetadas")
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar análises: {e}")
    
    def _reanalyze_recent_data(self, context: Dict[str, Any]) -> None:
        """Reanalisa dados recentes."""
        try:
            # Obter dados recentes (últimos 20 resultados)
            if hasattr(self.pattern_analyzer, 'data_history'):
                recent_data = list(self.pattern_analyzer.data_history)[-20:]
                
                if len(recent_data) >= 10:
                    # Reanalisar com foco em padrões frescos
                    fresh_analysis = self.pattern_analyzer.analyze_data(recent_data)
                    
                    # Atualizar cache com análise fresca
                    if hasattr(self.pattern_analyzer, 'analysis_cache'):
                        self.pattern_analyzer.analysis_cache['fresh_analysis'] = fresh_analysis
                        self.pattern_analyzer.analysis_cache['fresh_analysis_timestamp'] = datetime.now()
                    
                    self.logger.info(f"Dados recentes reanalisados: {len(recent_data)} resultados")
            
        except Exception as e:
            self.logger.error(f"Erro ao reanalisar dados recentes: {e}")
    
    def _detect_fresh_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões frescos."""
        try:
            # Detectar padrões baseados no contexto da reavaliação
            trigger = context.get('trigger')
            
            if trigger == 'prediction_validated':
                result = context.get('result')
                if result == 'incorrect':
                    # Padrão foi quebrado, procurar novos padrões
                    self._detect_pattern_break_patterns(context)
                elif result == 'correct':
                    # Padrão funcionou, procurar continuação
                    self._detect_pattern_continuation_patterns(context)
            
            elif trigger == 'new_sequence_started':
                # Nova sequência detectada, analisar padrões de sequência
                self._detect_sequence_patterns(context)
            
            elif trigger == 'performance_drop':
                # Performance caiu, procurar padrões alternativos
                self._detect_alternative_patterns(context)
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões frescos: {e}")
    
    def _detect_pattern_break_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões após quebra de padrão anterior."""
        try:
            # Implementar lógica específica para detectar novos padrões
            # após quebra de um padrão anterior
            self.logger.info("Detectando padrões após quebra de padrão anterior")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões de quebra: {e}")
    
    def _detect_pattern_continuation_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões de continuação."""
        try:
            # Implementar lógica para detectar continuação de padrões
            self.logger.info("Detectando padrões de continuação")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões de continuação: {e}")
    
    def _detect_sequence_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões de sequência."""
        try:
            # Implementar lógica para detectar padrões de sequência
            self.logger.info("Detectando padrões de sequência")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões de sequência: {e}")
    
    def _detect_alternative_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões alternativos."""
        try:
            # Implementar lógica para detectar padrões alternativos
            self.logger.info("Detectando padrões alternativos")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões alternativos: {e}")


class DualPatternDetectorReassessmentCallback:
    """Callback de reavaliação para o DualPatternDetector."""
    
    def __init__(self, dual_pattern_detector):
        """
        Inicializa o callback.
        
        Args:
            dual_pattern_detector: Instância do DualPatternDetector
        """
        self.dual_pattern_detector = dual_pattern_detector
        self.logger = logging.getLogger(f"{__name__}.DualPatternDetector")
    
    def __call__(self, reassessment_context: Dict[str, Any]) -> None:
        """
        Executa reavaliação do DualPatternDetector.
        
        Args:
            reassessment_context: Contexto da reavaliação
        """
        try:
            trigger = reassessment_context.get('trigger')
            context = reassessment_context.get('context', {})
            
            self.logger.info(f"Reavaliando DualPatternDetector - Gatilho: {trigger}")
            
            # Reset de padrões dual anteriores
            self._reset_dual_patterns()
            
            # Reanalisar interações entre cores
            self._reanalyze_color_interactions(context)
            
            # Detectar novos padrões dual
            self._detect_fresh_dual_patterns(context)
            
            self.logger.info("Reavaliação do DualPatternDetector concluída")
            
        except Exception as e:
            self.logger.error(f"Erro na reavaliação do DualPatternDetector: {e}")
    
    def _reset_dual_patterns(self) -> None:
        """Reseta padrões dual anteriores."""
        try:
            # Limpar padrões com baixa confiança
            patterns_to_remove = []
            
            for pattern_id, pattern in self.dual_pattern_detector.dual_patterns.items():
                if pattern.confidence < 0.3:  # Limiar mais baixo para reset
                    patterns_to_remove.append(pattern_id)
            
            for pattern_id in patterns_to_remove:
                del self.dual_pattern_detector.dual_patterns[pattern_id]
            
            # Reset de análises específicas por cor
            self.dual_pattern_detector.red_analysis['sequences'].clear()
            self.dual_pattern_detector.black_analysis['sequences'].clear()
            
            # Reset de interações
            self.dual_pattern_detector.color_interaction['alternation_patterns'].clear()
            
            self.logger.info(f"Resetados {len(patterns_to_remove)} padrões dual")
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar padrões dual: {e}")
    
    def _reanalyze_color_interactions(self, context: Dict[str, Any]) -> None:
        """Reanalisa interações entre cores."""
        try:
            # Obter dados recentes para reanálise
            recent_data = list(self.dual_pattern_detector.data_history)[-30:]
            
            if len(recent_data) >= 15:
                # Reanalisar interações com foco em padrões frescos
                colors = [r.get('color') for r in recent_data]
                
                # Recalcular alternações
                new_alternations = []
                for i in range(1, len(colors)):
                    if colors[i] != colors[i-1]:
                        alternation = f"{colors[i-1]}_{colors[i]}"
                        new_alternations.append(alternation)
                
                # Atualizar padrões de alternação
                self.dual_pattern_detector.color_interaction['alternation_patterns'] = new_alternations
                
                self.logger.info(f"Interações reanalisadas: {len(new_alternations)} alternações")
            
        except Exception as e:
            self.logger.error(f"Erro ao reanalisar interações: {e}")
    
    def _detect_fresh_dual_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta novos padrões dual."""
        try:
            trigger = context.get('trigger')
            
            if trigger == 'prediction_validated':
                result = context.get('result')
                if result == 'incorrect':
                    # Padrão dual foi quebrado, procurar novos padrões
                    self._detect_dual_pattern_break_patterns(context)
                elif result == 'correct':
                    # Padrão dual funcionou, procurar continuação
                    self._detect_dual_pattern_continuation_patterns(context)
            
            elif trigger == 'new_sequence_started':
                # Nova sequência, analisar padrões dual de sequência
                self._detect_dual_sequence_patterns(context)
            
            # Sempre detectar padrões frescos baseados em dados recentes
            self.dual_pattern_detector._detect_new_patterns()
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões dual frescos: {e}")
    
    def _detect_dual_pattern_break_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões dual após quebra."""
        try:
            # Implementar lógica específica para padrões dual após quebra
            self.logger.info("Detectando padrões dual após quebra")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões dual de quebra: {e}")
    
    def _detect_dual_pattern_continuation_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta continuação de padrões dual."""
        try:
            # Implementar lógica para continuação de padrões dual
            self.logger.info("Detectando continuação de padrões dual")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar continuação de padrões dual: {e}")
    
    def _detect_dual_sequence_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões dual de sequência."""
        try:
            # Implementar lógica para padrões dual de sequência
            self.logger.info("Detectando padrões dual de sequência")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões dual de sequência: {e}")


class AdaptiveLearnerReassessmentCallback:
    """Callback de reavaliação para o AdaptiveLearner."""
    
    def __init__(self, adaptive_learner):
        """
        Inicializa o callback.
        
        Args:
            adaptive_learner: Instância do AdaptiveLearner
        """
        self.adaptive_learner = adaptive_learner
        self.logger = logging.getLogger(f"{__name__}.AdaptiveLearner")
    
    def __call__(self, reassessment_context: Dict[str, Any]) -> None:
        """
        Executa reavaliação do AdaptiveLearner.
        
        Args:
            reassessment_context: Contexto da reavaliação
        """
        try:
            trigger = reassessment_context.get('trigger')
            context = reassessment_context.get('context', {})
            
            self.logger.info(f"Reavaliando AdaptiveLearner - Gatilho: {trigger}")
            
            # Reset de padrões aprendidos com baixa performance
            self._reset_low_performance_patterns()
            
            # Reaprender com dados recentes
            self._relearn_from_recent_data(context)
            
            # Detectar novos padrões de aprendizado
            self._detect_fresh_learning_patterns(context)
            
            self.logger.info("Reavaliação do AdaptiveLearner concluída")
            
        except Exception as e:
            self.logger.error(f"Erro na reavaliação do AdaptiveLearner: {e}")
    
    def _reset_low_performance_patterns(self) -> None:
        """Reseta padrões com baixa performance."""
        try:
            # Remover padrões com taxa de sucesso muito baixa
            patterns_to_remove = []
            
            for pattern_id, pattern in self.adaptive_learner.learned_patterns.items():
                if pattern.total_predictions > 0 and pattern.success_rate < 0.2:
                    patterns_to_remove.append(pattern_id)
            
            for pattern_id in patterns_to_remove:
                del self.adaptive_learner.learned_patterns[pattern_id]
            
            self.logger.info(f"Resetados {len(patterns_to_remove)} padrões com baixa performance")
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar padrões de baixa performance: {e}")
    
    def _relearn_from_recent_data(self, context: Dict[str, Any]) -> None:
        """Reaprende com dados recentes."""
        try:
            # Obter dados recentes para reaprendizado
            recent_data = list(self.adaptive_learner.data_history)[-20:]  # Era 50
            
            if len(recent_data) >= 5:  # Era 20
                # Reaprender padrões com dados frescos
                self.adaptive_learner._learn_from_new_data()
                
                self.logger.info(f"Reaprendizado com {len(recent_data)} dados recentes")
            
        except Exception as e:
            self.logger.error(f"Erro ao reaprender com dados recentes: {e}")
    
    def _detect_fresh_learning_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta novos padrões de aprendizado."""
        try:
            trigger = context.get('trigger')
            
            if trigger == 'prediction_validated':
                result = context.get('result')
                if result == 'incorrect':
                    # Padrão de aprendizado falhou, procurar novos padrões
                    self._detect_learning_pattern_break_patterns(context)
                elif result == 'correct':
                    # Padrão de aprendizado funcionou, procurar continuação
                    self._detect_learning_pattern_continuation_patterns(context)
            
            elif trigger == 'performance_drop':
                # Performance caiu, ajustar aprendizado
                self._adjust_learning_parameters(context)
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões de aprendizado frescos: {e}")
    
    def _detect_learning_pattern_break_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta padrões de aprendizado após quebra."""
        try:
            # Implementar lógica específica para padrões de aprendizado após quebra
            self.logger.info("Detectando padrões de aprendizado após quebra")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar padrões de aprendizado de quebra: {e}")
    
    def _detect_learning_pattern_continuation_patterns(self, context: Dict[str, Any]) -> None:
        """Detecta continuação de padrões de aprendizado."""
        try:
            # Implementar lógica para continuação de padrões de aprendizado
            self.logger.info("Detectando continuação de padrões de aprendizado")
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar continuação de padrões de aprendizado: {e}")
    
    def _adjust_learning_parameters(self, context: Dict[str, Any]) -> None:
        """Ajusta parâmetros de aprendizado."""
        try:
            # Ajustar parâmetros baseados na queda de performance
            accuracy_drop = context.get('accuracy_drop', 0)
            
            if accuracy_drop > 0.2:  # Queda significativa
                # Aumentar limiar de confiança
                self.adaptive_learner.min_confidence_threshold = min(0.8, 
                    self.adaptive_learner.min_confidence_threshold + 0.1)
                
                # Reduzir taxa de aprendizado
                self.adaptive_learner.learning_rate *= 0.9
                
                self.logger.info("Parâmetros de aprendizado ajustados devido à queda de performance")
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar parâmetros de aprendizado: {e}")
