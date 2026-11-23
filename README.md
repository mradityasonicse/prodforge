# ⚡ ProdForge — Autonomous Production AI Suite & Studio

> **Transform raw ideas and code into hardened, verified, production-ready systems.**

ProdForge is an autonomous AI agent and engineering suite built to take any system idea or messy codebase and elevate it to top-tier production standards:
- **Architecture & System Planner:** Translates raw concepts into production architectures, C4 diagrams, ER database schemas, STRIDE threat models, and phased execution roadmaps.
- **Deep Code Auditor & Telemetry:** Scans codebases for OWASP Top 10 vulnerabilities, hardcoded secrets, SQL/Command injections, complexity smells, and calculates a **Production Readiness Score (0-100)**.
- **Autonomous QA Test Generator:** Derives function signatures and generates comprehensive test suites (pytest, Vitest, Jest) with boundary checks, exceptions, and mock fixtures.
- **Production Hardener:** Autonomously generates multi-stage non-root Dockerfiles, `docker-compose.yml`, GitHub Actions CI/CD gates, and Kubernetes liveness/readiness probes.
- **FinOps & Scaling Feasibility Engine:** Computes peak RPS thresholds, concurrency limits, itemized monthly cloud infrastructure costs, and single-point-of-failure bottlenecks.
- **Interactive Web Studio:** A cyber-sleek, dark-mode real-time dashboard featuring live Mermaid diagram rendering, interactive code scanning, and telemetry meters.

---

## 🚀 Quickstart & Installation

ProdForge is installed locally in Drive `D:\prodforge`.

```powershell
cd D:\prodforge

# View available commands
python -m prodforge --help

# Inspect configured providers and models
python -m prodforge config
```

### Environment Configuration
ProdForge works **100% out-of-the-box in Offline Heuristic Mode** without needing any API key or internet access!

To unlock multi-provider dynamic LLM synthesis, copy `.env.example` to `.env` and add any of your preferred API keys:
```env
# Google Gemini
GEMINI_API_KEY=AIzaSy...

# OpenAI / Groq / Anthropic / OpenRouter
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
ANTHROPIC_API_KEY=sk-ant-...

# Or use local Ollama
OLLAMA_HOST=http://localhost:11434
```

---

## 🛠️ CLI Commands & Usage

### 1. Architecture & Execution Planner
```powershell
python -m prodforge plan "Real-time collaborative canvas with CRDT synchronization and WebSockets" --constraints "FastAPI, PostgreSQL, Redis" --out blueprint.md
```

### 2. Deep Code Auditor & Production Readiness Scorecard
```powershell
python -m prodforge audit D:\prodforge --out audit_report.md
```
Outputs a full telemetry card, cyclomatic complexity estimates, line counts, discovered vulnerabilities, and prioritized remediation steps.

### 3. Autonomous QA Suite Generator
```powershell
python -m prodforge test src/prodforge/config.py --out tests/test_generated.py
```

### 4. Production Hardener
```powershell
# Preview hardening assets
python -m prodforge harden D:\prodforge

# Automatically apply Dockerfile, compose, and CI/CD gates to disk
python -m prodforge harden D:\prodforge --apply
```

### 5. FinOps & Feasibility Engine
```powershell
python -m prodforge feasibility "FinTech order matching engine with ledger audit" --dau 100000
```

### 6. Interactive Web Studio
```powershell
python -m prodforge studio --port 8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to access the interactive web interface.

---

## 🏛️ Architecture & Project Structure

```
D:\prodforge\
├── pyproject.toml              # Dependencies & CLI entry point
├── README.md                   # Complete documentation
├── .env.example                # Provider template
├── src\
│   └── prodforge\
│       ├── __init__.py         # Package exports & version
│       ├── __main__.py         # python -m prodforge execution
│       ├── config.py           # Multi-provider configuration manager
│       ├── client.py           # Multi-LLM client (Gemini, OpenAI, Groq, Ollama, Offline)
│       ├── cli.py              # Interactive Rich Typer CLI
│       ├── engines\
│       │   ├── planner.py      # Architecture, C4 Mermaid, STRIDE, Roadmap
│       │   ├── auditor.py      # Static + AST + LLM Code Auditor (0-100 score)
│       │   ├── qa_tester.py    # Test generation (pytest/vitest) with edge cases
│       │   ├── hardener.py     # Dockerfile, docker-compose, CI/CD, healthchecks
│       │   └── feasibility.py  # FinOps cost models, RPS capacity, bottlenecks
│       ├── static_rules\
│       │   ├── security_rules.py # OWASP Top 10, Secrets, SQLi, RCE, Shell, XSS
│       │   └── quality_rules.py  # Error swallowing, debug prints, loose types
│       └── studio\
│           ├── server.py       # FastAPI backend & WebSocket server
│           └── static\
│               ├── index.html  # Cyberpunk Bento grid UI
│               ├── styles.css  # Bespoke glassmorphism styling
│               └── app.js      # Mermaid.js + REST controller
└── tests\
    ├── test_config.py
    ├── test_static_rules.py
    ├── test_engines.py
    └── test_studio_api.py
```

---

## 🧪 Verification & Testing

Run the full automated test suite:
```powershell
python -m pytest D:\prodforge\tests -v
```
All 24 unit and integration tests pass with 100% verification.
