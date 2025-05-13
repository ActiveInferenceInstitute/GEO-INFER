"""
Integration tests for deployment management.
"""
import os
import pytest
from pathlib import Path
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from geo_infer_ops.core.deployment import DeploymentManager
from geo_infer_ops.core.config import Config, DeploymentConfig

@pytest.fixture(scope="module")
def k8s_config():
    """Load Kubernetes configuration."""
    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()

@pytest.fixture(scope="module")
def k8s_client(k8s_config):
    """Create Kubernetes API clients."""
    return {
        "apps": client.AppsV1Api(),
        "core": client.CoreV1Api(),
        "networking": client.NetworkingV1Api()
    }

@pytest.fixture(scope="module")
def test_namespace():
    """Create and manage a test namespace."""
    namespace = "geo-infer-test"
    k8s_client = client.CoreV1Api()
    
    # Create namespace
    try:
        k8s_client.create_namespace(
            client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
        )
    except ApiException as e:
        if e.status != 409:  # Ignore if namespace already exists
            raise
    
    yield namespace
    
    # Cleanup namespace
    try:
        k8s_client.delete_namespace(name=namespace)
    except ApiException as e:
        if e.status != 404:  # Ignore if namespace doesn't exist
            raise

@pytest.fixture(scope="module")
def deployment_manager(test_namespace):
    """Create a deployment manager instance."""
    config = Config(
        deployment=DeploymentConfig(
            kubernetes=DeploymentConfig.KubernetesConfig(
                namespace=test_namespace
            )
        )
    )
    return DeploymentManager(config)

def test_deployment_lifecycle(deployment_manager, test_namespace):
    """Test complete deployment lifecycle."""
    # Test deployment creation
    deployment_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "test-deployment",
            "namespace": test_namespace
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": "test"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "test"
                    }
                },
                "spec": {
                    "containers": [{
                        "name": "test-container",
                        "image": "nginx:latest",
                        "ports": [{
                            "containerPort": 80
                        }]
                    }]
                }
            }
        }
    }
    
    result = deployment_manager.deploy_kubernetes(deployment_manifest)
    assert result is True
    
    # Test deployment status
    status = deployment_manager.get_deployment_status("test-deployment")
    assert status["name"] == "test-deployment"
    assert status["replicas"] == 1
    
    # Test pod health
    pods = deployment_manager.get_pods()
    assert len(pods) > 0
    pod_name = pods[0]["name"]
    health = deployment_manager.check_pod_health(pod_name)
    assert health["healthy"] is True
    
    # Test deployment scaling
    result = deployment_manager.scale_deployment("test-deployment", 2)
    assert result is True
    status = deployment_manager.get_deployment_status("test-deployment")
    assert status["replicas"] == 2
    
    # Test deployment deletion
    result = deployment_manager.delete_deployment("test-deployment")
    assert result is True

def test_resource_quota_management(deployment_manager, test_namespace):
    """Test resource quota management."""
    # Create resource quota
    quota_manifest = {
        "apiVersion": "v1",
        "kind": "ResourceQuota",
        "metadata": {
            "name": "test-quota",
            "namespace": test_namespace
        },
        "spec": {
            "hard": {
                "cpu": "2",
                "memory": "4Gi",
                "pods": "4"
            }
        }
    }
    
    result = deployment_manager.apply_resource_quota(quota_manifest)
    assert result is True
    
    # Test deployment with resource limits
    deployment_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "resource-test",
            "namespace": test_namespace
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": "resource-test"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "resource-test"
                    }
                },
                "spec": {
                    "containers": [{
                        "name": "test-container",
                        "image": "nginx:latest",
                        "resources": {
                            "requests": {
                                "cpu": "100m",
                                "memory": "128Mi"
                            },
                            "limits": {
                                "cpu": "200m",
                                "memory": "256Mi"
                            }
                        }
                    }]
                }
            }
        }
    }
    
    result = deployment_manager.deploy_kubernetes(deployment_manifest)
    assert result is True
    
    # Cleanup
    deployment_manager.delete_deployment("resource-test")

def test_network_policy_management(deployment_manager, test_namespace):
    """Test network policy management."""
    # Create network policy
    policy_manifest = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {
            "name": "test-policy",
            "namespace": test_namespace
        },
        "spec": {
            "podSelector": {
                "matchLabels": {
                    "app": "test"
                }
            },
            "policyTypes": ["Ingress"],
            "ingress": [{
                "from": [{
                    "podSelector": {
                        "matchLabels": {
                            "app": "test"
                        }
                    }
                }],
                "ports": [{
                    "protocol": "TCP",
                    "port": 80
                }]
            }]
        }
    }
    
    result = deployment_manager.apply_network_policy(policy_manifest)
    assert result is True
    
    # Cleanup
    deployment_manager.delete_network_policy("test-policy")

def test_deployment_rollback_scenario(deployment_manager, test_namespace):
    """Test deployment rollback scenario."""
    # Create initial deployment
    deployment_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "rollback-test",
            "namespace": test_namespace
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": "rollback-test"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "rollback-test"
                    }
                },
                "spec": {
                    "containers": [{
                        "name": "test-container",
                        "image": "nginx:1.19",
                        "ports": [{
                            "containerPort": 80
                        }]
                    }]
                }
            }
        }
    }
    
    result = deployment_manager.deploy_kubernetes(deployment_manifest)
    assert result is True
    
    # Update deployment with new image
    deployment_manifest["spec"]["template"]["spec"]["containers"][0]["image"] = "nginx:1.20"
    result = deployment_manager.deploy_kubernetes(deployment_manifest)
    assert result is True
    
    # Test rollback
    result = deployment_manager.rollback_deployment("rollback-test", "1")
    assert result is True
    
    # Verify rollback
    status = deployment_manager.get_deployment_status("rollback-test")
    assert status["name"] == "rollback-test"
    
    # Cleanup
    deployment_manager.delete_deployment("rollback-test") 