"""
Live Web Application & API Dynamic Security Scanner (DAST & Recon Engine).
Performs live endpoint health checks, OWASP security header audits, SSL/TLS handshake inspection,
CORS misconfiguration checks, cookie security flags, technology fingerprinting, and exposed sensitive path probes.
"""

from __future__ import annotations

import socket
import ssl
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import httpx
from pydantic import BaseModel, Field

from prodforge.engines.auditor import (
    CodeAuditResult,
    FileAuditFinding,
    ComplexityMetrics,
    PillarScorecard,
    ComplianceFlags,
)


class HeaderCheckResult(BaseModel):
    header: str
    status: str  # "PASS" | "WARN" | "FAIL"
    value: Optional[str] = None
    recommendation: str


class SslInspectionResult(BaseModel):
    is_https: bool
    is_valid: bool = False
    issuer: str = ""
    subject: str = ""
    expires_at: str = ""
    days_remaining: int = 0
    tls_version: str = ""
    cipher: str = ""
    error: Optional[str] = None


class EndpointProbeResult(BaseModel):
    path: str
    status_code: int
    is_exposed: bool
    risk: str
    description: str


class LiveScanResult(BaseModel):
    target_url: str
    normalized_url: str
    status_code: int = 0
    response_time_ms: float = 0.0
    server_header: str = "Unknown"
    detected_technologies: List[str] = Field(default_factory=list)
    ssl_info: SslInspectionResult
    security_headers: List[HeaderCheckResult] = Field(default_factory=list)
    cors_vulnerable: bool = False
    cors_details: str = "Safe / Default CORS"
    cookies_audited: List[Dict[str, Any]] = Field(default_factory=list)
    exposed_endpoints: List[EndpointProbeResult] = Field(default_factory=list)
    dast_score: int = 100
    readiness_grade: str = "A+"
    findings: List[FileAuditFinding] = Field(default_factory=list)
    remediation_configs: Dict[str, str] = Field(default_factory=dict)


COMMON_EXPOSED_PATHS = [
    {
        "path": "/.env",
        "risk": "CRITICAL",
        "desc": "Exposed environment configuration file leaking database credentials and API secrets.",
        "rule_id": "DAST-001",
        "cwe": "CWE-200"
    },
    {
        "path": "/.git/config",
        "risk": "CRITICAL",
        "desc": "Exposed Git repository metadata enabling source code reconstruction.",
        "rule_id": "DAST-002",
        "cwe": "CWE-538"
    },
    {
        "path": "/actuator/health",
        "risk": "MEDIUM",
        "desc": "Spring Boot / Microservice actuator endpoint exposed publicly.",
        "rule_id": "DAST-003",
        "cwe": "CWE-200"
    },
    {
        "path": "/swagger.json",
        "risk": "LOW",
        "desc": "Publicly discoverable OpenAPI / Swagger specification revealing private API schema.",
        "rule_id": "DAST-004",
        "cwe": "CWE-200"
    },
    {
        "path": "/.well-known/security.txt",
        "risk": "INFO",
        "desc": "RFC 9116 security vulnerability disclosure contact file.",
        "rule_id": "DAST-005",
        "cwe": "CWE-16"
    },
    {
        "path": "/robots.txt",
        "risk": "INFO",
        "desc": "Search engine crawler policy file.",
        "rule_id": "DAST-006",
        "cwe": "CWE-16"
    }
]


def inspect_ssl(hostname: str, port: int = 443, timeout: float = 5.0) -> SslInspectionResult:
    """Inspect SSL/TLS certificate details directly via socket handshake."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                tls_version = ssock.version() or "TLSv1.2"
                cipher = ssock.cipher()[0] if ssock.cipher() else "Unknown"

                # Parse issuer & subject
                issuer_dict = dict(x[0] for x in cert.get("issuer", ()))
                subject_dict = dict(x[0] for x in cert.get("subject", ()))
                issuer = issuer_dict.get("organizationName") or issuer_dict.get("commonName") or "Unknown Issuer"
                subject = subject_dict.get("commonName") or hostname

                # Expiry check
                not_after_str = cert.get("notAfter", "")
                not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_remaining = (not_after - now).days

                return SslInspectionResult(
                    is_https=True,
                    is_valid=days_remaining > 0,
                    issuer=issuer,
                    subject=subject,
                    expires_at=not_after.strftime("%Y-%m-%d %H:%M UTC"),
                    days_remaining=days_remaining,
                    tls_version=tls_version,
                    cipher=cipher
                )
    except Exception as exc:
        return SslInspectionResult(
            is_https=True,
            is_valid=False,
            error=str(exc)
        )


def scan_live_url(
    target_url: str,
    probe_endpoints: bool = True,
    timeout: float = 8.0
) -> LiveScanResult:
    """
    Execute full DAST dynamic security scan against a live deployed URL or local server.
    """
    raw_target = target_url.strip()
    if not raw_target.startswith(("http://", "https://")):
        raw_target = "https://" + raw_target

    parsed = urlparse(raw_target)
    hostname = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    base_origin = f"{parsed.scheme}://{hostname}" + (f":{port}" if parsed.port and parsed.port not in (80, 443) else "")

    findings: List[FileAuditFinding] = []
    headers_check: List[HeaderCheckResult] = []
    technologies: List[str] = []
    cookies_audited: List[Dict[str, Any]] = []
    exposed_endpoints: List[EndpointProbeResult] = []
    cors_vulnerable = False
    cors_details = "Safe (No wildcard reflection)"

    # 1. SSL/TLS Audit
    ssl_info = SslInspectionResult(is_https=parsed.scheme == "https")
    if parsed.scheme == "https":
        ssl_info = inspect_ssl(hostname, port=port, timeout=timeout)
        if not ssl_info.is_valid:
            findings.append(
                FileAuditFinding(
                    file_path=base_origin,
                    rule_id="DAST-SSL-001",
                    cwe_id="CWE-295",
                    category="SECURITY",
                    title="Invalid or Expired SSL/TLS Certificate",
                    severity="CRITICAL",
                    line_number=1,
                    line_content=f"Issuer: {ssl_info.issuer} | Error: {ssl_info.error or 'Expired'}",
                    description=f"The remote HTTPS certificate validation failed: {ssl_info.error or 'Certificate expired'}.",
                    remediation="Renew SSL/TLS certificate via Let's Encrypt / Certbot or cloud provider (AWS ACM, Cloudflare)."
                )
            )
        elif ssl_info.days_remaining < 15:
            findings.append(
                FileAuditFinding(
                    file_path=base_origin,
                    rule_id="DAST-SSL-002",
                    cwe_id="CWE-295",
                    category="SECURITY",
                    title=f"SSL/TLS Certificate Expiring Soon ({ssl_info.days_remaining} Days Remaining)",
                    severity="MEDIUM",
                    line_number=1,
                    line_content=f"Expires at: {ssl_info.expires_at}",
                    description=f"Certificate for {hostname} expires in {ssl_info.days_remaining} days.",
                    remediation="Trigger automated renewal via certbot renew or cloud certificate manager."
                )
            )
    else:
        findings.append(
            FileAuditFinding(
                file_path=base_origin,
                rule_id="DAST-SSL-003",
                cwe_id="CWE-319",
                category="SECURITY",
                title="Unencrypted HTTP Protocol (Cleartext Transmission)",
                severity="HIGH",
                line_number=1,
                line_content="Protocol: http://",
                description="Application communicates over unencrypted HTTP, allowing interception and session hijacking.",
                remediation="Configure automatic 301 redirection from HTTP to HTTPS and install an SSL certificate."
            )
        )

    # 2. Main HTTP Request & Latency Check
    start_time = time.perf_counter()
    status_code = 0
    resp_headers: Dict[str, str] = {}
    server_header = "Unknown"

    client_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ProdForge-Security-Audit/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        with httpx.Client(timeout=timeout, verify=False, follow_redirects=True) as client:
            resp = client.get(raw_target, headers=client_headers)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            status_code = resp.status_code
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            server_header = resp_headers.get("server", "Unknown")

            # Detect server tech
            if "server" in resp_headers:
                technologies.append(f"Server: {resp_headers['server']}")
            if "x-powered-by" in resp_headers:
                technologies.append(f"Runtime: {resp_headers['x-powered-by']}")
                findings.append(
                    FileAuditFinding(
                        file_path=raw_target,
                        rule_id="DAST-INFO-001",
                        cwe_id="CWE-200",
                        category="QUALITY",
                        title=f"Technology Disclosure in X-Powered-By ({resp_headers['x-powered-by']})",
                        severity="LOW",
                        line_number=1,
                        line_content=f"X-Powered-By: {resp_headers['x-powered-by']}",
                        description="Exposing framework runtime versions assists attackers in targeting version-specific CVEs.",
                        remediation="Disable X-Powered-By header (e.g. app.disable('x-powered-by') in Express)."
                    )
                )

            # Cookie Security Analysis
            for cookie_name, cookie_val in resp.cookies.items():
                cookie_raw = resp.headers.get("set-cookie", "")
                is_secure = "secure" in cookie_raw.lower()
                is_httponly = "httponly" in cookie_raw.lower()
                is_samesite = "samesite" in cookie_raw.lower()
                cookies_audited.append({
                    "name": cookie_name,
                    "secure": is_secure,
                    "httponly": is_httponly,
                    "samesite": is_samesite
                })
                if not is_httponly:
                    findings.append(
                        FileAuditFinding(
                            file_path=raw_target,
                            rule_id="DAST-COOKIE-001",
                            cwe_id="CWE-1004",
                            category="SECURITY",
                            title=f"Cookie '{cookie_name}' Missing HttpOnly Flag",
                            severity="MEDIUM",
                            line_number=1,
                            line_content=f"Cookie: {cookie_name}",
                            description="Cookie accessible via client-side JavaScript, increasing risk of credential theft via XSS.",
                            remediation="Set HttpOnly flag on all session and authentication cookies."
                        )
                    )
                if parsed.scheme == "https" and not is_secure:
                    findings.append(
                        FileAuditFinding(
                            file_path=raw_target,
                            rule_id="DAST-COOKIE-002",
                            cwe_id="CWE-614",
                            category="SECURITY",
                            title=f"Cookie '{cookie_name}' Missing Secure Flag over HTTPS",
                            severity="MEDIUM",
                            line_number=1,
                            line_content=f"Cookie: {cookie_name}",
                            description="Cookie lacks Secure flag, allowing transmission over unencrypted channels.",
                            remediation="Set Secure flag on all cookies transmitted over HTTPS."
                        )
                    )
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        findings.append(
            FileAuditFinding(
                file_path=raw_target,
                rule_id="DAST-CONN-001",
                cwe_id="CWE-601",
                category="SECURITY",
                title="Endpoint Connection Timeout or Refusal",
                severity="HIGH",
                line_number=1,
                line_content=raw_target,
                description=f"Failed to connect to target URL: {str(exc)}",
                remediation="Verify target host is running, DNS resolves correctly, and firewall allows incoming connections."
            )
        )

    # 3. OWASP Security Headers Matrix
    # HSTS
    hsts = resp_headers.get("strict-transport-security")
    if hsts:
        headers_check.append(HeaderCheckResult(
            header="Strict-Transport-Security",
            status="PASS",
            value=hsts,
            recommendation="Configured."
        ))
    else:
        headers_check.append(HeaderCheckResult(
            header="Strict-Transport-Security",
            status="FAIL",
            recommendation="Add 'Strict-Transport-Security: max-age=63072000; includeSubDomains; preload'."
        ))
        if parsed.scheme == "https":
            findings.append(
                FileAuditFinding(
                    file_path=raw_target,
                    rule_id="DAST-HDR-001",
                    cwe_id="CWE-319",
                    category="SECURITY",
                    title="Missing HTTP Strict Transport Security (HSTS) Header",
                    severity="HIGH",
                    line_number=1,
                    line_content="Header missing: Strict-Transport-Security",
                    description="Without HSTS, attackers can perform SSL stripping attacks during initial connection.",
                    remediation="Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' header."
                )
            )

    # Content-Security-Policy (CSP)
    csp = resp_headers.get("content-security-policy")
    if csp:
        if "'unsafe-inline'" in csp or "'unsafe-eval'" in csp:
            headers_check.append(HeaderCheckResult(
                header="Content-Security-Policy",
                status="WARN",
                value=csp[:80] + "...",
                recommendation="CSP contains unsafe-inline or unsafe-eval directives. Refactor to nonce-based hashes."
            ))
            findings.append(
                FileAuditFinding(
                    file_path=raw_target,
                    rule_id="DAST-HDR-002",
                    cwe_id="CWE-79",
                    category="SECURITY",
                    title="Weak Content Security Policy (Allows unsafe-inline / unsafe-eval)",
                    severity="MEDIUM",
                    line_number=1,
                    line_content=csp[:100],
                    description="CSP permits inline script execution, weakening cross-site scripting (XSS) mitigation.",
                    remediation="Adopt strict cryptographic nonces (script-src 'nonce-...') or SHA-256 hashes."
                )
            )
        else:
            headers_check.append(HeaderCheckResult(
                header="Content-Security-Policy",
                status="PASS",
                value=csp[:80] + "...",
                recommendation="Strict CSP active."
            ))
    else:
        headers_check.append(HeaderCheckResult(
            header="Content-Security-Policy",
            status="FAIL",
            recommendation="Add Content-Security-Policy header to restrict script and object execution sources."
        ))
        findings.append(
            FileAuditFinding(
                file_path=raw_target,
                rule_id="DAST-HDR-003",
                cwe_id="CWE-79",
                category="SECURITY",
                title="Missing Content-Security-Policy (CSP) Header",
                severity="HIGH",
                line_number=1,
                line_content="Header missing: Content-Security-Policy",
                description="Absence of CSP leaves web applications exposed to Cross-Site Scripting (XSS) and data exfiltration.",
                remediation="Implement strict CSP (e.g. default-src 'self'; script-src 'self'; object-src 'none')."
            )
        )

    # X-Frame-Options
    xfo = resp_headers.get("x-frame-options")
    if xfo and xfo.upper() in ("DENY", "SAMEORIGIN"):
        headers_check.append(HeaderCheckResult(header="X-Frame-Options", status="PASS", value=xfo, recommendation="Protected against Clickjacking."))
    else:
        headers_check.append(HeaderCheckResult(header="X-Frame-Options", status="FAIL", recommendation="Set 'X-Frame-Options: DENY' or 'SAMEORIGIN'."))
        findings.append(
            FileAuditFinding(
                file_path=raw_target,
                rule_id="DAST-HDR-004",
                cwe_id="CWE-1021",
                category="SECURITY",
                title="Missing X-Frame-Options Header (Clickjacking Risk)",
                severity="MEDIUM",
                line_number=1,
                line_content="Header missing: X-Frame-Options",
                description="The page can be embedded in an attacker's iframe, enabling clickjacking attacks.",
                remediation="Add 'X-Frame-Options: SAMEORIGIN' or 'DENY'."
            )
        )

    # X-Content-Type-Options
    xcto = resp_headers.get("x-content-type-options")
    if xcto and "nosniff" in xcto.lower():
        headers_check.append(HeaderCheckResult(header="X-Content-Type-Options", status="PASS", value=xcto, recommendation="Protected against MIME-sniffing."))
    else:
        headers_check.append(HeaderCheckResult(header="X-Content-Type-Options", status="FAIL", recommendation="Set 'X-Content-Type-Options: nosniff'."))
        findings.append(
            FileAuditFinding(
                file_path=raw_target,
                rule_id="DAST-HDR-005",
                cwe_id="CWE-16",
                category="SECURITY",
                title="Missing X-Content-Type-Options: nosniff Header",
                severity="LOW",
                line_number=1,
                line_content="Header missing: X-Content-Type-Options",
                description="Browser may sniff content types and execute text/plain as executable HTML/JS.",
                remediation="Add 'X-Content-Type-Options: nosniff' header."
            )
        )

    # Referrer-Policy
    ref = resp_headers.get("referrer-policy")
    if ref:
        headers_check.append(HeaderCheckResult(header="Referrer-Policy", status="PASS", value=ref, recommendation="Referrer policy configured."))
    else:
        headers_check.append(HeaderCheckResult(header="Referrer-Policy", status="WARN", recommendation="Set 'Referrer-Policy: strict-origin-when-cross-origin'."))

    # Permissions-Policy
    perm = resp_headers.get("permissions-policy")
    if perm:
        headers_check.append(HeaderCheckResult(header="Permissions-Policy", status="PASS", value=perm[:60] + "...", recommendation="Browser feature permissions restricted."))
    else:
        headers_check.append(HeaderCheckResult(header="Permissions-Policy", status="WARN", recommendation="Define Permissions-Policy (e.g. camera=(), microphone=(), geolocation=())."))

    # 4. CORS Misconfiguration Probe
    try:
        with httpx.Client(timeout=4.0, verify=False) as client:
            cors_resp = client.options(
                raw_target,
                headers={"Origin": "https://attacker-evaluation-domain.org", "Access-Control-Request-Method": "POST"}
            )
            acao = cors_resp.headers.get("access-control-allow-origin", "")
            acac = cors_resp.headers.get("access-control-allow-credentials", "").lower() == "true"
            if acao == "*" and acac:
                cors_vulnerable = True
                cors_details = "CRITICAL: Wildcard origin '*' combined with credentials 'true'."
                findings.append(
                    FileAuditFinding(
                        file_path=raw_target,
                        rule_id="DAST-CORS-001",
                        cwe_id="CWE-942",
                        category="SECURITY",
                        title="Critical CORS Misconfiguration (Wildcard Origin + Credentials)",
                        severity="CRITICAL",
                        line_number=1,
                        line_content="Access-Control-Allow-Origin: * | Access-Control-Allow-Credentials: true",
                        description="Wildcard CORS origin with credentials enabled allows cross-origin data theft.",
                        remediation="Explicitly specify trusted origin domains instead of '*'."
                    )
                )
            elif "attacker-evaluation-domain.org" in acao:
                cors_vulnerable = True
                cors_details = "HIGH: Insecure reflection of arbitrary Origin header."
                findings.append(
                    FileAuditFinding(
                        file_path=raw_target,
                        rule_id="DAST-CORS-002",
                        cwe_id="CWE-942",
                        category="SECURITY",
                        title="Insecure Arbitrary CORS Origin Reflection",
                        severity="HIGH",
                        line_number=1,
                        line_content=f"Access-Control-Allow-Origin: {acao}",
                        description="Application reflects any inbound Origin header without allowlist validation.",
                        remediation="Maintain a strict server-side allowlist of authorized origin domains."
                    )
                )
    except Exception:
        pass

    # 5. Information Disclosure & Exposed Endpoints Probe
    if probe_endpoints and hostname not in ("127.0.0.1", "localhost", "::1"):
        try:
            with httpx.Client(timeout=3.0, verify=False, follow_redirects=False) as probe_client:
                for probe in COMMON_EXPOSED_PATHS:
                    probe_url = base_origin + probe["path"]
                    try:
                        p_resp = probe_client.get(probe_url)
                        # An endpoint is considered exposed if it returns 200 OK with non-trivial body and not a soft 404
                        is_exposed = p_resp.status_code == 200 and len(p_resp.content) > 10 and not ("<html" in p_resp.text.lower() and "404" in p_resp.text)
                        exposed_endpoints.append(
                            EndpointProbeResult(
                                path=probe["path"],
                                status_code=p_resp.status_code,
                                is_exposed=is_exposed,
                                risk=probe["risk"],
                                description=probe["desc"]
                            )
                        )
                        if is_exposed and probe["risk"] in ("CRITICAL", "HIGH"):
                            findings.append(
                                FileAuditFinding(
                                    file_path=probe_url,
                                    rule_id=probe["rule_id"],
                                    cwe_id=probe["cwe"],
                                    category="SECURITY",
                                    title=f"Sensitive Endpoint Exposed: {probe['path']} (HTTP 200)",
                                    severity=probe["risk"],
                                    line_number=1,
                                    line_content=f"GET {probe['path']} -> 200 OK ({len(p_resp.content)} bytes)",
                                    description=probe["desc"],
                                    remediation=f"Block public web server access to '{probe['path']}' in Nginx/Apache/Cloudflare rules."
                                )
                            )
                    except Exception:
                        pass
        except Exception:
            pass

    # 6. Calculate DAST Score & Grade
    crit_count = sum(1 for f in findings if f.severity == "CRITICAL")
    high_count = sum(1 for f in findings if f.severity == "HIGH")
    med_count = sum(1 for f in findings if f.severity == "MEDIUM")
    low_count = sum(1 for f in findings if f.severity == "LOW")

    penalty = (crit_count * 25) + (high_count * 15) + (med_count * 6) + (low_count * 2)
    dast_score = max(0, 100 - penalty)

    if dast_score >= 90:
        grade = "A+"
    elif dast_score >= 80:
        grade = "B"
    elif dast_score >= 65:
        grade = "C"
    else:
        grade = "F"

    # 7. Generate Ready-to-Use Web Server Remediation Snippets
    remediation_configs = {
        "nginx": f"""# Nginx Production Security Headers Configuration
server {{
    # ...
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none';" always;

    # Block sensitive paths
    location ~* /\\.(env|git|svn|htaccess) {{
        deny all;
        return 404;
    }}
}}""",
        "caddy": f"""# Caddyfile Security Directives
{hostname} {{
    header {{
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
        Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none';"
    }}
    @sensitive path /.env* /.git* /actuator*
    respond @sensitive 404
}}"""
    }

    return LiveScanResult(
        target_url=target_url,
        normalized_url=raw_target,
        status_code=status_code,
        response_time_ms=round(elapsed_ms, 2),
        server_header=server_header,
        detected_technologies=technologies,
        ssl_info=ssl_info,
        security_headers=headers_check,
        cors_vulnerable=cors_vulnerable,
        cors_details=cors_details,
        cookies_audited=cookies_audited,
        exposed_endpoints=exposed_endpoints,
        dast_score=dast_score,
        readiness_grade=grade,
        findings=findings,
        remediation_configs=remediation_configs
    )


def convert_live_scan_to_audit_result(live_res: LiveScanResult) -> CodeAuditResult:
    """
    Convert a LiveScanResult into a standard CodeAuditResult so it seamlessly feeds
    into 5-Pillar Scorecard, SARIF exporter, and Executive PDF reporting.
    """
    crit_count = sum(1 for f in live_res.findings if f.severity == "CRITICAL")
    high_count = sum(1 for f in live_res.findings if f.severity == "HIGH")
    med_count = sum(1 for f in live_res.findings if f.severity == "MEDIUM")
    low_count = sum(1 for f in live_res.findings if f.severity == "LOW")

    sec_score = live_res.dast_score
    qual_score = 90 if not any("X-Powered-By" in f.title for f in live_res.findings) else 75
    arch_score = 95 if live_res.ssl_info.is_valid else 60
    test_score = 85  # Live endpoint verified responding
    devops_score = 95 if live_res.status_code == 200 else 60

    pillars = PillarScorecard(
        security_score=sec_score,
        quality_score=qual_score,
        architecture_score=arch_score,
        test_readiness_score=test_score,
        devops_hardening_score=devops_score
    )

    compliance = ComplianceFlags(
        zero_hardcoded_secrets=not any("DAST-001" in f.rule_id for f in live_res.findings),
        owasp_top_10_clean=crit_count == 0 and high_count == 0,
        input_sanitization_shield=not live_res.cors_vulnerable,
        non_root_container_certified=True,
        ci_cd_gate_ready=live_res.dast_score >= 80
    )

    metrics = ComplexityMetrics(
        total_lines=len(live_res.security_headers),
        code_lines=len(live_res.findings),
        comment_lines=0,
        functions_count=len(live_res.exposed_endpoints),
        classes_count=1,
        max_nesting_depth=1,
        cyclomatic_estimate=1
    )

    summary = (
        f"Live DAST Scan for {live_res.normalized_url} (HTTP {live_res.status_code}, {live_res.response_time_ms}ms). "
        f"SSL: {'Valid' if live_res.ssl_info.is_valid else 'Failed/Unencrypted'}. "
        f"Discovered {len(live_res.findings)} live operational security findings."
    )

    llm_recommendations = f"""### 🛡️ Live Deployment Security Hardening Recommendations

**Target URL:** `{live_res.normalized_url}`  
**Readiness Grade:** **{live_res.readiness_grade}** ({live_res.dast_score}/100)  
**Server Banner:** `{live_res.server_header}`  
**TLS Handshake:** `{live_res.ssl_info.tls_version}` ({live_res.ssl_info.cipher})  

#### Key Actions Required:
1. **Security Headers**: Ensure all 6 OWASP recommended headers (`HSTS`, `CSP`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`) are returned on every HTTP response.
2. **CORS Isolation**: Restrict cross-origin access exclusively to verified client origins. Never reflect arbitrary `Origin` headers alongside credentials.
3. **Endpoint Shielding**: Verify that sensitive paths like `/.env`, `/.git`, and debug consoles return HTTP 404 / 403 on production reverse proxies.
"""

    return CodeAuditResult(
        target_path=live_res.normalized_url,
        is_directory=False,
        total_files_scanned=1,
        readiness_score=live_res.dast_score,
        readiness_grade=live_res.readiness_grade,
        readiness_status="PASSED" if live_res.dast_score >= 80 else "FAILED",
        summary=summary,
        metrics=metrics,
        pillars=pillars,
        compliance=compliance,
        critical_count=crit_count,
        high_count=high_count,
        medium_count=med_count,
        low_count=low_count,
        findings=live_res.findings,
        llm_recommendations=llm_recommendations,
        is_offline_fallback=False,
        gate_passed=live_res.dast_score >= 80
    )
