# ⚡ ProdForge — Autonomous Production AI Suite & Studio

> **Transform raw ideas and code into hardened, verified, production-ready systems.**

ProdForge is an autonomous AI agent and engineering suite built to take any system idea or messy codebase and elevate it to top-tier production standards:
- **Architecture & System Planner:** Translates raw concepts into production architectures, C4 diagrams, ER database schemas, STRIDE threat models, and phased execution roadmaps.
- **Deep Code Auditor & Telemetry:** Scans codebases for OWASP Top 10 vulnerabilities, hardcoded secrets, SQL/Command injections, complexity smells, and calculates a **Production Readiness Score (0-100)**.
- **Autonomous QA Test Generator:** Derives function signatures and generates comprehensive test suites (pytest, Vitest, Jest) with boundary checks, exceptions, and mock fixtures.
- **Production Hardener:** Autonomously generates multi-stage non-root Dockerfiles, `docker-compose.yml`, GitHub Actions CI/CD gates, and Kubernetes liveness/readiness probes.
- **FinOps & Scaling Feasibility Engine:** Computes peak RPS thresholds, concurrency limits, itemized monthly cloud infrastructure costs, and single-point-of-failure bottlenecks.
- **Interactive Web Studio:** A cyber-sleek, dark-mode real-time dashboard featuring live Mermaid diagram rendering, interactive code scanning, and telemetry meters.
- **Instant Public Tunnel Sharing:** Expose your local Web Studio to the entire world over secure HTTPS via built-in Cloudflare Tunnel integration (`prodforge share`).

---

## 🚀 Quickstart

Run directly from any terminal:

```powershell
# View all commands
prodforge --help

# Inspect detected providers & models
prodforge config
```

### Environment Configuration
ProdForge works **100% out-of-the-box in Offline Heuristic Mode** without needing any API key or internet access!

To unlock multi-provider dynamic LLM synthesis, copy `.env.example` to `.env` in `D:\prodforge` and add your preferred API keys:
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

## ⚡ Quick Command Cheatsheet (In Simple Words)

| What you want to do | Command to run | What it does |
|:---|:---|:---|
| 🔍 **Scan any file for bugs & security holes** | `prodforge audit app.py` | Scans the file and gives it a 0-100 Production Readiness Score. |
| 🌐 **Scan an entire GitHub repo directly** | `prodforge audit https://github.com/user/repo` | Clones, audits all files, and outputs vulnerabilities. |
| 📊 **Generate a visual HTML report** | `prodforge audit . --html report.html` | Creates an executive HTML dashboard you can open in any browser. |
| 🛡️ **Export SARIF for GitHub Code Scanning** | `prodforge audit . --sarif report.sarif` | Generates official OASIS SARIF v2.1.0 report for CI/CD gates. |
| 🛠️ **Auto-fix vulnerabilities in code** | `prodforge fix app.py --apply` | Automatically fixes security bugs, removes leaks, and saves file. |
| 💡 **Turn any idea into system architecture** | `prodforge plan "Food delivery app"` | Creates C4 system design, database schemas, and roadmaps. |
| 🧪 **Auto-generate complete test suites** | `prodforge test app.py --out test_app.py` | Automatically writes pytest / unit tests with edge cases. |
| ☸️ **Generate enterprise Kubernetes manifests** | `prodforge k8s .` | Creates production-ready Deployment, Service, and Ingress YAMLs. |
| 🚀 **Generate GitHub Actions CI/CD gate** | `prodforge ci` | Creates a workflow that blocks insecure Pull Requests. |
| 🖥️ **Open visual web dashboard** | `prodforge studio` | Opens interactive browser UI at `http://localhost:8000`. |
| 🌍 **Share web studio globally with anyone** | `prodforge share` | Gives you a public HTTPS link to share with anyone worldwide. |
| ⚙️ **Check connected AI models & keys** | `prodforge config` | Shows whether Gemini, OpenAI, or Offline mode is active. |

---

## 🛠️ Detailed CLI Commands & Usage

### 1. Instant Public Web Studio Sharing
```powershell
prodforge share
```
*Starts the local Web Studio and generates an instant, secure public HTTPS URL (e.g. `https://xxxx.trycloudflare.com`) accessible from any mobile, tablet, or external computer worldwide.*

### 2. Local Interactive Web Studio
```powershell
prodforge studio --port 8000
```
*Opens [http://127.0.0.1:8000](http://127.0.0.1:8000) in your default browser.*

### 3. Architecture & Execution Planner
```powershell
prodforge plan "Real-time collaborative canvas with CRDT synchronization and WebSockets" --constraints "FastAPI, PostgreSQL, Redis" --out blueprint.md
```

### 4. Deep Code Auditor & Production Readiness Scorecard (0–100)
```powershell
prodforge audit D:\prodforge --out audit_report.md
```

### 5. Autonomous QA Suite Generator
```powershell
prodforge test src/prodforge/config.py --out tests/test_generated.py
```

### 6. Production Hardener
```powershell
# Preview hardening assets
prodforge harden D:\prodforge

# Automatically apply Dockerfile, compose, and CI/CD gates to disk
prodforge harden D:\prodforge --apply
```

### 7. FinOps & Feasibility Engine
```powershell
prodforge feasibility "FinTech order matching engine with ledger audit" --dau 100000
```

---

## 🌐 How to Make ProdForge Public

### Method 1: Instant Public URL (Live in 5 Seconds)
Run:
```powershell
prodforge share
```
Cloudflare Tunnel will output a public HTTPS link (e.g. `https://random-words.trycloudflare.com`). Share this link with friends or colleagues!

### Method 2: Publish as Public Open-Source on GitHub
Your GitHub CLI (`gh`) is already logged in! Run:
```powershell
cd D:\prodforge
gh repo create prodforge --public --source=. --push
```
Your code will instantly be live on GitHub at `https://github.com/mradityasonicse/prodforge`.

### Method 3: Publish to PyPI (`pip install prodforge`)
To allow any developer in the world to install your tool:
```powershell
cd D:\prodforge
python -m pip install build twine
python -m build
twine upload dist/*
```

### Method 4: Permanent 24/7 Cloud Hosting (Render / Railway / Hugging Face)
1. Push your repository to GitHub (Method 2).
2. Go to [render.com](https://render.com) or [railway.app](https://railway.app).
3. Connect your GitHub repository.
4. Select **Docker** or **Python** environment, set start command to:
   ```bash
   uvicorn prodforge.studio.server:app --host 0.0.0.0 --port 8000
   ```
5. Your studio will be live 24/7 on a permanent custom domain with free SSL!

---

## 🧪 Automated Testing
```powershell
python -m pytest D:\prodforge\tests -v
```
All 24 test suites pass with 100% verification.
