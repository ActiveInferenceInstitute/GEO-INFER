"""Behavior tests for ErrorRecoveryManager's recovery strategies.

Each strategy is exercised for both the recovering and the declining path,
so a strategy that silently degrades to "never recovers" fails these tests.
"""

import os
import time

import pytest

from geo_infer_git.utils.error_handler import (
    APILimitError,
    AuthenticationError,
    ErrorCategory,
    ErrorRecoveryManager,
    GitOperationError,
    NetworkError,
)


@pytest.fixture(name="manager")
def _manager():
    return ErrorRecoveryManager()


@pytest.fixture(name="fast_backoff")
def _fast_backoff(monkeypatch):
    """Record backoff delays instead of actually sleeping."""
    slept = []
    monkeypatch.setattr(
        "geo_infer_git.utils.error_handler.time.sleep", lambda s: slept.append(s)
    )
    return slept


class TestRetryWithBackoff:
    def test_grants_a_retry_and_sleeps_before_it(self, manager, fast_backoff):
        """A first failure earns a retry preceded by the base delay."""
        error = NetworkError("connection reset")
        assert manager._retry_with_backoff(error, {"attempt": 1}) is True
        assert fast_backoff == [manager.BASE_RETRY_DELAY_SECONDS]

    def test_delay_grows_exponentially_with_attempt(self, manager, fast_backoff):
        """Each successive attempt waits twice as long."""
        error = NetworkError("connection reset")
        manager._retry_with_backoff(error, {"attempt": 1, "max_retry_attempts": 9})
        manager._retry_with_backoff(error, {"attempt": 2, "max_retry_attempts": 9})
        manager._retry_with_backoff(error, {"attempt": 3, "max_retry_attempts": 9})
        assert fast_backoff == [1.0, 2.0, 4.0]

    def test_delay_is_capped(self, manager, fast_backoff):
        """Backoff never exceeds the configured ceiling."""
        error = NetworkError("connection reset")
        manager._retry_with_backoff(error, {"attempt": 20, "max_retry_attempts": 99})
        assert fast_backoff == [manager.MAX_BACKOFF_SECONDS]

    def test_declines_once_budget_is_spent(self, manager, fast_backoff):
        """The strategy stops granting retries at the attempt limit."""
        error = NetworkError("connection reset")
        assert manager._retry_with_backoff(error, {"attempt": 3, "max_retry_attempts": 3}) is False
        assert fast_backoff == []


class TestRefreshToken:
    def test_uses_supplied_callable_and_validates_result(self, manager, monkeypatch):
        """A token_refresh callable's result is stored and validated."""
        monkeypatch.setattr(manager, "_check_token_validity", lambda e, c: True)
        context = {"token_refresh": lambda: "refreshed-token"}
        assert manager._refresh_token(AuthenticationError("401"), context) is True
        assert context["token"] == "refreshed-token"

    def test_rejects_a_token_that_fails_validation(self, manager, monkeypatch):
        """A refreshed token that does not validate is not a recovery."""
        monkeypatch.setattr(manager, "_check_token_validity", lambda e, c: False)
        context = {"token_refresh": lambda: "still-bad"}
        assert manager._refresh_token(AuthenticationError("401"), context) is False

    def test_declines_when_no_mechanism_is_configured(self, manager):
        """With nothing to refresh from, the strategy declines."""
        assert manager._refresh_token(AuthenticationError("401"), {}) is False

    def test_survives_a_raising_refresh_callable(self, manager):
        """A refresher that raises is reported as a failed recovery, not a crash."""

        def boom():
            raise RuntimeError("refresh endpoint down")

        assert manager._refresh_token(AuthenticationError("401"), {"token_refresh": boom}) is False

    def test_oauth_exchange_stores_the_new_access_token(self, manager, monkeypatch):
        """A 200 from token_url yields the access_token and validates it."""

        class Response:
            status_code = 200

            @staticmethod
            def json():
                return {"access_token": "oauth-token"}

        monkeypatch.setattr(
            "geo_infer_git.utils.error_handler.requests.post", lambda *a, **k: Response()
        )
        monkeypatch.setattr(manager, "_check_token_validity", lambda e, c: True)
        context = {"refresh_token": "r", "token_url": "https://example.invalid/token"}
        assert manager._refresh_token(AuthenticationError("401"), context) is True
        assert context["token"] == "oauth-token"


class TestAlternateApiEndpoint:
    def _response(self, status):
        class Response:
            status_code = status

        return Response()

    def test_selects_the_first_healthy_endpoint(self, manager, monkeypatch):
        """A rate-limited candidate is skipped in favour of a healthy one."""
        seen = []

        def fake_get(url, **kwargs):
            seen.append(url)
            return self._response(429 if url.endswith("/a") else 200)

        monkeypatch.setattr("geo_infer_git.utils.error_handler.requests.get", fake_get)
        context = {
            "api_base_url": "https://api.example.invalid/current",
            "alternate_api_endpoints": [
                "https://api.example.invalid/a",
                "https://api.example.invalid/b",
            ],
        }
        assert manager._use_alternate_api_endpoint(APILimitError("rate limited"), context) is True
        assert context["api_base_url"] == "https://api.example.invalid/b"
        assert seen == [
            "https://api.example.invalid/a",
            "https://api.example.invalid/b",
        ]

    def test_skips_the_endpoint_that_is_already_failing(self, manager, monkeypatch):
        """The current base URL is never re-selected as its own alternate."""
        monkeypatch.setattr(
            "geo_infer_git.utils.error_handler.requests.get",
            lambda url, **k: self._response(200),
        )
        current = "https://api.example.invalid/current"
        context = {"api_base_url": current, "alternate_api_endpoints": [current]}
        assert manager._use_alternate_api_endpoint(APILimitError("rate limited"), context) is False
        assert context["api_base_url"] == current

    def test_declines_when_every_alternate_is_unhealthy(self, manager, monkeypatch):
        """All-5xx candidates mean no recovery."""
        monkeypatch.setattr(
            "geo_infer_git.utils.error_handler.requests.get",
            lambda url, **k: self._response(503),
        )
        context = {"alternate_api_endpoints": ["https://api.example.invalid/a"]}
        assert manager._use_alternate_api_endpoint(APILimitError("rate limited"), context) is False

    def test_declines_when_no_alternates_are_configured(self, manager):
        """Nothing to switch to is not a recovery."""
        assert manager._use_alternate_api_endpoint(APILimitError("rate limited"), {}) is False


class TestRetryGitOperation:
    def test_grants_retry_for_a_valid_repository(self, manager, fast_backoff, tmp_path):
        """A usable repository earns a backed-off retry."""
        import git
        git.Repo.init(tmp_path)
        context = {"path": str(tmp_path), "attempt": 1}
        assert manager._retry_git_operation(GitOperationError("fetch failed"), context) is True
        assert fast_backoff  # a delay was taken

    def test_declines_for_a_path_that_is_not_a_repository(self, manager, fast_backoff, tmp_path):
        """Retrying against a non-repository would just repeat the failure."""
        context = {"path": str(tmp_path), "attempt": 1}
        assert manager._retry_git_operation(GitOperationError("fetch failed"), context) is False
        assert fast_backoff == []


class TestCleanGitCache:
    def test_removes_a_stale_index_lock(self, manager, tmp_path):
        """An abandoned lock file is cleared so the retry can proceed."""
        import git
        repo = git.Repo.init(tmp_path)
        lock = os.path.join(repo.git_dir, "index.lock")
        with open(lock, "w", encoding="utf-8") as handle:
            handle.write("")
        stale = time.time() - 10_000
        os.utime(lock, (stale, stale))

        assert manager._clean_git_cache(GitOperationError("locked"), {"path": str(tmp_path)}) is True
        assert not os.path.exists(lock)

    def test_leaves_a_fresh_lock_alone(self, manager, tmp_path):
        """A lock a live process may hold is never taken away from it."""
        import git
        repo = git.Repo.init(tmp_path)
        lock = os.path.join(repo.git_dir, "index.lock")
        with open(lock, "w", encoding="utf-8") as handle:
            handle.write("")

        assert manager._clean_git_cache(GitOperationError("locked"), {"path": str(tmp_path)}) is False
        assert os.path.exists(lock)

    def test_declines_without_a_path(self, manager):
        """No repository to clean means no recovery."""
        assert manager._clean_git_cache(GitOperationError("locked"), {}) is False


class TestStrategyRegistry:
    def test_every_registered_strategy_is_callable(self, manager):
        """The registry wires real bound methods for each category."""
        assert set(manager.recovery_strategies) >= {
            ErrorCategory.NETWORK,
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.API_LIMIT,
            ErrorCategory.GIT_OPERATION,
            ErrorCategory.FILESYSTEM,
        }
        for strategies in manager.recovery_strategies.values():
            assert strategies
            for strategy in strategies:
                assert callable(strategy)

    def test_attempt_recovery_reports_success_from_a_strategy(self, manager, fast_backoff):
        """A recoverable network error is recovered by the backoff strategy."""
        error = NetworkError("connection reset")
        assert error.recoverable is True
        assert manager.attempt_recovery(error, {"attempt": 1}) is True

    def test_attempt_recovery_declines_a_non_recoverable_error(self, manager):
        """A non-recoverable error short-circuits before any strategy runs."""
        error = AuthenticationError("bad credentials")
        error.recoverable = False
        assert manager.attempt_recovery(error, {}) is False
