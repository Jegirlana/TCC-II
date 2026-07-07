import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzers.sampling_recommender import SamplingRecommender
from src.utils.log_processor import LogProcessor


def make_logs(count, service="svc", level="INFO"):
    return [
        {
            "timestamp": f"2026-01-01T{i // 60:02d}:{i % 60:02d}:00.000Z",
            "level": level,
            "service": service,
            "message": f"Message {i}",
        }
        for i in range(count)
    ]


LOW_RATE = {"rate_per_minute": 10, "rate_per_second": 0.17, "duration_minutes": 5, "total": 50}
HIGH_RATE = {"rate_per_minute": 200, "rate_per_second": 3.3, "duration_minutes": 5, "total": 1000}
CRITICAL_RATE = {"rate_per_minute": 600, "rate_per_second": 10, "duration_minutes": 5, "total": 3000}


class TestSamplingRecommenderStandard:
    def setup_method(self):
        self.recommender = SamplingRecommender(llm_client=None)

    def test_returns_required_keys(self):
        logs = make_logs(50)
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, LOW_RATE, service_dist, dupes)
        for key in ("analysis_type", "current_state", "recommended_strategies",
                    "estimated_reduction", "recommendations", "severity"):
            assert key in result

    def test_severity_ok_on_low_rate(self):
        logs = make_logs(50)
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, LOW_RATE, service_dist, dupes)
        assert result["severity"] in ("ok", "low")

    def test_severity_high_on_high_rate(self):
        logs = make_logs(1000)
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, HIGH_RATE, service_dist, dupes)
        assert result["severity"] in ("high", "critical")

    def test_severity_critical_on_very_high_rate(self):
        logs = make_logs(3000)
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, CRITICAL_RATE, service_dist, dupes)
        assert result["severity"] == "critical"

    def test_always_recommends_priority_based_strategy(self):
        logs = make_logs(50)
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, LOW_RATE, service_dist, dupes)
        strategy_types = [s["strategy"] for s in result["recommended_strategies"]]
        assert "priority_based" in strategy_types

    def test_recommends_rate_based_on_high_volume(self):
        logs = make_logs(1000)
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, HIGH_RATE, service_dist, dupes)
        strategy_types = [s["strategy"] for s in result["recommended_strategies"]]
        assert "rate_based" in strategy_types

    def test_estimated_reduction_has_percentage_key(self):
        logs = make_logs(50)
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, LOW_RATE, service_dist, dupes)
        assert "estimated_percentage" in result["estimated_reduction"]

    def test_empty_logs(self):
        result = self.recommender.analyze([], LOW_RATE, {}, [])
        assert isinstance(result["recommended_strategies"], list)
        assert result["current_state"]["total_logs"] == 0

    def test_multiple_services_analyzed(self):
        logs = make_logs(100, service="auth") + make_logs(100, service="payments")
        service_dist = LogProcessor.get_service_distribution(logs)
        dupes = LogProcessor.find_duplicate_logs(logs)
        result = self.recommender.analyze(logs, HIGH_RATE, service_dist, dupes)
        services_analyzed = [s["service"] for s in result["service_analysis"]]
        assert "auth" in services_analyzed
        assert "payments" in services_analyzed
