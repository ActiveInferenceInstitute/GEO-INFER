"""
Deployment management for GEO-INFER-OPS.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, List

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from geo_infer_ops.core.config import get_config
from geo_infer_ops.core.logging import get_logger

logger = get_logger(__name__)

class DeploymentManager:
    """Manages deployment operations for GEO-INFER-OPS."""
    
    def __init__(self, namespace: Optional[str] = None):
        """
        Initialize deployment manager.
        
        Args:
            namespace: Kubernetes namespace (default: from config)
        """
        self.config = get_config()
        self.namespace = namespace or self.config.deployment.kubernetes.namespace
        self._load_k8s_config()
    
    def _load_k8s_config(self) -> None:
        """Load Kubernetes configuration."""
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()
    
    def build_docker_image(self, tag: Optional[str] = None) -> bool:
        """
        Build Docker image for GEO-INFER-OPS.
        
        Args:
            tag: Image tag (default: from config)
            
        Returns:
            bool: True if build successful
        """
        try:
            image_tag = tag or self.config.deployment.docker.tag
            cmd = ["docker", "build", "-t", image_tag, "."]
            subprocess.run(cmd, check=True)
            logger.info("docker_image_built", tag=image_tag)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("docker_build_failed", error=str(e))
            return False
    
    def push_docker_image(self, registry: Optional[str] = None) -> bool:
        """
        Push Docker image to registry.
        
        Args:
            registry: Registry URL (default: from config)
            
        Returns:
            bool: True if push successful
        """
        try:
            registry = registry or self.config.deployment.docker.registry
            tag = self.config.deployment.docker.tag
            image = f"{registry}/{tag}"
            cmd = ["docker", "push", image]
            subprocess.run(cmd, check=True)
            logger.info("docker_image_pushed", image=image)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("docker_push_failed", error=str(e))
            return False
    
    def deploy_kubernetes(self, manifest_path: Optional[str] = None) -> bool:
        """
        Deploy to Kubernetes using manifests.
        
        Args:
            manifest_path: Path to manifest files (default: deployment/kubernetes)
            
        Returns:
            bool: True if deployment successful
        """
        try:
            if manifest_path is None:
                manifest_path = str(Path(__file__).parent.parent.parent.parent / "deployment" / "kubernetes")
            
            # Load and apply manifests
            for manifest_file in Path(manifest_path).glob("*.yml"):
                with open(manifest_file) as f:
                    manifest = yaml.safe_load(f)
                
                # Apply manifest
                if manifest["kind"] == "Deployment":
                    self._apply_deployment(manifest)
                elif manifest["kind"] == "Service":
                    self._apply_service(manifest)
                elif manifest["kind"] == "ConfigMap":
                    self._apply_configmap(manifest)
                elif manifest["kind"] == "Secret":
                    self._apply_secret(manifest)
            
            logger.info("kubernetes_deployment_completed")
            return True
        except Exception as e:
            logger.error("kubernetes_deployment_failed", error=str(e))
            return False
    
    def _apply_deployment(self, manifest: Dict) -> None:
        """Apply Kubernetes Deployment manifest."""
        apps_v1 = client.AppsV1Api()
        try:
            apps_v1.create_namespaced_deployment(
                namespace=self.namespace,
                body=manifest
            )
            logger.info("deployment_applied", name=manifest["metadata"]["name"])
        except ApiException as e:
            if e.status == 409:  # Already exists
                apps_v1.replace_namespaced_deployment(
                    name=manifest["metadata"]["name"],
                    namespace=self.namespace,
                    body=manifest
                )
                logger.info("deployment_updated", name=manifest["metadata"]["name"])
            else:
                raise
    
    def _apply_service(self, manifest: Dict) -> None:
        """Apply Kubernetes Service manifest."""
        core_v1 = client.CoreV1Api()
        try:
            core_v1.create_namespaced_service(
                namespace=self.namespace,
                body=manifest
            )
            logger.info("service_applied", name=manifest["metadata"]["name"])
        except ApiException as e:
            if e.status == 409:  # Already exists
                core_v1.replace_namespaced_service(
                    name=manifest["metadata"]["name"],
                    namespace=self.namespace,
                    body=manifest
                )
                logger.info("service_updated", name=manifest["metadata"]["name"])
            else:
                raise
    
    def _apply_configmap(self, manifest: Dict) -> None:
        """Apply Kubernetes ConfigMap manifest."""
        core_v1 = client.CoreV1Api()
        try:
            core_v1.create_namespaced_config_map(
                namespace=self.namespace,
                body=manifest
            )
            logger.info("configmap_applied", name=manifest["metadata"]["name"])
        except ApiException as e:
            if e.status == 409:  # Already exists
                core_v1.replace_namespaced_config_map(
                    name=manifest["metadata"]["name"],
                    namespace=self.namespace,
                    body=manifest
                )
                logger.info("configmap_updated", name=manifest["metadata"]["name"])
            else:
                raise
    
    def _apply_secret(self, manifest: Dict) -> None:
        """Apply Kubernetes Secret manifest."""
        core_v1 = client.CoreV1Api()
        try:
            core_v1.create_namespaced_secret(
                namespace=self.namespace,
                body=manifest
            )
            logger.info("secret_applied", name=manifest["metadata"]["name"])
        except ApiException as e:
            if e.status == 409:  # Already exists
                core_v1.replace_namespaced_secret(
                    name=manifest["metadata"]["name"],
                    namespace=self.namespace,
                    body=manifest
                )
                logger.info("secret_updated", name=manifest["metadata"]["name"])
            else:
                raise
    
    def get_deployment_status(self, name: str) -> Dict:
        """
        Get status of a Kubernetes deployment.
        
        Args:
            name: Deployment name
            
        Returns:
            Dict containing deployment status
        """
        apps_v1 = client.AppsV1Api()
        try:
            deployment = apps_v1.read_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )
            return {
                "name": deployment.metadata.name,
                "replicas": deployment.spec.replicas,
                "available_replicas": deployment.status.available_replicas,
                "ready_replicas": deployment.status.ready_replicas,
                "updated_replicas": deployment.status.updated_replicas,
                "conditions": [
                    {
                        "type": condition.type,
                        "status": condition.status,
                        "message": condition.message
                    }
                    for condition in deployment.status.conditions
                ]
            }
        except ApiException as e:
            logger.error("deployment_status_failed", name=name, error=str(e))
            return {}
    
    def scale_deployment(self, name: str, replicas: int) -> bool:
        """
        Scale a Kubernetes deployment.
        
        Args:
            name: Deployment name
            replicas: Number of replicas
            
        Returns:
            bool: True if scaling successful
        """
        apps_v1 = client.AppsV1Api()
        try:
            apps_v1.patch_namespaced_deployment_scale(
                name=name,
                namespace=self.namespace,
                body={"spec": {"replicas": replicas}}
            )
            logger.info("deployment_scaled", name=name, replicas=replicas)
            return True
        except ApiException as e:
            logger.error("deployment_scale_failed", name=name, error=str(e))
            return False
    
    def get_pods(self, label_selector: Optional[str] = None) -> List[Dict]:
        """
        Get pods in the namespace.
        
        Args:
            label_selector: Label selector for filtering pods
            
        Returns:
            List of pod information
        """
        core_v1 = client.CoreV1Api()
        try:
            pods = core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=label_selector
            )
            return [
                {
                    "name": pod.metadata.name,
                    "status": pod.status.phase,
                    "ip": pod.status.pod_ip,
                    "node": pod.spec.node_name,
                    "containers": [
                        {
                            "name": container.name,
                            "image": container.image,
                            "ready": container.ready
                        }
                        for container in pod.status.container_statuses
                    ]
                }
                for pod in pods.items
            ]
        except ApiException as e:
            logger.error("pods_list_failed", error=str(e))
            return [] 