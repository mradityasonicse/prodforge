// ProdForge Studio - Frontend Interactive Controller
document.addEventListener("DOMContentLoaded", () => {
  // Initialize Mermaid
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

  // --- INITIAL STATUS CHECK ---
  fetchStatus();

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
    planIdea.value = "Autonomous multi-currency crypto & fiat payment settlement gateway with idempotency keys, double-entry ledger in PostgreSQL, sub-second WebSocket order updates, and Redis distributed lock.";
    planConstraints.value = "FastAPI (Python), PostgreSQL, Redis, Docker, Zero-Trust TLS 1.3, STRIDE threat model";
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

      // Render Mermaid if diagram exists
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
  const auditLoading = document.getElementById("audit-loading");
  const auditEmpty = document.getElementById("audit-empty");
  const auditResults = document.getElementById("audit-results-content");
  const auditScoreBadge = document.getElementById("audit-score-badge");
  const tallyCrit = document.getElementById("tally-crit");
  const tallyHigh = document.getElementById("tally-high");
  const tallyMed = document.getElementById("tally-med");
  const tallyLow = document.getElementById("tally-low");
  const findingsList = document.getElementById("findings-list");
  const auditLlmAdvice = document.getElementById("audit-llm-advice");

  let auditMode = "snippet";

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

# Insecure Hardcoded API Key Exposure
AWS_SECRET_KEY = "AKIA1234567890EXAMPLEKEY"

def execute_user_query(user_id, raw_filter):
    # SQL Injection via string interpolation
    query = f"SELECT * FROM accounts WHERE id = {user_id} AND name = '{raw_filter}'"
    print(f"Executing: {query}")  # Dirty print in production

    try:
        # Command Injection risk
        subprocess.call(f"backup.sh {user_id}", shell=True)
    except:
        pass  # Blind silent error swallowing

    # Dangerous eval
    parsed = eval(raw_filter)
    return query
`;
  });

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
    auditScoreBadge.textContent = `${data.readiness_score}/100`;

    if (data.readiness_score >= 90) {
      auditScoreBadge.style.color = "var(--accent-emerald)";
      auditScoreBadge.style.borderColor = "rgba(16, 185, 129, 0.4)";
    } else if (data.readiness_score >= 70) {
      auditScoreBadge.style.color = "var(--accent-amber)";
      auditScoreBadge.style.borderColor = "rgba(245, 158, 11, 0.4)";
    } else {
      auditScoreBadge.style.color = "var(--accent-rose)";
      auditScoreBadge.style.borderColor = "rgba(244, 63, 94, 0.4)";
    }

    tallyCrit.textContent = data.critical_count;
    tallyHigh.textContent = data.high_count;
    tallyMed.textContent = data.medium_count;
    tallyLow.textContent = data.low_count;

    findingsList.innerHTML = "";
    if (data.findings && data.findings.length > 0) {
      data.findings.forEach(f => {
        const item = document.createElement("div");
        item.className = `finding-item ${f.severity}`;
        item.innerHTML = `
          <div class="finding-header">
            <span class="finding-title">[${f.severity}] ${f.title} (${f.rule_id})</span>
            <span class="finding-loc">Line ${f.line_number}</span>
          </div>
          <div class="finding-desc">${f.description}</div>
          ${f.line_content ? `<pre class="code-font" style="margin-bottom:0.4rem; font-size:0.75rem; color:#F87171;">${f.line_content}</pre>` : ''}
          <div class="finding-fix"><strong>Remediation:</strong> ${f.remediation}</div>
        `;
        findingsList.appendChild(item);
      });
    } else {
      findingsList.innerHTML = `<p style="color: var(--accent-emerald); font-size: 0.88rem;">✓ No security vulnerabilities or critical code smells discovered!</p>`;
    }

    if (data.llm_recommendations) {
      auditLlmAdvice.innerHTML = window.marked ? marked.parse(data.llm_recommendations) : `<pre>${data.llm_recommendations}</pre>`;
    }
  }

  // --- TAB 3: QA TEST SUITE ---
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

  // --- TAB 4: HARDENER ---
  const btnRunHarden = document.getElementById("btn-run-harden");
  const hardenPath = document.getElementById("harden-path");
  const hardenApply = document.getElementById("harden-apply");
  const hardenLoading = document.getElementById("harden-loading");
  const hardenContainer = document.getElementById("harden-artifacts-container");
  const hardenStackBadge = document.getElementById("harden-stack-badge");

  btnRunHarden.addEventListener("click", async () => {
    const path = hardenPath.value.trim() || ".";
    hardenLoading.classList.remove("hidden");
    hardenContainer.innerHTML = "";

    try {
      const res = await fetch("/api/harden", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_path: path,
          apply: hardenApply.checked
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Hardening failed");
      }

      const data = await res.json();
      hardenStackBadge.textContent = data.detected_stack.toUpperCase();

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

      if (data.applied) {
        alert("Production hardening files successfully created on disk!");
      }
    } catch (err) {
      hardenContainer.innerHTML = `<p style="color:var(--accent-rose);">Error: ${err.message}</p>`;
    } finally {
      hardenLoading.classList.add("hidden");
    }
  });

  // --- TAB 5: FINOPS & FEASIBILITY ---
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
