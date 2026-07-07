import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzers.log_level_analyzer import LogLevelAnalyzer
from src.utils.log_processor import LogProcessor


def make_logs(level_counts):
    """Cria lista de logs com a distribuição de níveis especificada."""
    logs = []
    for level, count in level_counts.items():
        for i in range(count):
            logs.append({
                "timestamp": f"2026-01-01T00:{i:02d}:00.000Z",
                "level": level,
                "service": "test-service",
                "message": f"Test message {i}",
            })
    return logs


class TestLogLevelAnalyzerStandard:
    def setup_method(self):
        self.analyzer = LogLevelAnalyzer(llm_client=None)

    def test_returns_required_keys(self):
        logs = make_logs({"INFO": 5, "ERROR": 1})
        service_levels = LogProcessor.group_by_service_and_level(logs)
        result = self.analyzer.analyze(logs, service_levels)
        for key in ("analysis_type", "total_logs", "level_distribution", "issues", "recommendations", "severity"):
            assert key in result

    def test_no_excessive_info_issue_when_below_threshold(self):
        # 60% INFO, 20% WARN, 20% ERROR — INFO abaixo do limite de 70%
        logs = make_logs({"INFO": 60, "WARN": 20, "ERROR": 20, "DEBUG": 0})
        service_levels = LogProcessor.group_by_service_and_level(logs)
        result = self.analyzer.analyze(logs, service_levels)
        issue_types = [i["type"] for i in result["issues"]]
        assert "excessive_info_logs" not in issue_types

    def test_detects_excessive_info_logs(self):
        # 95% INFO — acima do limite de 70%
        logs = make_logs({"INFO": 95, "ERROR": 5})
        service_levels = LogProcessor.group_by_service_and_level(logs)
        result = self.analyzer.analyze(logs, service_levels)
        issue_types = [i["type"] for i in result["issues"]]
        assert "excessive_info_logs" in issue_types

    def test_detects_debug_in_production(self):
        # 30% DEBUG — acima do limite de 5%, gera issue debug_in_production
        logs = make_logs({"INFO": 70, "DEBUG": 30})
        service_levels = LogProcessor.group_by_service_and_level(logs)
        result = self.analyzer.analyze(logs, service_levels)
        issue_types = [i["type"] for i in result["issues"]]
        assert "debug_in_production" in issue_types

    def test_severity_critical_on_very_high_info(self):
        logs = make_logs({"INFO": 100})
        service_levels = LogProcessor.group_by_service_and_level(logs)
        result = self.analyzer.analyze(logs, service_levels)
        assert result["severity"] in ("high", "critical")

    def test_total_logs_count(self):
        logs = make_logs({"INFO": 20, "ERROR": 5})
        service_levels = LogProcessor.group_by_service_and_level(logs)
        result = self.analyzer.analyze(logs, service_levels)
        assert result["total_logs"] == 25

    def test_empty_logs(self):
        result = self.analyzer.analyze([], {})
        assert result["total_logs"] == 0
        assert isinstance(result["issues"], list)
