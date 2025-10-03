"""
Analisador de Padrões de Roleta - FASE 2 (AVANÇADO)
Análise estatística complexa e detecção de bias em Python
"""

import numpy as np
from scipy import stats
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class RouletteAdvancedAnalyzer:
    """Análise avançada de padrões de roleta (Fase 2)"""

    # Definições de setores da roda europeia
    SECTORS = {
        "voisins": [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25],
        "tiers": [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33],
        "orphelins": [17, 34, 6, 1, 20, 14, 31, 9],
    }

    SECTOR_NAMES = {
        "voisins": "Vizinhos do Zero",
        "tiers": "Terço do Cilindro",
        "orphelins": "Órfãos",
    }

    WHEEL_ORDER = [
        0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5,
        24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26,
    ]

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 30  # Cache por 30 segundos

    # ==================== ANÁLISE DE SETORES ====================

    def analyze_sectors(self, results: List[Dict]) -> Optional[Dict]:
        """
        Detecta setor quente da roda com análise estatística avançada
        
        Args:
            results: Lista de resultados com {'number', 'color', 'timestamp'}
            
        Returns:
            Dict com informações do setor quente ou None
        """
        if len(results) < 20:
            return None

        last_50 = results[:50] if len(results) >= 50 else results

        # Contar aparições por setor
        sector_counts = {sector: 0 for sector in self.SECTORS.keys()}

        for result in last_50:
            num = result.get("number")
            for sector, numbers in self.SECTORS.items():
                if num in numbers:
                    sector_counts[sector] += 1

        # Encontrar setor dominante
        hot_sector = max(sector_counts, key=sector_counts.get)
        count = sector_counts[hot_sector]
        total = len(last_50)
        percentage = (count / total) * 100

        # Teste chi-square para significância estatística
        expected = total / 3  # Distribuição esperada (3 setores)
        observed = list(sector_counts.values())
        chi2, p_value = stats.chisquare(observed, [expected] * 3)

        # Só retorna se o setor estiver significativamente quente
        if percentage >= 45 and p_value < 0.05:
            confidence = min(55 + (percentage - 45) * 1.2, 80)

            return {
                "id": "hot-sector-advanced",
                "type": "advanced",
                "confidence": round(confidence, 1),
                "priority": percentage,
                "icon": "🎯",
                "title": f"Setor Quente: {self.SECTOR_NAMES[hot_sector]}",
                "description": f'O setor "{self.SECTOR_NAMES[hot_sector]}" apareceu em {count} de {total} resultados ({percentage:.1f}%). Teste chi-square indica desvio significativo (p={p_value:.4f}).',
                "suggestion": f"Apostar nos números: {', '.join(map(str, self.SECTORS[hot_sector]))}",
                "data": {
                    "Setor": self.SECTOR_NAMES[hot_sector],
                    "Aparições": f"{count}/{total}",
                    "Porcentagem": f"{percentage:.1f}%",
                    "P-value": f"{p_value:.4f}",
                },
                "statistical": {
                    "chi_square": round(chi2, 2),
                    "p_value": round(p_value, 4),
                    "significant": bool(p_value < 0.05),
                },
            }

        return None

    # ==================== DETECÇÃO DE BIAS ====================

    def detect_bias(self, results: List[Dict]) -> Optional[Dict]:
        """
        Detecta bias de roda usando teste chi-square
        
        Args:
            results: Lista de pelo menos 100 resultados
            
        Returns:
            Dict com informações de bias ou None
        """
        if len(results) < 100:
            return None

        # Contar frequência de cada número
        frequency = defaultdict(int)
        for result in results:
            frequency[result["number"]] += 1

        # Calcular frequências observadas e esperadas
        total = len(results)
        expected_freq = total / 37  # Distribuição uniforme
        observed = [frequency.get(i, 0) for i in range(37)]
        expected = [expected_freq] * 37

        # Teste chi-square
        chi2, p_value = stats.chisquare(observed, expected)

        # Detectar bias significativo
        if p_value < 0.01:  # Nível de significância 1%
            # Encontrar números com desvio significativo
            biased_numbers = []
            for num in range(37):
                obs_freq = frequency.get(num, 0)
                deviation = ((obs_freq - expected_freq) / expected_freq) * 100

                if abs(deviation) > 50:  # Desvio > 50%
                    biased_numbers.append(
                        {"number": num, "count": obs_freq, "deviation": deviation}
                    )

            if biased_numbers:
                biased_numbers.sort(key=lambda x: abs(x["deviation"]), reverse=True)
                top_biased = biased_numbers[0]

                confidence = min(70 + abs(top_biased["deviation"]) * 0.2, 90)

                return {
                    "id": "wheel-bias",
                    "type": "advanced",
                    "confidence": round(confidence, 1),
                    "priority": 100,  # Prioridade máxima
                    "icon": "⚠️",
                    "title": "BIAS DE RODA DETECTADO!",
                    "description": f"Análise estatística indica possível bias na roda! O número {top_biased['number']} apareceu {top_biased['count']} vezes em {total} rodadas (desvio: {top_biased['deviation']:.1f}%). Chi-square test: χ²={chi2:.2f}, p={p_value:.6f}",
                    "suggestion": f"Apostar nos números com bias: {', '.join([str(n['number']) for n in biased_numbers[:5]])}",
                    "data": {
                        "Chi-square": f"{chi2:.2f}",
                        "P-value": f"{p_value:.6f}",
                        "Top biased": f"{top_biased['number']} ({top_biased['deviation']:.1f}%)",
                        "Total analisado": f"{total} rodadas",
                    },
                    "statistical": {
                        "chi_square": round(chi2, 2),
                        "p_value": round(p_value, 6),
                        "biased_numbers": biased_numbers[:5],
                        "significant": True,
                    },
                }

        return None

    # ==================== ANÁLISE DE CLUSTERS ====================

    def analyze_spatial_clusters(self, results: List[Dict]) -> Optional[Dict]:
        """
        Detecta clusters espaciais de números na roda física
        
        Args:
            results: Lista de resultados recentes
            
        Returns:
            Dict com informações de cluster ou None
        """
        if len(results) < 20:
            return None

        last_20 = results[:20]

        # Mapear números para posições na roda
        positions = []
        for result in last_20:
            try:
                pos = self.WHEEL_ORDER.index(result["number"])
                positions.append(pos)
            except ValueError:
                continue

        if len(positions) < 15:
            return None

        # Calcular distâncias médias entre resultados consecutivos
        distances = []
        for i in range(len(positions) - 1):
            dist = min(
                abs(positions[i] - positions[i + 1]),
                37 - abs(positions[i] - positions[i + 1]),
            )
            distances.append(dist)

        avg_distance = np.mean(distances)
        expected_distance = 37 / 2  # ~18.5 para distribuição uniforme

        # Se a distância média é muito menor que esperado, há cluster
        if avg_distance < expected_distance * 0.6:  # 60% da distância esperada
            confidence = min(60 + (expected_distance - avg_distance) * 2, 78)

            # Encontrar a região mais quente
            position_freq = defaultdict(int)
            for pos in positions:
                # Contar em janelas de 7 posições
                for window_pos in range(max(0, pos - 3), min(37, pos + 4)):
                    position_freq[window_pos] += 1

            hot_position = max(position_freq, key=position_freq.get)
            hot_numbers = self.WHEEL_ORDER[
                max(0, hot_position - 3) : min(37, hot_position + 4)
            ]

            return {
                "id": "spatial-cluster",
                "type": "advanced",
                "confidence": round(confidence, 1),
                "priority": 85,
                "icon": "🎪",
                "title": "Cluster Espacial Detectado",
                "description": f"Os resultados estão concentrados em uma região específica da roda. Distância média entre números: {avg_distance:.1f} posições (esperado: {expected_distance:.1f}). Isso pode indicar viés físico ou padrão de lançamento.",
                "suggestion": f"Apostar em números ao redor da posição {hot_position}: {', '.join(map(str, hot_numbers))}",
                "data": {
                    "Dist. média": f"{avg_distance:.1f} posições",
                    "Dist. esperada": f"{expected_distance:.1f}",
                    "Região quente": f"Posição {hot_position}",
                    "Números": ", ".join(map(str, hot_numbers[:7])),
                },
                "statistical": {
                    "average_distance": round(avg_distance, 2),
                    "expected_distance": round(expected_distance, 2),
                    "cluster_strength": round(
                        (1 - avg_distance / expected_distance) * 100, 1
                    ),
                },
            }

        return None

    # ==================== ANÁLISE DE TENDÊNCIAS TEMPORAIS ====================

    def analyze_temporal_trends(self, results: List[Dict]) -> Optional[Dict]:
        """
        Analisa tendências ao longo do tempo
        
        Args:
            results: Lista de resultados com timestamps
            
        Returns:
            Dict com tendências detectadas ou None
        """
        if len(results) < 50:
            return None

        # Dividir em blocos de 10 resultados
        blocks = [results[i : i + 10] for i in range(0, min(50, len(results)), 10)]

        if len(blocks) < 3:
            return None

        # Analisar tendência de vermelho/preto em cada bloco
        red_percentages = []
        for block in blocks:
            red_count = sum(1 for r in block if r.get("color") == "red")
            red_percentages.append((red_count / len(block)) * 100)

        # Verificar se há tendência crescente ou decrescente
        if len(red_percentages) >= 3:
            # Regressão linear simples
            x = np.arange(len(red_percentages))
            slope, intercept = np.polyfit(x, red_percentages, 1)

            # Tendência significativa se slope > 5% por bloco
            if abs(slope) > 5:
                trend = "crescente" if slope > 0 else "decrescente"
                current_perc = red_percentages[-1]
                confidence = min(50 + abs(slope) * 3, 68)

                color = "Vermelho" if slope > 0 else "Preto"

                return {
                    "id": "temporal-trend",
                    "type": "advanced",
                    "confidence": round(confidence, 1),
                    "priority": abs(slope) * 3,
                    "icon": "📈" if slope > 0 else "📉",
                    "title": f"Tendência Temporal: {color}",
                    "description": f"Análise de blocos de 10 rodadas mostra tendência {trend} para {color}. Taxa de mudança: {slope:.1f}% por bloco. Percentual atual: {current_perc:.1f}%.",
                    "suggestion": f"Tendência favorece {color} no curto prazo",
                    "data": {
                        "Tendência": trend.capitalize(),
                        "Taxa": f"{slope:.1f}%/bloco",
                        "Cor favorecida": color,
                        "Atual": f"{current_perc:.1f}%",
                    },
                    "statistical": {
                        "slope": round(slope, 2),
                        "intercept": round(intercept, 2),
                        "blocks_analyzed": len(blocks),
                    },
                }

        return None

    # ==================== ANÁLISE CONSOLIDADA ====================

    def analyze_all_advanced_patterns(self, results: List[Dict]) -> List[Dict]:
        """
        Executa todas as análises avançadas
        
        Args:
            results: Lista completa de resultados
            
        Returns:
            Lista de padrões avançados detectados
        """
        patterns = []

        # 1. Análise de setores
        sector_pattern = self.analyze_sectors(results)
        if sector_pattern:
            patterns.append(sector_pattern)

        # 2. Detecção de bias (apenas com dados suficientes)
        if len(results) >= 100:
            bias_pattern = self.detect_bias(results)
            if bias_pattern:
                patterns.append(bias_pattern)

        # 3. Análise de clusters espaciais
        cluster_pattern = self.analyze_spatial_clusters(results)
        if cluster_pattern:
            patterns.append(cluster_pattern)

        # 4. Análise de tendências temporais
        temporal_pattern = self.analyze_temporal_trends(results)
        if temporal_pattern:
            patterns.append(temporal_pattern)

        # Ordenar por prioridade
        patterns.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return patterns

    # ==================== ESTATÍSTICAS GERAIS ====================

    def get_comprehensive_stats(self, results: List[Dict]) -> Dict:
        """
        Retorna estatísticas completas sobre os resultados
        
        Args:
            results: Lista de resultados
            
        Returns:
            Dict com estatísticas detalhadas
        """
        if not results:
            return {}

        total = len(results)

        # Frequências
        frequency = defaultdict(int)
        color_freq = defaultdict(int)
        for result in results:
            frequency[result["number"]] += 1
            color_freq[result.get("color", "unknown")] += 1

        # Números mais/menos frequentes
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        hot_nums = sorted_freq[:5]
        cold_nums = sorted_freq[-5:]

        # Estatísticas por setor
        sector_stats = {}
        for sector, numbers in self.SECTORS.items():
            count = sum(frequency.get(num, 0) for num in numbers)
            sector_stats[sector] = {
                "count": count,
                "percentage": round((count / total) * 100, 1),
            }

        return {
            "total_spins": total,
            "colors": {
                "red": color_freq.get("red", 0),
                "black": color_freq.get("black", 0),
                "green": color_freq.get("green", 0),
            },
            "hot_numbers": [{"number": n, "count": c} for n, c in hot_nums],
            "cold_numbers": [{"number": n, "count": c} for n, c in cold_nums],
            "sectors": sector_stats,
            "timestamp": datetime.now().isoformat(),
        }
