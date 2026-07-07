import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzers.unnecessary_logs_detector import UnnecessaryLogsDetector
from src.utils.log_processor import LogProcessor


def make_log(level="INFO", path="/api/data", method="GET", status=200, message="ok", service="svc"):
    return {
        "timestamp": "2026-01-01T00:00:00.000Z",
        "level": level,
        "service": service,
        "message": message,
        "http": {"method": method, "path": path, "status_code": status},
    }


class TestUnnecessaryLogsDetectorStandard:
    def setup_method(self):
        self.detector = UnnecessaryLogsDetector(llm_client=None)

    def test_returns_required_keys(self):
        logs = [make_log()]
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.detector.analyze(logs, dupes)
        for key in ("analysis_type", "total_logs", "unnecessary_logs_count",
                    "reduction_potential_percentage", "issues", "recommendations", "severity"):
            assert key in result

    def test_detects_static_asset_logs(self):
        logs = [
            make_log(path="/static/app.js"),
            make_log(path="/assets/style.css"),
            make_log(path="/api/orders", message="Order created"),
        ]
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.detector.analyze(logs, dupes)
        assert result["static_asset_logs"]["count"] == 2

    def test_detects_trivial_get_success_logs(self):
        logs = [
            make_log(method="GET", status=200, message="Request handled"),
            make_log(method="GET", status=204, message="Request handled"),
            make_log(method="POST", status=201, message="Order created"),  # não trivial
        ]
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.detector.analyze(logs, dupes)
        assert result["trivial_success_logs"]["count"] == 2

    def test_detects_excessive_duplicates(self):
        # 15 logs idênticos — acima do limite de 10
        logs = [make_log(message="Health check ok", path="/health")] * 15
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.detector.analyze(logs, dupes)
        assert result["excessive_duplicates"]["patterns_count"] >= 1

    def test_clean_logs_have_low_reduction_potential(self):
        logs = [
            make_log(method="POST", status=201, message=f"Order {i} created", path="/orders")
            for i in range(10)
        ]
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.detector.analyze(logs, dupes)
        assert result["reduction_potential_percentage"] < 10

    def test_reduction_percentage_within_bounds(self):
        logs = [make_log(path="/static/app.js")] * 50 + [make_log(message="Real event")] * 50
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.detector.analyze(logs, dupes)
        assert 0 <= result["reduction_potential_percentage"] <= 100

    def test_empty_logs(self):
        result = self.detector.analyze([], [])
        assert result["total_logs"] == 0
        assert result["unnecessary_logs_count"] == 0
        assert result["reduction_potential_percentage"] == 0

    def test_severity_high_when_many_unnecessary(self):
        # Quase todos os logs são assets estáticos
        logs = [make_log(path="/static/bundle.js")] * 90 + [make_log(message="Real event")] * 10
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.detector.analyze(logs, dupes)
        assert result["severity"] in ("high", "critical")
