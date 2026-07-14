"""Deterministic integration tests for the Kubernetes deployment boundary.

The production manager still uses the official Kubernetes client.  These tests
replace its client factories with an in-memory service so lifecycle behavior is
validated without requiring a cluster, kubeconfig, network, or cleanup hooks.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from geo_infer_ops.core.deployment import DeploymentManager
from geo_infer_ops.core import deployment as deployment_module


class FakeAppsApi:
    """Small in-memory implementation of the AppsV1 operations under test."""

    def __init__(self) -> None:
        self.deployments: dict[str, dict] = {}
        self.rollback_revisions: dict[str, int] = {}

    def create_namespaced_deployment(self, *, namespace: str, body: dict) -> None:
        del namespace
        self.deployments[body["metadata"]["name"]] = body

    def replace_namespaced_deployment(
        self, *, name: str, namespace: str, body: dict
    ) -> None:
        del namespace
        self.deployments[name] = body

    def read_namespaced_deployment(
        self, *, name: str, namespace: str
    ) -> SimpleNamespace:
        del namespace
        body = self.deployments[name]
        replicas = body["spec"]["replicas"]
        return SimpleNamespace(
            metadata=SimpleNamespace(name=name),
            spec=SimpleNamespace(replicas=replicas),
            status=SimpleNamespace(
                available_replicas=replicas,
                ready_replicas=replicas,
                updated_replicas=replicas,
                conditions=[],
            ),
        )

    def patch_namespaced_deployment_scale(
        self, *, name: str, namespace: str, body: dict
    ) -> None:
        del namespace
        self.deployments[name]["spec"]["replicas"] = body["spec"]["replicas"]

    def delete_namespaced_deployment(self, *, name: str, namespace: str) -> None:
        del namespace
        self.deployments.pop(name, None)

    def create_namespaced_deployment_rollback(
        self, *, name: str, namespace: str, body: dict
    ) -> None:
        del namespace
        self.rollback_revisions[name] = body["rollbackTo"]["revision"]

    def patch_namespaced_deployment(
        self, *, name: str, namespace: str, body: dict
    ) -> None:
        del namespace
        self.deployments[name].setdefault("metadata", {}).setdefault(
            "annotations", {}
        ).update(body.get("metadata", {}).get("annotations", {}))


class FakeCoreApi:
    """In-memory CoreV1 operations for quota and pod health checks."""

    def __init__(self, apps: FakeAppsApi) -> None:
        self.apps = apps
        self.quotas: dict[str, dict] = {}
        self.pods: dict[str, SimpleNamespace] = {}

    def create_namespaced_resource_quota(self, *, namespace: str, body: dict) -> None:
        self.quotas[body["metadata"]["name"]] = body
        del namespace

    def list_namespaced_pod(self, *, namespace: str, label_selector: str | None = None):
        del namespace, label_selector
        for deployment in self.apps.deployments.values():
            name = deployment["metadata"]["name"] + "-pod"
            self.pods[name] = self._healthy_pod(name)
        return SimpleNamespace(items=list(self.pods.values()))

    def read_namespaced_pod(self, *, name: str, namespace: str) -> SimpleNamespace:
        del namespace
        self.pods.setdefault(name, self._healthy_pod(name))
        return self.pods[name]

    def delete_namespaced_pod(self, *, name: str, namespace: str) -> None:
        del namespace
        self.pods.pop(name, None)

    def create_namespaced_pod(self, *, namespace: str, body: dict) -> None:
        del namespace
        name = body["metadata"]["name"]
        self.pods[name] = self._healthy_pod(name)

    def create_namespaced_binding(self, *, namespace: str, body: dict) -> None:
        del namespace, body

    @staticmethod
    def _healthy_pod(name: str) -> SimpleNamespace:
        return SimpleNamespace(
            metadata=SimpleNamespace(name=name),
            status=SimpleNamespace(
                phase="Running",
                pod_ip="127.0.0.1",
                node_name="local-test-node",
                conditions=[
                    SimpleNamespace(type="Ready", status="True"),
                    SimpleNamespace(type="Initialized", status="True"),
                ],
                container_statuses=[
                    SimpleNamespace(
                        name="test-container", image="local:test", ready=True
                    )
                ],
            ),
            spec=SimpleNamespace(node_name="local-test-node"),
        )


class FakeNetworkingApi:
    """In-memory NetworkPolicy operations."""

    def __init__(self) -> None:
        self.policies: dict[str, dict] = {}

    def create_namespaced_network_policy(self, *, namespace: str, body: dict) -> None:
        del namespace
        self.policies[body["metadata"]["name"]] = body

    def delete_namespaced_network_policy(self, *, name: str, namespace: str) -> None:
        del namespace
        self.policies.pop(name, None)


@pytest.fixture
def test_namespace() -> str:
    """Provide a deterministic namespace name without contacting Kubernetes."""
    return "geo-infer-test"


@pytest.fixture
def deployment_manager(monkeypatch: pytest.MonkeyPatch, test_namespace: str):
    """Create a manager backed by local fake Kubernetes services."""
    apps = FakeAppsApi()
    core = FakeCoreApi(apps)
    networking = FakeNetworkingApi()
    monkeypatch.setattr(deployment_module.config, "load_incluster_config", lambda: None)
    monkeypatch.setattr(deployment_module.client, "AppsV1Api", lambda: apps)
    monkeypatch.setattr(deployment_module.client, "CoreV1Api", lambda: core)
    monkeypatch.setattr(deployment_module.client, "NetworkingV1Api", lambda: networking)
    return DeploymentManager(namespace=test_namespace)


def deployment_manifest(
    name: str, image: str = "local:test", replicas: int = 1
) -> dict:
    """Build a minimal deployment manifest used by lifecycle tests."""
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": name},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name}},
                "spec": {"containers": [{"name": "test-container", "image": image}]},
            },
        },
    }


def test_deployment_lifecycle(deployment_manager, test_namespace):
    """Create, inspect, scale, health-check, and delete a local deployment."""
    del test_namespace
    assert (
        deployment_manager.deploy_kubernetes(deployment_manifest("test-deployment"))
        is True
    )
    status = deployment_manager.get_deployment_status("test-deployment")
    assert status["name"] == "test-deployment"
    assert status["replicas"] == 1

    pods = deployment_manager.get_pods()
    assert len(pods) == 1
    assert deployment_manager.check_pod_health(pods[0]["name"])["healthy"] is True
    assert deployment_manager.scale_deployment("test-deployment", 2) is True
    assert deployment_manager.get_deployment_status("test-deployment")["replicas"] == 2
    assert deployment_manager.delete_deployment("test-deployment") is True


def test_resource_quota_management(deployment_manager, test_namespace):
    """Apply a local resource quota and validate a resource-bearing deployment."""
    quota = {
        "apiVersion": "v1",
        "kind": "ResourceQuota",
        "metadata": {"name": "test-quota", "namespace": test_namespace},
        "spec": {"hard": {"cpu": "2", "memory": "4Gi", "pods": "4"}},
    }
    assert deployment_manager.apply_resource_quota(quota) is True
    manifest = deployment_manifest("resource-test")
    manifest["spec"]["template"]["spec"]["containers"][0]["resources"] = {
        "requests": {"cpu": "100m", "memory": "128Mi"},
        "limits": {"cpu": "200m", "memory": "256Mi"},
    }
    assert deployment_manager.validate_resource_quota(manifest) is True
    assert deployment_manager.deploy_kubernetes(manifest) is True
    assert deployment_manager.delete_deployment("resource-test") is True


def test_network_policy_management(deployment_manager, test_namespace):
    """Apply and delete a local NetworkPolicy through the manager."""
    policy = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {"name": "test-policy", "namespace": test_namespace},
        "spec": {
            "podSelector": {"matchLabels": {"app": "test"}},
            "policyTypes": ["Ingress"],
        },
    }
    assert deployment_manager.validate_network_policy(policy) is True
    assert deployment_manager.apply_network_policy(policy) is True
    assert deployment_manager.delete_network_policy("test-policy") is True


def test_deployment_rollback_scenario(deployment_manager, test_namespace):
    """Update a local deployment and record a deterministic rollback revision."""
    del test_namespace
    manifest = deployment_manifest("rollback-test", image="local:v1")
    assert deployment_manager.deploy_kubernetes(manifest) is True
    manifest["spec"]["template"]["spec"]["containers"][0]["image"] = "local:v2"
    assert deployment_manager.deploy_kubernetes(manifest) is True
    assert deployment_manager.rollback_deployment("rollback-test", "1") is True
    assert (
        deployment_manager.get_deployment_status("rollback-test")["name"]
        == "rollback-test"
    )
    assert deployment_manager.delete_deployment("rollback-test") is True
