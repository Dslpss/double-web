#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para o cliente aprimorado de estatísticas da Pragmatic Play.
Este script permite testar a funcionalidade do cliente aprimorado de forma isolada.
"""

import os
import json
import time
import sys
import argparse
from pprint import pprint

# Adicionar o diretório raiz ao path para importar módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from integrators.pragmatic_statistics_enhanced import PragmaticStatisticsClientEnhanced
    print("✅ Módulo PragmaticStatisticsClientEnhanced importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar PragmaticStatisticsClientEnhanced: {e}")
    sys.exit(1)

def main():
    """Função principal do script de teste."""
    parser = argparse.ArgumentParser(description="Teste do cliente aprimorado de estatísticas da Pragmatic Play")
    parser.add_argument("--jsessionid", help="JSESSIONID para autenticação (opcional)")
    parser.add_argument("--games", type=int, default=100, help="Número de jogos para recuperar (padrão: 100)")
    parser.add_argument("--output", help="Arquivo de saída para salvar os resultados (opcional)")
    parser.add_argument("--proxy", help="URL do proxy para teste (opcional)")
    parser.add_argument("--simulate", action="store_true", help="Forçar uso de dados simulados")
    args = parser.parse_args()

    # Configurar proxy se fornecido
    if args.proxy:
        os.environ["PRAGMATIC_PROXY_ENABLED"] = "true"
        os.environ["PRAGMATIC_PROXY_LIST"] = args.proxy
        print(f"✅ Usando proxy: {args.proxy}")

    # Inicializar o cliente
    print("🔄 Inicializando cliente de estatísticas...")
    client = PragmaticStatisticsClientEnhanced(
        table_id="rwbrzportrwa16rg",  # ID da Roleta Brasileira
        jsessionid=args.jsessionid if args.jsessionid else None
    )
    print(f"✅ Cliente inicializado {f'com JSESSIONID' if args.jsessionid else 'sem JSESSIONID'}")

    # Testar métodos
    start_time = time.time()
    
    if args.simulate:
        print(f"🔄 Gerando {args.games} resultados simulados...")
        results = client.generate_realistic_data(count=args.games)
        print("✅ Dados simulados gerados")
    else:
        print(f"🔄 Buscando {args.games} resultados da API...")
        results = client.get_history(games_count=args.games)
        
        # Verificar se são dados reais ou simulados
        if results and results[0].get("simulated", False):
            print("⚠️ Aviso: Retornados dados simulados (a API real falhou)")
        else:
            print("✅ Dados reais recuperados com sucesso da API")

    end_time = time.time()
    
    # Exibir informações
    print(f"\n📊 Recuperados {len(results)} resultados em {end_time - start_time:.2f} segundos")
    
    # Análise básica
    colors = {'red': 0, 'black': 0, 'green': 0}
    numbers = {}
    
    for result in results:
        # Contar cores
        if 'color' in result:
            color = result['color']
            colors[color] = colors.get(color, 0) + 1
        
        # Contar números
        if 'number' in result:
            number = result['number']
            numbers[number] = numbers.get(number, 0) + 1
    
    print("\n📊 Distribuição por cor:")
    for color, count in colors.items():
        percentage = (count / len(results)) * 100 if results else 0
        print(f"  {color}: {count} ({percentage:.1f}%)")
    
    print("\n📊 Top 5 números mais frequentes:")
    top_numbers = sorted(numbers.items(), key=lambda x: x[1], reverse=True)[:5]
    for number, count in top_numbers:
        percentage = (count / len(results)) * 100 if results else 0
        print(f"  {number}: {count} ({percentage:.1f}%)")
    
    # Salvar resultados se solicitado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Resultados salvos em {args.output}")
    
    # Exibir os 5 primeiros resultados
    print("\n📋 Amostra dos primeiros 5 resultados:")
    for i, result in enumerate(results[:5]):
        print(f"\n  Resultado #{i+1}:")
        for key, value in result.items():
            print(f"    {key}: {value}")

if __name__ == "__main__":
    print("🚀 Iniciando teste do cliente aprimorado de estatísticas")
    main()
    print("\n✅ Teste concluído")