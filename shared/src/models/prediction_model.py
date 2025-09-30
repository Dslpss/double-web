#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo de predição para o Double da Blaze.
"""

import logging
from collections import Counter, defaultdict, deque

class PredictionModel:
    """Classe para predição de resultados do Double da Blaze."""
    
    def __init__(self, config=None):
        """
        Inicializa o modelo de predição.
        
        Args:
            config (dict): Configurações do modelo de predição
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.result_history = []
        # parâmetros configuráveis
        self.window_size = int(self.config.get('history_size', 100))
        # estruturas para markov de ordem 1 (cor->cor)
        self.color_transitions = defaultdict(lambda: Counter())
        self.color_history = deque(maxlen=self.window_size)
        # contagem por cor
        self.color_counts = Counter()
        self.prediction_history = []
        self.accuracy = 0.0
        
    def update_history(self, results):
        """
        Atualiza o histórico de resultados.
        
        Args:
            results (list): Lista de resultados recentes
        """
        self.result_history = results
        # reconstruir estruturas
        self.color_transitions.clear()
        self.color_history = deque(maxlen=self.window_size)
        self.color_counts = Counter()
        for r in results[-self.window_size:]:
            roll = r.get('roll')
            color = 'white' if roll == 0 else ('red' if 1 <= roll <= 7 else 'black')
            if self.color_history:
                prev = self.color_history[-1]
                self.color_transitions[prev][color] += 1
            self.color_history.append(color)
            self.color_counts[color] += 1
        self.logger.info(f"Histórico de resultados atualizado com {len(results)} entradas")
        
    def predict_next_color(self):
        """
        Prediz a próxima cor com base nos dados históricos.
        
        Returns:
            dict: Dicionário com as probabilidades de cada cor
        """
        if not self.result_history:
            return {"red": 0.33, "black": 0.33, "white": 0.33}
        
        # Se tivermos histórico, combine frequência marginal com transição condicional
        total = sum(self.color_counts.values())
        if total == 0:
            return {"red": 0.33, "black": 0.33, "white": 0.33}

        marginal = {c: self.color_counts.get(c, 0) / total for c in ('red', 'black', 'white')}

        # transição condicional a partir da última cor observada
        last = self.color_history[-1] if self.color_history else None
        cond = {c: 1/3 for c in ('red','black','white')}
        if last:
            trans = self.color_transitions.get(last, {})
            s = sum(trans.values())
            if s > 0:
                for c in ('red','black','white'):
                    cond[c] = trans.get(c, 0) / s

        # combinar: peso ajustável entre marginal e condicional
        w_cond = float(self.config.get('transition_weight', 0.6))
        w_marg = 1.0 - w_cond
        probs = {c: w_marg * marginal.get(c, 0) + w_cond * cond.get(c, 1/3) for c in ('red','black','white')}
        # normalizar
        s = sum(probs.values())
        if s <= 0:
            return {"red": 0.33, "black": 0.33, "white": 0.33}
        for k in probs:
            probs[k] = probs[k] / s
        return probs

    def record_result(self, result: dict):
        """Registra um novo resultado (chamar ao receber eventos em tempo real)."""
        roll = result.get('roll')
        color = 'white' if roll == 0 else ('red' if 1 <= roll <= 7 else 'black')
        # atualizar estruturas
        if self.color_history:
            prev = self.color_history[-1]
            self.color_transitions[prev][color] += 1
        self.color_history.append(color)
        self.color_counts[color] += 1
        self.result_history.append(result)
        # manter janela
        if len(self.result_history) > self.window_size:
            old = self.result_history.pop(0)
            # nota: não decrementar color_counts nem transições para simplificar
        return self.predict_next_color()
    
    def evaluate_prediction(self, prediction, actual_result):
        """
        Avalia a precisão da predição.
        
        Args:
            prediction (dict): Predição feita
            actual_result (int): Resultado real
            
        Returns:
            float: Precisão da predição (0 a 1)
        """
        # Implementação básica
        return 0.0
    
    def get_performance_metrics(self):
        """
        Retorna métricas de desempenho do modelo.
        
        Returns:
            dict: Métricas de desempenho
        """
        return {
            "accuracy": self.accuracy,
            "predictions_made": len(self.prediction_history),
            "correct_predictions": 0
        }