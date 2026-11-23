"""Test suite for the Kubernetes Manifest Generator Engine."""

from prodforge.engines.k8s_generator import generate_k8s_manifests


def test_k8s_manifests_generation():
    manifests = generate_k8s_manifests(
        app_name="checkout-service",
        namespace="prod",
        image="ghcr.io/org/checkout-service:v1.2.0",
        port=8080,
        replicas=3,
        enable_hpa=True,
        enable_network_policy=True,
        enable_ingress=True,
        ingress_host="checkout.company.com"
    )

    assert manifests is not None
    assert manifests.app_name == "checkout-service"
    assert manifests.namespace == "prod"

    # Verify Deployment security standards
    assert "runAsNonRoot: true" in manifests.deployment_yaml
    assert "allowPrivilegeEscalation: false" in manifests.deployment_yaml
    assert "readOnlyRootFilesystem: true" in manifests.deployment_yaml
    assert "livenessProbe" in manifests.deployment_yaml
    assert "readinessProbe" in manifests.deployment_yaml

    # Verify Service
    assert manifests.service_yaml is not None
    assert "targetPort: 8080" in manifests.service_yaml

    # Verify HPA
    assert manifests.hpa_yaml is not None
    assert "HorizontalPodAutoscaler" in manifests.hpa_yaml

    # Verify NetworkPolicy
    assert manifests.network_policy_yaml is not None
    assert "NetworkPolicy" in manifests.network_policy_yaml

    # Verify Ingress
    assert manifests.ingress_yaml is not None
    assert "checkout.company.com" in manifests.ingress_yaml
    assert "cert-manager.io/cluster-issuer" in manifests.ingress_yaml
