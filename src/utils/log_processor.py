"""
Utilitários para processamento e análise de logs.
"""

import json
from typing import List, Dict, Any
from collections import Counter, defaultdict
from datetime import datetime


class LogProcessor:
    """Processador de logs para análise estatística."""

    @staticmethod
    def load_logs(file_path: str) -> List[Dict[str, Any]]:
        """Carrega logs de um arquivo JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def get_level_distribution(logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Retorna distribuição de níveis de log."""
        return dict(Counter(log.get('level', 'UNKNOWN') for log in logs))

    @staticmethod
    def get_service_distribution(logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Retorna distribuição de logs por serviço."""
        return dict(Counter(log.get('service', 'UNKNOWN') for log in logs))

    @staticmethod
    def get_error_types(logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Retorna distribuição de tipos de erro."""
        error_types = []
        for log in logs:
            if 'error' in log and isinstance(log['error'], dict):
                error_types.append(log['error'].get('type', 'UNKNOWN'))
        return dict(Counter(error_types))

    @staticmethod
    def get_http_status_distribution(logs: List[Dict[str, Any]]) -> Dict[int, int]:
        """Retorna distribuição de status HTTP."""
        statuses = []
        for log in logs:
            if 'http' in log and isinstance(log['http'], dict):
                status = log['http'].get('status_code')
                if status:
                    statuses.append(status)
        return dict(Counter(statuses))

    @staticmethod
    def get_tags_distribution(logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Retorna distribuição de tags."""
        all_tags = []
        for log in logs:
            tags = log.get('tags', [])
            if isinstance(tags, list):
                all_tags.extend(tags)
        return dict(Counter(all_tags))

    @staticmethod
    def find_duplicate_logs(logs: List[Dict[str, Any]],
                          time_window_seconds: int = 60) -> List[Dict[str, Any]]:
        """
        Identifica logs duplicados ou muito similares em uma janela de tempo.

        Args:
            logs: Lista de logs
            time_window_seconds: Janela de tempo em segundos para considerar duplicatas

        Returns:
            Lista de grupos de logs duplicados
        """
        duplicates = []
        seen = defaultdict(list)

        for log in logs:
            # Cria uma chave baseada em campos importantes
            key = (
                log.get('service'),
                log.get('level'),
                log.get('message'),
                log.get('http', {}).get('path') if isinstance(log.get('http'), dict) else None
            )
            seen[key].append(log)

        # Filtra apenas grupos com mais de um log
        for key, group in seen.items():
            if len(group) > 1:
                duplicates.append({
                    'pattern': {
                        'service': key[0],
                        'level': key[1],
                        'message': key[2],
                        'path': key[3]
                    },
                    'count': len(group),
                    'samples': group[:3]  # Primeiros 3 exemplos
                })

        return sorted(duplicates, key=lambda x: x['count'], reverse=True)

    @staticmethod
    def calculate_log_rate(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula taxa de logs por período.

        Returns:
            Estatísticas de taxa de logs
        """
        if not logs:
            return {'total': 0, 'rate_per_minute': 0}

        timestamps = []
        for log in logs:
            ts = log.get('timestamp')
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                except:
                    pass

        if len(timestamps) < 2:
            return {'total': len(logs), 'rate_per_minute': 0}

        timestamps.sort()
        duration_seconds = (timestamps[-1] - timestamps[0]).total_seconds()
        duration_minutes = max(duration_seconds / 60, 1)

        return {
            'total': len(logs),
            'duration_minutes': round(duration_minutes, 2),
            'rate_per_minute': round(len(logs) / duration_minutes, 2),
            'rate_per_second': round(len(logs) / max(duration_seconds, 1), 2)
        }

    @staticmethod
    def group_by_service_and_level(logs: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Agrupa logs por serviço e nível."""
        result = defaultdict(lambda: defaultdict(int))
        for log in logs:
            service = log.get('service', 'UNKNOWN')
            level = log.get('level', 'UNKNOWN')
            result[service][level] += 1
        return dict(result)

    @staticmethod
    def sample_logs(logs: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
        """Retorna uma amostra de logs."""
        import random
        if len(logs) <= n:
            return logs
        return random.sample(logs, n)
