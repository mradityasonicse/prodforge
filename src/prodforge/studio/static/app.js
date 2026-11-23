// ProdForge Studio - Enterprise Frontend Interactive Controller
document.addEventListener("DOMContentLoaded", () => {
  if (window.mermaid) {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      themeVariables: {
        darkMode: true,
        background: "#0A0F1C",
        primaryColor: "#1E293B",
        primaryTextColor: "#F8FAFC",
        primaryBorderColor: "#00F0FF",
        lineColor: "#64748B",
        secondaryColor: "#0F172A",
        tertiaryColor: "#1E293B"
      }
    });
  }

  // --- TAB NAVIGATION ---
  const tabButtons = document.querySelectorAll(".nav-tab");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const tabTarget = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPanel = document.getElementById(`tab-${tabTarget}`);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });

  // --- HomeNest Design System Theme Engine ---
  const btnThemeToggle = document.getElementById("btn-theme-toggle");
  const themeToggleIcon = document.getElementById("theme-toggle-icon");
  const themeToggleText = document.getElementById("theme-toggle-text");

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("prodforge-theme", theme);
    if (theme === "homenest") {
      if (themeToggleIcon) themeToggleIcon.textContent = "🏡";
      if (themeToggleText) themeToggleText.textContent = "HomeNest";
    } else {
      if (themeToggleIcon) themeToggleIcon.textContent = "🌙";
      if (themeToggleText) themeToggleText.textContent = "Cyber Dark";
    }
  }

  const savedTheme = localStorage.getItem("prodforge-theme") || "homenest";
  setTheme(savedTheme);

  if (btnThemeToggle) {
    btnThemeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "homenest";
      const nextTheme = current === "homenest" ? "cyber-dark" : "homenest";
      setTheme(nextTheme);
    });
  }

  fetchStatus();

  // ==========================================================================
  // Claude Code / Antigravity Elite Motion & Micro-Interaction Engine
  // ==========================================================================

  // 1. Toast Notification System
  function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? "✓" : type === "error" ? "✗" : "ℹ";
    toast.innerHTML = `<span style="font-weight:700;">${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 350);
    }, 3200);
  }

  // 2. Claude Code Live Telemetry Logger
  const terminalLogs = document.getElementById("terminal-logs");
  const agentLastActivity = document.getElementById("agent-last-activity");
  function logTelemetry(msg, level = "info") {
    if (agentLastActivity) agentLastActivity.textContent = msg;
    if (!terminalLogs) return;
    const now = new Date().toTimeString().split(" ")[0];
    const line = document.createElement("div");
    line.className = `log-line ${level}`;
    line.textContent = `[${now}] ${msg}`;
    terminalLogs.appendChild(line);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
  }

  // 3. Telemetry Drawer Expand / Collapse
  const btnToggleDrawer = document.getElementById("btn-toggle-drawer");
  const telemetryToggleBar = document.getElementById("telemetry-toggle-bar");
  const terminalBody = document.getElementById("terminal-body");
  const btnClearTerm = document.getElementById("btn-clear-term");

  if (telemetryToggleBar && terminalBody) {
    const toggle = () => {
      const isHidden = terminalBody.classList.toggle("hidden");
      if (btnToggleDrawer) {
        btnToggleDrawer.textContent = isHidden ? "▲ Expand Terminal" : "▼ Collapse Terminal";
      }
    };
    telemetryToggleBar.addEventListener("click", (e) => {
      if (e.target.id !== "btn-toggle-drawer") toggle();
    });
    if (btnToggleDrawer) btnToggleDrawer.addEventListener("click", toggle);
  }
  if (btnClearTerm && terminalLogs) {
    btnClearTerm.addEventListener("click", () => {
      terminalLogs.innerHTML = `<div class="log-line info">[SYS] Terminal cleared.</div>`;
    });
  }

  // 4. Tactile Button Ripple Effect (Material & Spring wave)
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn, .btn-sm, .nav-tab, .theme-toggle-btn");
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    const wave = document.createElement("span");
    wave.className = "ripple-wave";
    wave.style.width = wave.style.height = `${size}px`;
    wave.style.left = `${x}px`;
    wave.style.top = `${y}px`;

    btn.appendChild(wave);
    wave.addEventListener("animationend", () => wave.remove());
  });

  // 5. 3D Card Perspective Tilt & Cursor Specular Sheen
  document.querySelectorAll(".card").forEach((card) => {
    card.classList.add("interactive-card");
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      // Subtle tilt
      const rotateX = ((y - centerY) / centerY) * -2.5;
      const rotateY = ((x - centerX) / centerX) * 2.5;

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg)`;
      card.style.setProperty("--mouse-x", `${x}px`);
      card.style.setProperty("--mouse-y", `${y}px`);
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg)";
    });
  });

  // 6. Smooth Number Counter (Odometer Animation)
  function animateCounter(el, targetVal, duration = 800) {
    if (!el) return;
    const startVal = 0;
    const startTime = performance.now();
    function update(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(startVal + (targetVal - startVal) * eased);
      el.textContent = current;
      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = targetVal;
      }
    }
    requestAnimationFrame(update);
  }

  async function fetchStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      const badge = document.getElementById("provider-badge");
      const modelBadge = document.getElementById("active-model-badge");

      if (badge && modelBadge) {
        badge.textContent = data.detected_provider.toUpperCase();
        modelBadge.textContent = data.active_model;
        if (data.detected_provider === "offline") {
          badge.parentElement.style.borderColor = "rgba(245, 158, 11, 0.4)";
          badge.parentElement.style.color = "#F59E0B";
          const dot = badge.parentElement.querySelector(".pulse-dot");
          if (dot) {
            dot.style.background = "#F59E0B";
            dot.style.boxShadow = "0 0 8px #F59E0B";
          }
        }
      }
    } catch (err) {
      console.warn("Status check failed:", err);
    }
  }

  // --- TAB 1: PLANNER ---
  const btnRunPlan = document.getElementById("btn-run-plan");
  const btnPlanPreset = document.getElementById("btn-plan-preset");
  const planIdea = document.getElementById("plan-idea");
  const planConstraints = document.getElementById("plan-constraints");
  const planLoading = document.getElementById("plan-loading");
  const planMarkdownOutput = document.getElementById("plan-markdown-output");
  const planScorePill = document.getElementById("plan-score-pill");
  const planDiagramBox = document.getElementById("plan-diagram-box");
  const mermaidRender = document.getElementById("mermaid-render");
  const btnCopyPlan = document.getElementById("btn-copy-plan");

  let currentPlanMarkdown = "";

  btnPlanPreset.addEventListener("click", () => {
    planIdea.value = "Enterprise multi-currency payment settlement gateway with idempotency keys, double-entry ledger in PostgreSQL, sub-second WebSocket order updates, and Redis distributed lock.";
    planConstraints.value = "FastAPI (Python), PostgreSQL, Redis, Docker, Kubernetes, Zero-Trust TLS 1.3, STRIDE threat model";
  });

  btnRunPlan.addEventListener("click", async () => {
    const idea = planIdea.value.trim();
    if (!idea) {
      alert("Please enter a product or system idea.");
      return;
    }

    planLoading.classList.remove("hidden");
    planMarkdownOutput.innerHTML = "";
    planDiagramBox.classList.add("hidden");

    try {
      const res = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idea,
          constraints: planConstraints.value.trim() || undefined
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Planning engine error");
      }

      const data = await res.json();
      currentPlanMarkdown = data.markdown_report;

      planScorePill.textContent = `Feasibility: ${data.feasibility_score}/100`;
      planMarkdownOutput.innerHTML = window.marked ? marked.parse(data.markdown_report) : `<pre>${data.markdown_report}</pre>`;

      if (data.mermaid_diagram && window.mermaid) {
        planDiagramBox.classList.remove("hidden");
        const uniqueId = `mermaid-${Date.now()}`;
        mermaid.render(uniqueId, data.mermaid_diagram).then(({ svg }) => {
          mermaidRender.innerHTML = svg;
        }).catch(err => {
          console.warn("Mermaid render error:", err);
          mermaidRender.innerHTML = `<pre class="code-font">${data.mermaid_diagram}</pre>`;
        });
      }
    } catch (err) {
      planMarkdownOutput.innerHTML = `<p style="color: var(--accent-rose);">Error: ${err.message}</p>`;
    } finally {
      planLoading.classList.add("hidden");
    }
  });

  btnCopyPlan.addEventListener("click", () => {
    if (currentPlanMarkdown) {
      navigator.clipboard.writeText(currentPlanMarkdown);
      btnCopyPlan.textContent = "Copied!";
      setTimeout(() => (btnCopyPlan.textContent = "Copy Plan"), 2000);
    }
  });

  // --- TAB 2: AUDITOR ---
  const btnAuditSnippet = document.getElementById("btn-audit-snippet");
  const btnAuditPath = document.getElementById("btn-audit-path");
  const snippetGroup = document.getElementById("snippet-input-group");
  const pathGroup = document.getElementById("path-input-group");
  const auditCode = document.getElementById("audit-code");
  const auditPath = document.getElementById("audit-path");
  const btnRunAudit = document.getElementById("btn-run-audit");
  const btnAuditVulnPreset = document.getElementById("btn-audit-vuln-preset");
  const btnAuditRepoPreset = document.getElementById("btn-audit-repo-preset");
  const auditLoading = document.getElementById("audit-loading");
  const auditEmpty = document.getElementById("audit-empty");
  const auditResults = document.getElementById("audit-results-content");
  const auditScoreBadge = document.getElementById("audit-score-badge");
  const tallyCrit = document.getElementById("tally-crit");
  const tallyHigh = document.getElementById("tally-high");
  const tallyMed = document.getElementById("tally-med");
  const tallyLow = document.getElementById("tally-low");
  const pillarsContainer = document.getElementById("pillars-container");
  const findingsList = document.getElementById("findings-list");
  const auditLlmAdvice = document.getElementById("audit-llm-advice");
  const btnExportSarif = document.getElementById("btn-export-sarif");
  const btnExportPdf = document.getElementById("btn-export-pdf");

  let auditMode = "snippet";
  let lastAuditPayload = null;

  btnAuditSnippet.addEventListener("click", () => {
    auditMode = "snippet";
    btnAuditSnippet.classList.add("active");
    btnAuditPath.classList.remove("active");
    snippetGroup.classList.remove("hidden");
    pathGroup.classList.add("hidden");
  });

  btnAuditPath.addEventListener("click", () => {
    auditMode = "path";
    btnAuditPath.classList.add("active");
    btnAuditSnippet.classList.remove("active");
    snippetGroup.classList.add("hidden");
    pathGroup.classList.remove("hidden");
  });

  btnAuditVulnPreset.addEventListener("click", () => {
    auditCode.value = `import os
import subprocess

# Insecure Hardcoded AWS Key
AWS_SECRET_KEY = "AKIA1234567890EXAMPLEKEY"

def query_user_account(user_id, raw_filter):
    # SQL Injection via string interpolation (CWE-89)
    query = f"SELECT * FROM accounts WHERE id = {user_id} AND name = '{raw_filter}'"

    # Command Injection (CWE-78)
    subprocess.call(f"backup.sh {user_id}", shell=True)

    # Remote Code Execution (CWE-94)
    parsed = eval(raw_filter)
    return query
`;
  });

  if (btnAuditRepoPreset) {
    btnAuditRepoPreset.addEventListener("click", () => {
      auditMode = "path";
      btnAuditPath.classList.add("active");
      btnAuditSnippet.classList.remove("active");
      snippetGroup.classList.add("hidden");
      pathGroup.classList.remove("hidden");
      auditPath.value = "https://github.com/mradityasonicse/prodforge";
    });
  }

  btnRunAudit.addEventListener("click", async () => {
    const payload = {};
    if (auditMode === "snippet") {
      const code = auditCode.value.trim();
      if (!code) {
        alert("Please paste code to audit.");
        return;
      }
      payload.raw_code = code;
    } else {
      const p = auditPath.value.trim();
      if (!p) {
        alert("Please enter a local project or file path.");
        return;
      }
      payload.target_path = p;
    }

    lastAuditPayload = payload;
    auditLoading.classList.remove("hidden");
    auditEmpty.classList.add("hidden");
    auditResults.classList.add("hidden");

    try {
      const res = await fetch("/api/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Audit execution failed");
      }

      const data = await res.json();
      renderAuditResults(data);
    } catch (err) {
      alert("Audit Error: " + err.message);
    } finally {
      auditLoading.classList.add("hidden");
    }
  });

  function renderAuditResults(data) {
    auditResults.classList.remove("hidden");
    
    // Animate score counter
    animateCounter(auditScoreBadge, data.readiness_score);
    setTimeout(() => {
      auditScoreBadge.textContent = `${data.readiness_score}/100`;
    }, 850);

    if (data.readiness_score >= 90) {
      auditScoreBadge.style.color = "var(--hn-success)";
      auditScoreBadge.style.borderColor = "rgba(22, 163, 74, 0.4)";
    } else if (data.readiness_score >= 70) {
      auditScoreBadge.style.color = "var(--hn-warning)";
      auditScoreBadge.style.borderColor = "rgba(217, 119, 6, 0.4)";
    } else {
      auditScoreBadge.style.color = "var(--hn-error)";
      auditScoreBadge.style.borderColor = "rgba(220, 38, 38, 0.4)";
    }

    animateCounter(tallyCrit, data.critical_count);
    animateCounter(tallyHigh, data.high_count);
    animateCounter(tallyMed, data.medium_count);
    animateCounter(tallyLow, data.low_count);

    showToast(`Audit Completed: Readiness Score ${data.readiness_score}/100`, data.readiness_score >= 80 ? "success" : "warn");
    logTelemetry(`Audit finished for ${lastAuditPayload.target_path || 'snippet'} -> Score: ${data.readiness_score}/100 (${data.findings ? data.findings.length : 0} issues)`, "success");

    // Render 5-Pillar Scorecard
    if (data.pillars) {
      const p = data.pillars;
      pillarsContainer.innerHTML = `<table>
        <thead>
          <tr>
            <th>Production Dimension</th>
            <th>Weight</th>
            <th>Score</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>1. Security & Vulnerability Shield</strong></td>
            <td>35%</td>
            <td style="color:${p.security_score >= 80 ? 'var(--hn-success)' : 'var(--hn-error)'}; font-weight:bold;">${p.security_score}/100</td>
            <td>${p.security_score >= 80 ? 'Verified Shield' : 'Vulnerabilities Discovered'}</td>
          </tr>
          <tr>
            <td><strong>2. Code Quality & Technical Debt</strong></td>
            <td>20%</td>
            <td style="color:var(--hn-primary); font-weight:bold;">${p.quality_score}/100</td>
            <td>${p.quality_score >= 80 ? 'Clean Code' : 'Smells Detected'}</td>
          </tr>
          <tr>
            <td><strong>3. Architecture & Complexity</strong></td>
            <td>15%</td>
            <td style="color:var(--hn-primary); font-weight:bold;">${p.architecture_score}/100</td>
            <td>${p.architecture_score >= 80 ? 'Low Complexity' : 'High Branching'}</td>
          </tr>
          <tr>
            <td><strong>4. QA & Test Automation</strong></td>
            <td>15%</td>
            <td style="color:var(--hn-primary); font-weight:bold;">${p.test_readiness_score}/100</td>
            <td>${p.test_readiness_score >= 80 ? 'Tests Verified' : 'Coverage Needed'}</td>
          </tr>
          <tr>
            <td><strong>5. DevOps & Container Hardening</strong></td>
            <td>15%</td>
            <td style="color:var(--hn-primary); font-weight:bold;">${p.devops_hardening_score}/100</td>
            <td>${p.devops_hardening_score >= 80 ? 'Production Containers' : 'Hardening Recommended'}</td>
          </tr>
        </tbody>
      </table>`;
    }

    // Render Findings List with Staggered Cascading Animation
    findingsList.innerHTML = "";
    if (data.findings && data.findings.length > 0) {
      data.findings.forEach((f, idx) => {
        const item = document.createElement("div");
        item.className = `finding-item ${f.severity}`;
        item.style.setProperty("--item-idx", idx);
        item.innerHTML = `
          <div class="finding-header">
            <span class="finding-title">[${f.severity}] ${f.title} (${f.rule_id})</span>
            <span class="finding-loc">Line ${f.line_number}</span>
          </div>
          <div class="finding-desc">${f.description}</div>
          ${f.line_content ? `<pre class="code-font" style="margin-bottom:0.4rem; font-size:0.75rem; color:#DC2626;">${escapeHtml(f.line_content)}</pre>` : ''}
          <div class="finding-fix"><strong>Remediation:</strong> ${f.remediation}</div>
        `;
        findingsList.appendChild(item);
      });
    } else {
      findingsList.innerHTML = `<p style="color: var(--hn-success); font-size: 0.92rem;">✓ Zero security vulnerabilities or critical code smells discovered!</p>`;
    }

    if (data.llm_recommendations) {
      auditLlmAdvice.innerHTML = window.marked ? marked.parse(data.llm_recommendations) : `<pre>${data.llm_recommendations}</pre>`;
    }
  }

  btnExportSarif.addEventListener("click", async () => {
    if (!lastAuditPayload) {
      alert("Please execute an audit first to export SARIF.");
      return;
    }
    try {
      const res = await fetch("/api/sarif", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lastAuditPayload)
      });
      const sarifData = await res.json();
      const blob = new Blob([JSON.stringify(sarifData, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "prodforge.sarif";
      a.click();
      URL.revokeObjectURL(url);
      showToast("OASIS SARIF v2.1.0 exported successfully!", "success");
      logTelemetry("SARIF v2.1.0 exported for GitHub Code Scanning", "info");
    } catch (err) {
      showToast("SARIF export error: " + err.message, "error");
    }
  });

  if (btnExportPdf) {
    btnExportPdf.addEventListener("click", async () => {
      if (!lastAuditPayload) {
        showToast("Please execute an audit first to export PDF.", "error");
        return;
      }
      btnExportPdf.textContent = "⏳ Generating PDF...";
      btnExportPdf.disabled = true;
      logTelemetry("Rendering executive vector PDF audit report...", "info");
      try {
        const res = await fetch("/api/pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(lastAuditPayload)
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || "Failed to generate PDF report");
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "prodforge-audit-report.pdf";
        a.click();
        URL.revokeObjectURL(url);
        showToast("Executive PDF report generated and downloaded!", "success");
        logTelemetry("Executive PDF report successfully generated & dispatched", "success");
      } catch (err) {
        showToast("PDF export error: " + err.message, "error");
        logTelemetry("PDF generation error: " + err.message, "error");
      } finally {
        btnExportPdf.textContent = "📄 Export PDF";
        btnExportPdf.disabled = false;
      }
    });
  }

  // --- TAB 3: AUTO-FIXER ---
  const btnRunFix = document.getElementById("btn-run-fix");
  const fixTargetPath = document.getElementById("fix-target-path");
  const fixApplyCheckbox = document.getElementById("fix-apply-checkbox");
  const fixLoading = document.getElementById("fix-loading");
  const fixPatchOutput = document.getElementById("fix-patch-output");
  const btnCopyPatch = document.getElementById("btn-copy-patch");

  btnRunFix.addEventListener("click", async () => {
    const target = fixTargetPath.value.trim() || "D:\\prodforge";
    fixLoading.classList.remove("hidden");
    fixPatchOutput.textContent = "// Synthesizing unified patch...";

    try {
      const res = await fetch("/api/fix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_path: target,
          apply: fixApplyCheckbox.checked
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Auto-fix failed");
      }

      const data = await res.json();
      if (data.unified_patch) {
        fixPatchOutput.textContent = data.unified_patch;
      } else {
        fixPatchOutput.textContent = "// Target code has no auto-fixable vulnerabilities. Already clean!";
      }

      if (data.applied) {
        alert(`Successfully applied ${data.total_fixes_generated} code repair(s) directly to disk!`);
      }
    } catch (err) {
      fixPatchOutput.textContent = `// Auto-fix Error: ${err.message}`;
    } finally {
      fixLoading.classList.add("hidden");
    }
  });

  btnCopyPatch.addEventListener("click", () => {
    if (fixPatchOutput.textContent) {
      navigator.clipboard.writeText(fixPatchOutput.textContent);
      btnCopyPatch.textContent = "Copied!";
      setTimeout(() => (btnCopyPatch.textContent = "Copy Patch"), 2000);
    }
  });

  // --- TAB 4: QA TEST SUITE ---
  const btnRunTest = document.getElementById("btn-run-test");
  const btnQaPreset = document.getElementById("btn-qa-preset");
  const qaCode = document.getElementById("qa-code");
  const qaFramework = document.getElementById("qa-framework");
  const qaLoading = document.getElementById("qa-loading");
  const qaTestOutput = document.getElementById("qa-test-output");
  const btnCopyTest = document.getElementById("btn-copy-test");

  btnQaPreset.addEventListener("click", () => {
    qaCode.value = `def calculate_order_total(subtotal: float, discount_percent: float, tax_rate: float) -> float:
    \"\"\"Calculates final order total applying discount then tax.\"\"\"
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")
    if not (0 <= discount_percent <= 100):
        raise ValueError("Discount percent must be between 0 and 100")
    
    discounted = subtotal * (1 - discount_percent / 100)
    total = discounted * (1 + tax_rate)
    return round(total, 2)
`;
  });

  btnRunTest.addEventListener("click", async () => {
    const code = qaCode.value.trim();
    if (!code) {
      alert("Please provide source code to generate tests for.");
      return;
    }

    qaLoading.classList.remove("hidden");
    qaTestOutput.textContent = "// Synthesizing test suite...";

    try {
      const res = await fetch("/api/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_code: code,
          framework: qaFramework.value
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Test generation failed");
      }

      const data = await res.json();
      qaTestOutput.textContent = data.test_code;
    } catch (err) {
      qaTestOutput.textContent = `// Error: ${err.message}`;
    } finally {
      qaLoading.classList.add("hidden");
    }
  });

  btnCopyTest.addEventListener("click", () => {
    if (qaTestOutput.textContent) {
      navigator.clipboard.writeText(qaTestOutput.textContent);
      btnCopyTest.textContent = "Copied!";
      setTimeout(() => (btnCopyTest.textContent = "Copy Tests"), 2000);
    }
  });

  // --- TAB 5: CONTAINERS & KUBERNETES ---
  const btnRunK8s = document.getElementById("btn-run-k8s");
  const btnRunHarden = document.getElementById("btn-run-harden");
  const k8sAppName = document.getElementById("k8s-app-name");
  const k8sDomain = document.getElementById("k8s-domain");
  const hardenLoading = document.getElementById("harden-loading");
  const hardenContainer = document.getElementById("harden-artifacts-container");

  btnRunK8s.addEventListener("click", async () => {
    hardenLoading.classList.remove("hidden");
    hardenContainer.innerHTML = "";

    try {
      const res = await fetch("/api/k8s", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          app_name: k8sAppName.value.trim() || "prodforge-app",
          domain: k8sDomain.value.trim() || "api.example.com"
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Kubernetes generation failed");
      }

      const data = await res.json();
      hardenContainer.innerHTML = "";
      data.artifacts.forEach(art => {
        const div = document.createElement("div");
        div.style.marginBottom = "1.5rem";
        div.innerHTML = `
          <h4 style="font-size:0.88rem; margin-bottom:0.35rem; color:var(--accent-cyan);">${art.filename} <span style="font-size:0.75rem; color:var(--text-muted); font-weight:normal;">(${art.description})</span></h4>
          <pre class="code-block code-font">${escapeHtml(art.content)}</pre>
        `;
        hardenContainer.appendChild(div);
      });
    } catch (err) {
      hardenContainer.innerHTML = `<p style="color:var(--accent-rose);">Error: ${err.message}</p>`;
    } finally {
      hardenLoading.classList.add("hidden");
    }
  });

  btnRunHarden.addEventListener("click", async () => {
    hardenLoading.classList.remove("hidden");
    hardenContainer.innerHTML = "";

    try {
      const res = await fetch("/api/harden", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_path: "D:\\prodforge",
          apply: false
        })
      });

      const data = await res.json();
      hardenContainer.innerHTML = "";
      data.artifacts.forEach(art => {
        const div = document.createElement("div");
        div.style.marginBottom = "1.5rem";
        div.innerHTML = `
          <h4 style="font-size:0.88rem; margin-bottom:0.35rem; color:var(--accent-cyan);">${art.filename} <span style="font-size:0.75rem; color:var(--text-muted); font-weight:normal;">(${art.description})</span></h4>
          <pre class="code-block code-font">${escapeHtml(art.content)}</pre>
        `;
        hardenContainer.appendChild(div);
      });
    } catch (err) {
      hardenContainer.innerHTML = `<p style="color:var(--accent-rose);">Error: ${err.message}</p>`;
    } finally {
      hardenLoading.classList.add("hidden");
    }
  });

  // --- TAB 6: FINOPS & FEASIBILITY ---
  const btnRunFeas = document.getElementById("btn-run-feas");
  const feasIdea = document.getElementById("feas-idea");
  const feasDau = document.getElementById("feas-dau");
  const feasLoading = document.getElementById("feas-loading");
  const feasEmpty = document.getElementById("feas-empty");
  const feasResults = document.getElementById("feas-results-container");
  const feasCostBadge = document.getElementById("feas-cost-badge");
  const feasPeakRps = document.getElementById("feas-peak-rps");
  const feasCostTable = document.getElementById("feas-cost-table");
  const feasMarkdown = document.getElementById("feas-markdown");

  btnRunFeas.addEventListener("click", async () => {
    const idea = feasIdea.value.trim();
    if (!idea) {
      alert("Please describe the system workload or architecture.");
      return;
    }

    feasLoading.classList.remove("hidden");
    feasEmpty.classList.add("hidden");
    feasResults.classList.add("hidden");

    try {
      const res = await fetch("/api/feasibility", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idea,
          target_dau: parseInt(feasDau.value) || 50000
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "FinOps analysis failed");
      }

      const data = await res.json();
      feasCostBadge.textContent = `$${data.estimated_monthly_cost_usd.toFixed(2)} / mo`;
      feasPeakRps.textContent = data.concurrency_target_rps;

      let tableHtml = `<table>
        <thead>
          <tr>
            <th>Component</th>
            <th>Recommended Service</th>
            <th>Monthly (USD)</th>
            <th>Architecture Notes</th>
          </tr>
        </thead>
        <tbody>`;

      data.cost_breakdown.forEach(item => {
        tableHtml += `<tr>
          <td><strong>${item.component}</strong></td>
          <td>${item.recommended_service}</td>
          <td style="color:var(--accent-emerald); font-weight:bold;">$${item.monthly_estimate_usd.toFixed(2)}</td>
          <td>${item.notes}</td>
        </tr>`;
      });
      tableHtml += `</tbody></table>`;
      feasCostTable.innerHTML = tableHtml;

      feasMarkdown.innerHTML = window.marked ? marked.parse(data.executive_markdown) : `<pre>${data.executive_markdown}</pre>`;
      feasResults.classList.remove("hidden");
    } catch (err) {
      alert("Feasibility Error: " + err.message);
    } finally {
      feasLoading.classList.add("hidden");
    }
  });

  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
  }
});
