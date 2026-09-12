"""Regression tests: orchestrator workflow definitions must load via
``importlib.resources`` from the packaged ``geo_infer_examples/workflows``
directory (no parent-path climbing), with an explicit
``GEO_INFER_EXAMPLES_WORKFLOWS`` environment-variable override."""

import importlib.resources

from geo_infer_examples.core import ModuleOrchestrator


class TestPackagedWorkflows:
    """Packaged workflow YAMLs resolve without cwd or repo-root assumptions."""

    def test_default_resolution_works_from_empty_cwd(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GEO_INFER_EXAMPLES_WORKFLOWS", raising=False)
        monkeypatch.chdir(tmp_path)
        orchestrator = ModuleOrchestrator()
        assert "health_surveillance_basic" in orchestrator.list_workflows()
        workflow = orchestrator.get_workflow_definition("health_surveillance_basic")
        assert workflow is not None
        assert [step.name for step in workflow.steps] == [
            "data_ingestion",
            "spatial_analysis",
            "health_assessment",
        ]

    def test_default_resolution_targets_package_tree(self):
        files = ModuleOrchestrator()._workflow_definition_files()
        assert files, "packaged workflows directory must contain at least one YAML"
        package_dir = importlib.resources.files("geo_infer_examples")
        for workflow_file in files:
            assert str(workflow_file).startswith(str(package_dir))

    def test_env_override_is_honored(self, tmp_path, monkeypatch):
        override = tmp_path / "workflows"
        override.mkdir()
        (override / "custom_only.yaml").write_text(
            "id: custom_only\n"
            "name: Custom Only\n"
            "description: Loaded exclusively from the override directory\n"
            "steps:\n"
            "  - name: single_step\n"
            "    module: DATA\n"
            "    endpoint: /ingest\n"
            "    dependencies: []\n"
            "    optional: false\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("GEO_INFER_EXAMPLES_WORKFLOWS", str(override))
        orchestrator = ModuleOrchestrator()
        assert "custom_only" in orchestrator.list_workflows()
        # The override directory replaces the packaged directory, not merges it.
        assert [f.name for f in orchestrator._workflow_definition_files()] == [
            "custom_only.yaml"
        ]

    def test_bad_override_falls_back_to_packaged(self, tmp_path, monkeypatch):
        missing = tmp_path / "does_not_exist"
        monkeypatch.setenv("GEO_INFER_EXAMPLES_WORKFLOWS", str(missing))
        monkeypatch.chdir(tmp_path)
        orchestrator = ModuleOrchestrator()
        assert "health_surveillance_basic" in orchestrator.list_workflows()