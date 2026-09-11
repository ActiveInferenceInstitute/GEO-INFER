"""Unit tests for the SPMAPI upload/fit/contrast/results pipeline."""

import numpy as np
import pytest

from geo_infer_spm.api.endpoints import SPMAPI


def _json_payload(n_points: int = 10) -> dict:
    rng = np.random.default_rng(7)
    coords = np.column_stack(
        [rng.uniform(-170, 170, n_points), rng.uniform(-80, 80, n_points)]
    )
    elevation = rng.uniform(0, 100, n_points)
    values = 2.0 + 0.5 * elevation + 0.1 * rng.standard_normal(n_points)
    return {
        "coordinates": coords.tolist(),
        "data": values.tolist(),
        "covariates": {"elevation": elevation.tolist()},
    }


def _geojson_payload(n_points: int = 5) -> dict:
    rng = np.random.default_rng(11)
    features = []
    for lon, lat, value in zip(
        rng.uniform(-170, 170, n_points),
        rng.uniform(-80, 80, n_points),
        rng.uniform(0, 10, n_points),
    ):
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
                "properties": {"value": float(value)},
            }
        )
    return {"type": "FeatureCollection", "features": features}


class TestUploadData:
    """Tests for upload_data format handling and round trips."""

    def test_json_upload_round_trip(self):
        api = SPMAPI()
        payload = _json_payload()
        response = api.upload_data(payload, format="json")

        assert response["status"] == "success"
        dataset_id = response["dataset_id"]
        assert dataset_id == "dataset_1"
        assert response["n_points"] == 10

        stored = api.datasets[dataset_id]
        np.testing.assert_allclose(stored.coordinates, np.array(payload["coordinates"]))
        np.testing.assert_allclose(
            np.asarray(stored.data, dtype=float), np.array(payload["data"])
        )
        np.testing.assert_allclose(
            stored.covariates["elevation"], np.array(payload["covariates"]["elevation"])
        )

    def test_csv_upload_round_trip(self):
        api = SPMAPI()
        response = api.upload_data(
            {
                "rows": [
                    {"lat": 40.0, "lon": -100.0, "temperature": 12.5},
                    {"lat": 41.0, "lon": -101.0, "temperature": 13.5},
                    {"lat": 42.0, "lon": -102.0, "temperature": 14.5},
                ]
            },
            format="csv",
        )

        assert response["status"] == "success"
        assert response["n_points"] == 3
        stored = api.datasets[response["dataset_id"]]
        # Coordinates follow the SPMData (lon, lat) convention.
        np.testing.assert_allclose(
            stored.coordinates, [[-100.0, 40.0], [-101.0, 41.0], [-102.0, 42.0]]
        )
        assert stored.metadata["coordinate_columns"] == ["lon", "lat"]
        np.testing.assert_allclose(
            np.asarray(stored.data, dtype=float).ravel(), [12.5, 13.5, 14.5]
        )
        assert stored.metadata["source_format"] == "csv"

    def test_geojson_upload_round_trip(self):
        api = SPMAPI()
        payload = _geojson_payload()
        response = api.upload_data(payload, format="geojson")

        assert response["status"] == "success"
        assert response["n_points"] == 5
        stored = api.datasets[response["dataset_id"]]
        assert stored.metadata["source_format"] == "geojson"
        np.testing.assert_allclose(
            stored.coordinates,
            np.array(
                [f["geometry"]["coordinates"] for f in payload["features"]], dtype=float
            ),
        )
        np.testing.assert_allclose(
            np.asarray(stored.data, dtype=float),
            np.array([f["properties"]["value"] for f in payload["features"]]),
        )

    @pytest.mark.parametrize(
        "payload, format",
        [
            ({"coordinates": [[0.0, 0.0]], "data": [1.0]}, "netcdf"),
            ({"coordinates": "not-a-list"}, "json"),
            ({"type": "FeatureCollection", "features": []}, "geojson"),
            (
                {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [[0.0, 0.0], [1.0, 1.0]],
                            },
                            "properties": {"value": 1.0},
                        }
                    ],
                },
                "geojson",
            ),
            ({"rows": []}, "csv"),
        ],
    )
    def test_invalid_payloads_report_error(self, payload, format):
        api = SPMAPI()
        response = api.upload_data(payload, format=format)

        assert response["status"] == "error"
        assert "message" in response
        # A failed upload must not consume a dataset id.
        assert api.datasets == {}

    def test_next_id_shared_counter_advances(self):
        api = SPMAPI()
        first = api.upload_data(_json_payload(), format="json")
        second = api.upload_data(_json_payload(), format="json")
        assert first["dataset_id"] == "dataset_1"
        assert second["dataset_id"] == "dataset_2"


class TestFitContrastResults:
    """Tests for the fit -> contrast -> get_results pipeline."""

    def _fitted_api(self):
        api = SPMAPI()
        upload = api.upload_data(_json_payload(), format="json")
        assert upload["status"] == "success"
        fit = api.fit_model(upload["dataset_id"], {"covariates": ["elevation"]})
        assert fit["status"] == "success", fit
        return api, upload["dataset_id"], fit

    def test_fit_model_success(self):
        api, _, fit = self._fitted_api()
        assert fit["n_regressors"] == 2  # intercept + elevation
        assert 0.0 <= fit["r_squared"] <= 1.0
        assert api.list_results()["count"] == 1

    def test_fit_unknown_dataset_error(self):
        api = SPMAPI()
        response = api.fit_model("dataset_999", {"intercept": True})
        assert response["status"] == "error"
        assert "dataset_999" in response["message"]

    def test_contrast_unknown_result_error(self):
        api = SPMAPI()
        response = api.run_contrast("result_999", {"vector": [0, 1]})
        assert response["status"] == "error"
        assert "result_999" in response["message"]

    def test_contrast_missing_spec_error(self):
        api, _, _ = self._fitted_api()
        response = api.run_contrast("result_1", {"neither": True})
        assert response["status"] == "error"

    def test_contrast_pipeline_success(self):
        api, _, fit = self._fitted_api()
        response = api.run_contrast(fit["result_id"], {"vector": [0, 1]})

        assert response["status"] == "success"
        assert response["result_id"] == fit["result_id"]
        assert "n_significant" in response
        assert "threshold" in response

    def test_get_results_summary_and_full(self):
        api, _, fit = self._fitted_api()
        api.run_contrast(fit["result_id"], {"vector": [0, 1]})

        summary = api.get_results(fit["result_id"], format="summary")
        assert summary["status"] == "success"
        assert summary["n_points"] == 10
        assert summary["n_regressors"] == 2
        assert summary["n_contrasts"] == 1

        full = api.get_results(fit["result_id"], format="full")
        assert full["status"] == "success"
        assert "beta_coefficients" in full["result"]
        assert "residuals" in full["result"]
        assert "model_diagnostics" in full["result"]

    def test_get_results_visualization_is_raw_payload(self):
        api, _, fit = self._fitted_api()
        response = api.get_results(fit["result_id"], format="visualization")

        assert response["status"] == "success"
        payload = response["visualization_data"]
        assert "coordinates" in payload
        assert "beta_map" in payload
        assert "residuals" in payload
        assert len(payload["coordinates"]) == 10

    def test_get_results_unknown_result_error(self):
        api = SPMAPI()
        response = api.get_results("result_999", format="summary")
        assert response["status"] == "error"
        assert "result_999" in response["message"]

    def test_get_results_unknown_format_error(self):
        api, _, fit = self._fitted_api()
        response = api.get_results(fit["result_id"], format="pickle")
        assert response["status"] == "error"
        assert "pickle" in response["message"]
