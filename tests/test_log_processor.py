import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.log_processor import LogProcessor


SAMPLE_LOGS = [
    {"timestamp": "2026-01-01T00:00:00.000Z", "level": "INFO",  "service": "auth",     "message": "User login",           "http": {"method": "POST", "path": "/login",  "status_code": 200}},
    {"timestamp": "2026-01-01T00:01:00.000Z", "level": "INFO",  "service": "auth",     "message": "User login",           "http": {"method": "POST", "path": "/login",  "status_code": 200}},
    {"timestamp": "2026-01-01T00:02:00.000Z", "level": "ERROR", "service": "payments", "message": "Payment failed",       "error": {"type": "TimeoutError", "message": "timeout"}, "http": {"method": "POST", "path": "/pay", "status_code": 500}},
    {"timestamp": "2026-01-01T00:03:00.000Z", "level": "WARN",  "service": "payments", "message": "Retry attempt",        "http": {"method": "POST", "path": "/pay",    "status_code": 503}},
    {"timestamp": "2026-01-01T00:04:00.000Z", "level": "DEBUG", "service": "auth",     "message": "Token validated",      "tags": ["auth", "debug"]},
    {"timestamp": "2026-01-01T00:05:00.000Z", "level": "INFO",  "service": "orders",   "message": "Order created: 42",    "tags": ["order", "create"]},
]


class TestGetLevelDistribution:
    def test_counts_each_level(self):
        dist = LogProcessor.get_level_distribution(SAMPLE_LOGS)
        assert dist["INFO"] == 3
        assert dist["ERROR"] == 1
        assert dist["WARN"] == 1
        assert dist["DEBUG"] == 1

    def test_empty_logs(self):
        assert LogProcessor.get_level_distribution([]) == {}

    def test_missing_level_falls_back_to_unknown(self):
        logs = [{"message": "no level field"}]
        dist = LogProcessor.get_level_distribution(logs)
        assert dist.get("UNKNOWN") == 1


class TestGetServiceDistribution:
    def test_counts_each_service(self):
        dist = LogProcessor.get_service_distribution(SAMPLE_LOGS)
        assert dist["auth"] == 3
        assert dist["payments"] == 2
        assert dist["orders"] == 1

    def test_empty_logs(self):
        assert LogProcessor.get_service_distribution([]) == {}


class TestGetErrorTypes:
    def test_counts_error_types(self):
        types = LogProcessor.get_error_types(SAMPLE_LOGS)
        assert types["TimeoutError"] == 1

    def test_ignores_logs_without_error_field(self):
        types = LogProcessor.get_error_types([{"level": "INFO", "message": "ok"}])
        assert types == {}

    def test_empty_logs(self):
        assert LogProcessor.get_error_types([]) == {}


class TestGetHttpStatusDistribution:
    def test_counts_status_codes(self):
        dist = LogProcessor.get_http_status_distribution(SAMPLE_LOGS)
        assert dist[200] == 2
        assert dist[500] == 1
        assert dist[503] == 1

    def test_ignores_logs_without_http(self):
        dist = LogProcessor.get_http_status_distribution([{"level": "INFO"}])
        assert dist == {}


class TestGetTagsDistribution:
    def test_counts_tags(self):
        dist = LogProcessor.get_tags_distribution(SAMPLE_LOGS)
        assert dist["auth"] == 1
        assert dist["debug"] == 1
        assert dist["order"] == 1
        assert dist["create"] == 1

    def test_empty_logs(self):
        assert LogProcessor.get_tags_distribution([]) == {}


class TestFindDuplicateLogs:
    def test_finds_repeated_messages(self):
        dupes = LogProcessor.find_duplicate_logs(SAMPLE_LOGS)
        messages = [d["pattern"]["message"] for d in dupes]
        assert "User login" in messages

    def test_count_is_correct(self):
        dupes = LogProcessor.find_duplicate_logs(SAMPLE_LOGS)
        login_dupe = next(d for d in dupes if d["pattern"]["message"] == "User login")
        assert login_dupe["count"] == 2

    def test_no_duplicates(self):
        unique_logs = [
            {"level": "INFO", "service": "a", "message": "msg 1"},
            {"level": "INFO", "service": "a", "message": "msg 2"},
        ]
        dupes = LogProcessor.find_duplicate_logs(unique_logs)
        assert dupes == []

    def test_sorted_by_count_descending(self):
        logs = [
            {"level": "INFO", "service": "a", "message": "x"},
            {"level": "INFO", "service": "a", "message": "x"},
            {"level": "INFO", "service": "a", "message": "x"},
            {"level": "INFO", "service": "a", "message": "y"},
            {"level": "INFO", "service": "a", "message": "y"},
        ]
        dupes = LogProcessor.find_duplicate_logs(logs)
        assert dupes[0]["count"] >= dupes[-1]["count"]


class TestCalculateLogRate:
    def test_calculates_rate(self):
        rate = LogProcessor.calculate_log_rate(SAMPLE_LOGS)
        assert rate["total"] == len(SAMPLE_LOGS)
        assert rate["rate_per_minute"] > 0
        assert rate["duration_minutes"] > 0

    def test_empty_logs(self):
        rate = LogProcessor.calculate_log_rate([])
        assert rate["total"] == 0
        assert rate["rate_per_minute"] == 0

    def test_single_log(self):
        rate = LogProcessor.calculate_log_rate([SAMPLE_LOGS[0]])
        assert rate["total"] == 1
        assert rate["rate_per_minute"] == 0


class TestGroupByServiceAndLevel:
    def test_groups_correctly(self):
        groups = LogProcessor.group_by_service_and_level(SAMPLE_LOGS)
        assert groups["auth"]["INFO"] == 2
        assert groups["auth"]["DEBUG"] == 1
        assert groups["payments"]["ERROR"] == 1
        assert groups["payments"]["WARN"] == 1

    def test_empty_logs(self):
        assert LogProcessor.group_by_service_and_level([]) == {}
