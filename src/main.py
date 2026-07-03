#!/usr/bin/env python3
"""
Ferramenta de Análise de Logs Excessivos
Identifica antipadrões de logging e sugere estratégias de mitigação usando LMMs.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Adiciona o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.llm_client import LLMClient
from src.utils.log_processor import LogProcessor
from src.analyzers.log_level_analyzer import LogLevelAnalyzer
from src.analyzers.unnecessary_logs_detector import UnnecessaryLogsDetector
from src.analyzers.sampling_recommender import SamplingRecommender


class ExcessiveLogsAnalyzer:
    """Analisador principal para detecção de logs excessivos."""

    def __init__(self, analysis_mode: str = "all"):
        """
        Inicializa o analisador.

        Args:
            analysis_mode: Modo de análise (sempre "all" - executa todas as análises disponíveis)
        """
        self.analysis_mode = "all"
        self.llm_clients = {}

        # Inicializa cliente Groq (GRATUITO)
        try:
            self.llm_clients['groq'] = LLMClient(provider='groq')
            print(f"✓ Cliente Groq (GRATUITO) inicializado")
        except Exception as e:
            print(f"⚠ Não foi possível inicializar GROQ: {e}")
            self.llm_clients['groq'] = None

        # Inicializa cliente Google Gemini (GRATUITO)
        try:
            self.llm_clients['gemini'] = LLMClient(provider='gemini')
            print(f"✓ Cliente Google Gemini (GRATUITO) inicializado")
        except Exception as e:
            print(f"⚠ Não foi possível inicializar GEMINI: {e}")
            self.llm_clients['gemini'] = None

        # Inicializa cliente Claude - SEMPRE via Puter
        try:
            self.llm_clients['claude'] = LLMClient(provider='puter', model='claude-sonnet-4')
            print(f"✓ Cliente Claude via Puter (Claude Sonnet 4 - GRATUITO)")
        except Exception as e:
            print(f"⚠ Não foi possível inicializar CLAUDE via Puter: {e}")
            print(f"   Certifique-se de que o Puter Bridge está rodando: ./start_puter.sh")
            self.llm_clients['claude'] = None

        # Inicializa cliente ChatGPT - SEMPRE via Puter
        try:
            self.llm_clients['chatgpt'] = LLMClient(provider='puter', model='gpt-5.4-nano')
            print(f"✓ Cliente ChatGPT via Puter (GPT-5.4 Nano - GRATUITO)")
        except Exception as e:
            print(f"⚠ Não foi possível inicializar CHATGPT via Puter: {e}")
            print(f"   Certifique-se de que o Puter Bridge está rodando: ./start_puter.sh")
            self.llm_clients['chatgpt'] = None

        # Standard sempre disponível (sem LLM)
        self.llm_clients['standard'] = None
        print(f"✓ Análise Standard (sem IA) disponível")

        self.processor = LogProcessor()

    def analyze_file(self, log_file_path: str) -> Dict[str, Any]:
        """
        Analisa um arquivo de logs usando todos os modos disponíveis.

        Args:
            log_file_path: Caminho para o arquivo de logs JSON

        Returns:
            Relatório completo de análise com resultados de todos os modos
        """
        print(f"\n🔍 Analisando logs de: {log_file_path}")

        # 1. Carrega logs (uma vez para todos os modos)
        print("  → Carregando logs...")
        logs = self.processor.load_logs(log_file_path)
        print(f"  ✓ {len(logs)} logs carregados")

        # 2. Processa estatísticas básicas (uma vez para todos os modos)
        print("  → Processando estatísticas...")
        level_dist = self.processor.get_level_distribution(logs)
        service_dist = self.processor.get_service_distribution(logs)
        service_levels = self.processor.group_by_service_and_level(logs)
        duplicates = self.processor.find_duplicate_logs(logs)
        log_rate = self.processor.calculate_log_rate(logs)
        error_types = self.processor.get_error_types(logs)
        http_status_dist = self.processor.get_http_status_distribution(logs)
        tags_dist = self.processor.get_tags_distribution(logs)
        print(f"  ✓ Estatísticas processadas")

        # 3. Executa análise com todos os modos disponíveis
        all_results = {}

        for mode_name in ['groq', 'gemini', 'claude', 'chatgpt', 'standard']:
            print(f"\n{'='*80}")
            print(f"🤖 EXECUTANDO ANÁLISE COM: {mode_name.upper()}")
            print(f"{'='*80}")

            llm_client = self.llm_clients.get(mode_name)

            if mode_name != 'standard' and llm_client is None:
                print(f"  ⚠️  {mode_name.upper()} não disponível, pulando...")
                continue

            # Cria analisadores específicos para este modo
            level_analyzer = LogLevelAnalyzer(llm_client)
            unnecessary_detector = UnnecessaryLogsDetector(llm_client)
            sampling_recommender = SamplingRecommender(llm_client)

            # Análise 1: Níveis de log
            print("\n  📊 Executando Análise 1: Efetividade dos Níveis de Log...")
            level_analysis = level_analyzer.analyze(logs, service_levels)
            print(f"  ✓ Encontrados {len(level_analysis['issues'])} issues")

            # Análise 2: Logs desnecessários
            print("\n  🔎 Executando Análise 2: Detecção de Logs Desnecessários...")
            unnecessary_analysis = unnecessary_detector.analyze(logs, duplicates)
            print(f"  ✓ Potencial de redução: {unnecessary_analysis['reduction_potential_percentage']:.1f}%")

            # Análise 3: Recomendações de sampling
            print("\n  📈 Executando Análise 3: Recomendações de Sampling...")
            sampling_analysis = sampling_recommender.analyze(
                logs, log_rate, service_dist, duplicates
            )
            print(f"  ✓ {len(sampling_analysis['recommended_strategies'])} estratégias recomendadas")

            # Compila resultado para este modo
            all_results[mode_name] = {
                'metadata': {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'log_file': log_file_path,
                    'analysis_mode': mode_name,
                    'llm_provider': llm_client.provider if llm_client else None,
                    'model': llm_client.model if llm_client else None
                },
                'analyses': {
                    'log_levels': level_analysis,
                    'unnecessary_logs': unnecessary_analysis,
                    'sampling_recommendations': sampling_analysis
                },
                'overall_assessment': self._calculate_overall_assessment(
                    level_analysis, unnecessary_analysis, sampling_analysis
                )
            }

        # 4. Compila relatório final com todos os modos
        report = {
            'metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'log_file': log_file_path,
                'analysis_mode': 'all',
                'modes_executed': list(all_results.keys())
            },
            'summary': {
                'total_logs': len(logs),
                'level_distribution': level_dist,
                'service_distribution': service_dist,
                'log_rate': log_rate,
                'error_types': error_types,
                'http_status_distribution': http_status_dist,
                'tags_distribution': tags_dist,
                'duplicate_patterns': len(duplicates)
            },
            'results_by_mode': all_results
        }

        print("\n" + "="*80)
        print("✅ Todas as análises completadas!")
        print("="*80)
        return report

    def _calculate_overall_assessment(self, level_analysis: Dict[str, Any],
                                     unnecessary_analysis: Dict[str, Any],
                                     sampling_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula avaliação geral do sistema de logs."""
        severities = [
            level_analysis['severity'],
            unnecessary_analysis['severity'],
            sampling_analysis['severity']
        ]

        # Determina severidade máxima
        severity_order = ['ok', 'low', 'medium', 'high', 'critical']
        max_severity = max(severities, key=lambda s: severity_order.index(s))

        # Conta total de issues
        total_issues = (
            len(level_analysis['issues']) +
            len(unnecessary_analysis['issues']) +
            len(sampling_analysis.get('recommendations', []))
        )

        # Calcula score de saúde (0-100)
        health_score = 100
        if max_severity == 'critical':
            health_score = 20
        elif max_severity == 'high':
            health_score = 40
        elif max_severity == 'medium':
            health_score = 60
        elif max_severity == 'low':
            health_score = 80

        # Recomendações prioritárias
        priority_actions = []

        if level_analysis['severity'] in ['critical', 'high']:
            priority_actions.append({
                'priority': 1,
                'action': 'Ajustar níveis de log',
                'reason': 'Configuração inadequada de níveis detectada'
            })

        if unnecessary_analysis['reduction_potential_percentage'] > 30:
            priority_actions.append({
                'priority': 2,
                'action': 'Remover logs desnecessários',
                'reason': f"Potencial de redução de {unnecessary_analysis['reduction_potential_percentage']:.1f}%"
            })

        if sampling_analysis['severity'] in ['critical', 'high']:
            priority_actions.append({
                'priority': 3,
                'action': 'Implementar sampling',
                'reason': 'Volume de logs requer sampling'
            })

        return {
            'overall_severity': max_severity,
            'health_score': health_score,
            'total_issues': total_issues,
            'priority_actions': priority_actions,
            'summary': self._get_summary_text(max_severity, total_issues)
        }

    def _get_summary_text(self, severity: str, issue_count: int) -> str:
        """Gera texto resumido da avaliação."""
        severity_messages = {
            'ok': 'Sistema de logs está bem configurado.',
            'low': f'Alguns problemas menores identificados ({issue_count} issues).',
            'medium': f'Problemas moderados de logging detectados ({issue_count} issues). Ação recomendada.',
            'high': f'Problemas significativos de logging ({issue_count} issues). Ação necessária.',
            'critical': f'Problemas críticos de logging ({issue_count} issues). Ação urgente necessária!'
        }
        return severity_messages.get(severity, 'Status desconhecido')

    def generate_reports(self, analysis_result: Dict[str, Any],
                        base_filename: str = None) -> Dict[str, str]:
        """
        Gera relatórios separados para cada modo de análise na pasta reports/.

        Args:
            analysis_result: Resultado da análise com todos os modos
            base_filename: Nome base para os arquivos (opcional)

        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        # Cria pasta reports se não existir
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Define nome base (sem timestamp para sempre sobrescrever)
        if not base_filename:
            base_filename = "analysis"
        else:
            # Remove extensão se tiver
            base_filename = base_filename.replace('.json', '')

        generated_files = {}
        results_by_mode = analysis_result.get('results_by_mode', {})

        # Gera relatório para cada modo
        for mode_name in ['groq', 'gemini', 'claude', 'chatgpt', 'standard']:
            if mode_name not in results_by_mode:
                continue

            mode_data = results_by_mode[mode_name]

            # Monta relatório individual com summary compartilhado
            individual_report = {
                'metadata': mode_data['metadata'],
                'summary': analysis_result['summary'],
                'analyses': mode_data['analyses'],
                'overall_assessment': mode_data['overall_assessment']
            }

            # Define nome do arquivo
            mode_label = {
                'groq': 'groq',
                'gemini': 'gemini',
                'claude': 'claude_ai',
                'chatgpt': 'chatgpt',
                'standard': 'sem_ia'
            }
            filename = f"{base_filename}_{mode_label[mode_name]}.json"
            filepath = os.path.join(reports_dir, filename)

            # Salva arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(individual_report, f, indent=2, ensure_ascii=False)

            generated_files[mode_name] = filepath

        # Gera também relatório comparativo consolidado
        consolidated_filename = f"{base_filename}_comparativo.json"
        consolidated_filepath = os.path.join(reports_dir, consolidated_filename)

        with open(consolidated_filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)

        generated_files['comparativo'] = consolidated_filepath

        # Imprime resumo dos arquivos gerados
        print(f"\n📄 Relatórios salvos em: {reports_dir}/")
        if 'groq' in generated_files:
            print(f"   ├── {os.path.basename(generated_files['groq'])} (Groq - GRATUITO)")
        if 'gemini' in generated_files:
            print(f"   ├── {os.path.basename(generated_files['gemini'])} (Google Gemini - GRATUITO)")
        if 'claude' in generated_files:
            print(f"   ├── {os.path.basename(generated_files['claude'])} (Claude AI)")
        if 'chatgpt' in generated_files:
            print(f"   ├── {os.path.basename(generated_files['chatgpt'])} (ChatGPT)")
        if 'standard' in generated_files:
            print(f"   ├── {os.path.basename(generated_files['standard'])} (Sem IA)")
        print(f"   └── {os.path.basename(generated_files['comparativo'])} (Comparativo)")

        return generated_files

    def print_summary(self, analysis_result: Dict[str, Any]):
        """Imprime resumo comparativo das 3 análises no console."""
        print("\n" + "="*80)
        print("RESUMO COMPARATIVO - ANÁLISE DE LOGS EXCESSIVOS")
        print("="*80)

        summary = analysis_result['summary']
        print(f"\n📊 Total de logs analisados: {summary['total_logs']}")
        print(f"⏱️  Taxa: {summary['log_rate']['rate_per_minute']:.1f} logs/min")

        results_by_mode = analysis_result.get('results_by_mode', {})

        if not results_by_mode:
            print("\n⚠️  Nenhum resultado disponível")
            return

        print("\n" + "-"*80)
        print("COMPARAÇÃO ENTRE MODOS DE ANÁLISE")
        print("-"*80)

        # Cabeçalho da tabela
        print(f"\n{'Métrica':<30} {'Groq':<12} {'Gemini':<12} {'Claude':<12} {'ChatGPT':<12} {'Standard':<12}")
        print("-"*90)

        # Health Score
        health_scores = {}
        for mode in ['groq', 'gemini', 'claude', 'chatgpt', 'standard']:
            if mode in results_by_mode:
                health_scores[mode] = results_by_mode[mode]['overall_assessment']['health_score']
            else:
                health_scores[mode] = 'N/A'

        print(f"{'🏥 Health Score':<30} {str(health_scores.get('groq', 'N/A')):<12} {str(health_scores.get('gemini', 'N/A')):<12} {str(health_scores.get('claude', 'N/A')):<12} {str(health_scores.get('chatgpt', 'N/A')):<12} {str(health_scores.get('standard', 'N/A')):<12}")

        # Severidade
        severities = {}
        for mode in ['groq', 'gemini', 'claude', 'chatgpt', 'standard']:
            if mode in results_by_mode:
                severities[mode] = results_by_mode[mode]['overall_assessment']['overall_severity'].upper()
            else:
                severities[mode] = 'N/A'

        print(f"{'⚠️  Severidade':<30} {severities.get('groq', 'N/A'):<12} {severities.get('gemini', 'N/A'):<12} {severities.get('claude', 'N/A'):<12} {severities.get('chatgpt', 'N/A'):<12} {severities.get('standard', 'N/A'):<12}")

        # Total de Issues
        total_issues = {}
        for mode in ['groq', 'gemini', 'claude', 'chatgpt', 'standard']:
            if mode in results_by_mode:
                total_issues[mode] = results_by_mode[mode]['overall_assessment']['total_issues']
            else:
                total_issues[mode] = 'N/A'

        print(f"{'📋 Issues Encontrados':<30} {str(total_issues.get('groq', 'N/A')):<12} {str(total_issues.get('gemini', 'N/A')):<12} {str(total_issues.get('claude', 'N/A')):<12} {str(total_issues.get('chatgpt', 'N/A')):<12} {str(total_issues.get('standard', 'N/A')):<12}")

        # Potencial de Redução
        reduction_potential = {}
        for mode in ['groq', 'gemini', 'claude', 'chatgpt', 'standard']:
            if mode in results_by_mode:
                reduction = results_by_mode[mode]['analyses']['unnecessary_logs']['reduction_potential_percentage']
                reduction_potential[mode] = f"{reduction:.1f}%"
            else:
                reduction_potential[mode] = 'N/A'

        print(f"{'💾 Potencial de Redução':<30} {reduction_potential.get('groq', 'N/A'):<12} {reduction_potential.get('gemini', 'N/A'):<12} {reduction_potential.get('claude', 'N/A'):<12} {reduction_potential.get('chatgpt', 'N/A'):<12} {reduction_potential.get('standard', 'N/A'):<12}")

        # Detalhes por modo
        for mode_name in ['groq', 'gemini', 'claude', 'chatgpt', 'standard']:
            if mode_name not in results_by_mode:
                continue

            mode_data = results_by_mode[mode_name]
            assessment = mode_data['overall_assessment']
            analyses = mode_data['analyses']

            print("\n" + "-"*80)
            print(f"📊 DETALHES - {mode_name.upper()}")
            print("-"*80)

            print(f"\n🏥 Health Score: {assessment['health_score']}/100")
            print(f"⚠️  Severidade: {assessment['overall_severity'].upper()}")

            if assessment['priority_actions']:
                print("\n🎯 Ações Prioritárias:")
                for action in assessment['priority_actions']:
                    print(f"  {action['priority']}. {action['action']}")
                    print(f"     → {action['reason']}")

            level_analysis = analyses['log_levels']
            unnecessary = analyses['unnecessary_logs']
            sampling = analyses['sampling_recommendations']

            print(f"\n📈 Níveis de Log:")
            print(f"  • Issues: {len(level_analysis['issues'])}")
            print(f"  • Severidade: {level_analysis['severity']}")

            print(f"\n🔍 Logs Desnecessários:")
            print(f"  • Logs desnecessários: {unnecessary['unnecessary_logs_count']}")
            print(f"  • Potencial de redução: {unnecessary['reduction_potential_percentage']:.1f}%")
            print(f"  • Issues: {len(unnecessary['issues'])}")

            print(f"\n🎲 Sampling:")
            print(f"  • Estratégias recomendadas: {len(sampling['recommended_strategies'])}")
            print(f"  • Redução estimada: {sampling['estimated_reduction']['estimated_percentage']}")
            print(f"  • Severidade: {sampling['severity']}")

        print("\n" + "="*80)


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analisa logs para identificar antipadrão de Excessive Logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ATENÇÃO: A ferramenta executa TODAS as análises disponíveis:
  - Groq (GRATUITO - Llama 3.1)
  - Google Gemini (GRATUITO - Gemini 1.5 Flash)
  - Claude AI (Anthropic - pago)
  - ChatGPT (OpenAI - pago)
  - Standard (sem IA - gratuito)

Os relatórios são salvos na pasta reports/ (sobrescreve arquivos anteriores):
  - synthetic_logs_groq.json (GRATUITO)
  - synthetic_logs_gemini.json (GRATUITO)
  - synthetic_logs_claude_ai.json
  - synthetic_logs_chatgpt.json
  - synthetic_logs_sem_ia.json
  - synthetic_logs_comparativo.json

Exemplos:
  python src/main.py dataset/logs.json
  python src/main.py dataset/logs.json -o meu_relatorio
        """
    )
    parser.add_argument(
        'log_file',
        help='Caminho para o arquivo de logs JSON'
    )
    parser.add_argument(
        '-o', '--output',
        help='Nome base para os arquivos de relatório (sem extensão)',
        default=None
    )

    args = parser.parse_args()

    # Verifica se arquivo existe
    if not os.path.exists(args.log_file):
        print(f"❌ Erro: Arquivo não encontrado: {args.log_file}")
        sys.exit(1)

    # Banner informativo
    print(f"\n{'='*80}")
    print(f"  EXCESSIVE LOGS ANALYZER")
    print(f"  Executando análises: Groq + Gemini + Claude + ChatGPT + Standard")
    print(f"{'='*80}")

    # Executa análise com todos os modos
    analyzer = ExcessiveLogsAnalyzer()
    result = analyzer.analyze_file(args.log_file)

    # Gera relatórios separados
    base_name = args.output
    if not base_name:
        # Extrai nome do arquivo de log sem extensão (SEM timestamp para sobrescrever)
        log_basename = os.path.basename(args.log_file).replace('.json', '')
        base_name = log_basename

    generated_files = analyzer.generate_reports(result, base_name)

    # Imprime resumo comparativo
    analyzer.print_summary(result)


if __name__ == '__main__':
    main()
