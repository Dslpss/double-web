#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sincronizador da Roleta Brasileira com o sistema principal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrators.pragmatic_brazilian_roulette import PragmaticBrazilianRoulette
from shared.src.database.db_manager import DatabaseManager
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PragmaticBrazilianSync:
    """Sincronizador que integra Pragmatic Brazilian Roulette com o sistema."""
    
    def __init__(self, username: str, password: str, db_path: str = "pragmatic_roulette.db"):
        """
        Inicializa o sincronizador.
        
        Args:
            username: Email de login
            password: Senha
            db_path: Caminho do banco de dados
        """
        self.integrator = PragmaticBrazilianRoulette(username, password)
        self.db_manager = DatabaseManager(db_path)
        self.last_synced_id = None
        
        logger.info("Pragmatic Brazilian Sync inicializado")
    
    def sync_once(self, num_games: int = 100) -> int:
        """
        Sincroniza uma vez o histórico.
        
        Args:
            num_games: Número de jogos a buscar
            
        Returns:
            Número de resultados novos sincronizados
        """
        try:
            logger.info(f"Sincronizando últimos {num_games} jogos...")
            
            # Buscar histórico
            history = self.integrator.get_history(num_games)
            
            if not history:
                logger.warning("Nenhum resultado obtido")
                return 0
            
            # Filtrar apenas novos resultados
            new_results = []
            for result in history:
                if result['id'] != self.last_synced_id:
                    new_results.append(result)
                else:
                    break  # Já chegamos no último sincronizado
            
            if new_results:
                # Converter para formato do sistema
                formatted_results = self._format_for_db(new_results)
                
                # Salvar no banco
                self.db_manager.insert_results(formatted_results)
                
                # Atualizar último ID sincronizado
                self.last_synced_id = new_results[0]['id']
                
                logger.info(f"✅ {len(new_results)} novos resultados sincronizados")
                return len(new_results)
            else:
                logger.info("Nenhum resultado novo")
                return 0
                
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            return 0
    
    def _format_for_db(self, results: list) -> list:
        """
        Formata resultados para o formato do DatabaseManager.
        
        Args:
            results: Lista de resultados do integrador
            
        Returns:
            Lista formatada para o banco de dados
        """
        formatted = []
        
        for result in results:
            # Converter número da roleta europeia (0-36) para formato Blaze (0-14)
            # 0 = Green (0)
            # Red: 1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36 -> 1-7
            # Black: 2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35 -> 8-14
            
            number = result['number']
            color = result['color']
            
            # Mapeamento simplificado (você pode ajustar conforme necessário)
            if number == 0:
                blaze_number = 0
                blaze_color = "white"
            elif color == 'red':
                # Mapear red para 1-7
                blaze_number = ((number - 1) % 7) + 1
                blaze_color = "red"
            else:  # black
                # Mapear black para 8-14
                blaze_number = ((number - 2) % 7) + 8
                blaze_color = "black"
            
            formatted_result = {
                'id': result['id'],
                'created_at': result['timestamp'],
                'color': blaze_color,
                'roll': blaze_number,
                'server_seed': f"pragmatic_{result['id']}",
                'timestamp': time.time(),
                'source': 'pragmatic_brazilian_roulette',
                'original_number': number,
                'original_color': color
            }
            
            formatted.append(formatted_result)
        
        return formatted
    
    def monitor_continuous(self, interval: int = 30):
        """
        Monitora e sincroniza continuamente.
        
        Args:
            interval: Intervalo entre sincronizações em segundos
        """
        logger.info(f"🎰 Iniciando monitoramento contínuo (intervalo: {interval}s)")
        logger.info("Pressione Ctrl+C para parar\n")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while True:
            try:
                # Sincronizar
                new_count = self.sync_once()
                
                # Resetar contador de erros em caso de sucesso
                if new_count >= 0:
                    consecutive_errors = 0
                
                # Se houver novos resultados, mostrar estatísticas
                if new_count > 0:
                    self._show_recent_stats()
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("\n👋 Monitoramento interrompido pelo usuário")
                break
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Erro no monitoramento ({consecutive_errors}/{max_consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Muitos erros consecutivos, encerrando...")
                    break
                
                time.sleep(interval)
    
    def _show_recent_stats(self, num_results: int = 20):
        """
        Mostra estatísticas dos resultados recentes.
        
        Args:
            num_results: Número de resultados recentes a analisar
        """
        try:
            recent = self.db_manager.get_recent_results(num_results)
            
            if recent:
                colors = [r['color'] for r in recent]
                
                red_count = colors.count('red')
                black_count = colors.count('black')
                white_count = colors.count('white')
                
                print(f"\n📊 Estatísticas (últimos {len(recent)} resultados):")
                print(f"   🔴 Red:   {red_count:2d} ({red_count/len(recent)*100:.1f}%)")
                print(f"   ⚫ Black: {black_count:2d} ({black_count/len(recent)*100:.1f}%)")
                print(f"   ⚪ White: {white_count:2d} ({white_count/len(recent)*100:.1f}%)")
                
                # Último resultado
                last = recent[0]
                print(f"\n   Último: {last['roll']} {last['color']} (Original: {last.get('original_number', 'N/A')})")
                print()
                
        except Exception as e:
            logger.error(f"Erro ao mostrar estatísticas: {e}")


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sincronizador Pragmatic Brazilian Roulette')
    parser.add_argument('--username', required=True, help='Email de login')
    parser.add_argument('--password', required=True, help='Senha')
    parser.add_argument('--interval', type=int, default=30, help='Intervalo de sincronização (segundos)')
    parser.add_argument('--once', action='store_true', help='Sincronizar apenas uma vez')
    parser.add_argument('--db', default='pragmatic_roulette.db', help='Caminho do banco de dados')
    
    args = parser.parse_args()
    
    # Criar sincronizador
    sync = PragmaticBrazilianSync(args.username, args.password, args.db)
    
    if args.once:
        # Sincronizar uma vez
        count = sync.sync_once()
        print(f"\n✅ Sincronização concluída: {count} novos resultados")
    else:
        # Monitoramento contínuo
        sync.monitor_continuous(args.interval)


if __name__ == "__main__":
    main()
