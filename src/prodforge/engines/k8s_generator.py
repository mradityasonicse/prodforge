"""
Enterprise Kubernetes Manifest & Architecture Generator.
Generates hardened production-ready Kubernetes manifests with strict
Pod Security Standards (Restricted Profile), HPA autoscaling, Zero-Trust NetworkPolicies, and TLS Ingress.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel, Field


class K8sManifestArtifact(BaseModel):
    name: str
    filename: str
    content: str
    description: str


class K8sManifestResult(BaseModel):
    app_name: str
    namespace: str
    artifacts: List[K8sManifestArtifact] = Field(default_factory=list)
    applied: bool = False

    @property
    def deployment_yaml(self) -> str:
        for a in self.artifacts:
            if a.name == "Deployment":
                return a.content
        return ""

    @property
    def service_yaml(self) -> str:
        for a in self.artifacts:
            if a.name == "Service":
                return a.content
        return ""

    @property
    def hpa_yaml(self) -> str:
        for a in self.artifacts:
            if a.name == "HorizontalPodAutoscaler":
                return a.content
        return ""

    @property
    def network_policy_yaml(self) -> str:
        for a in self.artifacts:
            if a.name == "NetworkPolicy":
                return a.content
        return ""

    @property
    def ingress_yaml(self) -> str:
        for a in self.artifacts:
            if a.name == "Ingress":
                return a.content
        return ""


def generate_k8s_manifests(
    app_name: str = "prodforge-app",
    namespace: str = "production",
    domain: str = "api.example.com",
    container_image: str = "ghcr.io/org/app:v1.0.0",
    container_port: int = 8000,
    min_replicas: int = 2,
    max_replicas: int = 10,
    output_dir: Optional[Path] = None,
    image: Optional[str] = None,
    port: Optional[int] = None,
    replicas: Optional[int] = None,
    ingress_host: Optional[str] = None,
    **kwargs
) -> K8sManifestResult:
    """Synthesize complete enterprise-grade Kubernetes manifest suite."""
    if image:
        container_image = image
    if port:
        container_port = port
    if replicas:
        min_replicas = replicas
    if ingress_host:
        domain = ingress_host
    deployment_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: {namespace}
  labels:
    app.kubernetes.io/name: {app_name}
    app.kubernetes.io/part-of: {app_name}
    app.kubernetes.io/managed-by: prodforge
spec:
  replicas: {min_replicas}
  selector:
    matchLabels:
      app.kubernetes.io/name: {app_name}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {app_name}
    spec:
      # Pod Security Standards: Restricted Profile
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: app
          image: {container_image}
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: {container_port}
              name: http
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 2
          volumeMounts:
            - name: tmp-volume
              mountPath: /tmp
      volumes:
        - name: tmp-volume
          emptyDir: {{}}
"""

    service_yaml = f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}-svc
  namespace: {namespace}
  labels:
    app.kubernetes.io/name: {app_name}
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: {container_port}
      protocol: TCP
      name: http
  selector:
    app.kubernetes.io/name: {app_name}
"""

    hpa_yaml = f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {app_name}-hpa
  namespace: {namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {app_name}
  minReplicas: {min_replicas}
  maxReplicas: {max_replicas}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 75
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
"""

    network_policy_yaml = f"""apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {app_name}-netpol
  namespace: {namespace}
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: {app_name}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
      ports:
        - protocol: TCP
          port: {container_port}
  egress:
    # Allow DNS resolution
    - to:
        - namespaceSelector: {{}}
      ports:
        - protocol: UDP
          port: 53
    # Allow outbound database traffic
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: postgres
      ports:
        - protocol: TCP
          port: 5432
"""

    ingress_yaml = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app_name}-ingress
  namespace: {namespace}
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
    - hosts:
        - {domain}
      secretName: {app_name}-tls-secret
  rules:
    - host: {domain}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {app_name}-svc
                port:
                  number: 80
"""

    artifacts = [
        K8sManifestArtifact(
            name="Deployment",
            filename="deployment.yaml",
            content=deployment_yaml.strip(),
            description="Hardened Pod Security Restricted deployment with memory/CPU limits & health probes"
        ),
        K8sManifestArtifact(
            name="Service",
            filename="service.yaml",
            content=service_yaml.strip(),
            description="ClusterIP service routing to container http port"
        ),
        K8sManifestArtifact(
            name="HorizontalPodAutoscaler",
            filename="hpa.yaml",
            content=hpa_yaml.strip(),
            description="Auto-scaler scaling from 2 to 10 pods based on CPU/RAM thresholds"
        ),
        K8sManifestArtifact(
            name="NetworkPolicy",
            filename="networkpolicy.yaml",
            content=network_policy_yaml.strip(),
            description="Zero-trust traffic isolation restricting ingress and egress"
        ),
        K8sManifestArtifact(
            name="Ingress",
            filename="ingress.yaml",
            content=ingress_yaml.strip(),
            description="TLS-terminated ingress with Let's Encrypt automated SSL certificate issuance"
        )
    ]

    applied = False
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for art in artifacts:
            (output_dir / art.filename).write_text(art.content, encoding="utf-8")
        applied = True

    return K8sManifestResult(
        app_name=app_name,
        namespace=namespace,
        artifacts=artifacts,
        applied=applied
    )
