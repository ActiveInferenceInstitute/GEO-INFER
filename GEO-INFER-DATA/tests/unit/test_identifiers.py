"""Tests for SQL/GraphQL identifier validation and query builders."""

from datetime import datetime

import pytest

from geo_infer_data.connectors.api import GraphQLConnector
from geo_infer_data.connectors.database import DatabaseConnector
from geo_infer_data.utils.identifiers import validate_sql_identifier


class TestValidateSqlIdentifier:
    @pytest.mark.parametrize(
        "name",
        [
            "stations",
            "_private_table",
            "a",
            "Table_1",
            "x" * 63,
            "camelCase_2",
        ],
    )
    def test_valid_identifiers_pass(self, name):
        assert validate_sql_identifier(name) == name

    @pytest.mark.parametrize(
        "name",
        [
            # Path traversal
            "../etc/passwd",
            "table--drop",
            "..",
            # Quotes
            "table\"x",
            "tab'le",
            '`tick`',
            # Semicolon / statement injection
            "tbl; DROP TABLE users",
            "tbl;",
            # Whitespace and comments
            "two words",
            "tbl--comment",
            "tbl/*x*/",
            # Bad start characters
            "1table",
            "",
            "$var",
            # Oversized
            "x" * 64,
        ],
    )
    def test_invalid_identifiers_rejected(self, name):
        with pytest.raises(ValueError):
            validate_sql_identifier(name)

    def test_non_string_rejected(self):
        with pytest.raises(ValueError):
            validate_sql_identifier(42)  # type: ignore[arg-type]


class TestBuildSelectQuery:
    def test_query_contains_only_validated_identifiers(self):
        query, params = DatabaseConnector._build_select_query(
            table_name="weather_stations",
            columns=["station_id", "temperature"],
            spatial_filter={"bbox": ["-122.5", 37.7, -122.3, "37.9"]},
            temporal_filter={"column": "timestamp", "start": "2026-01-01"},
            limit="25",
            enable_geospatial=True,
        )
        assert "SELECT \"station_id\", \"temperature\" FROM weather_stations" in query
        assert "ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)" in query
        assert "timestamp >= :start_time" in query
        assert "LIMIT 25" in query
        # All values are bound parameters, never interpolated
        assert params["min_lon"] == -122.5
        assert params["max_lat"] == 37.9
        assert params["start_time"] == "2026-01-01"
        # No user string appears unvalidated: the only literals in the
        # statement come from validated identifiers and fixed SQL fragments.
        for user_string in ["-122.5", "2026-01-01", "25"]:
            assert user_string not in query.replace("LIMIT 25", "")

    def test_star_and_no_filters(self):
        query, params = DatabaseConnector._build_select_query(
            table_name="t",
            columns=None,
            spatial_filter=None,
            temporal_filter=None,
            limit=None,
            enable_geospatial=True,
        )
        assert query == "SELECT * FROM t"
        assert params == {}

    def test_injection_in_table_name_raises(self):
        with pytest.raises(ValueError):
            DatabaseConnector._build_select_query(
                table_name="t; DROP TABLE t2",
                columns=None,
                spatial_filter=None,
                temporal_filter=None,
                limit=None,
                enable_geospatial=True,
            )

    def test_injection_in_column_raises(self):
        with pytest.raises(ValueError):
            DatabaseConnector._build_select_query(
                table_name="t",
                columns=["a", "b' OR '1'='1"],
                spatial_filter=None,
                temporal_filter=None,
                limit=None,
                enable_geospatial=True,
            )

    def test_injection_in_time_column_raises(self):
        with pytest.raises(ValueError):
            DatabaseConnector._build_select_query(
                table_name="t",
                columns=None,
                spatial_filter=None,
                temporal_filter={"column": "ts; DROP TABLE t2", "start": "2026-01-01"},
                limit=None,
                enable_geospatial=True,
            )

    def test_non_numeric_limit_raises(self):
        with pytest.raises(ValueError):
            DatabaseConnector._build_select_query(
                table_name="t",
                columns=None,
                spatial_filter=None,
                temporal_filter=None,
                limit="10; DROP TABLE t",
                enable_geospatial=True,
            )

    def test_non_numeric_bbox_raises(self):
        with pytest.raises(ValueError):
            DatabaseConnector._build_select_query(
                table_name="t",
                columns=None,
                spatial_filter={"bbox": ["a", 1, 2, 3]},
                temporal_filter=None,
                limit=None,
                enable_geospatial=True,
            )


class TestBuildFeaturesQuery:
    def test_valid_query(self):
        query = GraphQLConnector._build_features_query(
            feature_type="countries",
            spatial_filter={"bbox": ["-10.5", "40.25", 10, 50]},
            temporal_filter={
                "start_date": "2026-01-01T00:00:00",
                "end_date": datetime(2026, 2, 1),
            },
            fields=["name", "geometry"],
            limit="100",
        )
        assert "countries" in query
        assert "minLon: -10.5" in query
        assert "minLat: 40.25" in query
        assert 'createdAfter: "2026-01-01T00:00:00"' in query
        assert "createdBefore: \"" in query
        assert "first: 100" in query
        assert "name, geometry" in query

    def test_invalid_feature_type_raises(self):
        with pytest.raises(ValueError):
            GraphQLConnector._build_features_query(
                feature_type="countries } x", fields=None, limit=None
            )

    def test_invalid_field_raises(self):
        with pytest.raises(ValueError):
            GraphQLConnector._build_features_query(
                feature_type="countries", fields=["a; b"], limit=None
            )

    def test_non_numeric_bbox_raises(self):
        with pytest.raises(ValueError):
            GraphQLConnector._build_features_query(
                feature_type="countries",
                spatial_filter={"bbox": ["north", 0, 1, 2]},
                fields=None,
                limit=None,
            )

    def test_unparseable_date_raises(self):
        with pytest.raises(ValueError):
            GraphQLConnector._build_features_query(
                feature_type="countries",
                temporal_filter={"start_date": "not-a-date"},
                fields=None,
                limit=None,
            )

    def test_non_integer_limit_raises(self):
        with pytest.raises(ValueError):
            GraphQLConnector._build_features_query(
                feature_type="countries", fields=None, limit="ten"
            )

    def test_quoted_value_cannot_escape_string(self):
        query = GraphQLConnector._build_features_query(
            feature_type="countries",
            temporal_filter={"start_date": "2026-01-01T00:00:00"},
            fields=None,
            limit=None,
        )
        assert '"\\"' not in query
        assert query.count('"') == 2
