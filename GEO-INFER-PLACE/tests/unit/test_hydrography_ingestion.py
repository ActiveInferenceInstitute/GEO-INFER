"""Real loopback HTTP exercises of pagination, integrity, resource limits and resume."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time
from threading import Thread
from urllib.parse import parse_qs, urlsplit

import pytest

from geo_infer_place.hydrography import (
    HydrographyError,
    HydrographySelection,
    IncompleteHydrographyError,
    NHDPlusHRIngestor,
    load_flowlines,
)


def feature(identifier):
    """Explicitly constructed topology record; no claim of measured hydrography."""
    return {
        "type": "Feature",
        "properties": {
            "OBJECTID": identifier,
            "nhdplusid": 1000 + identifier,
            "fromnode": identifier,
            "tonode": identifier + 1,
            "streamorde": 1,
            "lengthkm": 1.0,
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [[0, identifier], [0, identifier + 1]],
        },
    }


@contextmanager
def service(state):
    """Serve deterministic ArcGIS-shaped responses through real local requests."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = parse_qs(urlsplit(self.path).query)
            if "returnIdsOnly" in params:
                state.setdefault("id_queries", 0)
                state["id_queries"] += 1
                payload = {
                    "objectIdFieldName": "OBJECTID",
                    "objectIds": state.get("ids", [1, 2, 3]),
                }
            else:
                ids = [int(i) for i in params["objectIds"][0].split(",")]
                state.setdefault("pages", []).append(ids)
                if ids[0] == 3 and state.get("fail_once"):
                    state["fail_once"] = False
                    self.send_response(503)
                    self.end_headers()
                    return
                payload = {
                    "type": "FeatureCollection",
                    "features": [feature(i) for i in ids],
                }
                if state.get("missing"):
                    payload["features"] = payload["features"][:-1]
                if state.get("transfer_limit"):
                    payload["exceededTransferLimit"] = True
                if state.get("service_error"):
                    payload = {"error": {"code": 400, "message": "Bad query"}}
            content = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            if state.get("drip"):
                try:
                    for byte in content:
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        time.sleep(0.005)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                self.wfile.write(content)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/layer"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_resumes_verified_pages_and_preserves_native_topology(tmp_path):
    state = {"fail_once": True}
    selection = HydrographySelection(bbox=(-1, -1, 1, 5))
    with service(state) as url:
        client = NHDPlusHRIngestor(service_url=url, page_size=2)
        with pytest.raises(HydrographyError):
            client.ingest(selection, tmp_path)
        manifest = json.loads((tmp_path / "manifest.json").read_text())
        assert manifest["status"] == "incomplete"
        assert not (tmp_path / "flowlines.geojson").exists()
        path = client.ingest(selection, tmp_path)
    assert state["id_queries"] == 1
    assert state["pages"] == [[1, 2], [3], [3]]
    loaded = load_flowlines(path)
    assert list(loaded["nhdplusid"]) == list(loaded["comid"]) == [1001, 1002, 1003]
    assert list(loaded["from_node"]) == [1, 2, 3]
    assert loaded.crs.to_epsg() == 4326
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["feature_count"] == 3
    assert manifest["source_url"] == url
    assert manifest["acquired_at"]
    assert len(manifest["sha256"]) == 64


@pytest.mark.parametrize(
    "state", [{"missing": True}, {"transfer_limit": True}, {"service_error": True}]
)
def test_source_failure_is_never_certified_as_empty(tmp_path, state):
    with service(state) as url:
        with pytest.raises(HydrographyError):
            NHDPlusHRIngestor(service_url=url).ingest(
                HydrographySelection(huc8="18010101"), tmp_path
            )
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["status"] in {"failed", "incomplete"}
    assert not (tmp_path / "flowlines.geojson").exists()


def test_valid_empty_selection_is_distinct(tmp_path):
    with service({"ids": []}) as url:
        path = NHDPlusHRIngestor(service_url=url).ingest(
            HydrographySelection(huc8="18010101"), tmp_path
        )
    assert load_flowlines(path).empty
    assert json.loads((tmp_path / "manifest.json").read_text())["status"] == "empty"


def test_corrupted_page_and_output_are_rejected(tmp_path):
    selection = HydrographySelection(huc8="18010101")
    with service({}) as url:
        client = NHDPlusHRIngestor(service_url=url)
        path = client.ingest(selection, tmp_path)
        path.write_text("{}")
        with pytest.raises(IncompleteHydrographyError, match="match its manifest"):
            load_flowlines(path)
        (tmp_path / "page-000000000.geojson").write_text("{}")
        with pytest.raises(IncompleteHydrographyError, match="checksum"):
            client.ingest(selection, tmp_path)
        with pytest.raises(IncompleteHydrographyError, match="not complete"):
            load_flowlines(path)


@pytest.mark.parametrize("kwargs", [{"max_features": 2}, {"max_bytes": 100}])
def test_resource_caps_leave_no_complete_dataset(tmp_path, kwargs):
    with service({}) as url:
        with pytest.raises(IncompleteHydrographyError):
            NHDPlusHRIngestor(service_url=url, **kwargs).ingest(
                HydrographySelection(huc8="18010101"), tmp_path
            )
    assert not (tmp_path / "flowlines.geojson").exists()


def test_resume_selection_mismatch_fails_before_network(tmp_path):
    with service({}) as url:
        client = NHDPlusHRIngestor(service_url=url)
        client.ingest(HydrographySelection(huc8="18010101"), tmp_path)
        with pytest.raises(ValueError, match="different"):
            client.ingest(HydrographySelection(huc8="18010102"), tmp_path)


@pytest.mark.parametrize(
    "kwargs",
    [{}, {"huc8": "';DROP"}, {"bbox": (1, 0, 0, 1)}, {"bbox": (0, 0, float("nan"), 1)}],
)
def test_selection_validation(kwargs):
    with pytest.raises(ValueError):
        HydrographySelection(**kwargs)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/data",
        "https://secret@hydro.nationalmap.gov/data",
        "file:///tmp/data",
    ],
)
def test_source_url_validation(url):
    with pytest.raises(ValueError):
        NHDPlusHRIngestor(service_url=url)


def test_slow_drip_cannot_extend_request_duration_indefinitely(tmp_path):
    with service({"drip": True}) as url:
        started = time.monotonic()
        with pytest.raises(IncompleteHydrographyError, match="max_duration"):
            NHDPlusHRIngestor(service_url=url, timeout=0.2, max_duration=0.05).ingest(
                HydrographySelection(huc8="18010101"), tmp_path
            )
        assert time.monotonic() - started < 0.3
    assert not (tmp_path / "flowlines.geojson").exists()
