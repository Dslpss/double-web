#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de alertas para o Double da Blaze.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AlertSystem:
    """Sistema de alertas para notificações importantes."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o sistema de alertas.
        
        Args:
            config (Dict): Configurações do sistema de alertas
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', False)  # Desabilitado por padrão
        self.min_confidence = self.config.get('min_confidence', 0.7)
        self.desktop_notifications = self.config.get('desktop_notifications', False)  # Desabilitado por padrão
        self.sound_alerts = self.config.get('sound_alerts', False)  # Desabilitado por padrão
        
        # Configurações de notificações expandidas
        self.notification_types = self.config.get('types', ['sound', 'popup'])
        self.telegram_enabled = self.config.get('telegram', {}).get('enabled', False)
        self.telegram_token = self.config.get('telegram', {}).get('bot_token', '')
        self.telegram_chat_id = self.config.get('telegram', {}).get('chat_id', '')
        
        self.alerts = []
        # cooldown para evitar spam de alertas similares (segundos)
        self.cooldown_seconds = self.config.get('cooldown_seconds', 30)
        # margem de confiança para considerar um novo alerta mais relevante
        self.confidence_margin = self.config.get('confidence_margin', 0.10)

        logger.info("Sistema de alertas inicializado")
    
    def set_alert(self, prediction: Dict) -> bool:
        """
        Define um alerta baseado em uma predição.
        
        Args:
            prediction (Dict): Dados da predição
            
        Returns:
            bool: True se o alerta foi definido
        """
        if not self.enabled:
            return False
        
        confidence = prediction.get('confidence', 0)
        if confidence < self.min_confidence:
            return False

        # Normalizar chaves de cor (compatibilizar com diferentes pontos que chamam o sistema)
        # algumas partes da codebase usam 'recommended_color' ou 'prediction_color'
        if 'color' not in prediction:
            if 'recommended_color' in prediction:
                prediction['color'] = prediction.get('recommended_color')
            elif 'prediction_color' in prediction:
                prediction['color'] = prediction.get('prediction_color')

        method = prediction.get('method', 'unknown')
        color = (prediction.get('color') or '').lower()

        # Verificar alertas ativos recentes para deduplicação / resolução de conflito
        now_ts = datetime.now().timestamp()
        for alert in self.get_active_alerts():
            try:
                a_pred = alert.get('prediction') or {}
                a_method = a_pred.get('method', 'unknown')
                a_color = (a_pred.get('color') or a_pred.get('recommended_color') or a_pred.get('prediction_color') or '').lower()
                a_conf = float(a_pred.get('confidence') or 0)
                a_ts = datetime.fromisoformat(alert['timestamp']).timestamp()

                # Se é o mesmo método e mesma cor dentro do cooldown, pular
                if a_method == method and a_color and a_color == color and (now_ts - a_ts) < self.cooldown_seconds:
                    logger.debug('Pulando alerta duplicado: mesmo método/cor recente')
                    return False

                # Se cores diferentes mas existe alerta recente, preferir o com maior confiança
                if a_color and a_color != color and (now_ts - a_ts) < self.cooldown_seconds:
                    # se novo alerta tem confiança significativamente maior, substituir
                    if confidence > (a_conf + self.confidence_margin):
                        logger.info('Novo alerta (%s) substitui alerta recente (%s) por maior confiança', color, a_color)
                        # marcar alertas anteriores como reconhecidos/supercedidos
                        try:
                            alert['acknowledged'] = True
                        except Exception:
                            pass
                        break
                    else:
                        logger.debug('Pulando alerta conflitante com menor/igual confiança')
                        return False
            except Exception:
                continue
        
        alert = {
            'id': f"alert_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'message': self._generate_alert_message(prediction),
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        
        # Salvar predição no banco de dados para sincronização com a GUI
        try:
            self._save_prediction_to_db(prediction)
        except Exception as e:
            logger.error(f"Erro ao salvar predição no banco: {e}")
        
        # Envia notificações
        if self.desktop_notifications or 'popup' in self.notification_types:
            self._send_desktop_notification(alert)
        
        # Som desabilitado - usando apenas banner visual
        # if self.sound_alerts or 'sound' in self.notification_types:
        #     self._play_alert_sound()
            
        # Notificações via Telegram
        if self.telegram_enabled and 'telegram' in self.notification_types:
            self._send_telegram_notification(alert)
        
        logger.info(f"Alerta definido: {alert['message']}")
        return True

    def send_alert(self, prediction: Dict) -> bool:
        """
        Backwards-compatible wrapper expected by analyzer code. Delegates to set_alert.
        """
        try:
            return self.set_alert(prediction)
        except Exception:
            logger.exception('Erro em send_alert')
            return False
    
    def get_active_alerts(self) -> List[Dict]:
        """
        Obtém alertas ativos (não reconhecidos).
        
        Returns:
            List[Dict]: Lista de alertas ativos
        """
        return [alert for alert in self.alerts if not alert['acknowledged']]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Reconhece um alerta específico.
        
        Args:
            alert_id (str): ID do alerta
            
        Returns:
            bool: True se o alerta foi reconhecido
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                logger.info(f"Alerta {alert_id} reconhecido")
                return True
        
        return False
    
    def acknowledge_all_alerts(self) -> int:
        """
        Reconhece todos os alertas ativos.
        
        Returns:
            int: Número de alertas reconhecidos
        """
        count = 0
        for alert in self.alerts:
            if not alert['acknowledged']:
                alert['acknowledged'] = True
                count += 1
        
        logger.info(f"{count} alertas reconhecidos")
        return count
    
    def clear_old_alerts(self, hours: int = 24) -> int:
        """
        Remove alertas antigos.
        
        Args:
            hours (int): Idade máxima dos alertas em horas
            
        Returns:
            int: Número de alertas removidos
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        original_count = len(self.alerts)
        
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']).timestamp() > cutoff_time
        ]
        
        removed_count = original_count - len(self.alerts)
        if removed_count > 0:
            logger.info(f"{removed_count} alertas antigos removidos")
        
        return removed_count
    
    def _generate_alert_message(self, prediction: Dict) -> str:
        """
        Gera uma mensagem de alerta baseada na predição.
        
        Args:
            prediction (Dict): Dados da predição
            
        Returns:
            str: Mensagem do alerta
        """
        # Tentar encontrar um número (roll/number/result_number/roll_number) na predição
        number = None
        for key in ('roll', 'number', 'result_number', 'roll_number', 'saiu', 'numero'):
            if key in prediction and prediction.get(key) is not None:
                number = prediction.get(key)
                break

        # Também aceitar caso o número venha encapsulado em um dicionário 'result' ou similar
        if number is None:
            result_obj = prediction.get('result') or prediction.get('last_result') or {}
            if isinstance(result_obj, dict):
                for key in ('roll', 'number', 'result_number', 'roll_number'):
                    if key in result_obj and result_obj.get(key) is not None:
                        number = result_obj.get(key)
                        break

        # Normalizar cor
        color = (prediction.get('color') or prediction.get('recommended_color') or prediction.get('prediction_color') or 'desconhecida')
        color = color.lower() if isinstance(color, str) else color

        color_names = {
            'red': 'Vermelho',
            'black': 'Preto',
            'white': 'Branco'
        }
        color_pt = color_names.get(color, color)

        # Sempre gerar mensagem no formato solicitado pelo usuário
        if True:  # Sempre usar o formato novo
            try:
                num_str = str(int(number))
            except Exception:
                num_str = str(number)

            # Buscar último resultado para mostrar na mensagem
            last_result = self._get_last_result()
            last_number = last_result.get('number', last_result.get('roll', '?')) if last_result else '?'
            
            try:
                last_num_str = str(int(last_number))
            except Exception:
                last_num_str = str(last_number)

            # Confiança da predição
            confidence = prediction.get('confidence', 0)
            confidence_pct = confidence * 100

            # Mensagem no formato: "Saiu número X, na próxima apostar na cor Y (%)"
            message = f"Saiu número {last_num_str}, na próxima apostar na cor {color_pt} ({confidence_pct:.1f}%)"
            return message

        # Fallback: manter formato detalhado com confiança e justificativa
        confidence = prediction.get('confidence', 0)
        method = prediction.get('method', 'análise')
        confidence_pct = confidence * 100

        # Adicionar informações sobre padrões se disponíveis
        pattern_info = ""
        if 'pattern_triggers' in prediction:
            triggers = prediction['pattern_triggers']
            if triggers:
                pattern_names = [t.get('nome', '') for t in triggers[:2]]  # Máximo 2 padrões
                pattern_info = f"\nPadroes: {', '.join(pattern_names)}"

        reasoning = prediction.get('reasoning', '')
        if reasoning:
            pattern_info += f"\nJustificativa: {reasoning[:100]}..." if len(reasoning) > 100 else f"\nJustificativa: {reasoning}"

        message = f"SINAL DE APOSTA DETECTADO!\n\nCor Recomendada: {color_pt}\nConfianca: {confidence_pct:.1f}%\nMetodo: {method}{pattern_info}\n\nAposte com responsabilidade!"
        return message
    
    def _get_last_result(self) -> Optional[Dict]:
        """
        Busca o último resultado do jogo.
        
        Returns:
            Dict: Dados do último resultado ou None
        """
        try:
            # Tentar buscar do analyzer se disponível
            if hasattr(self, 'analyzer') and self.analyzer:
                # Buscar do manual_data primeiro
                if hasattr(self.analyzer, 'manual_data') and self.analyzer.manual_data:
                    last_result = self.analyzer.manual_data[-1]
                    return {
                        'number': last_result.get('roll', last_result.get('number')),
                        'color': last_result.get('color'),
                        'created_at': last_result.get('created_at')
                    }
                
                # Buscar do data se manual_data estiver vazio
                if hasattr(self.analyzer, 'data') and self.analyzer.data:
                    last_result = self.analyzer.data[-1]
                    return {
                        'number': last_result.get('roll', last_result.get('number')),
                        'color': last_result.get('color'),
                        'created_at': last_result.get('created_at')
                    }
            
            # Fallback: buscar do banco de dados
            if hasattr(self, 'db_manager') and self.db_manager:
                try:
                    with self.db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT roll, color, created_at 
                            FROM results 
                            ORDER BY created_at DESC 
                            LIMIT 1
                        ''')
                        row = cursor.fetchone()
                        if row:
                            return {
                                'number': row[0],
                                'color': row[1],
                                'created_at': row[2]
                            }
                except Exception:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar último resultado: {e}")
            return None
    def _send_desktop_notification(self, alert: Dict) -> bool:
        """
        Envia uma notificação para o desktop usando card popup.
        
        Args:
            alert (Dict): Dados do alerta
            
        Returns:
            bool: True se a notificação foi enviada
        """
        try:
            # Usar o sistema de card popup personalizado
            try:
                import sys
                import os
                # Adicionar o diretório scripts ao path
                scripts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
                if scripts_dir not in sys.path:
                    sys.path.insert(0, scripts_dir)
                
                from pattern_visual_notifier import show_banner_on_desktop
                
                # Extrair cor e confiança da mensagem do alerta
                message = alert.get('message', '')
                prediction = alert.get('prediction', {})
                
                # Tentar extrair cor da predição
                color = prediction.get('color') or prediction.get('predicted_color') or prediction.get('recommended_color')
                confidence = prediction.get('confidence', 0.0)
                
                # Se não conseguiu extrair da predição, tentar da mensagem
                if not color:
                    if 'RED' in message.upper():
                        color = 'red'
                    elif 'BLACK' in message.upper():
                        color = 'black'
                    elif 'WHITE' in message.upper():
                        color = 'white'
                
                if color and confidence:
                    # Usar thread para não bloquear
                    import threading
                    def show_popup():
                        show_banner_on_desktop(color, confidence, duration=8)
                    
                    threading.Thread(target=show_popup, daemon=True).start()
                    return True
                else:
                    # Fallback para notificação padrão se não conseguir extrair cor/confiança
                    return self._send_fallback_notification(alert)
                    
            except ImportError:
                logger.warning("Sistema de card popup não disponível")
                return self._send_fallback_notification(alert)
            except Exception as e:
                logger.error(f"Erro ao usar card popup: {str(e)}")
                return self._send_fallback_notification(alert)
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação desktop: {str(e)}")
            return False
    
    def _send_fallback_notification(self, alert: Dict) -> bool:
        """
        Fallback removido - usando apenas card popup.
        """
        logger.info("Notificação fallback removida - usando apenas card popup")
        return False
    
    def _send_telegram_notification(self, alert: Dict) -> bool:
        """
        Notificações via Telegram removidas - usando apenas card popup.
        """
        logger.info("Notificação Telegram removida - usando apenas card popup")
        return False
    
    def _play_alert_sound(self) -> bool:
        """
        Alertas de som removidos - usando apenas card popup.
        """
        logger.info("Alerta de som removido - usando apenas card popup")
        return False
    
    def _save_prediction_to_db(self, prediction: Dict) -> bool:
        """
        Salva a predição no banco de dados para sincronização com a GUI.
        
        Args:
            prediction (Dict): Dados da predição
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            # Importar DatabaseManager
            from ..database.db_manager import DatabaseManager
            
            # Criar instância do banco (usar o mesmo banco do sistema)
            db = DatabaseManager("data/blaze_enhanced.db")
            
            # Preparar dados para inserção
            pred_data = {
                'result_id': None,  # Será preenchido quando o resultado chegar
                'color': prediction.get('color', ''),
                'confidence': prediction.get('confidence', 0.0),
                'method': prediction.get('method', 'alert_system'),
                'correct': None  # Será preenchido na validação
            }
            
            # Inserir no banco
            pred_id = db.insert_prediction(pred_data)
            
            if pred_id:
                logger.info(f"Predição salva no banco (ID: {pred_id}): {pred_data['color']} ({pred_data['confidence']:.1%})")
                return True
            else:
                logger.error("Falha ao salvar predição no banco")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao salvar predição no banco: {e}")
            return False
    
    def get_alert_statistics(self) -> Dict:
        """
        Obtém estatísticas dos alertas.
        
        Returns:
            Dict: Estatísticas dos alertas
        """
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        acknowledged_alerts = total_alerts - active_alerts
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'acknowledged_alerts': acknowledged_alerts,
            'system_enabled': self.enabled
        }
