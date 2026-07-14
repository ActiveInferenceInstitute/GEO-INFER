"""Tests for integration_models: enums, ModuleSpec, ModuleConnection, WorkflowStep."""

from geo_infer_examples.models.integration_models import (
    ModuleType,
    DataFormat,
    IntegrationPattern,
    ModuleSpec,
    ModuleConnection,
    WorkflowStep,
)
from geo_infer_examples.core.module_orchestrator import ModuleOrchestrator


class TestEnums:
    """Verify all enum members are present and have string values."""

    def test_module_type_values(self):
        assert ModuleType.CORE_INFRASTRUCTURE.value == "core_infrastructure"
        assert ModuleType.DATA_PROCESSING.value == "data_processing"
        assert ModuleType.SPATIAL_TEMPORAL.value == "spatial_temporal"
        assert ModuleType.ANALYTICS_AI.value == "analytics_ai"
        assert ModuleType.DOMAIN_SPECIFIC.value == "domain_specific"
        assert ModuleType.USER_INTERFACE.value == "user_interface"
        assert ModuleType.OPERATIONS.value == "operations"

    def test_module_type_count(self):
        assert len(ModuleType) == 7

    def test_data_format_values(self):
        assert DataFormat.GEOJSON.value == "geojson"
        assert DataFormat.TIME_SERIES.value == "time_series"
        assert DataFormat.RISK_ASSESSMENT.value == "risk_assessment"

    def test_data_format_count(self):
        assert len(DataFormat) == 9

    def test_integration_pattern_values(self):
        assert IntegrationPattern.SEQUENTIAL.value == "sequential"
        assert IntegrationPattern.PARALLEL.value == "parallel"
        assert IntegrationPattern.FEEDBACK_LOOP.value == "feedback_loop"

    def test_integration_pattern_count(self):
        assert len(IntegrationPattern) == 9


class TestModuleSpec:
    """Tests for ModuleSpec dataclass."""

    def test_create_minimal(self):
        spec = ModuleSpec(
            name="TEST",
            module_type=ModuleType.CORE_INFRASTRUCTURE,
            api_base_url="http://localhost:9000",
            version="1.0.0",
        )
        assert spec.name == "TEST"
        assert spec.capabilities == []
        assert spec.health_endpoint == "/health"
        assert spec.documentation_url is None

    def test_create_full(self):
        spec = ModuleSpec(
            name="DATA",
            module_type=ModuleType.DATA_PROCESSING,
            api_base_url="http://localhost:8001",
            version="2.1.0",
            capabilities=["ingest", "fusion"],
            supported_formats=[DataFormat.GEOJSON, DataFormat.TIME_SERIES],
            dependencies=["OPS"],
            optional_dependencies=["SEC"],
            configuration={"batch_size": 100},
            health_endpoint="/status",
            documentation_url="http://docs.example.com",
        )
        assert len(spec.capabilities) == 2
        assert len(spec.supported_formats) == 2
        assert spec.configuration["batch_size"] == 100

    def test_to_dict(self):
        spec = ModuleSpec(
            name="SPACE",
            module_type=ModuleType.SPATIAL_TEMPORAL,
            api_base_url="http://localhost:8002",
            version="1.0.0",
            supported_formats=[DataFormat.GEOJSON],
        )
        d = spec.to_dict()
        assert d["name"] == "SPACE"
        assert d["module_type"] == "spatial_temporal"
        assert d["supported_formats"] == ["geojson"]
        assert d["health_endpoint"] == "/health"

    def test_from_dict_roundtrip(self):
        spec = ModuleSpec(
            name="AI",
            module_type=ModuleType.ANALYTICS_AI,
            api_base_url="http://localhost:8003",
            version="3.0.0",
            capabilities=["predict"],
            supported_formats=[DataFormat.PREDICTION_RESULT],
            dependencies=["MATH", "DATA"],
        )
        d = spec.to_dict()
        restored = ModuleSpec.from_dict(d)
        assert restored.name == spec.name
        assert restored.module_type == spec.module_type
        assert restored.dependencies == spec.dependencies
        assert restored.supported_formats == spec.supported_formats


class TestModuleConnection:
    """Tests for ModuleConnection dataclass."""

    def test_create(self):
        conn = ModuleConnection(
            source_module="DATA",
            target_module="SPACE",
            pattern=IntegrationPattern.PIPELINE,
            data_format=DataFormat.GEOJSON,
            endpoint="/process",
        )
        assert conn.source_module == "DATA"
        assert conn.transformation is None
        assert conn.timeout is None

    def test_to_dict(self):
        conn = ModuleConnection(
            source_module="SPACE",
            target_module="AI",
            pattern=IntegrationPattern.REQUEST_RESPONSE,
            data_format=DataFormat.SPATIAL_TEMPORAL_JSON,
            endpoint="/analyze",
            timeout=30,
        )
        d = conn.to_dict()
        assert d["pattern"] == "request_response"
        assert d["data_format"] == "spatial_temporal_json"
        assert d["timeout"] == 30


class TestWorkflowStep:
    """Tests for WorkflowStep dataclass."""

    def test_create_minimal(self):
        step = WorkflowStep(
            name="ingest",
            module="DATA",
            endpoint="/ingest",
        )
        assert step.dependencies == []
        assert step.retry_count == 0
        assert step.optional is False
        assert step.trigger_events == []
        assert step.emits_events == []

    def test_create_full(self):
        step = WorkflowStep(
            name="analyze",
            module="AI",
            endpoint="/predict",
            dependencies=["ingest"],
            input_mapping={"features": "processed_data"},
            output_mapping={"predictions": "result"},
            condition="data.count > 0",
            timeout=60,
            retry_count=3,
            optional=True,
            trigger_events=["data_ready"],
            emits_events=["prediction_done"],
            feedback_mapping={"prior": "posterior"},
        )
        assert step.retry_count == 3
        assert step.optional is True
        assert step.feedback_mapping == {"prior": "posterior"}

    def test_to_dict(self):
        step = WorkflowStep(
            name="geocode",
            module="SPACE",
            endpoint="/geocode",
            dependencies=["ingest"],
        )
        d = step.to_dict()
        assert d["name"] == "geocode"
        assert d["module"] == "SPACE"
        assert d["dependencies"] == ["ingest"]
        assert d["optional"] is False

    def test_from_dict_roundtrip(self):
        step = WorkflowStep(
            name="cluster",
            module="SPACE",
            endpoint="/cluster",
            dependencies=["geocode"],
            timeout=120,
        )
        d = step.to_dict()
        restored = WorkflowStep.from_dict(d)
        assert restored.name == step.name
        assert restored.timeout == 120
        assert restored.dependencies == ["geocode"]


class TestWorkflowConditions:
    """Verify workflow guards accept data expressions without executing code."""

    def test_data_expression_is_evaluated(self):
        orchestrator = ModuleOrchestrator()
        assert orchestrator._evaluate_condition("data.count > 0", {"count": 2})

    def test_function_calls_are_rejected(self):
        orchestrator = ModuleOrchestrator()
        condition = "data.get('count', 0) > 0"
        assert orchestrator._evaluate_condition(condition, {"count": 2}) is False
