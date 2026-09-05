"""Real local HTTP/process checks for supervised regional downloads."""

from contextlib import contextmanager
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time

import pytest

from geo_infer_place.core import regional_layers as module


@contextmanager
def local_source(mode, payload=b"source bytes"):
    """Run a finite loopback server; no external service participates in tests."""
    started = threading.Event()
    disconnected = threading.Event()
    stopping = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            started.set()
            self.close_connection = True
            try:
                if mode == "headers":
                    stopping.wait(8)
                    return
                if mode == "redirect":
                    self.send_response(302)
                    self.send_header("Location", "https://example.invalid/forbidden")
                    self.end_headers()
                    return
                if mode == "status":
                    self.send_error(503)
                    return
                body = gzip.compress(payload) if mode == "gzip" else payload
                self.send_response(200)
                self.send_header(
                    "Content-Length", str(100_000 if mode == "drip" else len(body))
                )
                if mode == "gzip":
                    self.send_header("Content-Encoding", "gzip")
                self.end_headers()
                if mode == "drip":
                    stop_at = time.monotonic() + 8
                    while not stopping.is_set() and time.monotonic() < stop_at:
                        self.wfile.write(b"x")
                        self.wfile.flush()
                        stopping.wait(0.03)
                else:
                    self.wfile.write(body)
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                disconnected.set()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True
    )
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/source", started, disconnected
    finally:
        stopping.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


@pytest.fixture
def spawned_workers(monkeypatch):
    import subprocess

    original = subprocess.Popen
    workers = []

    def capture(*args, **kwargs):
        worker = original(*args, **kwargs)
        workers.append(worker)
        return worker

    monkeypatch.setattr(subprocess, "Popen", capture)
    return workers


@pytest.mark.parametrize("mode", ["drip", "headers"])
def test_parent_deadline_stops_and_reaps_real_worker(mode, spawned_workers):
    with local_source(mode) as (url, started, disconnected):
        begin = time.monotonic()
        with pytest.raises(TimeoutError, match="deadline"):
            module._download(url, deadline=begin + 2, remaining_bytes=100_000)
        elapsed = time.monotonic() - begin
        assert started.is_set(), "The real HTTP request must have reached the server"
        assert elapsed < 3.5, f"Parent deadline was not enforced: {elapsed:.3f}s"
        if mode == "drip":
            assert disconnected.wait(0.5), (
                "Worker termination must close the slow stream"
            )
    assert len(spawned_workers) == 1
    worker = spawned_workers[0]
    assert worker.poll() is not None
    assert worker.stdout.closed and worker.stderr.closed


def test_success_preserves_exact_bytes_and_reaps_worker(spawned_workers):
    payload = b'{"source":"UTF-8 \xc3\xa9","value":1}\n'
    with local_source("success", payload) as (url, _, _):
        result = module._download(url, time.monotonic() + 10, len(payload))
    assert result == payload
    assert len(spawned_workers) == 1 and spawned_workers[0].returncode == 0


@pytest.mark.parametrize("mode", ["success", "gzip"])
def test_real_response_byte_cap_is_enforced_before_result(mode, spawned_workers):
    with local_source(mode, b"x" * 200_000) as (url, _, _):
        with pytest.raises(ValueError, match="budget"):
            module._download(url, time.monotonic() + 10, 1000)
    assert len(spawned_workers) == 1 and spawned_workers[0].poll() is not None


@pytest.mark.parametrize(
    "mode,error", [("redirect", ValueError), ("status", RuntimeError)]
)
def test_real_http_failures_do_not_return_partial_success(mode, error, spawned_workers):
    with local_source(mode) as (url, _, _):
        with pytest.raises(error):
            module._download(url, time.monotonic() + 10, 1000)
    assert len(spawned_workers) == 1 and spawned_workers[0].poll() is not None


def test_expired_deadline_does_not_spawn_a_worker(spawned_workers):
    with pytest.raises(TimeoutError, match="deadline"):
        module._download("https://example.invalid/source", time.monotonic() - 1, 1000)
    assert spawned_workers == []


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/hosts",
        "http://example.com/source",
        "https://user:password@example.com/source",
        "https://example.com/source#fragment",
        "https:///missing-host",
    ],
)
def test_invalid_worker_urls_never_launch(url, spawned_workers):
    with pytest.raises(ValueError):
        module._download(url, time.monotonic() + 10, 1000)
    assert spawned_workers == []


def test_worker_ignores_parent_pythonpath(tmp_path, monkeypatch, spawned_workers):
    (tmp_path / "requests.py").write_text(
        "raise RuntimeError('injected requests module')\n"
    )
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    with local_source("success", b"isolated") as (url, _, _):
        assert module._download(url, time.monotonic() + 10, 1000) == b"isolated"
    assert "-I" in spawned_workers[0].args
    assert Path(spawned_workers[0].args[2]).name == "_regional_download_worker.py"


def test_batch_deadline_preserves_existing_artifacts_after_prior_download(
    tmp_path, monkeypatch, spawned_workers
):
    config = Path(__file__).resolve().parents[2] / "locations/cascadia/config"
    raw_volcano = (config / "cascadia_volcanoes.source.json").read_bytes()
    old_output = tmp_path / "cascadia_volcanoes.geojson"
    old_output.write_bytes(b"existing layer")
    old_receipt = tmp_path / "cascadia_layers.provenance.json"
    old_receipt.write_bytes(b"existing receipt")
    with local_source("success", raw_volcano) as (first_url, _, _):
        with local_source("drip") as (second_url, started, _):
            sources = {kind: dict(spec) for kind, spec in module.SOURCES.items()}
            sources["volcanoes"]["url"] = first_url
            sources["watersheds"]["url"] = second_url
            monkeypatch.setattr(module, "SOURCES", sources)
            monkeypatch.setattr(module, "_BATCH_TIMEOUT_SECONDS", 3.0)
            begin = time.monotonic()
            with pytest.raises(TimeoutError, match="deadline"):
                module.acquire_regional_layers(tmp_path)
            assert started.is_set()
            assert time.monotonic() - begin < 4.5
    assert len(spawned_workers) == 2
    assert spawned_workers[0].returncode == 0
    assert all(process.poll() is not None for process in spawned_workers)
    assert old_output.read_bytes() == b"existing layer"
    assert old_receipt.read_bytes() == b"existing receipt"
    assert set(tmp_path.iterdir()) == {old_output, old_receipt}


@pytest.mark.parametrize("budget", [0, -1, True, 1.5, module.MAX_BYTES + 1])
def test_invalid_byte_budgets_never_launch(budget, spawned_workers):
    with pytest.raises(ValueError):
        module._download(
            "https://example.invalid/source", time.monotonic() + 10, budget
        )
    assert spawned_workers == []


@pytest.mark.parametrize("deadline", [True, float("nan"), float("inf"), 10**1000])
def test_invalid_deadlines_never_launch(deadline, spawned_workers):
    with pytest.raises(ValueError):
        module._download("https://example.invalid/source", deadline, 1000)
    assert spawned_workers == []
