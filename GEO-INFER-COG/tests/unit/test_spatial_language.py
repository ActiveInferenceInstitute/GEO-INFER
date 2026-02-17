"""
Unit tests for spatial language processing: SpatialEntity, SpatialLanguageProcessor.
"""

import pytest

from geo_infer_cog.spatial_language.processor import (
    SpatialEntity,
    SpatialLanguageProcessor,
)


class TestSpatialEntity:
    """Test SpatialEntity data class."""

    def test_to_geojson_with_coordinates(self) -> None:
        entity = SpatialEntity(
            text='Central Park',
            entity_type='landmark',
            confidence=0.9,
            coordinates=(40.7829, -73.9654),
        )
        geojson = entity.to_geojson()
        assert geojson['type'] == 'Feature'
        assert geojson['geometry']['type'] == 'Point'
        # GeoJSON is [lon, lat]
        assert geojson['geometry']['coordinates'] == [-73.9654, 40.7829]

    def test_to_geojson_no_coordinates(self) -> None:
        entity = SpatialEntity(text='Somewhere', entity_type='region')
        geojson = entity.to_geojson()
        assert geojson['geometry'] is None

    def test_default_confidence(self) -> None:
        entity = SpatialEntity(text='Place', entity_type='location')
        assert entity.confidence == 1.0


class TestSpatialLanguageProcessor:
    """Test SpatialLanguageProcessor class."""

    @pytest.fixture
    def processor(self) -> SpatialLanguageProcessor:
        return SpatialLanguageProcessor(language='en', domain='general')

    def test_init_defaults(self, processor: SpatialLanguageProcessor) -> None:
        assert processor.language == 'en'
        assert processor.domain == 'general'

    def test_extract_coordinate_entities(self, processor: SpatialLanguageProcessor) -> None:
        text = "The location is at 40.7128, -74.0060 near the harbor."
        entities = processor.extract_spatial_entities(text)
        coord_entities = [e for e in entities if e.entity_type == 'coordinate']
        assert len(coord_entities) >= 1
        assert coord_entities[0].coordinates is not None

    def test_extract_landmark_entities(self, processor: SpatialLanguageProcessor) -> None:
        text = "We visited Central Park and then headed to Grand Station."
        entities = processor.extract_spatial_entities(text)
        landmark_entities = [e for e in entities if e.entity_type == 'landmark']
        assert len(landmark_entities) >= 1

    def test_geocoding_known_city(self, processor: SpatialLanguageProcessor) -> None:
        coords = processor._attempt_geocoding('New York City', 'city')
        assert coords is not None
        assert abs(coords[0] - 40.7128) < 0.01

    def test_geocoding_unknown_returns_none(self, processor: SpatialLanguageProcessor) -> None:
        coords = processor._attempt_geocoding('Atlantis', 'city')
        assert coords is None

    def test_extract_direction_from_text(self, processor: SpatialLanguageProcessor) -> None:
        direction = processor._extract_direction_from_text('north of the river')
        assert direction == 'north'

    def test_extract_distance_from_text(self, processor: SpatialLanguageProcessor) -> None:
        distance = processor._extract_distance_from_text('the hotel is near the station')
        assert distance == 'near'

    def test_extract_spatial_concepts(self, processor: SpatialLanguageProcessor) -> None:
        concepts = processor._extract_spatial_concepts(
            'The urban area has a large park and a busy highway.'
        )
        concept_types = [c['concept_type'] for c in concepts]
        assert 'urban' in concept_types
        assert 'natural' in concept_types
        assert 'transportation' in concept_types

    def test_identify_uncertainty_indicators(self, processor: SpatialLanguageProcessor) -> None:
        indicators = processor._identify_uncertainty_indicators(
            'It is approximately near the lake, maybe close to the forest.'
        )
        assert 'approximately' in indicators
        assert 'maybe' in indicators

    def test_process_place_description_returns_keys(self, processor: SpatialLanguageProcessor) -> None:
        result = processor.process_place_description(
            'Central Park in New York City, near 40.7829, -73.9654'
        )
        assert 'entities' in result
        assert 'relations' in result
        assert 'spatial_concepts' in result
        assert 'interpretation_confidence' in result
        assert result['interpretation_confidence'] >= 0.0

    def test_deduplicate_keeps_highest_confidence(self, processor: SpatialLanguageProcessor) -> None:
        entities = [
            SpatialEntity(text='Park', entity_type='landmark', confidence=0.6),
            SpatialEntity(text='Park', entity_type='landmark', confidence=0.9),
        ]
        unique = processor._deduplicate_entities(entities)
        assert len(unique) == 1
        assert unique[0].confidence == 0.9
