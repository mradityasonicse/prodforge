# ProdForge Regulatory Compliance & Controls Mapping

This document outlines how ProdForge controls map to industry standards: **OWASP Top 10 (2021)**, **SOC2 Type II Common Criteria**, **HIPAA Security Rule**, and **PCI-DSS v4.0**.

---

## 1. OWASP Top 10 (2021) Mapping

| OWASP Category | Vulnerability Type | Rule ID | CWE Mapping | Automated Remediation (`prodforge fix`) |
|---|---|---|---|---|
| **A01:2021-Broken Access Control** | Path Traversal / Arbitrary File Read | `SEC-008` | CWE-22 | Boundary validation with `os.path.realpath` |
| **A02:2021-Cryptographic Failures** | Weak Hash Functions (MD5, SHA-1) | `SEC-007` | CWE-327 | Upgrade to SHA-256 or Argon2id |
| **A03:2021-Injection** | SQL Injection via String Interpolation | `SEC-002` | CWE-89 | Convert to parameterized queries / ORM bindings |
| **A03:2021-Injection** | Remote Code Execution via Eval/Exec | `SEC-003` | CWE-94 | Replace with safe JSON/ast parsing |
| **A03:2021-Injection** | Command Injection via Subprocess | `SEC-004` | CWE-78 | Enforce `shell=False` and argument tokenization |
| **A03:2021-Injection** | Cross-Site Scripting (DOM XSS) | `SEC-005` | CWE-79 | Sanitize inputs via DOMPurify |
| **A03:2021-Injection** | Prototype Pollution | `SEC-009` | CWE-1321 | Schema freeze & Map structures |
| **A05:2021-Security Misconfiguration** | Dockerfile Running as Root | `SEC-DOCKER-001` | CWE-250 | Create and switch to non-root `appuser` |
| **A05:2021-Security Misconfiguration** | Mutable `:latest` Container Tags | `SEC-DOCKER-002` | CWE-1188 | Pin base image to explicit SHA/version |
| **A07:2021-Identification Failures** | Hardcoded Secrets & Private Keys | `SEC-001` | CWE-798 | Extract secrets to `.env` and `os.getenv` |
| **A08:2021-Software Integrity** | Insecure Deserialization | `SEC-006` | CWE-502 | Use `yaml.safe_load()` or JSON |
| **A10:2021-SSRF** | Server-Side Request Forgery | `SEC-010` | CWE-918 | Enforce outbound URL allowlists |

---

## 2. SOC2 Type II Trust Services Criteria

| SOC2 Common Criteria | Trust Principle | ProdForge Technical Control |
|---|---|---|
| **CC6.1** | Logical Access Security | Static & Shannon entropy credential scanner detects AWS, GitHub, GCP, Stripe, and Slack API keys before commit. |
| **CC6.2** | User Registration & Access | Kubernetes generator specifies RBAC ServiceAccount bindings with `automountServiceAccountToken: false`. |
| **CC6.6** | Vulnerability Management | Continuous static code analysis with automated CI/CD gating (`--fail-under 80`). |
| **CC6.8** | Malicious Code Prevention | Scans for dynamic code execution (`eval`, `exec`, `subprocess(shell=True)`) and prototype pollution. |
| **CC7.1** | Infrastructure Monitoring | Hardener generates container health check endpoints (`/healthz`, `/readyz`) for automated liveness probes. |
| **CC8.1** | Change Management | Automated PR quality gate generates verifiable OASIS SARIF v2.1.0 audit receipts for every change. |

---

## 3. HIPAA Security Rule (§164.312 Technical Safeguards)

| Section | Safeguard | ProdForge Implementation |
|---|---|---|
| **§164.312(a)(1)** | Access Control & Unique User ID | Container hardening mandates non-root execution (`USER appuser`) and unprivileged execution context. |
| **§164.312(a)(2)(iv)** | Encryption and Decryption | Cryptographic auditing flags weak MD5/SHA-1 and requires SHA-256 or AES-GCM. |
| **§164.312(c)(1)** | Integrity Controls | Prevents unvalidated deserialization (`pickle.loads`, `yaml.load`) and arbitrary string evaluation. |
| **§164.312(e)(1)** | Transmission Security | Kubernetes generator provisions TLS-terminated Ingress with cert-manager annotations and modern cipher suites. |

---

## 4. PCI-DSS v4.0 (Requirement 6: Secure Systems & Software)

| Requirement | Requirement Description | ProdForge Verification |
|---|---|---|
| **6.2.4** | Software engineering techniques prevent common software vulnerabilities | Scans and enforces OWASP Top 10, input sanitization, and parameterized database queries. |
| **6.3.1** | Security vulnerabilities are identified and managed | Automated SARIF export integrates into enterprise vulnerability scanners and dashboards. |
| **6.3.2** | Bespoke and custom software is reviewed prior to release | ProdForge CI PR gate automatically audits all commits, blocking code that fails the quality gate. |
| **6.4.1** | Separation of development and production environments | Hardener enforces environment isolation, separating development secrets from runtime container environments. |
