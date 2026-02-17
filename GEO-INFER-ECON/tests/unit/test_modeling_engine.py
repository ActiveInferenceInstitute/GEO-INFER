"""Tests for the economic modeling engine."""

import pytest
from geo_infer_econ.core.modeling_engine import (
    EconomicModelingEngine,
    ModelConfiguration,
)


class DummyModel:
    """A minimal model for testing the engine."""

    def __init__(self, config: ModelConfiguration):
        self.config = config

    def run(self, data: dict) -> dict:
        return {"result": data.get("input", 0) * 2}

    def validate_inputs(self, data: dict) -> None:
        if "input" not in data:
            raise ValueError("Missing 'input'")


class DummyExecuteModel:
    """Model that uses execute instead of run."""

    def __init__(self, config: ModelConfiguration):
        self.config = config

    def execute(self, data: dict) -> dict:
        return {"status": "ok"}


class TestEconomicModelingEngine:
    """Tests for the economic modeling engine."""

    def setup_method(self) -> None:
        self.engine = EconomicModelingEngine()

    def test_register_model(self) -> None:
        self.engine.register_model("dummy", DummyModel)
        assert "dummy" in self.engine.model_registry

    def test_create_model(self) -> None:
        self.engine.register_model("dummy", DummyModel)
        config = ModelConfiguration(model_type="test", parameters={"x": 1})
        instance = self.engine.create_model("dummy", config)
        assert isinstance(instance, DummyModel)
        assert len(self.engine.active_models) == 1

    def test_create_unregistered_model_raises(self) -> None:
        config = ModelConfiguration(model_type="test", parameters={})
        with pytest.raises(ValueError, match="not registered"):
            self.engine.create_model("missing", config)

    def test_execute_model_with_run(self) -> None:
        self.engine.register_model("dummy", DummyModel)
        config = ModelConfiguration(model_type="test", parameters={})
        instance = self.engine.create_model("dummy", config)
        result = self.engine.execute_model(instance, {"input": 5})
        assert result["result"] == 10

    def test_execute_model_with_execute_method(self) -> None:
        self.engine.register_model("exec_model", DummyExecuteModel)
        config = ModelConfiguration(model_type="test", parameters={})
        instance = self.engine.create_model("exec_model", config)
        result = self.engine.execute_model(instance, {})
        assert result["status"] == "ok"

    def test_execute_model_validates_inputs(self) -> None:
        self.engine.register_model("dummy", DummyModel)
        config = ModelConfiguration(model_type="test", parameters={})
        instance = self.engine.create_model("dummy", config)
        with pytest.raises(ValueError, match="Missing 'input'"):
            self.engine.execute_model(instance, {})

    def test_batch_execute(self) -> None:
        self.engine.register_model("dummy", DummyModel)
        config = ModelConfiguration(model_type="test", parameters={})
        m1 = self.engine.create_model("dummy", config)
        m2 = self.engine.create_model("dummy", config)
        results = self.engine.batch_execute(
            [(m1, {"input": 3}), (m2, {"input": 7})],
            common_data={},
        )
        assert "model_0" in results
        assert "model_1" in results

    def test_list_models(self) -> None:
        self.engine.register_model("a", DummyModel)
        self.engine.register_model("b", DummyExecuteModel)
        models = self.engine.list_models()
        assert "a" in models
        assert "b" in models

    def test_get_model_info(self) -> None:
        self.engine.register_model("dummy", DummyModel)
        info = self.engine.get_model_info("dummy")
        assert info["name"] == "dummy"
        assert info["class"] == "DummyModel"

    def test_get_model_info_unregistered_raises(self) -> None:
        with pytest.raises(ValueError, match="not registered"):
            self.engine.get_model_info("nonexistent")

    def test_cleanup(self) -> None:
        self.engine.register_model("dummy", DummyModel)
        config = ModelConfiguration(model_type="test", parameters={})
        self.engine.create_model("dummy", config)
        self.engine.cleanup()
        assert len(self.engine.active_models) == 0
