"""Tests for the LLM proxy policy (item 7)."""

from __future__ import annotations

import pytest

from geo_infer_agent.core.llm_proxy import (
    LLMProxyPolicy,
    LLMProxyPolicyError,
    TokenBucket,
    check_allowed_model,
    check_output_tokens,
    check_request_size,
    enforce_llm_proxy_policy,
)

ALLOWED = ["gemma3:4b", "openrouter/deepseek"]


def test_allowed_model_ok() -> None:
    check_allowed_model(LLMProxyPolicy(allowed_models=ALLOWED), "gemma3:4b")
    # No allowlist configured -> anything passes.
    check_allowed_model(LLMProxyPolicy(), "any-model")


def test_allowed_model_rejected() -> None:
    with pytest.raises(LLMProxyPolicyError):
        check_allowed_model(LLMProxyPolicy(allowed_models=ALLOWED), "gpt-4o")


def test_request_size_ok() -> None:
    check_request_size(LLMProxyPolicy(max_request_chars=1000), 500)


def test_request_size_rejected() -> None:
    with pytest.raises(LLMProxyPolicyError):
        check_request_size(LLMProxyPolicy(max_request_chars=1000), 5000)


def test_output_tokens_ok() -> None:
    check_output_tokens(LLMProxyPolicy(max_output_tokens=4096), 1000)


def test_output_tokens_rejected() -> None:
    with pytest.raises(LLMProxyPolicyError):
        check_output_tokens(LLMProxyPolicy(max_output_tokens=4096), 5000)


def test_enforce_full_pass() -> None:
    policy = LLMProxyPolicy(allowed_models=ALLOWED, max_request_chars=1000)
    enforce_llm_proxy_policy(
        policy,
        model="gemma3:4b",
        request_payload="hi",
        requested_output_tokens=100,
    )
    # No exception raised.


def test_enforce_model_rejected() -> None:
    policy = LLMProxyPolicy(allowed_models=ALLOWED)
    with pytest.raises(LLMProxyPolicyError):
        enforce_llm_proxy_policy(policy, model="gpt-4o", request_payload="hi")


def test_enforce_size_via_payload_chars() -> None:
    policy = LLMProxyPolicy(max_request_chars=10)
    with pytest.raises(LLMProxyPolicyError):
        enforce_llm_proxy_policy(policy, model="gemma3:4b", payload_chars=100)


def test_token_bucket_allows_up_to_limit() -> None:
    bucket = TokenBucket(limit=2)
    assert bucket.allow("alice") is True
    assert bucket.allow("alice") is True
    assert bucket.allow("alice") is False
    # Different client unaffected.
    assert bucket.allow("bob") is True


def test_token_bucket_resets_after_window() -> None:
    bucket = TokenBucket(limit=1, window_seconds=0.001)
    assert bucket.allow("alice") is True
    assert bucket.allow("alice") is False
    import time

    time.sleep(0.005)
    # New window -> allowed again.
    assert bucket.allow("alice") is True


def test_enforce_rate_limit_rejects() -> None:
    policy = LLMProxyPolicy(allowed_models=ALLOWED)
    bucket = TokenBucket(limit=1)
    enforce_llm_proxy_policy(
        policy, model="gemma3:4b", request_payload="hi", client_id="alice", rate_limiter=bucket
    )
    with pytest.raises(LLMProxyPolicyError):
        enforce_llm_proxy_policy(
            policy,
            model="gemma3:4b",
            request_payload="hi",
            client_id="alice",
            rate_limiter=bucket,
        )
