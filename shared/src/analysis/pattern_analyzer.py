#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para análise de padrões nos resultados do Double da Blaze.
"""

import logging
import numpy as np
from collections import Counter, defaultdict
from .advanced_patterns import AdvancedPatternDetector

class PatternAnalyzer:
    """Classe para análise de padrões nos resultados do Double da Blaze."""
    
    def __init__(self, config=None):
        """
        Inicializa o analisador de padrões.
        
        Args:
            config (dict): Configurações para análise de padrões.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.min_pattern_length = self.config.get('min_pattern_length', 3)
        self.max_pattern_length = self.config.get('max_pattern_length', 10)
        
        # Inicializar detector de padrões avançados
        self.advanced_detector = AdvancedPatternDetector(config)
        
        self.logger.info("PatternAnalyzer inicializado")
    
    def analyze_data(self, results):
        """
        Analisa os dados para identificar padrões.
        
        Args:
            results (list): Lista de resultados para análise.
            
        Returns:
            dict: Análise de padrões encontrados.
        """
        if not results:
            self.logger.warning("Sem dados para análise")
            return {}
        
        self.logger.info(f"Analisando {len(results)} resultados")
        
        # Extrai cores e números
        colors = [r.get('color', '') for r in results]
        numbers = [r.get('roll', 0) for r in results]
        
        analysis = {
            'color_distribution': self._calculate_color_distribution(colors),
            'number_distribution': self._calculate_number_distribution(numbers),
            'color_patterns': self._find_patterns(colors),
            'number_patterns': self._find_patterns(numbers),
            'streaks': self._find_streaks(colors)
        }
        
        # Adicionar análise de padrões avançados
        try:
            advanced_analysis = self.advanced_detector.detect_all_patterns(results)
            if advanced_analysis:
                analysis['advanced_patterns'] = advanced_analysis
        except Exception as e:
            self.logger.warning(f"Erro na análise avançada: {e}")
        
        self.logger.info("Análise de padrões concluída")
        return analysis
    
    def _calculate_color_distribution(self, colors):
        """Calcula a distribuição de cores."""
        counter = Counter(colors)
        total = len(colors)
        
        return {
            'counts': dict(counter),
            'percentages': {color: count/total*100 for color, count in counter.items()}
        }
    
    def _calculate_number_distribution(self, numbers):
        """Calcula a distribuição de números."""
        counter = Counter(numbers)
        return dict(counter)
    
    def _find_patterns(self, sequence):
        """Encontra padrões na sequência."""
        patterns = {}
        
        for length in range(self.min_pattern_length, min(self.max_pattern_length, len(sequence)//2)):
            pattern_counts = defaultdict(int)
            
            for i in range(len(sequence) - length + 1):
                pattern = tuple(sequence[i:i+length])
                pattern_counts[pattern] += 1
            
            # Filtra padrões que ocorrem mais de uma vez
            frequent_patterns = {str(pattern): count for pattern, count in pattern_counts.items() 
                               if count > 1}
            
            if frequent_patterns:
                patterns[length] = frequent_patterns
        
        return patterns
    
    def _find_streaks(self, colors):
        """Encontra sequências de cores repetidas."""
        streaks = {'red': 0, 'black': 0, 'white': 0}
        current_streak = {'color': None, 'count': 0}
        
        for color in colors:
            if color == current_streak['color']:
                current_streak['count'] += 1
            else:
                if current_streak['color'] and current_streak['count'] > streaks.get(current_streak['color'], 0):
                    streaks[current_streak['color']] = current_streak['count']
                current_streak = {'color': color, 'count': 1}
        
        # Verifica a última sequência
        if current_streak['color'] and current_streak['count'] > streaks.get(current_streak['color'], 0):
            streaks[current_streak['color']] = current_streak['count']
            
        return streaks

    def get_triggers(self, results):
        """
        Gera uma lista de gatilhos/recomendações baseadas em padrões estatísticos/táticos.

        Args:
            results (list): lista de resultados (cada item deve ter 'color' e opcionalmente 'roll')

        Returns:
            list[dict]: lista de gatilhos no formato similar ao exemplo fornecido pelo usuário
        """
        colors = [r.get('color', '') for r in results]
        triggers = []

        # helper: longest streak
        longest = {'color': None, 'length': 0}
        cur = {'color': None, 'count': 0}
        for c in colors:
            if c == cur['color']:
                cur['count'] += 1
            else:
                if cur['color'] and cur['count'] > longest['length']:
                    longest = {'color': cur['color'], 'length': cur['count']}
                cur = {'color': c, 'count': 1}
        if cur['color'] and cur['count'] > longest['length']:
            longest = {'color': cur['color'], 'length': cur['count']}

        # Sequência Repetitiva
        if longest['length'] >= 4:
            action = 'Aguardar rompimento, entrada na cor oposta ou branco'
            # reforçar gatilho mais forte para 6+
            if longest['length'] >= 6:
                action = 'Gatilho forte: aguardar rompimento imediato; possível inversão ou branco.'
            triggers.append({
                'nome': 'Sequência Repetitiva',
                'gatilho': f"{longest['length']} {longest['color']}s consecutivos",
                'acao': action,
                'meta': {'color': longest['color'], 'length': longest['length']}
            })

        # Alternância (Xadrez): procurar janelas alternadas de tamanho >=4
        def is_alternating(seq):
            if len(seq) < 2:
                return False
            for i in range(1, len(seq)):
                if seq[i] == seq[i-1]:
                    return False
            return True

        alt_found = False
        for window in range(4, 7):
            for i in range(len(colors) - window + 1):
                sub = colors[i:i+window]
                if is_alternating(sub):
                    alt_found = True
                    triggers.append({
                        'nome': 'Alternância (Xadrez)',
                        'gatilho': f"{window} alternâncias detectadas",
                        'acao': 'Aguardar quebra; possível sequência repetitiva em seguida',
                        'meta': {'window': window, 'index': i}
                    })
                    break
            if alt_found:
                break

        # 2x2 e 3x3
        for i in range(len(colors) - 3):
            # 2x2
            a, b, c, d = colors[i], colors[i+1], colors[i+2], colors[i+3]
            if a == b and c == d and a != c:
                triggers.append({
                    'nome': 'Padrão 2x2',
                    'gatilho': f"{a}, {a}, {c}, {c} no índice {i}",
                    'acao': 'Entrada rápida ou alerta para inversão após bloco',
                    'meta': {'index': i, 'pattern': [a,a,c,c]}
                })
        for i in range(len(colors) - 5):
            # 3x3
            block = colors[i:i+6]
            if block[0] == block[1] == block[2] and block[3] == block[4] == block[5] and block[0] != block[3]:
                triggers.append({
                    'nome': 'Padrão 3x3',
                    'gatilho': f"{' ,'.join(block)} no índice {i}",
                    'acao': 'Entrada na cor inversa após o bloco',
                    'meta': {'index': i, 'pattern': block}
                })

        # Branco Isca (white bait): detectar branco vindo após grande sequência
        for i, c in enumerate(colors):
            if c == 'white' and i > 0:
                # contar streak anterior
                j = i-1
                prev_color = colors[j]
                streak = 0
                while j >= 0 and colors[j] == prev_color:
                    streak += 1
                    j -= 1
                if streak >= 4:
                    triggers.append({
                        'nome': 'Branco Isca',
                        'gatilho': f"Branco em {i} apos sequência de {streak} {prev_color}",
                        'acao': 'Atenção: chance aumentada de branco nas próximas 2 rodadas (G1-G2)',
                        'meta': {'index': i, 'prior_streak': streak, 'prior_color': prev_color}
                    })

        # Espelhado
        for size in range(2, 7, 2):
            for i in range(len(colors) - size + 1):
                half = size // 2
                a = colors[i:i+half]
                b = colors[i+half:i+size]
                if a == b and len(a) >= 2:
                    triggers.append({
                        'nome': 'Espelhado',
                        'gatilho': f"Bloco espelhado de tamanho {size} no índice {i}",
                        'acao': 'Sinal para possível branco ou quebra',
                        'meta': {'index': i, 'size': size, 'block': a + b}
                    })
                    break

        # Contagem regressiva de branco: verificar último branco
        last_white_idx = None
        for i in range(len(colors)-1, -1, -1):
            if colors[i] == 'white':
                last_white_idx = i
                break
        if last_white_idx is not None:
            rounds_since = len(colors) - 1 - last_white_idx
            triggers.append({
                'nome': 'Contagem Pós-Branco',
                'gatilho': f"Último branco há {rounds_since} rodadas",
                'acao': 'Se dentro de 5-8 rodadas considerar entrada na cor oposta ao padrão inicial; abortar se repetição durante a contagem',
                'meta': {'last_white_index': last_white_idx, 'rounds_since': rounds_since}
            })

        # Quente e Frio (últimas 50 e 100)
        for window in (50, 100):
            if len(colors) >= 10:
                seg = colors[-window:] if len(colors) >= window else colors
                total = len(seg)
                counts = {c: seg.count(c) for c in ('red', 'black', 'white')}
                hot = [c for c, cnt in counts.items() if total and (cnt/total) > 0.5]
                cold = [c for c, cnt in counts.items() if total and (cnt/total) < 0.2]
                if hot or cold:
                    triggers.append({
                        'nome': 'Quente/Fri o',
                        'gatilho': f"Window {window}: hot={hot}, cold={cold}",
                        'acao': 'Ajuste estatístico: entradas visando correção da média histórica',
                        'meta': {'window': window, 'counts': counts}
                    })

        return triggers
    
    def analyze_new_data(self, new_result, recent_results):
        """
        Analisa um novo resultado no contexto dos resultados recentes.
        
        Args:
            new_result (dict): Novo resultado a ser analisado.
            recent_results (list): Lista de resultados recentes.
            
        Returns:
            dict: Análise do novo resultado.
        """
        all_results = recent_results + [new_result]
        return self.analyze_data(all_results)

    def suggest_next_color(self, results):
        """
        Sugere a próxima cor para apostar com base nas regras fornecidas (implementa o prompt do usuário).

        Args:
            results (list): lista de resultados (cada item deve ter 'color')

        Returns:
            str: texto formatado com a sugestão e fundamento, exemplo:
                'Sugestão: preto\nFundamento: sequência de 4 vermelhos detectada; alta chance de inversão.'
        """
        colors = [r.get('color', '').lower() for r in results if r.get('color')]
        n = len(colors)

        # helper para tradução simples
        trans = {'red': 'vermelho', 'black': 'preto', 'white': 'branco'}

        def to_label(c):
            return trans.get(c, c)

        # Regra 3 (prioridade de branco nas próximas 2 rodadas)
        last_white_idx = None
        for i in range(n-1, -1, -1):
            if colors[i] == 'white':
                last_white_idx = i
                break
        if last_white_idx is not None and (n - 1 - last_white_idx) <= 1:
            return f"Sugestão: branco\nFundamento: 'branco' detectado recentemente; priorizar branco nas próximas 2 jogadas."

        # Regra 1: sequência de 4+ vermelhos ou pretos
        if n >= 4:
            # verificar streak final
            last_color = colors[-1]
            if last_color in ('red', 'black'):
                streak = 1
                for i in range(n-2, -1, -1):
                    if colors[i] == last_color:
                        streak += 1
                    else:
                        break
                if streak >= 4:
                    opposite = 'black' if last_color == 'red' else 'red'
                    return f"Sugestão: {to_label(opposite)}\nFundamento: sequência de {streak} {to_label(last_color)}s detectada; sugerir a cor oposta."

        # Regra 2: alternância nas últimas 6 jogadas
        if n >= 6:
            last6 = colors[-6:]
            # ignorar se houver branco
            if all(c in ('red', 'black') for c in last6):
                alt = True
                for i in range(1, 6):
                    if last6[i] == last6[i-1]:
                        alt = False
                        break
                if alt:
                    # se alterna, prever continuação do padrão
                    next_color = 'black' if last6[-1] == 'red' else 'red'
                    return (f"Sugestão: {to_label(next_color)}\nFundamento: alternância (xadrez) nas últimas 6 jogadas; seguir a alternância, mas alertar para possível rompimento.")

        # Regra 4: detectar blocos 2x2 ou 3x3 no final
        if n >= 4:
            # verificar 2x2 no final
            if colors[-4] == colors[-3] and colors[-2] == colors[-1] and colors[-4] != colors[-2]:
                new_block_color = colors[-1]
                return f"Sugestão: {to_label(new_block_color)}\nFundamento: padrão 2x2 detectado no final ({to_label(colors[-4])},{to_label(colors[-3])},{to_label(colors[-2])},{to_label(colors[-1])}); seguir o novo bloco."
        if n >= 6:
            # verificar 3x3 no final
            if colors[-6] == colors[-5] == colors[-4] and colors[-3] == colors[-2] == colors[-1] and colors[-6] != colors[-3]:
                new_block_color = colors[-1]
                return f"Sugestão: {to_label(new_block_color)}\nFundamento: padrão 3x3 detectado no final; seguir o novo bloco."

        # Regra 5: cor >60% nas últimas 20 jogadas
        if n >= 10:
            window = colors[-20:] if n >= 20 else colors
            from collections import Counter
            cnt = Counter(window)
            total = len(window)
            for c in ('red', 'black'):
                if cnt.get(c, 0) / total > 0.6:
                    opposite = 'black' if c == 'red' else 'red'
                    return f"Sugestão: {to_label(opposite)}\nFundamento: {to_label(c)} apareceu mais de 60% nas últimas {total} jogadas; sugerir a cor oposta para ajuste estatístico."

        # Regra 6: fallback - sem padrão forte
        # Sugestão: não apostar ou sugerir com base em frequência (escolher a menos frequente)
        if n > 0:
            from collections import Counter
            cnt = Counter(colors)
            # remover branco para decisão estatística se branco estiver presente
            for k in list(cnt.keys()):
                if k not in ('red', 'black', 'white'):
                    del cnt[k]
            # escolher a menos frequente entre red/black/white
            least = min(cnt.items(), key=lambda x: x[1])[0] if cnt else None
            if least and cnt.get(least, 0) / n < 0.5:
                # sugerir não apostar quando não há padrão forte
                return f"Sugestão: não apostar\nFundamento: nenhum padrão forte detectado nas últimas {n} jogadas; preferir evitar aposta ou aguardar mais dados."

        return "Sugestão: não apostar\nFundamento: dados insuficientes ou sem padrão detectável."
    
    def set_active_patterns(self, patterns: list):
        """
        Define quais padrões avançados estão ativos.
        
        Args:
            patterns (list): Lista de nomes dos padrões a ativar.
        """
        try:
            self.advanced_detector.set_active_patterns(patterns)
            self.logger.info(f"Padrões ativos definidos: {patterns}")
        except Exception as e:
            self.logger.error(f"Erro ao definir padrões ativos: {e}")
    
    def get_available_patterns(self) -> list:
        """
        Retorna lista de padrões avançados disponíveis.
        
        Returns:
            list: Lista de nomes dos padrões disponíveis.
        """
        try:
            return self.advanced_detector.get_available_patterns()
        except Exception as e:
            self.logger.error(f"Erro ao obter padrões disponíveis: {e}")
            return []
    
    def get_active_patterns(self) -> list:
        """
        Retorna lista de padrões avançados ativos.
        
        Returns:
            list: Lista de nomes dos padrões ativos.
        """
        try:
            return self.advanced_detector.active_patterns
        except Exception as e:
            self.logger.error(f"Erro ao obter padrões ativos: {e}")
            return []